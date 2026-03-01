from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    """
    Basic health check for the Phase 2 backend.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


def test_recommendations_integration_structure():
    """
    Integration-style test for /api/recommendations.

    This will:
    - Call the real Hugging Face dataset API through DatasetService.
    - Optionally call Groq LLM (if GROQ_API_KEY is configured).

    The test only checks the response structure so it remains stable
    even if the external services return different data over time.
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

    # Top-level keys
    assert "results" in data
    assert "llm_used" in data
    assert "llm_summary" in data

    assert isinstance(data["results"], list)
    assert isinstance(data["llm_used"], bool)
    # llm_summary can be None or a string, depending on whether Groq was called successfully.
    assert data["llm_summary"] is None or isinstance(data["llm_summary"], str)

    # If we get any results, check the basic structure of the first one.
    if data["results"]:
        first = data["results"][0]
        assert "name" in first
        assert "location" in first
        assert "rating" in first
        assert "price" in first
        assert "cuisine" in first
        assert "reason" in first

