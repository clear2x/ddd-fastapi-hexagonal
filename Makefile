PYTHON ?= python3
UVICORN ?= uvicorn
APP_MODULE ?= task_management.main:app
RUFF_TARGETS ?= src tests
PYTEST_ARGS ?=

.PHONY: install run test test-cov lint format-check check ci clean

install:
	$(PYTHON) -m pip install -e .[dev]

run:
	$(PYTHON) -m $(UVICORN) $(APP_MODULE) --reload

test:
	$(PYTHON) -m pytest $(PYTEST_ARGS)

test-cov:
	$(PYTHON) -m pytest --cov=task_management --cov-report=term-missing $(PYTEST_ARGS)

lint:
	$(PYTHON) -m ruff check $(RUFF_TARGETS)

format-check:
	$(PYTHON) -m ruff format --check $(RUFF_TARGETS)

check: lint test

ci: lint format-check test-cov

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist build .eggs
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -f tasks.db
