from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException, Query, status

from task_management.application.dto import AssignTaskCommand, CompleteTaskCommand, CreateTaskCommand
from task_management.application.use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
    TaskNotFoundError,
)
from task_management.domain.models import DomainError, TaskAlreadyCompletedError
from task_management.infrastructure.config import settings
from task_management.infrastructure.repository import SqlAlchemyTaskRepository, create_session_factory
from task_management.interfaces.http.schemas import (
    AssignTaskRequest,
    CreateTaskRequest,
    ErrorBody,
    ErrorResponse,
    TaskResponse,
)

session_factory = create_session_factory(settings.database_url)
router = APIRouter(prefix="/api/v1")


def _repository() -> SqlAlchemyTaskRepository:
    session = session_factory()
    return SqlAlchemyTaskRepository(session)


def _to_response(view) -> TaskResponse:
    return TaskResponse(
        id=view.id,
        title=view.title,
        description=view.description,
        assignee_id=view.assignee_id,
        status=view.status.value if hasattr(view.status, "value") else str(view.status),
        created_at=view.created_at,
        updated_at=view.updated_at,
        completed_at=view.completed_at,
    )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: CreateTaskRequest) -> TaskResponse:
    try:
        view = CreateTaskUseCase(_repository()).execute(CreateTaskCommand(**payload.model_dump()))
        return _to_response(view)
    except DomainError as exc:
        raise HTTPException(status_code=400, detail={"code": "DOMAIN_ERROR", "message": str(exc)}) from exc


@router.get("/tasks/{task_id}", response_model=TaskResponse, responses={404: {"model": ErrorResponse}})
def get_task(task_id: str) -> TaskResponse:
    try:
        view = GetTaskUseCase(_repository()).execute(task_id)
        return _to_response(view)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "TASK_NOT_FOUND", "message": str(exc)}) from exc


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    status: str | None = Query(default=None),
    assignee_id: str | None = Query(default=None),
) -> list[TaskResponse]:
    views = ListTasksUseCase(_repository()).execute(status=status, assignee_id=assignee_id)
    return [_to_response(view) for view in views]


@router.post("/tasks/{task_id}/assignments", response_model=TaskResponse)
def assign_task(task_id: str, payload: AssignTaskRequest) -> TaskResponse:
    try:
        view = AssignTaskUseCase(_repository()).execute(
            AssignTaskCommand(task_id=task_id, assignee_id=payload.assignee_id)
        )
        return _to_response(view)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "TASK_NOT_FOUND", "message": str(exc)}) from exc


@router.post("/tasks/{task_id}/completion", response_model=TaskResponse)
def complete_task(task_id: str) -> TaskResponse:
    try:
        view = CompleteTaskUseCase(_repository()).execute(CompleteTaskCommand(task_id=task_id))
        return _to_response(view)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "TASK_NOT_FOUND", "message": str(exc)}) from exc
    except TaskAlreadyCompletedError as exc:
        raise HTTPException(status_code=409, detail={"code": "TASK_ALREADY_COMPLETED", "message": str(exc)}) from exc


def create_app() -> FastAPI:
    app = FastAPI(title="DDD FastAPI Hexagonal Example", version="0.1.0")
    app.include_router(router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
