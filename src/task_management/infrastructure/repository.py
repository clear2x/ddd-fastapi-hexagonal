from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from task_management.domain.models import AssigneeId, Task, TaskDescription, TaskId, TaskStatus, TaskTitle
from task_management.domain.ports import TaskRepository


class Base(DeclarativeBase):
    pass


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, task: Task) -> None:
        self.session.add(self._to_model(task))
        self.session.commit()

    def get(self, task_id: str) -> Optional[Task]:
        model = self.session.get(TaskModel, task_id)
        if model is None:
            return None
        return self._to_domain(model)

    def list(self, status: str | None = None, assignee_id: str | None = None) -> Iterable[Task]:
        stmt = select(TaskModel)
        if status:
            stmt = stmt.where(TaskModel.status == status)
        if assignee_id:
            stmt = stmt.where(TaskModel.assignee_id == assignee_id)
        stmt = stmt.order_by(TaskModel.created_at.desc())
        return [self._to_domain(row) for row in self.session.scalars(stmt).all()]

    def save(self, task: Task) -> None:
        model = self.session.get(TaskModel, task.id.value)
        if model is None:
            self.session.add(self._to_model(task))
        else:
            model.title = task.title.value
            model.description = task.description.value if task.description is not None else None
            model.assignee_id = task.assignee_id.value if task.assignee_id is not None else None
            model.status = task.status.value
            model.created_at = task.created_at
            model.updated_at = task.updated_at
            model.completed_at = task.completed_at
        self.session.commit()

    @staticmethod
    def _to_domain(model: TaskModel) -> Task:
        return Task(
            id=TaskId(model.id),
            title=TaskTitle(model.title),
            description=TaskDescription(model.description) if model.description is not None else None,
            assignee_id=AssigneeId(model.assignee_id) if model.assignee_id is not None else None,
            status=TaskStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
        )

    @staticmethod
    def _to_model(task: Task) -> TaskModel:
        return TaskModel(
            id=task.id.value,
            title=task.title.value,
            description=task.description.value if task.description is not None else None,
            assignee_id=task.assignee_id.value if task.assignee_id is not None else None,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )


def create_session_factory(database_url: str):
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
