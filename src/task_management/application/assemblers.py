"""应用层组装模块。

这个模块显式表达“限界上下文内部如何完成依赖组装”。
教学目的上，它让 interfaces 层不必直接了解基础设施实现细节，
从而更容易看清入站适配器、应用层与基础设施之间的责任边界。

当前主干先只建立 ACL / bounded context / 组装边界基线：
- 命令侧与查询侧都仍复用当前仓储实现
- 不在这一块提前引入尚未进入主干的读模型投影/event bus/UoW 细节
- 后续若继续引入 CQRS 读模型链路，再在下一块增量提交里推进
"""

from task_management.application.use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
)
from task_management.infrastructure.config import settings
from task_management.infrastructure.repository import SqlAlchemyTaskRepository, create_session_factory

session_factory = create_session_factory(settings.database_url)


def _repository() -> SqlAlchemyTaskRepository:
    """创建任务仓储实现。

    当前示例仍使用 SQLAlchemy 仓储。
    之所以把它集中在这里，是为了把“依赖组装”从 HTTP 适配器中抽离出来。
    """

    session = session_factory()
    return SqlAlchemyTaskRepository(session)


def create_task_use_case() -> CreateTaskUseCase:
    return CreateTaskUseCase(_repository())


def get_task_use_case() -> GetTaskUseCase:
    return GetTaskUseCase(_repository())


def list_tasks_use_case() -> ListTasksUseCase:
    return ListTasksUseCase(_repository())


def assign_task_use_case() -> AssignTaskUseCase:
    return AssignTaskUseCase(_repository())


def complete_task_use_case() -> CompleteTaskUseCase:
    return CompleteTaskUseCase(_repository())
