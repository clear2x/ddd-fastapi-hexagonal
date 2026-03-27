import pytest

from task_management.domain.errors import (
    InvalidAssigneeIdError,
    InvalidTaskDescriptionError,
    InvalidTaskTitleError,
    TaskAlreadyCompletedError,
    TaskAssignmentNotAllowedError,
)
from task_management.domain.models import Task, TaskStatus
from task_management.domain.services import TaskDomainService


def test_create_task_success() -> None:
    task = Task.create(title="Write docs", description="Explain architecture")
    assert task.title.value == "Write docs"
    assert task.description is not None
    assert task.description.value == "Explain architecture"
    assert task.status == TaskStatus.PENDING


def test_create_task_with_empty_title_fails() -> None:
    with pytest.raises(InvalidTaskTitleError):
        Task.create(title="   ")


def test_create_task_with_blank_description_fails() -> None:
    with pytest.raises(InvalidTaskDescriptionError):
        Task.create(title="Write docs", description="   ")


def test_assign_task_with_empty_assignee_fails() -> None:
    task = Task.create(title="Ship MVP")
    with pytest.raises(InvalidAssigneeIdError):
        task.assign("   ")


def test_complete_task_twice_fails() -> None:
    task = Task.create(title="Ship MVP")
    task.complete()
    with pytest.raises(TaskAlreadyCompletedError):
        task.complete()


def test_create_task_records_domain_event() -> None:
    task = Task.create(title="Track event")

    events = task.pull_domain_events()

    assert len(events) == 1
    assert events[0].event_type == "task.created"
    assert events[0].task_id == task.id.value


def test_completed_task_cannot_be_assigned_again() -> None:
    task = Task.create(title="Guard completed task")
    task.complete()

    with pytest.raises(TaskAssignmentNotAllowedError):
        if not TaskDomainService().can_assign(task):
            raise TaskAssignmentNotAllowedError("已完成任务不能再次指派。")
