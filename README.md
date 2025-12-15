# 🇳🇵 Nepal Data Hub Platform
> Real-Time Multi-Source Disaster & Civic Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docker.com)
[![kafka](https://img.shields.io/badge/Kafka-Streaming-black)](https://kafka.apache.org)

**Nepal Data Hub** is a production-grade analytics platform designed to ingest, process, and visualize critical data streams in real-time. It correlates Earthquake data (USGS), Weather metrics (OpenWeather), and Government Flood Alerts to provide actionable intelligence for disaster management in Nepal.

---

## 🏗 Architecture
The platform follows a modern microservices architecture containerized with Docker:

```mermaid
graph TD
    A[Data Sources] -->|Pull/Push| B(Ingestion Service)
    B -->|Produce| C{Kafka Message Broker}
    C -->|Consume| D[Processing Service]
    C -->|Stream| E[DB Writer]
    D -->|Correlate| F[(Redis Cache)]
    E -->|Persist| G[(TimescaleDB + PostGIS)]
    
    H[API Service] -->|Read| G
    H -->|Read| F
    H -->|WebSocket| I[Dashboard / Clients]
    
    style B fill:#f9f,stroke:#333
    style D fill:#bbf,stroke:#333
    style H fill:#dfd,stroke:#333
```

### Core Services
1.  **Ingestion Service**: Async Python workers that fetch data from external APIs (USGS, OpenWeather) and scrapers (Govt Hydrology). Pushes normalized data to Kafka topics.
2.  **Processing Service (Faust)**: Real-time stream processor that aggregates data and detects patterns (e.g., "Landslide Risk" = Quake > 4.0 + High Rain).
3.  **API Service (FastAPI)**: High-performance backend providing REST endpoints, WebSockets for live updates, and Server-Sent Events (SSE).
4.  **Dashboard (Streamlit)**: Interactive frontend with real-time maps, charts, and alert monitoring.
5.  **Storage Layer**: 
    *   **TimescaleDB**: For efficient time-series storage of millions of sensor readings.
    *   **PostGIS**: For geospatial queries (e.g., "Earthquakes within 50km of Kathmandu").
    *   **Redis**: For high-speed caching and real-time state management.

---

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   (Optional) OpenWeatherMap API Key

### Installation
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/nepal-data-hub.git
    cd nepal-data-hub
    ```

2.  **Set Environment Variables**:
    Create a `.env` file (optional, defaults provided for dev):
    ```env
    OPENWEATHER_API_KEY=your_key_here
    DATABASE_URL=postgresql://postgres:password@timescaledb:5432/nepaldatalab
    ```

3.  **Start the Platform**:
    ```bash
    docker-compose up -d --build
    ```

4.  **Access the Interfaces**:
    *   **Dashboard**: [http://localhost:8501](http://localhost:8501)
    *   **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚡ Features

### 1. Real-Time Monitoring
*   **Earthquakes**: Live feed from USGS, filtered for the Nepal region. Visualized with magnitude heatmaps.
*   **Flood Alerts**: Simulated connection to Department of Hydrology water level stations (Koshi, Gandaki). 
*   **Weather**: Live temperature and condition updates for major Nepali cities.

### 2. Intelligent Insights
*   **Correlation Engine**: Automatically detects compound risks.
    *   *Example*: A magnitude 4.5 earthquake in a district experiencing heavy rainfall triggers a **"Landslide Risk"** alert.
*   **Trend Analysis**: 24h/7d historical views of seismic activity and weather patterns.

### 3. API & Connectivity
*   **WebSockets**: Subscribe to `/ws/earthquakes` for millisecond-latency updates.
*   **Geospatial Queries**: Filter data by radius, district, or bounding box.

### 4. User Experience (New)
*   **Ultra-Minimalist UI**: Custom CSS styling with "Inter" typography and glassmorphism.
*   **Interactive Maps**: High-performance Folium maps with custom markers.

---

## 📚 API Documentation

### Endpoints
| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/dashboard` | **Aggregation**: Returns all data needed for the main view (Stats, Map, Alerts). |
| `GET` | `/api/v1/earthquakes` | **Query**: Historical earthquake data with filters. |
| `GET` | `/api/v1/correlations` | **Intelligence**: Access generated risk insights. |
| `WS` | `/ws/earthquakes` | **Stream**: Real-time earthquake event stream. |
| `WS` | `/ws/alerts` | **Stream**: Real-time flood and system alerts. |

Full interactive documentation is available at `/docs` when the service is running.

---

## 🛠 Tech Stack Details

*   **Language**: Python 3.11
*   **Streaming**: Apache Kafka, Faust-Streaming
*   **Database**: PostgreSQL 14, TimescaleDB, PostGIS, Redis 7
*   **Frontend**: Streamlit (with Custom CSS/JS), Plotly, Folium
*   **Backend**: FastAPI, AsyncPG, SSE-Starlette

---

## 🤝 Contributing

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ for Nepal.** 🇳🇵
