import faust
import logging
import os
import json
from datetime import datetime
from correlation_engine import CorrelationEngine

# Monkey Patch for Faust Stores TypeError
from faust.tables import table
from faust import stores
def _new_store_by_url(self, url):
    return stores.by_url(url)(
        url,
        app=self.app,
        table=self,
    )
table.Table._new_store_by_url = _new_store_by_url

# Configure Logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Initialize Faust App
app = faust.App(
    'nepal-data-hub-processor',
    broker=f'kafka://{KAFKA_BROKER}',
    # store='memory://', # Use in-memory to avoid faust-streaming bug
)

# Topics
earthquake_topic = app.topic('raw.usgs.earthquakes', value_type=bytes)
weather_topic = app.topic('raw.weather', value_type=bytes)
flood_topic = app.topic('raw.flood', value_type=bytes)

# Output Alert Topic
alerts_topic = app.topic('processed.alerts', value_type=bytes)

# Models (Faust Records)
# For simplicity in this iteration, we treat incoming data as dictionaries (json)

# State Tables
# Store latest weather per city to use for correlation
weather_table = app.Table('weather_state', default=dict)

correlation_engine = CorrelationEngine()

from schemas.models import EarthquakeEvent, WeatherMeasurement
from pydantic import ValidationError

@app.agent(weather_topic)
async def process_weather(stream):
    async for value in stream:
        try:
            if isinstance(value, dict):
                data = value
            else:
                data = json.loads(value.decode('utf-8'))
            # Schema Validation
            try:
                WeatherMeasurement(**data)
            except ValidationError as ve:
                logger.error(f"SCHEMA VIOLATION [Weather]: {ve}")
                continue # Skip invalid data (Simulates DLQ)

            city = data.get('city')
            if city:
                weather_table[city] = data
                logger.debug(f"Updated weather state for {city}")
        except Exception as e:
            logger.error(f"Error processing weather stream: {e}")

@app.agent(earthquake_topic)
async def process_earthquakes(stream):
    async for value in stream:
        try:
            if isinstance(value, dict):
                event_dict = value
            else:
                event_dict = json.loads(value.decode('utf-8'))
            
            # Schema Validation
            try:
                EarthquakeEvent(**event_dict)
            except ValidationError as ve:
                logger.error(f"SCHEMA VIOLATION [Earthquake]: {ve}")
                continue

            logger.info(f"Processing earthquake: {event_dict.get('id')}")

            # 1. Fetch latest weather state
            current_weather = list(weather_table.values())
            
            # 2. Run Correlation Engine
            risk = correlation_engine.evaluate_landslide_risk(event, current_weather)
            
            if risk['level'] in ["MEDIUM", "HIGH"]:
                logger.warning(f"Risk Detected: {risk}")
                # Send to Alert Topic
                await alerts_topic.send(value=json.dumps(risk).encode('utf-8'))
                
        except Exception as e:
            logger.error(f"Error processing earthquake stream: {e}")

if __name__ == '__main__':
    app.main()
