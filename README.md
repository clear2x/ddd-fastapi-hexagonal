# ddd-fastapi-hexagonal

一个使用 Python + FastAPI 构建的 **DDD（领域驱动设计）+ 六边形架构（Hexagonal Architecture）** 开源示例项目。

仓库地址：<https://github.com/clear2x/ddd-fastapi-hexagonal>

## 这个项目演示什么

- 领域驱动设计（DDD）
- 六边形架构（端口与适配器）
- 使用 FastAPI 作为入站 HTTP 适配器
- 使用 SQLAlchemy 作为出站持久化适配器
- 清晰拆分 domain、application、infrastructure、interfaces

## 示例领域

本示例项目使用一个简单的**任务管理（Task Management）**领域，当前包含 5 个核心操作：
- 创建任务
- 获取任务详情
- 查询任务列表
- 指派任务
- 完成任务

## 项目结构

```text
src/task_management/
  domain/
  application/
  infrastructure/
  interfaces/http/
tests/
docs/
```

## API

- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks/{task_id}/assignments`
- `POST /api/v1/tasks/{task_id}/completion`
- `GET /health`

## 本地开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn task_management.main:app --reload
pytest
```

## CI

项目已提供 GitHub Actions CI 骨架，用于在 push 和 pull request 时执行测试。

## 并行开发策略

当前建议的并行工作分支：
- `feat/domain-core`
- `feat/http-api`
- `feat/tests-docs-ci`

相关文档：
- `docs/architecture.md`
- `docs/testing.md`
- `CONTRIBUTING.md`

## 当前状态

仓库已经包含：
- 第一版 MVP 代码骨架
- 初始测试文件
- 基础文档
- CI 骨架
- 协作规范

下一步会继续补强：
- 更清晰的领域边界
- 更稳定的 HTTP 错误模型
- 更完整的测试与文档

## 为什么它算六边形架构

- **Domain**：承载业务模型与业务规则
- **Application**：编排用例
- **Infrastructure**：实现端口，例如 SQLAlchemy 仓储
- **Interfaces**：通过 FastAPI 对外暴露能力

这个项目会刻意保持“小而清楚”，重点不是堆很多功能，而是把架构边界讲明白。
