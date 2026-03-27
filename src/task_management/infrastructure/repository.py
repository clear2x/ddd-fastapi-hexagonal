from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from task_management.application.read_models import TaskReadModel
from task_management.domain.errors import TaskReadModelNotProjectedError
from task_management.domain.models import AssigneeId, Task, TaskDescription, TaskId, TaskStatus, TaskTitle
from task_management.domain.ports import TaskQueryService, TaskReadModelStore, TaskRepository


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


class TaskReadModelModel(Base):
    __tablename__ = "task_read_models"

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


class SqlAlchemyTaskReadModelStore(TaskReadModelStore):
    """把领域事件投影到独立读模型表。

    这是教学版 CQRS：同步、单进程、直接写读模型表。
    如果写模型已成功推进，但这里找不到对应读模型，就视为可探测坏状态，
    必须显式失败，而不是静默吞掉；但它仍不是生产级 outbox / 重试 / 事务一致性方案。
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_task(
        self,
        *,
        task_id: str,
        title: str,
        description: str | None,
        occurred_at: datetime,
    ) -> None:
        self.session.merge(
            TaskReadModelModel(
                id=task_id,
                title=title,
                description=description,
                assignee_id=None,
                status=TaskStatus.PENDING.value,
                created_at=occurred_at,
                updated_at=occurred_at,
                completed_at=None,
            )
        )
        self.session.commit()

    def assign_task(self, *, task_id: str, assignee_id: str, occurred_at: datetime) -> None:
        model = self._get_required_model(task_id)
        model.assignee_id = assignee_id
        model.status = TaskStatus.ASSIGNED.value
        model.updated_at = occurred_at
        self.session.commit()

    def complete_task(
        self,
        *,
        task_id: str,
        completed_at: datetime,
        occurred_at: datetime,
    ) -> None:
        model = self._get_required_model(task_id)
        model.status = TaskStatus.COMPLETED.value
        model.completed_at = completed_at
        model.updated_at = occurred_at
        self.session.commit()

    def _get_required_model(self, task_id: str) -> TaskReadModelModel:
        model = self.session.get(TaskReadModelModel, task_id)
        if model is None:
            raise TaskReadModelNotProjectedError(
                f"读模型缺失：task_id={task_id}。写模型可能已存在，但查询侧投影未完成或已损坏。"
            )
        return model


class SqlAlchemyTaskQueryService(TaskQueryService):
    """从查询表读取任务列表，体现命令侧与查询侧分离。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, task_id: str) -> Optional[TaskReadModel]:
        model = self.session.get(TaskReadModelModel, task_id)
        if model is None:
            return None
        return self._to_read_model(model)

    def list(self, *, status: str | None = None, assignee_id: str | None = None) -> Iterable[TaskReadModel]:
        stmt = select(TaskReadModelModel)
        if status:
            stmt = stmt.where(TaskReadModelModel.status == status)
        if assignee_id:
            stmt = stmt.where(TaskReadModelModel.assignee_id == assignee_id)
        stmt = stmt.order_by(TaskReadModelModel.created_at.desc())
        return [self._to_read_model(row) for row in self.session.scalars(stmt).all()]

    @staticmethod
    def _to_read_model(model: TaskReadModelModel) -> TaskReadModel:
        return TaskReadModel(
            id=model.id,
            title=model.title,
            description=model.description,
            assignee_id=model.assignee_id,
            status=TaskStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
        )


def create_session_factory(database_url: str):
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
