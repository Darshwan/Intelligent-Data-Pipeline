import requests
import time
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from .config import settings
from .models import USGSResponse, Earthquake
from .monitoring import INGESTION_ERRORS, REQUEST_LATENCY

logger = logging.getLogger(__name__)

def fetch_earthquakes() -> List[Earthquake]:
    """
    Fetches earthquake data from USGS API.
    Handles errors and reports metrics.
    """
    start_time = time.time()
    try:
        # Calculate time window (e.g., last 24 hours)
        endtime = datetime.utcnow()
        starttime = endtime - timedelta(days=1)
        
        params = {
            "format": "geojson",
            "starttime": starttime.isoformat(),
            "endtime": endtime.isoformat(),
            "minmagnitude": 2.5,
            # Optional: Filter by Nepal region if needed, or get global
            # "minlatitude": settings.NEPAL_MIN_LAT,
            # "maxlatitude": settings.NEPAL_MAX_LAT,
            # "minlongitude": settings.NEPAL_MIN_LON,
            # "maxlongitude": settings.NEPAL_MAX_LON,
        }

        response = requests.get(settings.USGS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Validate with Pydantic
        usgs_response = USGSResponse(**data)
        
        logger.info(f"Fetched {len(usgs_response.features)} earthquakes.")
        return usgs_response.features

    except requests.exceptions.RequestException as e:
        logger.error(f"USGS API Request failed: {e}")
        INGESTION_ERRORS.inc()
        return []
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        INGESTION_ERRORS.inc()
        return []
    finally:
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)
