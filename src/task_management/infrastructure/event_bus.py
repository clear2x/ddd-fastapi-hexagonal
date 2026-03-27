from __future__ import annotations

from collections.abc import Callable, Iterable

from task_management.application.services import DomainEventBus
from task_management.domain.events import DomainEvent


class InMemoryDomainEventBus(DomainEventBus):
    """同步事件总线，适合教学项目与单进程场景。"""

    def __init__(self, handlers: Iterable[Callable[[DomainEvent], None]] | None = None) -> None:
        self.handlers = list(handlers or [])

    def publish(self, events: Iterable[DomainEvent]) -> None:
        """逐个分发事件，保持实现简单直接。"""
        for event in events:
            for handler in self.handlers:
                handler(event)
