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
  conftest.py            # 测试共享夹具与公共初始化
  test_api.py            # HTTP 接口集成测试
  test_domain.py         # 领域模型单元测试
  test_quality.py        # 质量约定与结构性守护测试
.github/
  ISSUE_TEMPLATE/        # Issue 模板
  pull_request_template.md
  workflows/ci.yml       # 持续集成检查
```

## API 概览

- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks/{task_id}/assignments`
- `POST /api/v1/tasks/{task_id}/completion`
- `GET /health`

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

```bash
python -m pytest
python -m pytest --cov=task_management --cov-report=term-missing
ruff check .
```

## 测试策略

本项目把测试分为三层：

### 1. 领域层单元测试

关注纯业务规则，不依赖 HTTP 或数据库细节。

示例：
- 空标题不可创建任务
- 已完成任务不可重复完成
- 创建任务时默认状态正确

### 2. HTTP 接口集成测试

关注接口契约、状态码和关键返回字段。

示例：
- `GET /health` 返回健康状态
- 任务生命周期接口能串通创建、查询、指派、完成流程
- 非法或不存在资源应返回明确错误

### 3. 质量守护测试

关注项目协作与架构约定，避免“项目还能跑，但约定已经悄悄坏掉”。

示例：
- README 中必须说明测试与质量检查命令
- `.github/workflows/ci.yml` 必须存在
- PR / Issue 模板必须存在

## 质量约定

为避免示例项目在迭代中失去教学价值，建议持续遵守以下约定：

- **文档与注释使用中文**，便于团队内部沉淀与评审
- **类名、函数名、模块名保持英文**，与 Python 生态一致
- 新增功能时，至少补充对应层级测试之一
- 修复缺陷时，优先补一个可复现该问题的测试
- PR 应说明改动边界、测试方式、潜在影响
- 不把复杂业务逻辑直接塞进 FastAPI 路由

## 持续集成（CI）

CI 默认执行以下步骤：

1. 安装项目与开发依赖
2. 运行 `ruff check .`
3. 运行 `pytest`
4. 运行带覆盖率的测试命令

如果你准备扩展该仓库，建议把以下检查逐步纳入：

- 最低覆盖率门槛
- 格式化检查
- 类型检查
- 多 Python 版本矩阵

## 协作流程建议

- 提交前先运行：

```bash
ruff check .
python -m pytest
```

- 发起 PR 时重点说明：
  - 改了哪一层
  - 为什么这样改
  - 如何验证
  - 是否影响现有 API 或领域规则

## 为什么这算六边形架构

- **Domain**：放业务模型与业务规则
- **Application**：组织用例与流程编排
- **Infrastructure**：实现端口，例如 SQLAlchemy 仓储
- **Interfaces**：通过 FastAPI 对外暴露能力

核心思想是：

> 业务规则应尽量独立于 Web 框架、数据库与外部交互细节。

这样测试会更清晰，替换适配器也更容易。
