import asyncio
import json
import logging
import os
import aiohttp
from aiokafka import AIOKafkaProducer
import asyncpg
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
KAFKA_TOPIC = "raw.usgs.earthquakes"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/nepaldatalab")
POLL_INTERVAL = 60  # seconds

# Nepal Bounding Box (approx)
NEPAL_LAT_MIN = 26.0
NEPAL_LAT_MAX = 31.0
NEPAL_LON_MIN = 80.0
NEPAL_LON_MAX = 89.0

async def get_kafka_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )
    await producer.start()
    return producer

async def fetch_earthquakes(session):
    try:
        async with session.get(USGS_API_URL) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Failed to fetch data from USGS: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

def is_in_nepal_region(feature):
    try:
        coords = feature['geometry']['coordinates']
        lon = coords[0]
        lat = coords[1]
        return (NEPAL_LAT_MIN <= lat <= NEPAL_LAT_MAX) and (NEPAL_LON_MIN <= lon <= NEPAL_LON_MAX)
    except (KeyError, IndexError):
        return False

async def save_to_db(pool, feature):
    try:
        props = feature['properties']
        geom = feature['geometry']['coordinates']
        
        # Geometry is typically [lon, lat, depth]
        lon, lat, depth = geom[0], geom[1], geom[2]
        event_id = feature['id']
        time_ms = props['time']
        timestamp = datetime.fromtimestamp(time_ms / 1000.0)
        
        query = """
            INSERT INTO earthquakes (id, time, latitude, longitude, depth, magnitude, place, location)
            VALUES ($1, $2, $3, $4, $5, $6, $7, ST_SetSRID(ST_MakePoint($8, $9), 4326))
            ON CONFLICT (id, time) DO NOTHING
        """
        
        await pool.execute(
            query,
            event_id,
            timestamp,
            lat,
            lon,
            depth,
            props['mag'],
            props['place'],
            lon,
            lat
        )
        logger.info(f"Saved earthquake {event_id} to DB")
    except Exception as e:
        logger.error(f"Error saving to DB: {e}")

async def main():
    logger.info("Starting Earthquake Ingestor Service")
    
    # Wait for services to be ready (naive approach, rely on restart policy in real prod)
    await asyncio.sleep(10) 

    producer = await get_kafka_producer()
    
    # Connect to DB
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            logger.info("Fetching earthquake data...")
            data = await fetch_earthquakes(session)
            
            if data and 'features' in data:
                count = 0
                for feature in data['features']:
                    if is_in_nepal_region(feature):
                        # 1. Produce to Kafka
                        try:
                            value_json = json.dumps(feature).encode('utf-8')
                            await producer.send_and_wait(KAFKA_TOPIC, value_json)
                            logger.info(f"Produced event to Kafka: {feature['id']}")
                        except Exception as e:
                            logger.error(f"Failed to send to Kafka: {e}")
                        
                        # 2. Save to DB directly (for MVP simplicity per plan)
                        await save_to_db(pool, feature)
                        count += 1
                
                logger.info(f"Processed {len(data['features'])} events. {count} were in Nepal region.")
            
            await asyncio.sleep(POLL_INTERVAL)

    await producer.stop()
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
