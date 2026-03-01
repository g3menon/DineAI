import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import feedback, recommendations

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_DOTENV_PATH = os.path.join(_BASE_DIR, ".env")
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application for Phase 4.
    """
    app = FastAPI(title="AI Restaurant Recommendation Service - Phase 4")

    # Enable CORS for local frontend development (http://localhost:3000, http://localhost:5173, etc.)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For learning/demo. In production, restrict origins.
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        """
        Initialize the database on application startup.
        """
        init_db()

    @app.get("/health")
    async def health_check():
        """
        Simple health-check endpoint. Returns {"status": "ok"} when the API is running.
        """
        return {"status": "ok"}

    @app.get("/api/config")
    async def get_config():
        """
        Returns public frontend configuration, such as the Google Client ID.
        """
        return {"google_client_id": os.getenv("GOOGLE_CLIENT_ID", "")}

    # Include routers under a common prefix.
    app.include_router(recommendations.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    # This block lets you run the app directly with `python app/main.py`
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8004, reload=True)

