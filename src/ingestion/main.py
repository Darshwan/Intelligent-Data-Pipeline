import asyncio
import logging
from earthquake_ingestor import main as earthquake_main
from weather_ingestor import run_weather_ingestion
from flood_scraper import run_flood_ingestion

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_all():
    logger.info("Starting All Ingestion Services...")
    await asyncio.gather(
        earthquake_main(),
        run_weather_ingestion(),
        run_flood_ingestion()
    )

if __name__ == "__main__":
    try:
        asyncio.run(run_all())
    except KeyboardInterrupt:
        logger.info("Services stopped.")
