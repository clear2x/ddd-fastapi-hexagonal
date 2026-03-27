# 限界上下文与防腐层说明

## 为什么这个仓库现在要显式引入这些概念

这个仓库原本已经具备 DDD + 六边形架构的基本分层，但如果只停留在
`domain / application / infrastructure / interfaces` 四层，读者很容易把它理解成
“分层项目模板”，而不是“有上下文边界意识的 DDD 教学样板”。

因此，这次调整额外把两个概念正式落进仓库：

- **限界上下文（Bounded Context）**
- **防腐层（Anti-Corruption Layer, ACL）**

目标不是把项目做复杂，而是让“边界”在目录、命名和文档里都可见。

---

## 当前限界上下文

当前示例只有一个核心业务上下文：

- `task_management`：任务管理限界上下文

这意味着：

- 任务实体、值对象、领域错误和仓储端口，都属于 `task_management` 自己的语言模型
- 外部系统即使也有“任务”概念，也不能默认与这里的 `Task` 等价
- 当未来出现“用户中心”“通知中心”“项目协作”等上下文时，应优先通过边界协作，而不是互相直接引用领域模型

---

## 为什么要有 ACL

当一个上下文与外部系统或其他上下文交互时，最常见的问题不是“连不上”，而是：

- 名称一样，语义不同
- 字段看似相似，约束不同
- 对方状态机、生命周期、标识规则与本上下文不一致

如果直接把外部 DTO、SDK model、HTTP payload 带进领域层，核心模型就会逐渐被外部语义污染。

ACL 的作用就是：

> 在边界上做翻译，而不是在领域里做妥协。

---

## 本仓库中的 ACL 落点

### 1. 应用层定义边界语义

`src/task_management/application/acl.py`

这里定义：

- `ExternalTaskSnapshot`：外部世界送进来的任务快照
- `ImportedTaskDraft`：翻译后、可被本上下文理解的任务草稿
- `ExternalTaskTranslator`：翻译器协议

为什么放在 application：

- ACL 的目标是服务“跨边界用例”
- 它不是纯领域不变量本身
- 也不应该直接依赖某个具体基础设施 SDK

### 2. interfaces/acl 放具体适配器

`src/task_management/interfaces/acl/task_import_acl.py`

这里放的是一个教学型的最小实现 `SimpleExternalTaskTranslator`，用来演示：

- 外部字段如何被改名
- 外部状态如何被阻断，不直接进入领域层
- 来源系统元信息如何在边界处补齐

这类模块未来可以演进为：

- 第三方任务系统 webhook 适配器
- 其他 bounded context 的事件翻译器
- 外部协作平台导入器

---

## 目录结构中的边界表达

现在的目录可以这样理解：

```text
src/task_management/
  domain/                  # 任务管理上下文的核心领域
  application/             # 本上下文的用例与边界编排
    acl.py                 # 本上下文视角下的 ACL 协议与跨边界语义
    assemblers.py          # 本上下文内部依赖组装
  infrastructure/          # 仓储实现、配置、数据库等基础设施
  interfaces/
    http/                  # 入站 HTTP 适配器
    acl/                   # 边界翻译适配器（防腐层具体实现）
```

请注意一个教学重点：

- `interfaces/http` 解决“请求怎么进来”
- `interfaces/acl` 解决“外部语义怎么翻译后再进来”

两者都属于适配器，但关注点不同。

---

## 依赖原则

为了避免边界倒塌，建议遵守以下原则：

1. **domain 不认识外部系统模型**
2. **application 定义跨边界用例需要的语义接口**
3. **interfaces/acl 或 infrastructure 中的实现去适配外部表达**
4. **不要把第三方字段名、状态值、错误码直接扩散到核心领域对象中**

---

## 这次改动为什么没有引入完整外部集成

这是一个教学型仓库，因此本次只把 ACL 的“结构落点”和“协作意图”立起来，刻意不引入：

- 额外第三方依赖
- 新数据库表
- 真实外部 API client
- 大规模业务改写

这样可以把注意力集中在：

- 结构边界是否清晰
- 概念落点是否明确
- 未来扩展位是否预留正确

---

## 后续可演进方向

如果未来继续把这个仓库做成更完整的教学样板，可以考虑增加：

1. “外部工单系统导入任务”的完整 use case
2. 多个 bounded context 之间通过事件协作的示例
3. source system / external mapping 的持久化模型
4. ACL 转换失败时的错误建模与补偿策略

当前版本的重点不是功能多少，而是：

**让读者一眼看出：这里不仅有分层，还有上下文边界意识。**
