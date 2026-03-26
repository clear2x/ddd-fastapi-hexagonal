from __future__ import annotations

from typing import List, Optional

from task_management.application.dto import (
    AssignTaskCommand,
    CompleteTaskCommand,
    CreateTaskCommand,
    TaskView,
)
from task_management.domain.models import Task
from task_management.domain.ports import TaskRepository


class TaskNotFoundError(Exception):
    pass


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
            raise TaskNotFoundError(f"Task '{task_id}' not found.")
        return TaskView.from_domain(task)


class ListTasksUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, status: Optional[str] = None, assignee_id: Optional[str] = None) -> List[TaskView]:
        tasks = self.repository.list(status=status, assignee_id=assignee_id)
        return [TaskView.from_domain(task) for task in tasks]


class AssignTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, command: AssignTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"Task '{command.task_id}' not found.")
        task.assign(command.assignee_id)
        self.repository.save(task)
        return TaskView.from_domain(task)


class CompleteTaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def execute(self, command: CompleteTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"Task '{command.task_id}' not found.")
        task.complete()
        self.repository.save(task)
        return TaskView.from_domain(task)
