from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .services.ingestion import fetch_earthquakes
from .monitoring import REQUEST_COUNT

app = FastAPI(title="Nepal Data Hub Platform")

@app.get("/")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "service": "Nepal Data Hub Platform"}

@app.get("/earthquakes")
def get_earthquakes():
    """
    Fetch and return earthquake data.
    """
    REQUEST_COUNT.labels(method="GET", endpoint="/earthquakes", status="200").inc()
    data = fetch_earthquakes()
    return {"count": len(data), "data": data}

@app.get("/metrics")
def metrics():
    """
    Expose Prometheus metrics.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
