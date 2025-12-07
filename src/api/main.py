from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import os
from datetime import datetime

# Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/nepaldatalab")

app = FastAPI(
    title="Nepal Data Hub API",
    description="Real-time Multi-Source Analytics Platform for Nepal",
    version="0.1.0"
)

# Database Connection
async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@app.on_event("startup")
async def startup():
    app.state.pool = await get_db_pool()

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

# Models
class Earthquake(BaseModel):
    id: str
    time: datetime
    latitude: float
    longitude: float
    depth: Optional[float]
    magnitude: Optional[float]
    place: Optional[str]

    class Config:
        from_attributes = True

class Weather(BaseModel):
    time: datetime
    city: str
    temperature: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]
    condition: Optional[str]

    class Config:
        from_attributes = True

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to Nepal Data Hub API"}

@app.get("/earthquakes", response_model=List[Earthquake])
async def get_earthquakes(
    limit: int = Query(100, le=1000),
    min_mag: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = "SELECT id, time, latitude, longitude, depth, magnitude, place FROM earthquakes WHERE 1=1"
    params = []
    param_count = 1

    if min_mag:
        query += f" AND magnitude >= ${param_count}"
        params.append(min_mag)
        param_count += 1
    
    if start_date:
        query += f" AND time >= ${param_count}"
        params.append(start_date)
        param_count += 1

    if end_date:
        query += f" AND time <= ${param_count}"
        params.append(end_date)
        param_count += 1

    query += f" ORDER BY time DESC LIMIT ${param_count}"
    params.append(limit)

    try:
        async with app.state.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [Earthquake(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather", response_model=List[Weather])
async def get_weather(
    city: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    query = "SELECT time, city, temperature, humidity, pressure, condition FROM weather_measurements WHERE 1=1"
    params = []
    param_count = 1

    if city:
        query += f" AND city = ${param_count}"
        params.append(city)
        param_count += 1
    
    query += f" ORDER BY time DESC LIMIT ${param_count}"
    params.append(limit)

    try:
        async with app.state.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [Weather(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
