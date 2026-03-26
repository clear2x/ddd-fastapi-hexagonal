import pytest

from task_management.domain.models import (
    InvalidTaskTitleError,
    Task,
    TaskAlreadyCompletedError,
    TaskStatus,
)


def test_create_task_success() -> None:
    task = Task.create(title="Write docs", description="Explain architecture")
    assert task.title.value == "Write docs"
    assert task.description == "Explain architecture"
    assert task.status == TaskStatus.PENDING


def test_create_task_with_empty_title_fails() -> None:
    with pytest.raises(InvalidTaskTitleError):
        Task.create(title="   ")


def test_complete_task_twice_fails() -> None:
    task = Task.create(title="Ship MVP")
    task.complete()
    with pytest.raises(TaskAlreadyCompletedError):
        task.complete()
