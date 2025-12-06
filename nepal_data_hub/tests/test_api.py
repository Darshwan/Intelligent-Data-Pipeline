from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ..main import app
from ..models import Earthquake

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Nepal Data Hub Platform"}

@patch('nepal_data_hub.services.ingestion.requests.get')
def test_get_earthquakes_success(mock_get):
    # Mock USGS response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "type": "FeatureCollection",
        "features": [
            {
                "id": "test1",
                "type": "Feature",
                "properties": {
                    "mag": 5.0,
                    "place": "Nepal",
                    "time": 1600000000000,
                    "url": "http://example.com",
                    "title": "M 5.0 - Nepal"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [85.0, 27.0, 10.0]
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    response = client.get("/earthquakes")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["properties"]["place"] == "Nepal"

@patch('nepal_data_hub.services.ingestion.requests.get')
def test_get_earthquakes_failure(mock_get):
    # Mock API failure
    mock_get.side_effect = Exception("API Error")

    response = client.get("/earthquakes")
    assert response.status_code == 200 # App handles error and returns empty list
    data = response.json()
    assert data["count"] == 0
    assert data["data"] == []
