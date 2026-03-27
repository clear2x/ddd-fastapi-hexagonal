from __future__ import annotations

from typing import List

from task_management.application.dto import (
    AssignTaskCommand,
    CompleteTaskCommand,
    CreateTaskCommand,
    ListTasksQuery,
    TaskView,
)
from task_management.application.read_models import TaskQueryService
from task_management.domain.errors import TaskNotFoundError
from task_management.domain.models import Task
from task_management.domain.ports import TaskRepository


class CreateTaskUseCase:
    def __init__(self, repository: TaskRepository, event_bus=None) -> None:
        self.repository = repository
        self.event_bus = event_bus

    def execute(self, command: CreateTaskCommand) -> TaskView:
        task = Task.create(title=command.title, description=command.description)
        self.repository.add(task)
        if self.event_bus is not None:
            self.event_bus.publish(task.pull_domain_events())
        return TaskView.from_domain(task)


class GetTaskUseCase:
    """查询单任务时只依赖查询侧端口。

    这里刻意不接受 TaskRepository，避免组装层把教学主路径
    从「TaskQueryService + 读模型」悄悄退回到直接查写库。
    """

    def __init__(self, query_service: TaskQueryService) -> None:
        self.query_service = query_service

    def execute(self, task_id: str) -> TaskView:
        task = self.query_service.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{task_id}")
        return TaskView.from_read_model(task)


class ListTasksUseCase:
    """查询列表时只依赖查询侧端口。

    教学语义上，这里应展示 CQRS 风格的读模型读取，
    而不是回退为直接遍历命令侧聚合仓储。
    """

    def __init__(self, query_service: TaskQueryService) -> None:
        self.query_service = query_service

    def execute(self, query: ListTasksQuery) -> List[TaskView]:
        tasks = self.query_service.list(status=query.status, assignee_id=query.assignee_id)
        return [TaskView.from_read_model(task) for task in tasks]


class AssignTaskUseCase:
    def __init__(self, repository: TaskRepository, event_bus=None) -> None:
        self.repository = repository
        self.event_bus = event_bus

    def execute(self, command: AssignTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{command.task_id}")
        task.assign(command.assignee_id)
        self.repository.save(task)
        if self.event_bus is not None:
            self.event_bus.publish(task.pull_domain_events())
        return TaskView.from_domain(task)


class CompleteTaskUseCase:
    def __init__(self, repository: TaskRepository, event_bus=None) -> None:
        self.repository = repository
        self.event_bus = event_bus

    def execute(self, command: CompleteTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{command.task_id}")
        task.complete()
        self.repository.save(task)
        if self.event_bus is not None:
            self.event_bus.publish(task.pull_domain_events())
        return TaskView.from_domain(task)
