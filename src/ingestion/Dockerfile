FROM python:3.11-slim

WORKDIR /app

COPY src/ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ingestion/earthquake_ingestor.py .

CMD ["python", "-u", "earthquake_ingestor.py"]
