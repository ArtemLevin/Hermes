# Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install "uvicorn[standard]==0.30.6" && \
    pip install "fastapi==0.115.0" && \
    pip install "sqlalchemy==2.0.34" && \
    pip install "alembic==1.13.2" && \
    pip install "psycopg2-binary==2.9.9" && \
    pip install "passlib[argon2]==1.7.4" && \
    pip install "pyjwt==2.9.0" && \
    pip install "redis==5.0.8" && \
    pip install "rq==1.16.2" && \
    pip install "rq-scheduler==0.11.0" && \
    pip install "requests==2.32.3" && \
    pip install "prometheus-client==0.20.0" && \
    pip install "pydantic==2.9.2" && \
    pip install "pydantic-settings==2.6.0" && \
    pip install "python-multipart==0.0.9" && \
    pip install "tenacity==8.5.0" && \
    pip install "python-jose[cryptography]==3.3.0" && \
    pip install "structlog==24.4.0"

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]