from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# --- Core Event Models ---

class EarthquakeEvent(BaseModel):
    id: str
    time: datetime
    latitude: float
    longitude: float
    depth: float
    magnitude: float
    place: str
    location_label: Optional[str] = None # Enriched field

class WeatherMeasurement(BaseModel):
    city: str
    time: datetime
    temp: float
    humidity: float
    pressure: float
    condition: str

class FloodAlert(BaseModel):
    station: str
    time: datetime
    water_level: float
    warning_level: float
    danger_level: float
    status: str

class ForexRate(BaseModel):
    currency: str
    time: datetime
    buy: float
    sell: float
    unit: int
