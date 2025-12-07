from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncpg
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import asyncio
import os
import redis
from contextlib import asynccontextmanager

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# Config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@timescaledb:5432/nepaldatalab")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
REDIS_HOST = "redis"
REDIS_PORT = 6379

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        app.state.pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    except Exception as e:
        print(f"DB Connection Failed: {e}")
    
    # Start background tasks
    app.state.background_tasks = set()
    
    # Alert broadcasting task
    task = asyncio.create_task(broadcast_alerts(manager))
    app.state.background_tasks.add(task)
    task.add_done_callback(app.state.background_tasks.discard)
    
    yield
    
    # Shutdown
    if hasattr(app.state, 'pool'):
        await app.state.pool.close()
    for task in app.state.background_tasks:
        task.cancel()

app = FastAPI(
    title="Nepal Data Hub API",
    description="Real-time analytics platform for Nepal disaster and civic data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "Nepal Data Hub",
        "description": "Real-time analytics platform for disaster and civic data in Nepal",
        "endpoints": {
            "earthquakes": "/api/v1/earthquakes",
            "weather": "/api/v1/weather",
            "alerts": "/api/v1/alerts",
            "correlations": "/api/v1/correlations",
            "stats": "/api/v1/stats",
            "dashboard": "/api/v1/dashboard"
        },
        "sources": ["USGS", "OpenWeather", "Nepal Government", "OpenAQ"],
        "github": "https://github.com/yourusername/nepal-data-hub"
    }

