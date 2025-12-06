from prometheus_client import Counter, Histogram

# Metrics
REQUEST_COUNT = Counter(
    "app_request_count", 
    "Total number of requests received",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", 
    "Request latency in seconds"
)

INGESTION_ERRORS = Counter(
    "app_ingestion_errors_total",
    "Total number of errors during data ingestion from USGS"
)
