from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DomainEvent:
    """领域事件基类，用于表达领域内已经发生的事实。"""

    event_type: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class TaskCreatedEvent(DomainEvent):
    """任务创建事件。"""

    task_id: str = ""
    title: str = ""
    description: str | None = None

    def __init__(self, task_id: str, title: str, description: str | None) -> None:
        """显式定义初始化逻辑，确保事件名固定且语义清晰。"""
        object.__setattr__(self, "event_type", "task.created")
        object.__setattr__(self, "occurred_at", datetime.now(timezone.utc))
        object.__setattr__(self, "task_id", task_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "description", description)


@dataclass(frozen=True)
class TaskAssignedEvent(DomainEvent):
    """任务指派事件。"""

    task_id: str = ""
    assignee_id: str = ""

    def __init__(self, task_id: str, assignee_id: str) -> None:
        """显式定义初始化逻辑，确保事件名固定且语义清晰。"""
        object.__setattr__(self, "event_type", "task.assigned")
        object.__setattr__(self, "occurred_at", datetime.now(timezone.utc))
        object.__setattr__(self, "task_id", task_id)
        object.__setattr__(self, "assignee_id", assignee_id)


@dataclass(frozen=True)
class TaskCompletedEvent(DomainEvent):
    """任务完成事件。"""

    task_id: str = ""
    completed_at: datetime | None = None

    def __init__(self, task_id: str, completed_at: datetime) -> None:
        """显式定义初始化逻辑，确保事件名固定且语义清晰。"""
        object.__setattr__(self, "event_type", "task.completed")
        object.__setattr__(self, "occurred_at", datetime.now(timezone.utc))
        object.__setattr__(self, "task_id", task_id)
        object.__setattr__(self, "completed_at", completed_at)
