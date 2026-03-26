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

    @classmethod
    def create(cls, title: str, description: Optional[str] = None) -> "Task":
        return cls(
            id=TaskId.new(),
            title=TaskTitle(title),
            description=TaskDescription(description) if description is not None else None,
        )

    def assign(self, assignee_id: str) -> None:
        self.assignee_id = AssigneeId(assignee_id)
        if self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.ASSIGNED
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        if self.status == TaskStatus.COMPLETED:
            raise TaskAlreadyCompletedError("任务已完成，不能重复完成。")
        now = datetime.now(timezone.utc)
        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self.updated_at = now
