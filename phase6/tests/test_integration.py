import json
from fastapi.testclient import TestClient
import sys
import os

# Add the phase6/api directory to sys.path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from app.main import app

import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.anyio
async def test_full_user_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        response_health = await client.get("/health")
        assert response_health.status_code == 200
        
        # 2. Config check for UI Google Sign-in to ensure backend passes variables reliably
        response_config = await client.get("/api/config")
        assert response_config.status_code == 200
        assert "google_client_id" in response_config.json()
        assert response_config.json()["google_client_id"] != ""

        # 3. Request recommendations
        payload = {
            "location": "Bangalore",
            "price_range": "mid",
            "min_rating": 3.0,
            "cuisine": "Indian",
            "user_id": "test_integration_user"
        }
        response_recs = await client.post("/api/recommendations", json=payload)
        if response_recs.status_code != 200:
            print(f"Error: {response_recs.json()}")
        assert response_recs.status_code == 200
        data = response_recs.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
        
        # 4. If we got results, provide feedback on the first one
        if len(data["results"]) > 0:
            first_restaurant_name = data["results"][0]["name"]
            feedback_payload = {
                "user_id": "test_integration_user",
                "restaurant_name": first_restaurant_name,
                "liked": True
            }
            response_feedback = await client.post("/api/feedback", json=feedback_payload)
            assert response_feedback.status_code == 200
            assert response_feedback.json() == {"status": "ok"}

