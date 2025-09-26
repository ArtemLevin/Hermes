# Hermes API

Production-ready FastAPI service that powers the Hermes tutoring platform. The service exposes
secure CRUD APIs for tutors and students, includes observability tooling, and ships with database
migrations, Docker images, and automated tests.

## Features

- **FastAPI** with async SQLAlchemy 2.0 and PostgreSQL/SQLite support
- JWT-based authentication with Argon2 password hashing
- Idempotent POST endpoints backed by persistent tokens
- Structured JSON logging (request/response correlation id)
- Prometheus `/metrics` endpoint and OpenTelemetry hooks for distributed tracing
- Graceful shutdown, request timeouts, rate limiting, gzip compression, and CORS controls
- Alembic migrations and reusable Makefile workflow
- Comprehensive pytest suite covering API flows

## Project layout

```
app/
  api/            # Routers, dependencies, middleware
  core/           # Configuration, logging, security, tracing
  db/             # SQLAlchemy base + session factory
  instrumentation/# Metrics & rate limiting helpers
  models/         # ORM models
  schemas/        # Pydantic response/request models
  services/       # Business logic services
  main.py         # FastAPI application instance
alembic/          # Database migrations
Dockerfile        # Production-ready container image
Makefile          # Common developer commands
docker-compose.yml# Local orchestrator (API + Postgres)
```

## Requirements

- Python 3.11+
- PostgreSQL 13+ (or SQLite for local dev/test)
- Optional: Docker 24+ and Docker Compose v2

## Environment configuration

All runtime settings are provided via environment variables (prefixed with `HERMES_`). An example is
available in `.env.example`.

| Variable | Description | Default |
|----------|-------------|---------|
| `HERMES_DATABASE_URL` | SQLAlchemy database URL | `sqlite+aiosqlite:///./hermes.db` |
| `HERMES_JWT_SECRET_KEY` | Secret used to sign JWT tokens | `change-me` (override in prod) |
| `HERMES_RATE_LIMIT_PER_MINUTE` | Requests per minute per client | `120` |
| `HERMES_REQUEST_TIMEOUT_SECONDS` | Request timeout | `10` |
| `HERMES_CORS_ORIGINS` | JSON array of allowed origins | `[]` (allows all) |
| `HERMES_OTLP_ENDPOINT` | OTLP collector endpoint for tracing | unset |

## Local development (venv)

```bash
# Create a virtual environment and install dependencies
make install

# Run linting, type-checks, and tests
make lint
make typecheck
make test

# Apply migrations (optional when using SQLite)
make migrate

# Start the API with hot reload
make run
```

Visit http://localhost:8000/docs for the interactive OpenAPI UI.

## Docker usage

```bash
# Build and run the stack (API + PostgreSQL)
make compose-up

# Tear everything down
make compose-down
```

The API will be available at http://localhost:8000 once the Postgres health check passes.

## Database migrations

```bash
# Generate a new revision (after modifying models)
make revision msg="describe change"

# Apply the latest migrations
make migrate
```

## Testing

```bash
make test
```

Tests run against an in-memory SQLite database and exercise authentication, idempotency, and
observability endpoints.

## Observability

- **Logs**: JSON-formatted with `request_id`, method, and path context.
- **Metrics**: Prometheus-compatible metrics exposed at `/metrics`.
- **Tracing**: Enable by setting `HERMES_OTLP_ENDPOINT` to an OTLP collector URL.
- **Health checks**: `/health`, `/health/live`, `/health/ready`.

## OpenAPI

The OpenAPI specification is served at `/openapi.json`. Swagger UI is available at `/docs`. Example
request:

```bash
curl -X POST http://localhost:8000/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=tutor@example.com&password=SuperSecure123'
```

## Security notes

- Always set a strong `HERMES_JWT_SECRET_KEY` in production.
- TLS termination and OAuth2 client registration should be handled by the ingress/proxy layer.
- Configure `HERMES_ALLOWED_HOSTS` (extra setting) when deploying to lock down Host headers.

## License

MIT
