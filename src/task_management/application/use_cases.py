from __future__ import annotations

from typing import List

from task_management.application.dto import (
    AssignTaskCommand,
    CompleteTaskCommand,
    CreateTaskCommand,
    ListTasksQuery,
    TaskView,
)
from task_management.domain.errors import TaskNotFoundError
from task_management.domain.models import Task
from task_management.domain.ports import TaskRepository


class CreateTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, command: CreateTaskCommand) -> TaskView:
        task = Task.create(title=command.title, description=command.description)
        self.repository.add(task)
        return TaskView.from_domain(task)


class GetTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, task_id: str) -> TaskView:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{task_id}")
        return TaskView.from_domain(task)


class ListTasksUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, query: ListTasksQuery) -> List[TaskView]:
        tasks = self.repository.list(status=query.status, assignee_id=query.assignee_id)
        return [TaskView.from_domain(task) for task in tasks]


class AssignTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, command: AssignTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{command.task_id}")
        task.assign(command.assignee_id)
        self.repository.save(task)
        return TaskView.from_domain(task)


class CompleteTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, command: CompleteTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{command.task_id}")
        task.complete()
        self.repository.save(task)
        return TaskView.from_domain(task)
