# Makefile
SHELL := /bin/bash

.PHONY: up down logs api web migrate seed seed2 test lint fmt rebuild

# - Базовые -
up:
	docker-compose up -d --build

down:
	docker-compose down -v

logs:
	docker-compose logs -f --tail=200 api worker scheduler web db redis

rebuild:
	docker-compose build --no-cache api web

# - Миграции -
migrate:
	docker-compose exec api alembic upgrade head

migrate-down:
	docker-compose exec api alembic downgrade -1

# - Сиды -
seed: ## базовые фикстуры этапа 0 (если уже есть — выполнится быстро)
	docker-compose exec api python scripts/seed.py

seed2: ## доп. фикстуры этапа 2 (темы, аватары, мемы, турнир, задания)
	docker-compose exec api python scripts/seed_stage2.py

# - Тесты -
test:
	# Smoke Stage 0/1
	BASE=http://localhost:8000 pytest -q api/tests/test_smoke.py || true
	# Stage 2
	BASE=http://localhost:8000 pytest -q api/tests/test_stage2.py || true

# - Формат/линт (опционально) -
fmt:
	docker-compose exec api python -m black .

lint:
	docker-compose exec api python -m ruff check .

# - Удобные команды -
api:
	docker-compose exec api bash

web:
	docker-compose exec web bash