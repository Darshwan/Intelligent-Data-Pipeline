FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY stream_processor.py .
COPY correlation_engine.py .

# Run the Faust worker
CMD ["faust", "-A", "stream_processor", "worker", "-l", "info"]
