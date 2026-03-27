from __future__ import annotations

from task_management.domain.models import Task, TaskStatus


class TaskDomainService:
    """封装跨实体规则，避免把策略判断散落到应用层。"""

    def can_assign(self, task: Task) -> bool:
        """已完成任务不能再次被指派。"""
        return task.status != TaskStatus.COMPLETED
