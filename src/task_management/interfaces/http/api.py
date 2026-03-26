from __future__ import annotations

from fastapi import APIRouter, FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from task_management.application.dto import AssignTaskCommand, CompleteTaskCommand, CreateTaskCommand, ListTasksQuery
from task_management.application.use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
)
from task_management.domain.errors import DomainError, TaskAlreadyCompletedError, TaskNotFoundError
from task_management.domain.models import TaskStatus
from task_management.infrastructure.config import settings
from task_management.infrastructure.repository import SqlAlchemyTaskRepository, create_session_factory
from task_management.interfaces.http.schemas import (
    ApiResponse,
    AssignTaskRequest,
    CreateTaskRequest,
    ErrorBody,
    ErrorResponse,
    HealthResponse,
    TaskResponse,
)

session_factory = create_session_factory(settings.database_url)
router = APIRouter(prefix="/api/v1")


def _repository() -> SqlAlchemyTaskRepository:
    session = session_factory()
    return SqlAlchemyTaskRepository(session)


def _to_response(view) -> TaskResponse:
    status_value = view.status.value if isinstance(view.status, TaskStatus) else str(view.status)
    return TaskResponse(
        id=view.id,
        title=view.title,
        description=view.description,
        assignee_id=view.assignee_id,
        status=status_value,
        created_at=view.created_at,
        updated_at=view.updated_at,
        completed_at=view.completed_at,
    )


def _success_response(data):
    return ApiResponse(data=data)


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, object]] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or []),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


def _validation_error_detail(exc: RequestValidationError) -> list[dict[str, object]]:
    details: list[dict[str, object]] = []
    for error in exc.errors():
        details.append(
            {
                "field": ".".join(str(item) for item in error.get("loc", []) if item != "body"),
                "message": error.get("msg", "请求参数校验失败"),
                "type": error.get("type", "validation_error"),
            }
        )
    return details


def _register_exception_handlers(app: FastAPI) -> None:
    async def handle_task_not_found(_: Request, exc: TaskNotFoundError) -> JSONResponse:
        return _error_response(status_code=404, code="TASK_NOT_FOUND", message=str(exc))

    async def handle_task_completed(_: Request, exc: TaskAlreadyCompletedError) -> JSONResponse:
        return _error_response(status_code=409, code="TASK_ALREADY_COMPLETED", message=str(exc))

    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return _error_response(status_code=400, code="DOMAIN_ERROR", message=str(exc))

    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            status_code=422,
            code="REQUEST_VALIDATION_ERROR",
            message="请求参数校验失败",
            details=_validation_error_detail(exc),
        )

    app.add_exception_handler(TaskNotFoundError, handle_task_not_found)
    app.add_exception_handler(TaskAlreadyCompletedError, handle_task_completed)
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)


@router.post(
    "/tasks",
    response_model=ApiResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_task(payload: CreateTaskRequest) -> ApiResponse[TaskResponse]:
    view = CreateTaskUseCase(_repository()).execute(CreateTaskCommand(**payload.model_dump()))
    return _success_response(_to_response(view))


@router.get(
    "/tasks/{task_id}",
    response_model=ApiResponse[TaskResponse],
    responses={404: {"model": ErrorResponse}},
)
def get_task(task_id: str) -> ApiResponse[TaskResponse]:
    view = GetTaskUseCase(_repository()).execute(task_id)
    return _success_response(_to_response(view))


@router.get(
    "/tasks",
    response_model=ApiResponse[list[TaskResponse]],
    responses={422: {"model": ErrorResponse}},
)
def list_tasks(
    status: str | None = Query(default=None),
    assignee_id: str | None = Query(default=None),
) -> ApiResponse[list[TaskResponse]]:
    views = ListTasksUseCase(_repository()).execute(
        ListTasksQuery(status=status, assignee_id=assignee_id)
    )
    return _success_response([_to_response(view) for view in views])


@router.post(
    "/tasks/{task_id}/assignments",
    response_model=ApiResponse[TaskResponse],
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def assign_task(task_id: str, payload: AssignTaskRequest) -> ApiResponse[TaskResponse]:
    view = AssignTaskUseCase(_repository()).execute(
        AssignTaskCommand(task_id=task_id, assignee_id=payload.assignee_id)
    )
    return _success_response(_to_response(view))


@router.post(
    "/tasks/{task_id}/completion",
    response_model=ApiResponse[TaskResponse],
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def complete_task(task_id: str) -> ApiResponse[TaskResponse]:
    view = CompleteTaskUseCase(_repository()).execute(CompleteTaskCommand(task_id=task_id))
    return _success_response(_to_response(view))


def create_app() -> FastAPI:
    app = FastAPI(title="DDD FastAPI Hexagonal Example", version="0.1.0")
    _register_exception_handlers(app)
    app.include_router(router)

    @app.get("/health", response_model=ApiResponse[HealthResponse])
    def health() -> ApiResponse[HealthResponse]:
        return _success_response(HealthResponse(status="ok"))

    return app


app = create_app()
