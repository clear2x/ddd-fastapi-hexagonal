PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .[dev]

run:
	uvicorn task_management.main:app --reload

test:
	pytest

lint:
	ruff check src tests
