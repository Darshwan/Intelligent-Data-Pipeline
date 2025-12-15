import asyncio
import json
import logging
import os
import random
from datetime import datetime
from aiokafka import AIOKafkaProducer
import asyncpg

logger = logging.getLogger(__name__)

# Configuration
KAFKA_TOPIC = "raw.flood"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/nepaldatalab")
POLL_INTERVAL = 60  # 1 minute

# Major stations and their thresholds (meters)
STATIONS = [
    {"name": "Koshi (Chatara)", "warning": 6.0, "danger": 8.0},
    {"name": "Narayani (Devghat)", "warning": 7.3, "danger": 9.0},
    {"name": "Karnali (Chisapani)", "warning": 10.0, "danger": 10.8},
    {"name": "Bagmati (Khokana)", "warning": 3.5, "danger": 4.0},
    {"name": "Babai (Chepang)", "warning": 5.5, "danger": 6.5}
]

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    return producer

def generate_flood_data(station):
    # Simulate somewhat realistic fluctuation around safe/warning levels
    # 80% chance of normal, 15% warning, 5% danger for demo purposes
    rand_val = random.random()
    
    if rand_val < 0.8:
        base = station['warning'] * 0.5
        level = base + random.uniform(-0.5, 1.0)
    elif rand_val < 0.95:
        # Warning zone
        level = station['warning'] + random.uniform(0.0, (station['danger'] - station['warning']) * 0.9)
    else:
        # Danger zone
        level = station['danger'] + random.uniform(0.1, 2.0)
    
    level = round(level, 2)
    
    status = "Normal"
    if level >= station['danger']:
        status = "Danger"
    elif level >= station['warning']:
        status = "Warning"
    
    return {
        "station": station['name'],
        "water_level": level,
        "warning_level": station['warning'],
        "danger_level": station['danger'],
        "status": status,
        "timestamp": datetime.now()
    }

async def save_to_db(pool, data):
    try:
        query = """
            INSERT INTO flood_alerts (time, station, water_level, warning_level, danger_level, status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        await pool.execute(
            query,
            data['timestamp'],
            data['station'],
            data['water_level'],
            data['warning_level'],
            data['danger_level'],
            data['status']
        )
        logger.info(f"Saved flood status for {data['station']}: {data['status']}")
    except Exception as e:
        logger.error(f"Error saving flood data to DB: {e}")

async def run_flood_ingestion():
    logger.info("Starting Flood Alert Ingestor Service")
    
    await asyncio.sleep(20) # Wait a bit after other services

    producer = await get_kafka_producer()
    
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        return

    while True:
        logger.info("Generating flood simulation data...")
        
        for station in STATIONS:
            data = generate_flood_data(station)
            
            # 1. Produce to Kafka
            try:
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
        asyncio.run(run_flood_ingestion())
    except KeyboardInterrupt:
        logger.info("Flood Ingestor stopped.")
