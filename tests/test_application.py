from datetime import datetime

from task_management.application.acl import ExternalTaskSnapshot
from task_management.application.assemblers import get_task_use_case, list_tasks_use_case
from task_management.application.dto import AssignTaskCommand, CreateTaskCommand, ListTasksQuery
from task_management.application.event_handlers import TaskReadModelProjector
from task_management.application.read_models import TaskReadModel
from task_management.application.use_cases import AssignTaskUseCase, CreateTaskUseCase, ListTasksUseCase
from task_management.domain.models import Task, TaskStatus
from task_management.domain.ports import TaskQueryService, TaskReadModelStore, TaskRepository
from task_management.infrastructure.event_bus import InMemoryDomainEventBus
from task_management.interfaces.acl.task_import_acl import SimpleExternalTaskTranslator


class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self.items: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self.items[task.id.value] = task

    def get(self, task_id: str) -> Task | None:
        return self.items.get(task_id)

    def list(self, status: str | None = None, assignee_id: str | None = None) -> list[Task]:
        tasks = list(self.items.values())
        if status is not None:
            tasks = [task for task in tasks if task.status.value == status]
        if assignee_id is not None:
            tasks = [task for task in tasks if task.assignee_id and task.assignee_id.value == assignee_id]
        return tasks

    def save(self, task: Task) -> None:
        self.items[task.id.value] = task


class InMemoryTaskReadModelStore(TaskReadModelStore, TaskQueryService):
    def __init__(self) -> None:
        self.items: dict[str, TaskReadModel] = {}

    def create_task(
        self,
        *,
        task_id: str,
        title: str,
        description: str | None,
        occurred_at: datetime,
    ) -> None:
        self.items[task_id] = TaskReadModel(
            id=task_id,
            title=title,
            description=description,
            assignee_id=None,
            status=TaskStatus.PENDING,
            created_at=occurred_at,
            updated_at=occurred_at,
            completed_at=None,
        )

    def assign_task(self, *, task_id: str, assignee_id: str, occurred_at: datetime) -> None:
        item = self.items[task_id]
        self.items[task_id] = TaskReadModel(
            id=item.id,
            title=item.title,
            description=item.description,
            assignee_id=assignee_id,
            status=TaskStatus.ASSIGNED,
            created_at=item.created_at,
            updated_at=occurred_at,
            completed_at=item.completed_at,
        )

    def complete_task(
        self,
        *,
        task_id: str,
        completed_at: datetime,
        occurred_at: datetime,
    ) -> None:
        item = self.items[task_id]
        self.items[task_id] = TaskReadModel(
            id=item.id,
            title=item.title,
            description=item.description,
            assignee_id=item.assignee_id,
            status=TaskStatus.COMPLETED,
            created_at=item.created_at,
            updated_at=occurred_at,
            completed_at=completed_at,
        )

    def get(self, task_id: str) -> TaskReadModel | None:
        return self.items.get(task_id)

    def list(
        self,
        *,
        status: str | None = None,
        assignee_id: str | None = None,
    ) -> list[TaskReadModel]:
        tasks = list(self.items.values())
        if status is not None:
            tasks = [task for task in tasks if task.status.value == status]
        if assignee_id is not None:
            tasks = [task for task in tasks if task.assignee_id == assignee_id]
        return tasks


class RepositoryOnlyQueryService(TaskQueryService):
    """若 assembler/用例误用写库路径，这个测试替身会直接炸掉。"""

    def get(self, task_id: str) -> TaskReadModel | None:
        raise AssertionError("query path must not fall back to repository-backed lookup")

    def list(
        self,
        *,
        status: str | None = None,
        assignee_id: str | None = None,
    ) -> list[TaskReadModel]:
        raise AssertionError("query path must not fall back to repository-backed lookup")


def test_create_task_use_case_returns_view() -> None:
    repository = InMemoryTaskRepository()
    read_store = InMemoryTaskReadModelStore()
    event_bus = InMemoryDomainEventBus([TaskReadModelProjector(read_store).handle])
    view = CreateTaskUseCase(repository, event_bus).execute(
        CreateTaskCommand(title="  Design domain ", description="  refine aggregate ")
    )

    assert view.title == "Design domain"
    assert view.description == "refine aggregate"
    assert view.id in repository.items
    assert read_store.get(view.id) is not None


def test_list_tasks_use_case_uses_query_object() -> None:
    repository = InMemoryTaskRepository()
    read_store = InMemoryTaskReadModelStore()
    event_bus = InMemoryDomainEventBus([TaskReadModelProjector(read_store).handle])
    created = CreateTaskUseCase(repository, event_bus).execute(
        CreateTaskCommand(title="Domain event mapping")
    )
    AssignTaskUseCase(repository, event_bus=event_bus).execute(
        AssignTaskCommand(task_id=created.id, assignee_id="user_001")
    )

    result = ListTasksUseCase(read_store).execute(
        ListTasksQuery(status="assigned", assignee_id="user_001")
    )

    assert len(result) == 1
    assert result[0].assignee_id == "user_001"
    assert result[0].status.value == "assigned"


def test_get_and_list_use_cases_only_accept_query_service_read_models() -> None:
    query_service = RepositoryOnlyQueryService()

    get_use_case = get_task_use_case()
    list_use_case = list_tasks_use_case()

    assert type(get_use_case.query_service).__name__ == "SqlAlchemyTaskQueryService"
    assert type(list_use_case.query_service).__name__ == "SqlAlchemyTaskQueryService"

    direct_get = type(get_use_case)(query_service)
    direct_list = type(list_use_case)(query_service)

    try:
        direct_get.execute("task_123")
    except AssertionError as exc:
        assert "must not fall back" in str(exc)
    else:
        raise AssertionError("GetTaskUseCase should read through TaskQueryService only")

    try:
        direct_list.execute(ListTasksQuery())
    except AssertionError as exc:
        assert "must not fall back" in str(exc)
    else:
        raise AssertionError("ListTasksUseCase should read through TaskQueryService only")


def test_acl_translator_maps_external_snapshot_into_internal_draft() -> None:
    translator = SimpleExternalTaskTranslator(source_system="jira")

    draft = translator.translate(
        ExternalTaskSnapshot(
            external_id="JIRA-123",
            title="  Sync ACL boundary  ",
            description="  keep external shape outside domain  ",
            assignee_reference="account_42",
            state="in_progress",
        )
    )

    assert draft.title == "Sync ACL boundary"
    assert draft.description == "keep external shape outside domain"
    assert draft.assignee_id == "account_42"
    assert draft.source_system == "jira"
    assert draft.source_identifier == "JIRA-123"


def test_acl_translator_keeps_external_state_outside_imported_draft() -> None:
    translator = SimpleExternalTaskTranslator(source_system="trello")

    draft = translator.translate(
        ExternalTaskSnapshot(
            external_id="card-9",
            title="Review ACL",
            description=None,
            assignee_reference=None,
            state="done",
        )
    )

    assert not hasattr(draft, "state")
    assert draft.description is None
    assert draft.assignee_id is None
