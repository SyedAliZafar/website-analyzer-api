from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.logging import setup_logging

BASE_DIR = Path(__file__).resolve().parent

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Website Analyzer API",
        description="Analyze website performance, SEO, content quality, and AI insights",
        version="1.0.0",
    )

    # 1️⃣ API routes FIRST
    app.include_router(api_router, prefix="/api", tags=["analysis"])

    # 2️⃣ Static frontend LAST (ABSOLUTE PATH)
    app.mount(
        "/",
        StaticFiles(directory=BASE_DIR / "frontend", html=True),
        name="static",
    )

    return app


app = create_app()
