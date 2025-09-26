PYTHON ?= python3.11
VENV ?= .venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: install lint typecheck test run migrate revision compose-up compose-down format

install:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE); pip install --upgrade pip
	$(ACTIVATE); pip install -e .[dev]

lint:
	$(ACTIVATE); ruff check app tests

format:
	$(ACTIVATE); ruff check --fix app tests

typecheck:
	$(ACTIVATE); mypy app tests

test:
	$(ACTIVATE); pytest

run:
	$(ACTIVATE); uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	$(ACTIVATE); alembic upgrade head

revision:
	@if [ -z "$(msg)" ]; then echo "Usage: make revision msg=message"; exit 1; fi
	$(ACTIVATE); alembic revision --autogenerate -m "$(msg)"

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down -v
