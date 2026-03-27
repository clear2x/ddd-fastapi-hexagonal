from __future__ import annotations

from collections.abc import Iterable

from task_management.domain.events import DomainEvent


class DomainEventBus:
    """领域事件总线端口，负责发布已经发生的领域事实。"""

    def publish(self, events: Iterable[DomainEvent]) -> None:
        raise NotImplementedError
