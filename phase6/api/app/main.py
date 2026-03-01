import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DOTENV_PATH = os.path.join(_BASE_DIR, ".env")
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)

from app.db import init_db
from app.routers import feedback, recommendations

def create_app() -> FastAPI:
    app = FastAPI(title="AI Restaurant Recommendation Service - Vercel")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        init_db()

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    @app.get("/api/config")
    async def get_config():
        return {"google_client_id": os.getenv("GOOGLE_CLIENT_ID", "")}

    app.include_router(recommendations.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8004, reload=True)
