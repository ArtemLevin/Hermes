FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Системные зависимости для psycopg2-binary и компиляции (минимально)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем зависимости
# Если используете pyproject.toml — можно заменить на "pip install -r requirements.txt" при наличии
COPY pyproject.toml ./
RUN python -m pip install --upgrade pip && \
    pip install "fastapi==0.115.0" "uvicorn[standard]==0.30.6" \
                "sqlalchemy==2.0.34" "psycopg2-binary==2.9.9" \
                "alembic==1.13.2" "passlib[argon2]==1.7.4" \
                "pyjwt==2.9.0" "redis==5.0.8" "rq==1.16.2" \
                "requests==2.32.3"

# Копируем исходники API
COPY api/ ./

# Порт API
EXPOSE 8000

# Старт: применяем миграции (мягко) и запускаем Uvicorn
CMD bash -lc "alembic upgrade head || true && uvicorn main:app --host 0.0.0.0 --port 8000"
