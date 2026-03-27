"""任务管理限界上下文的防腐层（ACL）端口定义。

这个文件故意保持轻量，目的是把 DDD 教学中的 ACL 概念正式落进仓库：
- 当任务管理上下文需要接入外部系统时，不应把对方模型直接带入领域层
- 应先经过 ACL 做翻译、裁剪、语义对齐
- 这里定义的是“任务管理上下文眼中的外部能力”，而不是外部系统原始 SDK 接口

当前仓库尚未接入真实外部系统，因此这里只放教学型占位接口与数据结构。
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExternalTaskSnapshot:
    """外部任务快照。

    这是 ACL 接收到的“外部世界表达”，仍处于边界地带，
    尚未进入本上下文的领域模型。
    """

    external_id: str
    title: str
    description: str | None
    assignee_reference: str | None
    state: str


@dataclass(frozen=True)
class ImportedTaskDraft:
    """转换后的任务草稿。

    这是 ACL 输出给应用层的“本上下文可理解语义”，
    但仍刻意不直接暴露领域实体，避免把转换职责塞进 domain。
    """

    title: str
    description: str | None
    assignee_id: str | None
    source_system: str
    source_identifier: str


class ExternalTaskTranslator(Protocol):
    """外部任务翻译器。

    责任：把外部上下文中的任务表达翻译为任务管理上下文能接受的草稿对象。
    """

    def translate(self, snapshot: ExternalTaskSnapshot) -> ImportedTaskDraft: ...
