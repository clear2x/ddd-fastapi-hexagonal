from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

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
