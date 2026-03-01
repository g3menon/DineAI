from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import recommendations


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application for Phase 3.
    """
    app = FastAPI(title="AI Restaurant Recommendation Service - Phase 3")

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

    # Include routers under a common prefix.
    app.include_router(recommendations.router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    # This block lets you run the app directly with `python app/main.py`
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)

