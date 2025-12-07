FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY src/processing/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/processing/stream_processor.py .
COPY src/processing/correlation_engine.py .

# Run the Faust worker
CMD ["faust", "-A", "stream_processor", "worker", "-l", "info"]
