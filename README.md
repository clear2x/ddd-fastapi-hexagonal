# ddd-fastapi-hexagonal

一个用于演示 **DDD（领域驱动设计）+ 六边形架构（Hexagonal Architecture）+ FastAPI** 的最小可运行示例项目。

这个仓库的目标不是堆叠业务功能，而是把一个适合开源阅读与团队接手的 Python Web 项目骨架讲清楚：

- 目录为什么这样分层
- 依赖应该朝哪个方向流动
- HTTP 层与业务核心如何解耦
- 新同学第一次 clone 后应该如何启动、测试、扩展

如果你正在找一个“能跑、能看懂、能继续演化”的 DDD + FastAPI 示例，这个仓库就是为这个目的准备的。

## 仓库特点

- **可直接运行**：默认使用 SQLite，本地零额外依赖即可启动
- **分层克制**：聚焦 `domain / application / infrastructure / interfaces` 的边界表达
- **测试齐全**：覆盖领域规则、应用用例、HTTP 接口与质量约束
- **适合作为脚手架参考**：可以作为教学示例、PoC 起点或团队内部模板
- **中文文档优先**：降低团队阅读与评审门槛

## 示例业务域

当前示例使用一个简单的 **任务管理（Task Management）** 领域，包含以下能力：

- 创建任务
- 获取单个任务
- 列出任务
- 指派任务
- 完成任务

## 技术栈

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Pytest
- Ruff
- Uvicorn

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/clear2x/ddd-fastapi-hexagonal.git
cd ddd-fastapi-hexagonal
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
. .venv/bin/activate
```

Windows PowerShell 可使用：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
make install
```

如果本机没有 `make`，也可以直接执行：

```bash
python -m pip install -e .[dev]
```

### 4. 准备环境变量

```bash
cp .env.example .env
```

默认配置即可运行；如需自定义，可编辑 `.env`：

```env
APP_ENV=dev
DATABASE_URL=sqlite:///./tasks.db
```

### 5. 启动服务

```bash
make run
```

启动后访问：

- 应用健康检查：<http://127.0.0.1:8000/health>
- Swagger 文档：<http://127.0.0.1:8000/docs>
- ReDoc 文档：<http://127.0.0.1:8000/redoc>

## 常用命令

```bash
make install      # 安装开发依赖
make run          # 启动本地开发服务
make test         # 运行测试
make test-cov     # 运行测试并输出覆盖率
make lint         # 运行 Ruff 静态检查
make check        # 一次执行 lint + test
make clean        # 清理缓存、测试产物与本地数据库
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

## 目录结构

```text
.
├── .env.example               # 环境变量示例
├── Makefile                   # 常用开发命令入口
├── README.md                  # 项目总览与快速开始
├── CONTRIBUTING.md            # 协作约定
├── docs/
│   ├── architecture.md        # 架构与分层说明
│   ├── development.md         # 本地开发与运行环境说明
│   ├── project-structure.md   # 仓库目录职责说明
│   └── testing.md             # 测试策略说明
├── src/task_management/
│   ├── application/           # 用例编排、输入输出 DTO
│   ├── domain/                # 领域模型、领域规则、端口定义
│   ├── infrastructure/        # 仓储实现、配置与运行时支撑
│   ├── interfaces/http/       # FastAPI 路由与请求响应模型
│   └── main.py                # 应用启动入口
└── tests/                     # 测试集合
```

更详细的说明可继续阅读：

- [docs/development.md](docs/development.md)
- [docs/project-structure.md](docs/project-structure.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/testing.md](docs/testing.md)

## 本地开发建议流程

### 方式一：最小启动路径

适合第一次体验仓库：

```bash
make install
make run
```

### 方式二：开发前完整自检

适合提交代码前执行：

```bash
make lint
make test
make test-cov
```

或直接：

```bash
make check
```

## 测试策略

本项目把测试分为三层：

### 1. 领域层单元测试

关注纯业务规则，不依赖 HTTP 或数据库细节。

示例：

- 空标题不可创建任务
- 空白描述不能直接进入领域对象
- 空白指派人不可指派
- 已完成任务不可重复完成

### 2. 应用层用例测试

关注用例编排是否正确调用仓储、是否返回预期视图对象。

### 3. HTTP 接口集成测试

关注接口契约、状态码和关键返回字段。

示例：

- `GET /health` 返回统一成功结构
- 任务生命周期接口能串通创建、查询、指派、完成流程
- create / assign 的缺字段与全空白输入会返回 `422`
- description 空白值会被归一化为 `null`

## 适合从哪里开始阅读

如果你是第一次接触这个仓库，建议按下面顺序阅读：

1. `README.md`：先建立整体认知
2. `docs/project-structure.md`：理解目录职责
3. `docs/architecture.md`：理解分层边界与依赖方向
4. `src/task_management/domain/`：先看领域对象和规则
5. `src/task_management/application/`：再看用例组织方式
6. `src/task_management/interfaces/http/`：最后看 FastAPI 如何作为适配层接入

## 常见问题

### 1. 为什么默认用 SQLite？

因为这个仓库首先是教学与示例项目。默认使用 SQLite 能让读者在没有外部数据库服务的情况下直接运行，降低上手成本。

### 2. 这是生产级模板吗？

不是完整生产模板，但它适合作为生产项目的“起步骨架”参考。你仍然需要根据真实场景补充认证、配置管理、日志、迁移、可观测性、部署流程等能力。

### 3. 为什么没有把复杂逻辑写进 FastAPI 路由？

因为这个仓库想强调：HTTP 层应该只做入站适配与协议转换，业务规则应尽量留在领域层或应用层中，避免框架绑死核心逻辑。

### 4. 为什么文档和注释统一用中文？

这是仓库当前的协作约定，目标是让中文团队更容易评审、交接与沉淀知识；同时代码命名仍保持英文，以对齐 Python 生态习惯。

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
