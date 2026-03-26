from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from task_management.domain.models import Task, TaskStatus


@dataclass(frozen=True)
class CreateTaskCommand:
    title: str
    description: Optional[str] = None


@dataclass(frozen=True)
class AssignTaskCommand:
    task_id: str
    assignee_id: str


@dataclass(frozen=True)
class CompleteTaskCommand:
    task_id: str


@dataclass(frozen=True)
class TaskView:
    id: str
    title: str
    description: Optional[str]
    assignee_id: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    @staticmethod
    def from_domain(task: Task) -> "TaskView":
        return TaskView(
            id=task.id.value,
            title=task.title.value,
            description=task.description,
            assignee_id=task.assignee_id,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )
