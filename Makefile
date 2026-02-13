.PHONY: help check fix lint format typecheck test test-quick coverage security notify clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Quality ===

lint: ## Run linter
	uv run ruff check src/

format: ## Format code
	uv run ruff format src/

fix: ## Auto-fix lint issues and format
	uv run ruff check --fix src/
	uv run ruff format src/

typecheck: ## Run type checker
	uv run mypy src/

check: lint typecheck test ## Run lint + types + tests

# === Testing ===

test: ## Run all tests
	uv run pytest tests/ -v

test-quick: ## Run tests with fast fail
	uv run pytest tests/ -x -q --tb=short

coverage: ## Run tests with coverage report
	uv run pytest tests/ --cov=src/ --cov-report=term-missing --cov-report=html

# === Security ===

security: ## Run security scan
	uv run bandit -r src/ -c pyproject.toml || true

# === Notifications ===

notify: ## Send notification (MSG="your message")
	@if [ -n "$$NTFY_TOPIC" ]; then \
		curl -s -H "Title: $(or $(TITLE),Project Notification)" \
			-d "$(or $(MSG),Task completed)" \
			ntfy.sh/$$NTFY_TOPIC; \
		echo ""; \
	else \
		echo "NTFY_TOPIC not set. Run: export NTFY_TOPIC=your-topic"; \
	fi

# === Cleanup ===

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov/ .coverage coverage.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
