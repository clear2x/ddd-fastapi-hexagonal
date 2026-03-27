from datetime import datetime

from task_management.application.acl import ExternalTaskSnapshot
from task_management.application.dto import AssignTaskCommand, CreateTaskCommand, ListTasksQuery
from task_management.application.event_handlers import TaskReadModelProjector
from task_management.application.read_models import TaskReadModel
from task_management.application.use_cases import AssignTaskUseCase, CreateTaskUseCase, ListTasksUseCase
from task_management.domain.errors import TaskReadModelNotProjectedError
from task_management.domain.models import Task, TaskStatus
from task_management.domain.ports import TaskQueryService, TaskReadModelStore, TaskRepository
from task_management.infrastructure.event_bus import InMemoryDomainEventBus
from task_management.interfaces.acl.task_import_acl import SimpleExternalTaskTranslator


class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self.items: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self.items[task.id.value] = task

    def get(self, task_id: str):
        return self.items.get(task_id)

    def list(self, status: str | None = None, assignee_id: str | None = None):
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

    def _require_item(self, task_id: str) -> TaskReadModel:
        item = self.items.get(task_id)
        if item is None:
            raise TaskReadModelNotProjectedError(
                f"读模型缺失：task_id={task_id}。写模型可能已存在，但查询侧投影未完成或已损坏。"
            )
        return item

    def assign_task(self, *, task_id: str, assignee_id: str, occurred_at: datetime) -> None:
        item = self._require_item(task_id)
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
        item = self._require_item(task_id)
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


def test_assign_fails_explicitly_when_write_model_exists_but_read_model_is_missing() -> None:
    repository = InMemoryTaskRepository()
    read_store = InMemoryTaskReadModelStore()
    created = CreateTaskUseCase(repository).execute(CreateTaskCommand(title="Broken projection state"))

    try:
        AssignTaskUseCase(
            repository,
            event_bus=InMemoryDomainEventBus([TaskReadModelProjector(read_store).handle]),
        ).execute(AssignTaskCommand(task_id=created.id, assignee_id="user_001"))
    except TaskReadModelNotProjectedError as exc:
        assert created.id in str(exc)
        assert read_store.get(created.id) is None
    else:
        raise AssertionError("missing read model should fail explicitly instead of being swallowed")


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
