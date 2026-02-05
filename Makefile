.PHONY: help install install-dev test test-cov test-prompts run run-prod verify verify-prompts examples docker-build docker-run clean lint format

help:
	@echo "Healthcare AI Service - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run          Run development server with auto-reload"
	@echo "  make test         Run all tests"
	@echo "  make test-cov     Run tests with coverage report"
	@echo "  make test-prompts Run prompt system tests only"
	@echo "  make lint         Run code linters"
	@echo "  make format       Format code with black and isort"
	@echo ""
	@echo "Verification:"
	@echo "  make verify        Run all verification checks"
	@echo "  make verify-prompts Verify prompt system (Post 3)"
	@echo ""
	@echo "Examples:"
	@echo "  make examples      Run all example scripts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"
	@echo "  make docker-up    Start with docker-compose"
	@echo "  make docker-down  Stop docker-compose"
	@echo ""
	@echo "Production:"
	@echo "  make run-prod     Run production server"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove cache files and build artifacts"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-prompts:
	pytest tests/test_prompts.py -v

verify:
	@echo "Running verification checks..."
	@python verify_prompts.py
	@echo ""
	@echo "Running test suite..."
	@pytest tests/ -q
	@echo ""
	@echo "✓ All verifications passed!"

verify-prompts:
	python verify_prompts.py

examples:
	@echo "Running example: Basic ingestion (Post 1)"
	@python examples/test_client.py
	@echo ""
	@echo "Running example: Prompt versioning (Post 3)"
	@python examples/test_prompts.py
	@echo ""
	@echo "For LLM example (Post 2), set ANTHROPIC_API_KEY and run:"
	@echo "  python examples/test_summarize.py"

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

docker-build:
	docker build -t healthcare-ai-service:latest .

docker-run:
	docker run -p 8000:8000 healthcare-ai-service:latest

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

lint:
	flake8 app tests
	mypy app

format:
	black app tests examples
	isort app tests examples

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
