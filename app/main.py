"""FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.timeout import TimeoutMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.middleware import RequestContextMiddleware
from app.api.routers import assignments, auth, health, students
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.tracing import configure_tracing
from app.db.session import get_database
from app.instrumentation.metrics import setup_metrics
from app.instrumentation.rate_limiter import RateLimitMiddleware, SlidingWindowRateLimiter

settings = get_settings()
setup_logging(settings)
database = get_database()
configure_tracing(settings, database.engine)

app = FastAPI(title=settings.app_name, version="0.4.0", debug=settings.debug)
app.state.settings = settings
app.state.database = database

app.add_middleware(RequestContextMiddleware)
app.add_middleware(TimeoutMiddleware, timeout=settings.request_timeout_seconds)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins] if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
allowed_hosts = getattr(settings, "allowed_hosts", ["*"])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
app.add_middleware(
    RateLimitMiddleware,
    limiter=SlidingWindowRateLimiter(limit=settings.rate_limit_per_minute),
)

setup_metrics(app)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(assignments.router)


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"app": settings.app_name, "version": "0.4.0"}


@app.on_event("startup")
async def on_startup() -> None:
    async with database.session():
        pass


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await database.engine.dispose()
