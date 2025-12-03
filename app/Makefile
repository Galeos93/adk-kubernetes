# Makefile for ADK Kubernetes Agent
# Development commands for linting, testing, formatting, and running the application

.PHONY: help install install-dev lint format test test-unit test-integration test-coverage quality clean dev prod

# Default target
help: ## Show this help message
	@echo "📚 Available commands:"
	@echo ""
	@echo "🛠️  Setup:"
	@grep -E '^install.*:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧹 Code Quality:"
	@grep -E '^(lint|format|quality).*:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧪 Testing:"
	@grep -E '^test.*:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🚀 Server:"
	@grep -E '^(dev|prod).*:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "� Poetry:"
	@grep -E '^poetry.*:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "�🛠️  Utilities:"
	@grep -E '^(clean|watch|serve).*:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	@echo "📦 Installing production dependencies..."
	poetry install --only=main

install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	poetry install

# Code Quality
lint: ## Run linting checks (ruff + mypy)
	@echo "🧹 Running linting checks..."
	poetry run ruff check .
    # @echo "🔍 Running type checking..."
    # poetry run mypy .
	@echo "✅ Linting completed!"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	poetry run ruff check --fix .
	poetry run ruff format .
	@echo "✅ Code formatting completed!"

quality: lint test ## Run all quality checks (lint + test)
	@echo "🎉 All quality checks passed!"

# Testing
test: ## Run all tests
	@echo "🧪 Running all tests..."
	poetry run pytest -vvv
	@echo "✅ All tests completed!"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	poetry run pytest -m unit
	@echo "✅ Unit tests completed!"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	poetry run pytest -m integration
	@echo "✅ Integration tests completed!"

test-e2e: ## Run end-to-end tests only
	@echo "🧪 Running e2e tests..."
	poetry run pytest -m e2e
	@echo "✅ E2E tests completed!"

# Utilities
clean: ## Clean up generated files and caches
	@echo "🧹 Cleaning up generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/ 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Shortcuts for common workflows
check: format lint ## Format code and run linting
	@echo "🎉 Code check completed!"

ci: format lint test ## Run CI pipeline (format, lint, test)
	@echo "🎉 CI pipeline completed!"

# Docker commands (if you plan to use Docker)
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -f docker/Dockerfile -t fastapi-agent:latest .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run --env-file .env -p 8080:80 fastapi-agent:latest

docker-run-dev: ## Run Docker container in development mode
	@echo "🐳 Running Docker container in development mode..."
	docker run --user root --env-file .env -v ~/.config/gcloud/:/app/.config/gcloud/ \
	-e GOOGLE_APPLICATION_CREDENTIALS=/app/.config/gcloud/application_default_credentials.json \
	-p 8080:8080 fastapi-agent:latest

# Development workflow helpers
watch-test: ## Run tests in watch mode (requires pytest-watch)
	@echo "👀 Running tests in watch mode..."
	poetry run ptw -- --tb=short

# Poetry specific commands
poetry-shell: ## Activate poetry shell
	@echo "🐚 Activating poetry shell..."
	poetry shell

poetry-show: ## Show installed packages
	@echo "📋 Showing installed packages..."
	poetry show

poetry-update: ## Update dependencies
	@echo "⬆️  Updating dependencies..."
	poetry update

poetry-lock: ## Generate/update poetry.lock
	@echo "🔒 Generating/updating poetry.lock..."
	poetry lock

poetry-export: ## Export requirements.txt
	@echo "📤 Exporting requirements.txt..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes