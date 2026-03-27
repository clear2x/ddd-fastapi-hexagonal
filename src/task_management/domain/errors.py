from __future__ import annotations


class DomainError(Exception):
    """领域层异常基类。"""


class InvalidTaskTitleError(DomainError):
    """任务标题不合法。"""


class InvalidTaskDescriptionError(DomainError):
    """任务描述不合法。"""


class InvalidAssigneeIdError(DomainError):
    """指派人标识不合法。"""


class TaskAlreadyCompletedError(DomainError):
    """任务已完成，不允许重复完成。"""


class TaskAssignmentNotAllowedError(DomainError):
    """任务当前状态不允许再被指派。"""


class TaskNotFoundError(DomainError):
    """任务不存在。"""
