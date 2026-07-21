.PHONY: help install install-dev lint format test cov type check clean run docker

help:
	@echo "Available targets:"
	@echo "  install       Install runtime dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  lint          Run ruff"
	@echo "  format        Auto-format with ruff"
	@echo "  test          Run the test suite"
	@echo "  cov           Run tests with coverage report"
	@echo "  type          Run mypy type checking"
	@echo "  check         Run lint + type + test"
	@echo "  clean         Remove build/test artifacts"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

lint:
	ruff check .

format:
	ruff format .
	test:

test:
	pytest

cov:
	pytest --cov=. --cov-report=term-missing --cov-report=xml

type:
	mypy core modules config.py main.py

check: lint type test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +

run:
	python main.py scan example.com --verbose
