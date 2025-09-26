# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \ 
    && apt-get install -y --no-install-recommends build-essential libpq-dev \ 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY alembic alembic
COPY app app

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir .

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app app
COPY alembic alembic
COPY alembic.ini pyproject.toml README.md ./

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/health'); sys.exit(0)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
