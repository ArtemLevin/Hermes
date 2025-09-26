# Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Убедимся, что PATH включает системную директорию для исполняемых файлов
    PATH="/root/.local/bin:/home/appuser/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project and install via pyproject.toml so ALL deps get in (incl. prometheus-client, rq-scheduler, python-json-logger)
# Do this as root to allow pip to install to system/user locations correctly during build
COPY pyproject.toml ./

# Upgrade pip and install the package
# pip install . установит зависимости в site-packages (или используя --user если нужно) и исполняемые файлы в PATH
# We use --root-user-action=ignore to suppress warnings about installing as root, as this is a common practice in containers.
RUN python -m pip install --upgrade pip && \
    # Install build dependencies first if needed by the project itself (e.g., setuptools_scm)
    pip install --upgrade setuptools wheel && \
    pip install .

# Copy application code *after* installing dependencies to leverage Docker layer caching
COPY . .

# Change ownership of the entire /app directory to non-root user
# This is crucial for the runtime user (appuser) to access the code and any runtime-generated files within /app
RUN chown -R appuser:appuser /app

# Switch to non-root user for runtime
USER appuser

EXPOSE 8000

# Default runtime envs
ENV PORT=8000

# Run API - only uvicorn, migrations in compose
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]