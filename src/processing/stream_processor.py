import faust
import logging
import os
import json
from datetime import datetime
from correlation_engine import CorrelationEngine

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
    store=f'redis://{REDIS_URL}',
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

@app.agent(weather_topic)
async def process_weather(stream):
    async for value in stream:
        try:
            data = json.loads(value.decode('utf-8'))
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
            event = json.loads(value.decode('utf-8'))
            logger.info(f"Processing earthquake: {event.get('id')}")

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
