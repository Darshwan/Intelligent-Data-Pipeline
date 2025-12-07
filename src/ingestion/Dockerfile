FROM python:3.11-slim

WORKDIR /app

COPY src/ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ingestion/earthquake_ingestor.py .
COPY src/ingestion/weather_ingestor.py .
COPY src/ingestion/flood_scraper.py .
COPY src/ingestion/main.py .

CMD ["python", "-u", "main.py"]
