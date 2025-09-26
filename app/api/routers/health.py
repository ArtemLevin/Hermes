"""Health check endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.api.dependencies import get_settings_dependency

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Liveness probe")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready", summary="Readiness probe")
async def readiness(settings: Settings = Depends(get_settings_dependency)) -> dict[str, str]:
    return {"status": "ready", "environment": settings.environment}


@router.get("/health", summary="Legacy health endpoint")
async def health() -> dict[str, str]:
    return {"status": "ok"}
