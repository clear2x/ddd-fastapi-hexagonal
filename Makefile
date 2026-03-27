PYTHON ?= python3

.PHONY: install run test lint quality clean

install:
	$(PYTHON) -m pip install -e .[dev]

run:
	uvicorn task_management.main:app --reload

test:
	$(PYTHON) -m pytest

lint:
	ruff check .

quality:
	$(PYTHON) -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80
	$(PYTHON) -m pytest tests/test_quality.py
	$(MAKE) lint

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist build .eggs
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -f tasks.db
