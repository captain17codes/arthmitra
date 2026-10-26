.PHONY: up down restart build test lint test-backend test-frontend lint-backend lint-frontend clean

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

build:
	docker compose build

test: test-backend test-frontend

test-backend:
	cd backend && pytest -v

test-frontend:
	cd frontend && npm test

lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check . && mypy app engines adapters

lint-frontend:
	cd frontend && npm run lint

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
