# Architecture

This project demonstrates a small but readable DDD + Hexagonal Architecture example.

## Layers

- **Domain**: business model and invariants
- **Application**: use-case orchestration
- **Infrastructure**: persistence and runtime concerns
- **Interfaces**: HTTP API via FastAPI

## Dependency direction

Outer layers depend on inner abstractions.

- interfaces -> application
- application -> domain
- infrastructure -> domain/application ports
- domain -> nothing external

## Example domain

The demo uses a Task Management domain:
- create task
- get task
- list tasks
- assign task
- complete task

## Why this repository stays intentionally small

The goal is not feature richness.
The goal is to make architectural boundaries easy to read and easy to extend.
