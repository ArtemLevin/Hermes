from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, students, dashboard, notifications

from rate_limit import RateLimitMiddleware


# Логи и correlation-id
from logging_config import setup_json_logging, CorrelationIdMiddleware

# Метрики
from metrics import MetricsMiddleware, router as metrics_router

# Ваши роутеры
from routers import auth, students, dashboard

# ==== Инициализация приложения ====
setup_json_logging()

app = FastAPI(title="Tutor MVP", version="0.2")  # версия ↑ для этапа 1

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(RateLimitMiddleware)  # разместите после CORS, до метрик — по желанию

# Middlewares: correlation-id и метрики
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(MetricsMiddleware)

# Технические эндпоинты
@app.get("/health")
def health():
    return {"status": "ok"}

# Маршруты приложения
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# /metrics для Prometheus
app.include_router(metrics_router, tags=["metrics"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
