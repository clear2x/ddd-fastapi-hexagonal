from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import Optional

from task_management.application.read_models import TaskReadModel
from task_management.domain.models import Task


class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> None: ...

    @abstractmethod
    def get(self, task_id: str) -> Optional[Task]: ...

    @abstractmethod
    def list(self, status: str | None = None, assignee_id: str | None = None) -> Iterable[Task]: ...

    @abstractmethod
    def save(self, task: Task) -> None: ...


class TaskReadModelStore(ABC):
    """查询侧端口，负责维护任务读模型。"""

    @abstractmethod
    def create_task(
        self,
        *,
        task_id: str,
        title: str,
        description: str | None,
        occurred_at: datetime,
    ) -> None: ...

    @abstractmethod
    def assign_task(self, *, task_id: str, assignee_id: str, occurred_at: datetime) -> None: ...

    @abstractmethod
    def complete_task(
        self,
        *,
        task_id: str,
        completed_at: datetime,
        occurred_at: datetime,
    ) -> None: ...


class TaskQueryService(ABC):
    """查询服务端口，应用层通过它读取读模型。"""

    @abstractmethod
    def get(self, task_id: str) -> Optional[TaskReadModel]: ...

    @abstractmethod
    def list(
        self,
        *,
        status: str | None = None,
        assignee_id: str | None = None,
    ) -> Iterable[TaskReadModel]: ...
