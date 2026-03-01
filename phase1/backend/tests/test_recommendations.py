import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


@pytest.mark.skip(reason="This test calls the real Hugging Face API and may be slow or flaky.")
def test_recommendations_basic_flow():
    """
    Simple integration-style test that exercises the /api/recommendations endpoint.

    It uses the real DatasetService, which in turn calls the Hugging Face dataset API.
    For local development, you can temporarily remove the @pytest.mark.skip decorator
    to verify the full flow.
    """
    payload = {
        "location": "Bangalore",
        "price_range": "mid",
        "min_rating": 3.5,
        "cuisine": "Italian",
    }

    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

    # If we get any results, check the basic structure of the first one.
    if data["results"]:
        first = data["results"][0]
        assert "name" in first
        assert "location" in first
        assert "rating" in first
        assert "price" in first
        assert "cuisine" in first
        assert "reason" in first

