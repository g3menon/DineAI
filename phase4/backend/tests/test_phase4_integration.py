import os
from pathlib import Path

from fastapi.testclient import TestClient

# Before importing the app, point DATABASE_URL at a local SQLite file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DB_PATH = PROJECT_ROOT / "restaurants_phase4_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402

# Ensure the database schema exists for tests.
init_db()

client = TestClient(app)


def test_health_endpoint():
    """
    Basic health check for the Phase 4 backend.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


def test_recommendations_and_feedback_flow():
    """
    Integration-style test for /api/recommendations and /api/feedback.

    This will:
    - On first run, populate the local SQLite database from the Hugging Face dataset.
    - Request recommendations for a user.
    - Submit feedback that the user liked one of the recommended restaurants.
    - Request recommendations again and ensure the API still responds correctly.
    """
    user_id = "test-user-phase4"

    payload = {
        "location": "Bangalore",
        "price_range": "mid",
        "min_rating": 3.5,
        "cuisine": "Italian",
        "user_id": user_id,
    }

    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

    assert len(data["results"]) > 0, "No restaurants found!"

    first = data["results"][0]
    restaurant_name = first["name"]

    feedback_payload = {
        "user_id": user_id,
        "restaurant_name": restaurant_name,
        "liked": True,
    }

    feedback_response = client.post("/api/feedback", json=feedback_payload)
    assert feedback_response.status_code == 200
    feedback_data = feedback_response.json()
    assert feedback_data.get("status") == "ok"

    # Call recommendations again; main goal is to ensure the endpoint still works
    # and returns a structurally valid response after feedback is stored.
    response_after_feedback = client.post("/api/recommendations", json=payload)
    assert response_after_feedback.status_code == 200

    data2 = response_after_feedback.json()
    assert "results" in data2
    assert isinstance(data2["results"], list)
    assert "llm_used" in data2
    assert "llm_summary" in data2


def test_oauth_user_id_and_optional_location():
    """
    Test that the backend correctly handles requests coming from the updated
    frontend using Google OAuth. This involves:
    1. A missing/optional location field.
    2. A long string user_id corresponding to a Google 'sub' token format.
    """
    oauth_user_id = "104939201948392039492"  # Simulating Google 'sub' id

    # Payload matching the updated frontend with location empty/omitted
    payload = {
        "location": "",
        "price_range": "mid",
        "min_rating": 3.0,
        "cuisine": "Cafe",
        "user_id": oauth_user_id,
    }

    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200, f"Error: {response.text}"

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

    results = data["results"]
    if results:
        # Give feedback to ensure the long OAuth string works properly in the DB
        feed_payload = {
            "user_id": oauth_user_id,
            "restaurant_name": results[0]["name"],
            "liked": True,
        }
        feed_response = client.post("/api/feedback", json=feed_payload)
        assert feed_response.status_code == 200, f"Feed Error: {feed_response.text}"
        feed_data = feed_response.json()
        assert feed_data.get("status") == "ok"
