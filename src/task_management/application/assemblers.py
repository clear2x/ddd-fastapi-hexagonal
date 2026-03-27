"""应用层组装模块。

这个模块显式表达“限界上下文内部如何完成依赖组装”。
教学目的上，它让 interfaces 层不必直接了解基础设施实现细节，
从而更容易看清入站适配器、应用层与基础设施之间的责任边界。

额外约束：
- 命令侧 use case 使用独立短生命周期 session
- 查询侧 use case 只经由 TaskQueryService 读取读模型，不直接查写库
- projector 使用自己的 session，把“事件投影”和“HTTP 请求中的命令处理”边界分开

这里仍是教学型、同步内存内事件总线示例；不扩展成完整 Unit of Work。
"""

from task_management.application.event_handlers import TaskReadModelProjector
from task_management.application.use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
)
from task_management.infrastructure.config import settings
from task_management.infrastructure.event_bus import InMemoryDomainEventBus
from task_management.infrastructure.repository import (
    SqlAlchemyTaskQueryService,
    SqlAlchemyTaskReadModelStore,
    SqlAlchemyTaskRepository,
    create_session_factory,
)

session_factory = create_session_factory(settings.database_url)


def _repository() -> SqlAlchemyTaskRepository:
    """创建命令侧任务仓储实现。

    每次组装都新建一个 session，避免把跨请求复用 session
    误解成推荐范式；当前示例仅表达“短生命周期依赖由 assembler 负责拼装”。
    """

    session = session_factory()
    return SqlAlchemyTaskRepository(session)


def _query_service() -> SqlAlchemyTaskQueryService:
    """创建查询侧任务服务实现。

    查询主路径固定走独立 TaskQueryService + 读模型表，
    不允许为了省事退回到 TaskRepository。
    """

    session = session_factory()
    return SqlAlchemyTaskQueryService(session)


def _event_bus() -> InMemoryDomainEventBus:
    """创建同步领域事件总线，并注册读模型投影器。

    projector 持有独立 session，目的是把“写模型持久化”和“读模型投影”
    明确成两个基础设施协作点；即使当前仍是同步调用，也不把同一个 session
    透传到所有对象里，免得示范成隐式共享生命周期。
    """

    session = session_factory()
    projector = TaskReadModelProjector(SqlAlchemyTaskReadModelStore(session))
    return InMemoryDomainEventBus(handlers=[projector.handle])


def create_task_use_case() -> CreateTaskUseCase:
    return CreateTaskUseCase(_repository(), _event_bus())


def get_task_use_case() -> GetTaskUseCase:
    return GetTaskUseCase(_query_service())


def list_tasks_use_case() -> ListTasksUseCase:
    return ListTasksUseCase(_query_service())


def assign_task_use_case() -> AssignTaskUseCase:
    return AssignTaskUseCase(_repository(), event_bus=_event_bus())


def complete_task_use_case() -> CompleteTaskUseCase:
    return CompleteTaskUseCase(_repository(), _event_bus())
