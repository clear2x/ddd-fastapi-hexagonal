from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from task_management.domain.models import TaskStatus


@dataclass(frozen=True)
class TaskReadModel:
    """查询侧读模型，面向展示与列表筛选。"""

    id: str
    title: str
    description: Optional[str]
    assignee_id: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
