"""任务导入场景的 ACL 适配器示例。

注意：
- 这是教学型占位实现，不在当前 HTTP 主路径中启用
- 目标是把“ACL 放在哪里、负责什么”用代码结构固定下来
- 真正接第三方系统时，可在这里承接 SDK / HTTP client / webhook payload 等外部模型
"""

from task_management.application.acl import ExternalTaskSnapshot, ExternalTaskTranslator, ImportedTaskDraft


class SimpleExternalTaskTranslator(ExternalTaskTranslator):
    """最小可运行的防腐层翻译器。

    规则保持简单：
    - 外部 state 不直接穿透到领域层
    - assignee_reference 在 ACL 中改名为 assignee_id
    - 补充来源系统元信息，方便未来审计与追踪
    """

    def __init__(self, source_system: str) -> None:
        self.source_system = source_system

    def translate(self, snapshot: ExternalTaskSnapshot) -> ImportedTaskDraft:
        return ImportedTaskDraft(
            title=snapshot.title.strip(),
            description=snapshot.description.strip() if snapshot.description else None,
            assignee_id=snapshot.assignee_reference,
            source_system=self.source_system,
            source_identifier=snapshot.external_id,
        )
