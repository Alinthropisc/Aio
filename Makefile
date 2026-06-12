.PHONY: help install dev test lint typecheck migrate docker-up docker-down

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

docker-up: ## Start PostgreSQL + Redis
	docker compose up -d

docker-down: ## Stop infrastructure
	docker compose down

install: ## Install all dependencies
	cd aioback && uv sync
	npm install
	cd aiomobile && flutter pub get && dart run build_runner build --delete-conflicting-outputs

migrate: ## Run Alembic migrations
	cd aioback && alembic upgrade head

dev: docker-up ## Start backend + frontend dev servers
	@echo "Starting backend and frontend..."
	cd aioback && python main.py &
	cd aiofront && npm run dev

test: ## Run all test suites
	cd aioback && uv run pytest --cov
	npm test
	cd aiomobile && flutter test

lint: ## Lint all packages
	cd aioback && ruff check .
	npm run lint
	cd aiomobile && flutter analyze

typecheck: ## Type-check all TS packages
	npm run typecheck

format: ## Auto-format all code
	cd aioback && ruff format .
	cd aiomobile && dart format lib/ test/
