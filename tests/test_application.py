from task_management.application.acl import ExternalTaskSnapshot
from task_management.application.dto import CreateTaskCommand, ListTasksQuery
from task_management.application.use_cases import CreateTaskUseCase, ListTasksUseCase
from task_management.domain.models import Task
from task_management.domain.ports import TaskRepository
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


def test_create_task_use_case_returns_view() -> None:
    repository = InMemoryTaskRepository()
    view = CreateTaskUseCase(repository).execute(
        CreateTaskCommand(title="  Design domain ", description="  refine aggregate ")
    )

    assert view.title == "Design domain"
    assert view.description == "refine aggregate"
    assert view.id in repository.items


def test_list_tasks_use_case_uses_query_object() -> None:
    repository = InMemoryTaskRepository()
    task = Task.create(title="Domain event mapping")
    task.assign("user_001")
    repository.add(task)

    result = ListTasksUseCase(repository).execute(ListTasksQuery(status="assigned", assignee_id="user_001"))

    assert len(result) == 1
    assert result[0].assignee_id == "user_001"
    assert result[0].status.value == "assigned"


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