@app.get("/api/v1/earthquakes")
async def get_earthquakes(
    days: int = Query(7, ge=1, le=365),
    min_magnitude: Optional[float] = Query(None, ge=0.0, le=10.0),
    place: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get earthquake data for Nepal"""
    query = """
        SELECT id, time, latitude, longitude, depth, magnitude, place FROM earthquakes 
        WHERE time > $1
    """
    params = [datetime.utcnow() - timedelta(days=days)]
    
    conditions = []
    if min_magnitude:
        conditions.append(f"magnitude >= ${len(params) + 1}")
        params.append(min_magnitude)
    
    # Using 'place' instead of 'district' as per our schema
    if place:
        conditions.append(f"place ILIKE ${len(params) + 1}")
        params.append(f"%{place}%")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += f" ORDER BY time DESC LIMIT ${len(params) + 1}"
    params.append(limit)
    
    async with app.state.pool.acquire() as conn:
        records = await conn.fetch(query, *params)
    
    return [dict(record) for record in records]

@app.get("/api/v1/weather")
async def get_weather(
    city: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Get weather data for Nepal cities"""
    query = """
        SELECT time, city, temperature, humidity, pressure, condition FROM weather_measurements
        WHERE time > $1
    """
    params = [datetime.utcnow() - timedelta(hours=hours)]
    
    if city:
        query += f" AND city ILIKE ${len(params) + 1}"
        params.append(f"%{city}%")
    
    query += " ORDER BY time DESC"
    
    async with app.state.pool.acquire() as conn:
        records = await conn.fetch(query, *params)
    
    return [dict(record) for record in records]

@app.get("/api/v1/alerts")
async def get_alerts(
    status: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Get recent alerts (Flood)"""
    # Mapping 'govt_alerts' from user prompt to our 'flood_alerts' table
    query = """
        SELECT time, station, water_level, warning_level, danger_level, status as severity, station as district 
        FROM flood_alerts 
        WHERE time > $1
    """
    params = [datetime.utcnow() - timedelta(hours=hours)]
    
    if status:
        query += f" AND status = ${len(params) + 1}"
        params.append(status)
    
    query += " ORDER BY time DESC"
    
    async with app.state.pool.acquire() as conn:
        records = await conn.fetch(query, *params)
    
    # Enrich simple records to match user expected schema roughly (alert_type, etc)
    return [{**dict(r), "alert_type": "Flood"} for r in records]


@app.get("/api/v1/correlations")
async def get_correlations():
    """Get data correlations and insights"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        
        # Get latest correlations (mock logic or reading actual if available)
        # Using a fallback for demo if redis empty
        correlations = []
        
    except:
        correlations = []
    
    # Get additional insights via SQL aggregation
    async with app.state.pool.acquire() as conn:
        # Earthquake frequency
        quake_freq = await conn.fetch("""
            SELECT 
                DATE_TRUNC('hour', time) as hour,
                COUNT(*) as count
            FROM earthquakes 
            WHERE time > NOW() - INTERVAL '24 hours'
            GROUP BY 1
            ORDER BY 1
        """)
        
        # Weather patterns (simple avg)
        weather_patterns = await conn.fetch("""
            SELECT 
                city,
                AVG(temperature) as avg_temp,
                MAX(temperature) as max_temp
            FROM weather_measurements
            WHERE time > NOW() - INTERVAL '24 hours'
            GROUP BY city
        """)
    
    return {
        "correlations": correlations,
        "insights": {
            "earthquake_frequency": [{k: str(v) if k=='hour' else v for k,v in dict(r).items()} for r in quake_freq],
            "weather_patterns": [dict(r) for r in weather_patterns],
            "generated_at": datetime.utcnow().isoformat()
        }
    }

@app.get("/api/v1/stats")
async def get_stats():
    """Get comprehensive statistics"""
    async with app.state.pool.acquire() as conn:
        # Overall stats
        stats = await conn.fetchrow("""
             SELECT 
                (SELECT COUNT(*) FROM earthquakes WHERE time > NOW() - INTERVAL '24 hours') as earthquakes_24h,
                (SELECT COUNT(DISTINCT city) FROM weather_measurements WHERE time > NOW() - INTERVAL '1 hour') as active_weather_stations,
                (SELECT COUNT(*) FROM flood_alerts WHERE time > NOW() - INTERVAL '24 hours') as alerts_24h
        """)
        
        # Recent significant events
        recent_significant = await conn.fetch("""
            (SELECT 'earthquake' as type, time, place as description, magnitude as value
             FROM earthquakes 
             WHERE magnitude >= 4.0 AND time > NOW() - INTERVAL '7 days'
             ORDER BY time DESC LIMIT 5)
            UNION ALL
            (SELECT 'weather' as type, time, city || ': ' || condition as description, temperature as value
             FROM weather_measurements
             WHERE (condition = 'Rain' OR temperature > 30)
             AND time > NOW() - INTERVAL '1 day'
             ORDER BY time DESC LIMIT 5)
            ORDER BY time DESC LIMIT 10
        """)
    
    return {
        "overall": dict(stats) if stats else {},
        "recent_significant_events": [dict(r) for r in recent_significant],
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dashboard")
async def get_dashboard_data():
    """Get all data needed for dashboard in one call"""
    async with app.state.pool.acquire() as conn:
        # Fetch Earthquakes (last 24h)
        earthquakes = await conn.fetch("SELECT id, time, latitude, longitude, depth, magnitude, place FROM earthquakes WHERE time > NOW() - INTERVAL '24 hours' ORDER BY time DESC LIMIT 100")
        
        # Fetch Weather (Latest per city - 6h)
        weather = await conn.fetch("SELECT time, city, temperature, humidity, pressure, condition FROM weather_measurements WHERE time > NOW() - INTERVAL '6 hours' ORDER BY time DESC")
        
        # Fetch Flood Alerts
        alerts = await conn.fetch("SELECT time, station, water_level, warning_level, danger_level, status FROM flood_alerts WHERE time > NOW() - INTERVAL '24 hours' ORDER BY time DESC")

    return {
        "earthquakes": [dict(r) for r in earthquakes],
        "weather": [dict(r) for r in weather],
        "alerts": [dict(r) for r in alerts],
        "power_outages": [], # Placeholder
        "dashboard_stats": {
             "weather_updates": {"count": len(weather)}
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# WebSocket endpoints for real-time updates
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/earthquakes")
async def websocket_earthquakes(websocket: WebSocket):
    await websocket.accept()
    try:
        # Send real-time earthquake updates (Polling DB for new ones for demo simplicity)
        last_sent = datetime.utcnow()
        while True:
            async with app.state.pool.acquire() as conn:
                recent = await conn.fetch("""
                    SELECT id, time, latitude, longitude, depth, magnitude, place FROM earthquakes 
                    WHERE time > $1
                    ORDER BY time DESC
                    LIMIT 10
                """, last_sent)
                
                if recent:
                    await websocket.send_json({
                        "type": "earthquake_update",
                        "data": [dict(r) for r in recent],
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    last_sent = datetime.utcnow()
            
            await asyncio.sleep(10)  # Update every 10 seconds
    except WebSocketDisconnect:
        pass

async def broadcast_alerts(manager: ConnectionManager):
    """Background task to broadcast new alerts"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        
        while True:
            # Placeholder for reading alert queue if implemented
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"Error in broadcast_alerts: {e}")

# SSE endpoint for older clients
@app.get("/sse/alerts")
async def sse_alerts():
    async def event_generator():
        last_sent = datetime.utcnow()
        while True:
            # Check for new alerts (Floods)
            async with app.state.pool.acquire() as conn:
                new_alerts = await conn.fetch("""
                    SELECT * FROM flood_alerts
                    WHERE time > $1
                    ORDER BY time DESC
                """, last_sent)
                
                for alert in new_alerts:
                    # Convert asyncpg record to dict and datetime to string
                    data = dict(alert)
                    data['time'] = data['time'].isoformat()
                    data['created_at'] = data['created_at'].isoformat()
                    yield f"data: {json.dumps(data)}\n\n"
                    last_sent = datetime.utcnow()
            
            await asyncio.sleep(5)
    
    return EventSourceResponse(event_generator())
