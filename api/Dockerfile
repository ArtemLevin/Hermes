# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (build & runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project and install via pyproject.toml so ALL deps get in (incl. prometheus-client, rq-scheduler, python-json-logger)
COPY . /app

# Upgrade pip and install the package
RUN python -m pip install --upgrade pip && \
    pip install .

# Default runtime envs
ENV PORT=8000

EXPOSE 8000

# Run API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
