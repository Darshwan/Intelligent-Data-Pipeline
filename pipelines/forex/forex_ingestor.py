import asyncio
import json
import logging
import os
import random
import aiohttp
from aiokafka import AIOKafkaProducer
import asyncpg
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_TOPIC = "raw.forex"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/nepaldatalab")
POLL_INTERVAL = 300  # 5 minutes
NRB_API_URL = "https://www.nrb.org.np/api/forex/v1/rates?page=1&per_page=1&from={}&to={}"

# Major currencies to track
CURRENCIES = ["USD", "EUR", "GBP", "AUD", "JPY", "INR"]

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    return producer

def generate_mock_forex():
    data = []
    base_rates = {
        "USD": 133.5,
        "EUR": 145.2,
        "GBP": 168.9,
        "AUD": 87.5,
        "JPY": 0.89,
        "INR": 1.6
    }
    
    timestamp = datetime.now()
    
    for currency, base in base_rates.items():
        # Fluctuation
        variance = base * 0.01 
        buy = round(base + random.uniform(-variance, variance), 2)
        sell = round(buy * (1 + random.uniform(0.005, 0.015)), 2) # Sell is slightly higher
        
        data.append({
            "currency": currency,
            "buy": buy,
            "sell": sell,
            "unit": 10 if currency == "JPY" else 1, # JPY usually per 10
            "timestamp": timestamp
        })
    return data

async def save_to_db(pool, rates):
    try:
        query = """
            INSERT INTO forex_rates (time, currency, buy, sell, unit)
            VALUES ($1, $2, $3, $4, $5)
        """
        async with pool.acquire() as conn:
            async with conn.transaction():
                for rate in rates:
                    await conn.execute(
                        query,
                        rate['timestamp'],
                        rate['currency'],
                        rate['buy'],
                        rate['sell'],
                        rate['unit']
                    )
        logger.info(f"Saved {len(rates)} forex rates to DB")
    except Exception as e:
        logger.error(f"Error saving forex to DB: {e}")

async def run_forex_ingestion():
    logger.info("Starting Forex Ingestor Service")
    
    await asyncio.sleep(10) # Wait for dependencies

    producer = await get_kafka_producer()
    
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        return

    while True:
        logger.info("Fetching forex data...")
        
        # Use mock for reliability in MVP
        rates = generate_mock_forex()
        
        if rates:
            # 1. Produce to Kafka
            for rate in rates:
                try:
                    msg = rate.copy()
                    msg['timestamp'] = msg['timestamp'].isoformat()
                    await producer.send_and_wait(KAFKA_TOPIC, json.dumps(msg).encode('utf-8'))
                except Exception as e:
                    logger.error(f"Failed to produce to Kafka: {e}")
            
            # 2. Save to DB
            await save_to_db(pool, rates)
        
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(run_forex_ingestion())
    except KeyboardInterrupt:
        logger.info("Forex Ingestor stopped.")
