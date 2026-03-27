from __future__ import annotations

from typing import List

from task_management.application.dto import (
    AssignTaskCommand,
    CompleteTaskCommand,
    CreateTaskCommand,
    ListTasksQuery,
    TaskView,
)
from task_management.application.services import DomainEventBus
from task_management.domain.errors import (
    TaskAssignmentNotAllowedError,
    TaskNotFoundError,
)
from task_management.domain.models import Task
from task_management.domain.ports import TaskQueryService, TaskRepository
from task_management.domain.services import TaskDomainService


class CreateTaskUseCase:
    def __init__(self, repository: TaskRepository, event_bus: DomainEventBus | None = None) -> None:
        self.repository = repository
        self.event_bus = event_bus

    def execute(self, command: CreateTaskCommand) -> TaskView:
        task = Task.create(title=command.title, description=command.description)
        self.repository.add(task)
        self._publish(task)
        return TaskView.from_domain(task)

    def _publish(self, task: Task) -> None:
        if self.event_bus is None:
            task.pull_domain_events()
            return
        self.event_bus.publish(task.pull_domain_events())


class GetTaskUseCase:
    """查询单任务时只依赖查询侧端口。

    这里刻意不接受 TaskRepository，避免组装层把教学主路径
    从「TaskQueryService + 读模型」悄悄退回到直接查写库。
    这也意味着：如果写模型存在但读模型缺失，会显式暴露为查询异常状态，
    而不是在查询用例里偷偷回退到命令侧仓储兜底。
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

    当前教学重点是展示“查询侧面向读模型”，
    而不是继续复用命令侧仓储去做列表筛选。
    这也意味着：查询可见性受投影完成度约束，
    当前实现不把它包装成生产级一致性方案。
    """

    def __init__(self, query_service: TaskQueryService) -> None:
        self.query_service = query_service

    def execute(self, query: ListTasksQuery) -> List[TaskView]:
        tasks = self.query_service.list(status=query.status, assignee_id=query.assignee_id)
        return [TaskView.from_read_model(task) for task in tasks]


class AssignTaskUseCase:
    def __init__(
        self,
        repository: TaskRepository,
        domain_service: TaskDomainService | None = None,
        event_bus: DomainEventBus | None = None,
    ) -> None:
        self.repository = repository
        self.domain_service = domain_service or TaskDomainService()
        self.event_bus = event_bus

    def execute(self, command: AssignTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{command.task_id}")
        if not self.domain_service.can_assign(task):
            raise TaskAssignmentNotAllowedError("已完成任务不能再次指派。")
        task.assign(command.assignee_id)
        self.repository.save(task)
        self._publish(task)
        return TaskView.from_domain(task)

    def _publish(self, task: Task) -> None:
        if self.event_bus is None:
            task.pull_domain_events()
            return
        self.event_bus.publish(task.pull_domain_events())


class CompleteTaskUseCase:
    def __init__(self, repository: TaskRepository, event_bus: DomainEventBus | None = None) -> None:
        self.repository = repository
        self.event_bus = event_bus

    def execute(self, command: CompleteTaskCommand) -> TaskView:
        task = self.repository.get(command.task_id)
        if task is None:
            raise TaskNotFoundError(f"任务不存在：{command.task_id}")
        task.complete()
        self.repository.save(task)
        self._publish(task)
        return TaskView.from_domain(task)

    def _publish(self, task: Task) -> None:
        if self.event_bus is None:
            task.pull_domain_events()
            return
        self.event_bus.publish(task.pull_domain_events())
