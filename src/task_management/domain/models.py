from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"


class DomainError(Exception):
    """Base domain error."""


class InvalidTaskTitleError(DomainError):
    pass


class TaskAlreadyCompletedError(DomainError):
    pass


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
            raise InvalidTaskTitleError("Task title must not be empty.")
        if len(normalized) > 200:
            raise InvalidTaskTitleError("Task title must be at most 200 characters.")
        object.__setattr__(self, "value", normalized)


@dataclass
class Task:
    id: TaskId
    title: TaskTitle
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    @classmethod
    def create(cls, title: str, description: Optional[str] = None) -> "Task":
        return cls(
            id=TaskId.new(),
            title=TaskTitle(title),
            description=description.strip() if description else None,
        )

    def assign(self, assignee_id: str) -> None:
        cleaned = assignee_id.strip()
        if not cleaned:
            raise ValueError("assignee_id must not be empty")
        self.assignee_id = cleaned
        if self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.ASSIGNED
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        if self.status == TaskStatus.COMPLETED:
            raise TaskAlreadyCompletedError("Task is already completed.")
        now = datetime.now(timezone.utc)
        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self.updated_at = now
