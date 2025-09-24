up:
	docker-compose up --build -d

logs:
	docker-compose logs -f api

migrate:
	docker-compose exec api alembic upgrade head

seed:
	docker-compose exec api python scripts/seed.py

smoke:
	pytest -q api/tests/test_smoke.py || true

down:
	docker-compose down -v