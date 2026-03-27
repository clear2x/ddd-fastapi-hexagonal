# 项目结构说明

## 仓库定位

这是一个用于教学与脚手架参考的 DDD + 六边形架构示例仓库。

它不追求功能丰富，而追求下面三件事足够清楚：

- 业务核心放在哪里
- 边界协作放在哪里
- 外部依赖如何在不污染核心的前提下接入

---

## 顶层结构

```text
.
├── docs/                         # 架构、测试与项目结构文档
├── src/task_management/          # 任务管理限界上下文
├── tests/                        # 不同层次的测试
├── README.md                     # 项目入口说明
└── PROJECT_PLAN.md               # 项目规划与演进记录
```

---

## src/task_management 结构

```text
src/task_management/
├── domain/                       # 领域模型、值对象、领域错误、仓储端口
├── application/                  # 用例、DTO、跨边界协议、依赖组装
│   ├── dto.py
│   ├── use_cases.py
│   ├── acl.py                    # ACL 语义定义：外部快照、草稿、翻译协议
│   └── assemblers.py             # 用例组装入口，隔离 interfaces 与 infrastructure
├── infrastructure/               # 配置、数据库、仓储实现
└── interfaces/
    ├── http/                     # FastAPI 入站适配器
    └── acl/                      # 防腐层适配器示例
```

---

## 如何理解这些目录

### domain

这里是任务管理上下文最稳定、最核心的部分。

应放：

- 实体 / 值对象
- 领域规则
- 领域错误
- 端口抽象

不应放：

- FastAPI 请求模型
- SQLAlchemy ORM 细节
- 第三方平台字段定义

### application

这里负责把用户意图或系统指令编排成用例执行流程。

应放：

- 命令 / 查询 DTO
- use case
- 跨边界协作需要的 ACL 协议
- 依赖组装入口

### infrastructure

这里承接数据库、配置和技术实现。

它是“怎么做”的区域，不是“业务为何这样做”的区域。

### interfaces/http

这里负责把 HTTP 请求适配为应用层命令，把应用层结果适配为 HTTP 响应。

它不应承担复杂业务决策。

### interfaces/acl

这里负责把外部上下文或第三方系统的表达翻译为本上下文可理解的语义对象。

这是“边界翻译层”，不是领域模型本身。

---

## 教学视角下最重要的两条线

### 1. 业务主线

```text
HTTP 请求
  -> application use case
  -> domain model / domain rule
  -> repository port
  -> infrastructure implementation
```

### 2. 边界协作线

```text
外部系统表达
  -> ACL 适配器翻译
  -> application 边界语义
  -> 本上下文用例 / 领域对象
```

这两条线分开，读者才更容易理解：

- 入站接口适配，不等于边界翻译
- 分层清楚，不代表上下文边界就天然清楚

---

## 当前仓库的刻意克制

为了保持教学清晰度，当前只放一个 bounded context，并用轻量 ACL 占位模块来表达设计意图。

这样做的好处是：

- 不会因为多上下文示例太重而干扰主线理解
- 但又保留了继续演进到“上下文协作”示例的正确结构
