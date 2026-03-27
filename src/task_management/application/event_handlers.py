from __future__ import annotations

from task_management.domain.events import DomainEvent, TaskAssignedEvent, TaskCompletedEvent, TaskCreatedEvent
from task_management.domain.ports import TaskReadModelStore


class TaskReadModelProjector:
    """把领域事件投影到查询读模型。"""

    def __init__(self, store: TaskReadModelStore) -> None:
        self.store = store

    def handle(self, event: DomainEvent) -> None:
        """根据事件类型更新读模型。"""
        if isinstance(event, TaskCreatedEvent):
            self.store.create_task(
                task_id=event.task_id,
                title=event.title,
                description=event.description,
                occurred_at=event.occurred_at,
            )
            return

        if isinstance(event, TaskAssignedEvent):
            self.store.assign_task(
                task_id=event.task_id,
                assignee_id=event.assignee_id,
                occurred_at=event.occurred_at,
            )
            return

        if isinstance(event, TaskCompletedEvent):
            self.store.complete_task(
                task_id=event.task_id,
                completed_at=event.completed_at,
                occurred_at=event.occurred_at,
            )
