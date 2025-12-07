FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY earthquake_ingestor.py .

CMD ["python", "-u", "earthquake_ingestor.py"]
