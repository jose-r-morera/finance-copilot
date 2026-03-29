# =============================================================================
# finance-copilot — Makefile
# Convenience targets for development, testing, and deployment.
# Run `make help` for a full list of available commands.
# =============================================================================

.PHONY: help install install-dev dev up down build \
        test lint format typecheck clean

# --- Variables ---------------------------------------------------------------
PYTHON      := $(shell if [ -f .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
PIP         := $(PYTHON) -m pip
UVICORN     := uvicorn backend.app.main:app
COMPOSE     := docker compose

## help: Show this help message
help:
	@grep -E '^## ' Makefile | sed 's/## //'

# --- Setup -------------------------------------------------------------------

## install: Install runtime dependencies
install:
	$(PIP) install -r requirements.txt

## install-dev: Install runtime + dev dependencies and pre-commit hooks
install-dev:
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	pre-commit install
	cd frontend && npm install

# --- Development server ------------------------------------------------------

## dev: Run FastAPI backend in hot-reload mode (no Docker)
dev:
	$(UVICORN) --reload --host 0.0.0.0 --port 8000

## dev-frontend: Run Next.js frontend in hot-reload mode (no Docker)
dev-frontend:
	cd frontend && npm run dev

## up: Start all services via Docker Compose
up:
	$(COMPOSE) up --build -d

## down: Stop all Docker Compose services
down:
	$(COMPOSE) down

## logs: Tail Docker Compose logs
logs:
	$(COMPOSE) logs -f

# --- Quality -----------------------------------------------------------------

## test: Run the full test suite (local)
test:
	$(PYTHON) -m pytest backend/tests/ -v --tb=short

## docker-test: Run the full test suite inside Docker
docker-test:
	$(COMPOSE) run --rm backend pytest backend/tests/ -v --tb=short

## lint: Run ruff linter (local)
lint:
	$(PYTHON) -m ruff check .

## docker-lint: Run ruff linter inside Docker
docker-lint:
	$(COMPOSE) run --rm backend ruff check .

## format: Auto-format code with ruff (local)
format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check . --fix

## docker-format: Auto-format code with ruff inside Docker
docker-format:
	$(COMPOSE) run --rm backend ruff format .
	$(COMPOSE) run --rm backend ruff check . --fix

## typecheck: Run mypy static type checker (local)
typecheck:
	$(PYTHON) -m mypy backend/

## docker-typecheck: Run mypy static type checker inside Docker
docker-typecheck:
	$(COMPOSE) run --rm backend mypy backend/

## check: Run all quality checks (local)
check: lint typecheck test

## docker-check: Run all quality checks inside Docker
docker-check: docker-lint docker-typecheck docker-test

# --- Build -------------------------------------------------------------------

## build: Build Docker images
build:
	$(COMPOSE) build

# --- Utilities ---------------------------------------------------------------

## clean: Remove caches and build artefacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/

## purge-logos: Remove all local logos and clear database URLs
purge-logos:
	rm -rf backend/static/logos/*
	docker exec finance-copilot-db-1 psql -U postgres -d finance_copilot -c "UPDATE company SET logo_url = NULL;"
