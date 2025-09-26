# api/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.logging_config import setup_json_logging, CorrelationIdMiddleware
from api.metrics import MetricsMiddleware, router as metrics_router
from api.rate_limit import RateLimitMiddleware
from api.routers import (
    auth,
    students,
    dashboard,
    notifications,
    assignments,
    analytics,
    mems,
    tournaments,
    topics,
    lessons,
    student_bio,
    payments,
)
from api.deps import engine
from sqlalchemy.ext.asyncio import create_async_engine

# Setup logging before app starts
setup_json_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    # Initialize async engine if needed for async operations
    yield
    logger.info("Application shutting down")

app = FastAPI(
    title="Hermes MVP",
    version="0.3.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middlewares: order matters
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(MetricsMiddleware)

# Routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(student_bio.router, tags=["students"]) # /students/{id}/bio, /students/{id}/avatar
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
app.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
app.include_router(topics.router, prefix="/topics", tags=["topics"])
app.include_router(mems.router, prefix="/mems", tags=["mems"])
app.include_router(tournaments.router, prefix="/tournaments", tags=["tournaments"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])

@app.get("/health", response_class=JSONResponse)
def health():
    return {"status": "ok"}

@app.get("/", response_class=JSONResponse)
def root():
    return {"app": "Tutor MVP", "version": "0.3.0"}