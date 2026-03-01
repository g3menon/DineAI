import os
from pathlib import Path

from fastapi.testclient import TestClient

# Before importing the app, point DATABASE_URL at a local SQLite file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DB_PATH = PROJECT_ROOT / "restaurants_phase3_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402

# Ensure the database schema exists for tests.
init_db()

client = TestClient(app)


def test_health_endpoint():
    """
    Basic health check for the Phase 3 backend.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


def test_recommendations_integration_with_db():
    """
    Integration-style test for /api/recommendations using the database-backed Phase 3 service.

    This will:
    - On first run, populate the local SQLite database from the Hugging Face dataset.
    - Then read restaurants from the database and return recommendations.
    - Optionally call Groq LLM (if GROQ_API_KEY is configured).
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

