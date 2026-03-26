# ddd-fastapi-hexagonal

A minimal open-source example project showing how to build a DDD + Hexagonal Architecture service with Python and FastAPI.

Repository: <https://github.com/clear2x/ddd-fastapi-hexagonal>

## What this project demonstrates

- Domain-driven design (DDD)
- Hexagonal architecture (ports and adapters)
- FastAPI as the inbound HTTP adapter
- SQLAlchemy as the outbound persistence adapter
- A clean split between domain, application, infrastructure, and interfaces

## Example domain

This demo uses a simple **Task Management** domain with five operations:
- Create task
- Get task
- List tasks
- Assign task
- Complete task

## Project structure

```text
src/task_management/
  domain/
  application/
  infrastructure/
  interfaces/http/
tests/
docs/
```

## API

- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks/{task_id}/assignments`
- `POST /api/v1/tasks/{task_id}/completion`
- `GET /health`

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn task_management.main:app --reload
pytest
```

## CI

GitHub Actions runs tests on push and pull request.

## Contributing strategy

Current parallel work split:
- `feat/domain-core`
- `feat/http-api`
- `feat/tests-docs-ci`

See also:
- `docs/architecture.md`
- `docs/testing.md`
- `CONTRIBUTING.md`

## Current status

This repository already contains a working MVP code structure and initial test files.
The next step is to deepen domain boundaries, improve HTTP error modeling, and strengthen tests and documentation.

## Why this is hexagonal

- **Domain** contains the business model and rules
- **Application** orchestrates use cases
- **Infrastructure** implements ports (SQLAlchemy repository)
- **Interfaces** expose the app via FastAPI

This is intentionally small so the architecture stays readable.
