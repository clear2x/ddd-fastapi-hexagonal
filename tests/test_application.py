from task_management.application.dto import CreateTaskCommand, ListTasksQuery
from task_management.application.use_cases import CreateTaskUseCase, ListTasksUseCase
from task_management.domain.models import Task
from task_management.domain.ports import TaskRepository


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
