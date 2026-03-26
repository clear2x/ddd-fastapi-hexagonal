# Contributing

## Branches

Suggested long-lived work branches:
- feat/domain-core
- feat/http-api
- feat/tests-docs-ci

## Rules

- Keep domain free from FastAPI and SQLAlchemy imports
- Prefer one use case per file when the application layer grows
- Add or update tests with behavior changes
- Keep README and docs aligned with the actual API

## Before opening a PR

- Run tests
- Check API examples
- Verify architectural boundaries still make sense
