from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Логи и correlation-id
from logging_config import setup_json_logging, CorrelationIdMiddleware

# Метрики
from metrics import MetricsMiddleware, router as metrics_router

# Rate limit (Redis token-bucket)
from rate_limit import RateLimitMiddleware

# Роутеры
from routers import (
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

# ==== Инициализация приложения ====
setup_json_logging()

app = FastAPI(title="Hermes MVP", version="0.3")  # версия ↑ для Stage 2

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Middlewares: порядок — CORS -> RateLimit -> CorrelationId -> Metrics
app.add_middleware(RateLimitMiddleware)         # 5 rps / ip, исключая /health,/metrics,/docs
app.add_middleware(CorrelationIdMiddleware)     # X-Request-ID
app.add_middleware(MetricsMiddleware)           # Prometheus

# Технические эндпоинты
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"app": "Tutor MVP", "version": "0.3"}

# Маршруты приложения
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(student_bio.router, tags=["students"])  # /students/{id}/bio, /students/{id}/avatar
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

app.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
app.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(topics.router, prefix="/topics", tags=["topics"])

app.include_router(mems.router, prefix="/mems", tags=["mems"])
app.include_router(tournaments.router, prefix="/tournaments", tags=["tournaments"])

app.include_router(payments.router, prefix="/finance", tags=["finance"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# /metrics для Prometheus
app.include_router(metrics_router, tags=["metrics"])
