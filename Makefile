PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .[dev]

run:
	uvicorn task_management.main:app --reload

test:
	$(PYTHON) -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check .
