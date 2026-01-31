"""
Application entrypoint for the Website Analyzer API.
Wires configuration, logging, and API routes.
"""

from fastapi import FastAPI

from app.core.logging import setup_logging
from app.api.routes import router as api_router


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Website Analyzer API",
        description="Analyze website performance, SEO, content quality, and AI insights",
        version="1.0.0",
    )

    # Mount API routes under /api
    app.include_router(api_router, prefix="/api", tags=["analysis"])

    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
