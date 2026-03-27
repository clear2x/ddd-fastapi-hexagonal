# ddd-fastapi-hexagonal

一个用于演示 **DDD（领域驱动设计）+ Hexagonal Architecture（六边形架构）+ FastAPI** 的最小可运行示例项目。

项目刻意保持精简，目标不是堆功能，而是让目录分层、依赖方向、测试边界与协作约定都足够清晰，适合作为学习、脚手架参考或团队内部 PoC 起点。

## 项目目标

这个示例重点展示：

- 如何把 **domain / application / infrastructure / interfaces** 分层拆开
- 如何让 FastAPI 只承担输入适配职责，而不是吞掉全部业务逻辑
- 如何通过测试验证领域规则与 HTTP 接口行为
- 如何在小项目里就建立基础质量约定、PR 模板与 CI 检查
- 如何通过清晰边界让 application / domain / interfaces 的职责分工更贴近 DDD

## 示例业务域

当前示例使用一个简单的 **任务管理（Task Management）** 领域，包含以下操作：

- 创建任务
- 获取单个任务
- 列出任务
- 指派任务
- 完成任务

## 目录结构

```text
src/task_management/
  domain/                # 领域模型、领域规则、端口定义
  application/           # 用例编排、输入输出 DTO
  infrastructure/        # 数据库与仓储实现等基础设施
  interfaces/http/       # FastAPI 路由与请求/响应模型
tests/
  test_api.py            # HTTP 接口集成测试
  test_application.py    # 应用层用例测试
  test_domain.py         # 领域模型单元测试
```

## API 概览

- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks/{task_id}/assignments`
- `POST /api/v1/tasks/{task_id}/completion`
- `GET /health`

更完整的接口边界说明见：[`docs/api.md`](docs/api.md)

### 为什么这个 API 不是普通 CRUD

这个仓库虽然只暴露了几个很小的任务接口，但设计重点不是“把表做成 REST”。

它刻意演示下面几层翻译边界：

- **HTTP 请求模型**：只负责对外契约、字段校验、空值归一化
- **应用层命令 / 查询**：表达用例，而不是绑定某个 Web 框架
- **领域模型**：维护标题、描述、指派、完成等业务规则
- **HTTP 响应模型**：把内部结果投影成稳定的外部 JSON 结构

从 DDD 视角看，`interfaces/http` 可以理解成一个面向调用方的轻量 **ACL（Anti-Corruption Layer，防腐层）**：

- 它吸收 HTTP / JSON / 校验错误这些外部协议细节
- 它不让 FastAPI 或 Pydantic 的模型直接污染领域层
- 它也不让领域对象直接裸露为外部契约

因此读这个项目时，建议重点看“边界如何翻译”，而不是只看接口路径。

### HTTP 返回契约

成功响应统一为：

```json
{
  "data": {}
}
```

错误响应统一为：

```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "请求参数校验失败",
    "details": []
  }
}
```

常见状态码语义：

- `422`：请求体缺字段、类型不匹配、字符串全空白等输入校验失败。表示外部契约尚未成立，请求还没有以合法命令进入应用层
- `404`：任务不存在。表示资源定位失败，而不是格式错误
- `409`：任务已完成，不能重复完成。表示请求合法，但资源当前状态与动作冲突
- `400`：进入领域层后触发业务规则错误。表示“格式合法”不等于“业务合法”

### description 空值归一化策略

`POST /api/v1/tasks` 的 `description` 字段采用以下策略：

- 未传：保存为 `null`
- 显式传 `null`：保存为 `null`
- 传入仅包含空白字符的字符串：会先 `trim`，然后归一化为 `null`
- 传入非空字符串：会 `trim` 后保存

这样做的目的是把“没有描述”和“空白描述”收敛成同一种语义，避免把无意义空字符串写入领域对象或持久化层。

这正是接口边界层的职责之一：

- 对外部输入保持适度宽容
- 对内部领域保持语义严格
- 在边界完成一次明确的模型翻译

## 本地开发

### 1. 创建虚拟环境

```bash
python -m venv .venv
. .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -e .[dev]
```

### 3. 启动服务

```bash
uvicorn task_management.main:app --reload
```

### 4. 运行测试与质量检查

先跑通最小检查：

```bash
make check
```

完整本地质量检查：

```bash
make ci
```

如果你更习惯直接调用命令，对应关系如下：

```bash
python -m pytest
ruff check .
python -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80
```

## CI 的质量守护意图

当前仓库在 CI 中只守两道最核心的门：

- `ruff check .`
- `python -m pytest --cov=task_management --cov-report=term-missing --cov-fail-under=80`

这样做的目的不是把教学型仓库变成规则怪兽，而是保证下面这几件事始终成立：

- 文档里写的命令是真实存在的
- Makefile 里的入口与 CI 实际执行口径一致
- 测试不仅能跑，还能覆盖核心主路径
- 质量守护规则不会在文档、脚本、workflow 之间悄悄漂移

## 测试策略

本项目把测试分为三层：

### 1. 领域层单元测试

关注纯业务规则，不依赖 HTTP 或数据库细节。

示例：
- 空标题不可创建任务
- 空白描述不能直接进入领域对象
- 空白指派人不可指派
- 已完成任务不可重复完成

### 2. HTTP 接口集成测试

关注接口契约、状态码和关键返回字段。

示例：
- `GET /health` 返回统一成功结构
- 任务生命周期接口能串通创建、查询、指派、完成流程
- create / assign 的缺字段与全空白输入会返回 `422`
- description 空白值会被归一化为 `null`

## 质量约定

为避免示例项目在迭代中失去教学价值，建议持续遵守以下约定：

- **文档与注释使用中文**，便于团队内部沉淀与评审
- **类名、函数名、模块名保持英文**，与 Python 生态一致
- 新增功能时，至少补充对应层级测试之一
- 修复缺陷时，优先补一个可复现该问题的测试
- 不把复杂业务逻辑直接塞进 FastAPI 路由

## 为什么这算六边形架构

- **Domain**：放业务模型与业务规则
- **Application**：组织用例与流程编排
- **Infrastructure**：实现端口，例如 SQLAlchemy 仓储
- **Interfaces**：通过 FastAPI 对外暴露能力

核心思想是：

> 业务规则应尽量独立于 Web 框架、数据库与外部交互细节。

这样测试会更清晰，替换适配器也更容易。

## 这次补充了哪些更“DDD”的东西

为了保持教学仓库的小而清晰，这次没有大改 HTTP 层，而是在 domain / application 深化了三件事：

- **领域事件**：`Task` 聚合会记录 `task.created`、`task.assigned`、`task.completed`
- **领域服务**：`TaskDomainService` 承担“已完成任务不能再次指派”的状态策略判断
- **查询读模型**：新增 `task_read_models` 查询表，`GET /tasks` 与 `GET /tasks/{id}` 从读模型读取

这样可以直观看到一个更贴近 DDD/CQRS 入门版的流转：

1. HTTP 层把请求翻译成命令
2. 应用层驱动聚合执行业务动作
3. 聚合产生领域事件
4. 事件总线把事件同步投影到查询侧读模型
5. 查询接口从读模型返回结果

这里要刻意说明它的教学边界：

- **同步**：命令执行时会立刻发布事件并更新读模型，没有异步队列
- **单进程**：事件总线与投影器都在同一进程内，不涉及跨服务投递
- **非事务 outbox**：没有 outbox、消息重试、幂等消费、最终一致性补偿等生产机制

因此，这一块应理解为**教学版 CQRS**：它的目标是把“命令侧写聚合、查询侧读投影”讲清楚，而不是直接充当生产级消息架构模板。

之所以让 `GET /tasks` 与 `GET /tasks/{id}` 改为读取 `task_read_models`，不是为了炫技，而是为了把查询路径明确切到**读模型**：

- 查询接口读取的是面向展示/筛选的投影结果，而不是命令侧聚合本身
- 这样读者能直接看到“写模型负责业务动作，读模型负责查询返回”的职责切分
- 代价也同样明确：如果事件投影缺失或损坏，查询侧可能暂时看不到写侧已发生的变更

换句话说，这里的重点不是“查询更快”，而是**把边界讲清楚**：查询为何不再直接查写库，以及这会带来怎样的可见性与一致性限制。

> 注意：这里是**教学版 CQRS**，实现方式是**同步、单进程、直接投影到单表读模型**。
> 它明确**不是**生产级消息系统方案：没有事务 outbox、没有异步重试、没有跨进程投递保证。
> 同时，为了避免坏状态被悄悄吞掉，若写模型已推进但读模型缺失，投影层会显式失败。

## 为什么这里还强调 bounded context 与 ACL

很多示例项目虽然叫 DDD，但只展示了“分层”，没有把“上下文边界”讲清楚。

这个仓库现在额外明确了两件事：

1. `task_management` 是一个**任务管理限界上下文**
2. 当外部系统想把“任务”同步进来时，需要先经过 **ACL（防腐层）** 翻译，再进入本上下文语义

这能帮助读者区分两种常见但不同的适配：

- **HTTP 适配**：解决“请求怎么进来”
- **ACL 适配**：解决“外部语义如何翻译后再进来”

进一步说明见：

- `docs/architecture.md`
- `docs/project-structure.md`
- `docs/bounded-context-and-acl.md`
