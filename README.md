# ddd-fastapi-hexagonal

一个用于演示 **DDD（领域驱动设计）+ Hexagonal Architecture（六边形架构）+ FastAPI** 的最小可运行示例项目。

项目刻意保持精简，目标不是堆功能，而是让目录分层、依赖方向、测试边界与协作约定都足够清晰，适合作为学习、脚手架参考或团队内部 PoC 起点。

## 项目目标

这个示例重点展示：

- 如何把 **domain / application / infrastructure / interfaces** 分层拆开
- 如何让 FastAPI 只承担输入适配职责，而不是吞掉全部业务逻辑
- 如何通过测试验证领域规则与 HTTP 接口行为
- 如何在小项目里就建立基础质量约定、PR 模板与 CI 检查

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

- `422`：请求体缺字段、类型不匹配、字符串全空白等输入校验失败
- `404`：任务不存在
- `409`：任务已完成，不能重复完成
- `400`：进入领域层后触发业务规则错误

### description 空值归一化策略

`POST /api/v1/tasks` 的 `description` 字段采用以下策略：

- 未传：保存为 `null`
- 显式传 `null`：保存为 `null`
- 传入仅包含空白字符的字符串：会先 `trim`，然后归一化为 `null`
- 传入非空字符串：会 `trim` 后保存

这样做的目的是把“没有描述”和“空白描述”收敛成同一种语义，避免把无意义空字符串写入领域对象或持久化层。

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
