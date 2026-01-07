"""Main FastAPI application."""

from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

