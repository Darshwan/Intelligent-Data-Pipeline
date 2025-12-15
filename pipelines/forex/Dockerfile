FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY forex_ingestor.py .

CMD ["python", "-u", "forex_ingestor.py"]
