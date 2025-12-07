import asyncio
import json
import logging
import os
import random
import aiohttp
from aiokafka import AIOKafkaProducer
import asyncpg
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
KAFKA_TOPIC = "raw.weather"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/nepaldatalab")
POLL_INTERVAL = 300  # 5 minutes

CITIES = [
    {"name": "Kathmandu", "lat": 27.7172, "lon": 85.3240},
    {"name": "Pokhara", "lat": 28.2096, "lon": 83.9856},
    {"name": "Biratnagar", "lat": 26.4525, "lon": 87.2718},
    {"name": "Lalitpur", "lat": 27.6766, "lon": 85.3206},
    {"name": "Bharatpur", "lat": 27.6833, "lon": 84.4333}
]

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    return producer

async def fetch_real_weather(session, city):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "city": city['name'],
                    "temp": data['main']['temp'],
                    "humidity": data['main']['humidity'],
                    "pressure": data['main']['pressure'],
                    "condition": data['weather'][0]['main'],
                    "timestamp": datetime.now()
                }
            else:
                logger.error(f"Failed to fetch weather for {city['name']}: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return None

def generate_mock_weather(city):
    # Simulate valid ranges for Nepal
    return {
        "city": city['name'],
        "temp": round(random.uniform(10, 35), 2),
        "humidity": round(random.uniform(40, 90), 2),
        "pressure": round(random.uniform(1000, 1020), 2),
        "condition": random.choice(["Clear", "Clouds", "Rain", "Mist"]),
        "timestamp": datetime.now()
    }

async def save_to_db(pool, data):
    try:
        query = """
            INSERT INTO weather_measurements (time, city, temperature, humidity, pressure, condition)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        await pool.execute(
            query,
            data['timestamp'],
            data['city'],
            data['temp'],
            data['humidity'],
            data['pressure'],
            data['condition']
        )
        logger.info(f"Saved weather for {data['city']} to DB")
    except Exception as e:
        logger.error(f"Error saving weather to DB: {e}")

async def run_weather_ingestion():
    logger.info("Starting Weather Ingestor Service")
    
    # Wait for services
    await asyncio.sleep(15)

    producer = await get_kafka_producer()
    
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            logger.info("Fetching weather data...")
            
            for city in CITIES:
                if OPENWEATHER_API_KEY:
                    data = await fetch_real_weather(session, city)
                else:
                    data = generate_mock_weather(city)
                
                if data:
                    # 1. Produce to Kafka
                    try:
                        # Convert datetime to str for JSON serialization
                        msg = data.copy()
                        msg['timestamp'] = msg['timestamp'].isoformat()
                        await producer.send_and_wait(KAFKA_TOPIC, json.dumps(msg).encode('utf-8'))
                    except Exception as e:
                        logger.error(f"Failed to produce to Kafka: {e}")
                    
                    # 2. Save directly to DB
                    await save_to_db(pool, data)
            
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    try:
        asyncio.run(run_weather_ingestion())
    except KeyboardInterrupt:
        logger.info("Weather Ingestor stopped.")
