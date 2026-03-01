import json
from fastapi.testclient import TestClient
import sys
import os

# Add the phase6/api directory to sys.path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    assert "google_client_id" in response.json()

def test_get_recommendations():
    payload = {
        "location": "Banashankari",
        "price_range": "mid",
        "min_rating": 3.0,
        "cuisine": "Italian"
    }
    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    # Results should be a list
    assert isinstance(data["results"], list)
