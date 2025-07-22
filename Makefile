.PHONY: test test-unit test-integration test-coverage install clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  install         Install package in development mode"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  clean          Clean up build artifacts"

# Install package in development mode
install:
	pip install -e .
	pip install -r requirements.txt

# Run all tests
test:
	pytest tests/ -v

# Run unit tests only
test-unit:
	pytest tests/unit/ -v

# Run integration tests only
test-integration:
	pytest tests/integration/ -v

# Run tests with coverage
test-coverage:
	pip install coverage
	coverage run -m pytest tests/
	coverage report -m
	coverage html

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete