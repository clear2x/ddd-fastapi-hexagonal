from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from task_management.domain.errors import (
    InvalidAssigneeIdError,
    InvalidTaskDescriptionError,
    InvalidTaskTitleError,
    TaskAlreadyCompletedError,
)
from task_management.domain.events import DomainEvent, TaskAssignedEvent, TaskCompletedEvent, TaskCreatedEvent


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"


@dataclass(frozen=True)
class TaskId:
    value: str

    @staticmethod
    def new() -> "TaskId":
        return TaskId(value=f"task_{uuid4().hex}")


@dataclass(frozen=True)
class TaskTitle:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidTaskTitleError("任务标题不能为空。")
        if len(normalized) > 200:
            raise InvalidTaskTitleError("任务标题长度不能超过 200 个字符。")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class TaskDescription:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidTaskDescriptionError("任务描述不能为空字符串。")
        if len(normalized) > 2000:
            raise InvalidTaskDescriptionError("任务描述长度不能超过 2000 个字符。")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class AssigneeId:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidAssigneeIdError("指派人标识不能为空。")
        if len(normalized) > 128:
            raise InvalidAssigneeIdError("指派人标识长度不能超过 128 个字符。")
        object.__setattr__(self, "value", normalized)


@dataclass
class Task:
    id: TaskId
    title: TaskTitle
    description: Optional[TaskDescription] = None
    assignee_id: Optional[AssigneeId] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(cls, title: str, description: Optional[str] = None) -> "Task":
        task = cls(
            id=TaskId.new(),
            title=TaskTitle(title),
            description=TaskDescription(description) if description is not None else None,
        )
        task._record_event(
            TaskCreatedEvent(
                task_id=task.id.value,
                title=task.title.value,
                description=task.description.value if task.description is not None else None,
            )
        )
        return task

    def assign(self, assignee_id: str) -> None:
        self.assignee_id = AssigneeId(assignee_id)
        if self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.ASSIGNED
        self.updated_at = datetime.now(timezone.utc)
        self._record_event(
            TaskAssignedEvent(task_id=self.id.value, assignee_id=self.assignee_id.value)
        )

    def complete(self) -> None:
        if self.status == TaskStatus.COMPLETED:
            raise TaskAlreadyCompletedError("任务已完成，不能重复完成。")
        now = datetime.now(timezone.utc)
        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self.updated_at = now
        self._record_event(TaskCompletedEvent(task_id=self.id.value, completed_at=now))

    def pull_domain_events(self) -> list[DomainEvent]:
        """拉取并清空聚合内积累的领域事件。"""
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def _record_event(self, event: DomainEvent) -> None:
        """记录聚合内发生的领域事件，等待应用层统一发布。"""
        self._domain_events.append(event)
