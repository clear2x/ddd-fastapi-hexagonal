PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .[dev]

run:
	uvicorn task_management.main:app --reload

check:
	$(PYTHON) -m pytest

lint:
	ruff check .

test:
	$(PYTHON) -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80

ci:
	ruff check .
	$(PYTHON) -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80
