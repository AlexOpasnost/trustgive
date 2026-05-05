.PHONY: help dev test lint typecheck migrate seed perf clean install
.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## First-time install (backend + frontend + e2e)
	cd backend && python -m venv .venv && \
		. .venv/bin/activate && pip install -r requirements.txt
	cd frontend/web && npm install
	cd e2e && npm install && npx playwright install --with-deps chromium

dev-backend: ## Run backend dev server
	cd backend && . .venv/bin/activate && python manage.py runserver

dev-frontend: ## Run frontend dev server
	cd frontend/web && npm run dev

migrate: ## Apply DB migrations
	cd backend && . .venv/bin/activate && \
		python manage.py makemigrations charities ingestion events i18n_app && \
		python manage.py migrate

seed: ## Ingest 100 sample charities from ProPublica
	cd backend && . .venv/bin/activate && \
		python manage.py ingest_propublica --bootstrap --limit=100

test: test-backend test-frontend ## Run all unit tests

test-backend: ## Backend pytest
	cd backend && . .venv/bin/activate && pytest --tb=short -q

test-frontend: ## Frontend vitest
	cd frontend/web && npm test -- --run

test-e2e: ## E2E Playwright (requires backend + frontend running)
	cd e2e && npm test

lint: ## Lint backend + frontend
	cd backend && . .venv/bin/activate && ruff check .
	cd frontend/web && npm run lint

typecheck: ## Type-check frontend
	cd frontend/web && npm run typecheck

perf: ## Run k6 smoke + load against localhost
	k6 run performance/k6-smoke.js
	k6 run performance/k6-load.js

clean: ## Remove caches + build artifacts
	cd backend && rm -rf .pytest_cache .mypy_cache .ruff_cache __pycache__
	cd frontend/web && rm -rf node_modules dist .vite
