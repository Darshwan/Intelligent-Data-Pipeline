from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional

class EarthquakeFeatures(BaseModel):
    mag: float
    place: str
    time: int
    url: str
    title: str

    @field_validator('mag')
    def validate_magnitude(cls, v):
        if v is None:
            return 0.0 # Handle null magnitudes occasionally returned by USGS
        return v

class EarthquakeGeometry(BaseModel):
    type: str
    coordinates: List[float] # [longitude, latitude, depth]

class Earthquake(BaseModel):
    id: str
    type: str
    properties: EarthquakeFeatures
    geometry: EarthquakeGeometry

class USGSResponse(BaseModel):
    type: str
    features: List[Earthquake]
