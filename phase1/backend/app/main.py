from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import recommendations


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(title="AI Restaurant Recommendation Service - Phase 1")

    # Enable CORS for local frontend development (http://localhost:3000, http://localhost:5173, etc.)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For learning/demo. In production, restrict origins.
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    # Include routers
    app.include_router(recommendations.router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

