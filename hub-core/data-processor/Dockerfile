FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY data-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pydantic

# Copy source code
COPY data-processor/stream_processor.py .
COPY data-processor/correlation_engine.py .
COPY schemas/ ./schemas/

# Run the Faust worker
CMD ["faust", "-A", "stream_processor", "worker", "-l", "info"]
