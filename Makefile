# =============================================================================
# finance-copilot — Makefile
# Convenience targets for development, testing, and deployment.
# Run `make help` for a full list of available commands.
# =============================================================================

.PHONY: help install install-dev dev up down build \
        test lint format typecheck clean

# --- Variables ---------------------------------------------------------------
PYTHON      := python3.11
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

# --- Development server ------------------------------------------------------

## dev: Run FastAPI backend in hot-reload mode (no Docker)
dev:
	$(UVICORN) --reload --host 0.0.0.0 --port 8000

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

## test: Run the full test suite
test:
	pytest backend/tests/ -v --tb=short

## lint: Run ruff linter
lint:
	ruff check .

## format: Auto-format code with ruff
format:
	ruff format .
	ruff check . --fix

## typecheck: Run mypy static type checker
typecheck:
	mypy backend/

## check: Run lint + typecheck (used in CI)
check: lint typecheck

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
