up:
\tdocker-compose up --build -d

logs:
\tdocker-compose logs -f api

migrate:
\tdocker-compose exec api alembic upgrade head

seed:
\tdocker-compose exec api python scripts/seed.py

smoke:
\tpytest -q api/tests/test_smoke.py || true

down:
\tdocker-compose down -v
