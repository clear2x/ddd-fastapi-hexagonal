# PROJECT_PLAN.md

## Objective
Build an open-source example project using Python + FastAPI with DDD and Hexagonal Architecture.

## Domain choice
Task Management

## Architecture
- Domain: entities, value objects, domain services, repository ports
- Application: commands, use cases, DTOs
- Infrastructure: SQLAlchemy repositories, DB setup
- Interfaces: FastAPI routers, schemas
- Bootstrap: dependency wiring

## Milestones
1. Project scaffold
2. Domain model
3. Application use cases
4. FastAPI HTTP adapter
5. Persistence adapter
6. Tests
7. Documentation

## Parallel work split
- shrimp-architect: propose project structure + coding conventions
- shrimp-backend: implement domain + application core
- shrimp-frontend: define API surface / request-response schemas (used here as interface design)
- shrimp-qa: design tests
- shrimp-reviewer: final review checklist
