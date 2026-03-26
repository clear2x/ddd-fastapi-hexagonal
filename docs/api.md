# API 契约说明

本文档描述当前示例项目对外暴露的 HTTP API 契约，目标是让开源读者在不深入阅读源码的情况下，也能快速理解接口语义、输入约束与响应结构。

## 基本信息

- 基础路径：`/api/v1`
- 内容类型：`application/json`
- 时间字段：ISO 8601 格式的 UTC 时间
- 成功响应：统一使用 `{ "data": ... }`
- 错误响应：统一使用 `{ "error": ... }`

## 统一响应结构

### 成功响应结构

所有成功响应都遵循如下结构：

```json
{
  "data": {}
}
```

`data` 的具体类型由接口决定，可能是：

- 单个对象
- 对象数组
- 健康检查结果

### 错误响应结构

所有错误响应都遵循如下结构：

```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "请求参数校验失败",
    "details": []
  }
}
```

字段含义如下：

- `code`：稳定的机器可读错误码，适合前端或调用方分支处理
- `message`：面向人类阅读的错误说明
- `details`：可选的结构化细节列表；当没有更多细节时返回空数组

### 错误码说明

| 错误码 | HTTP 状态码 | 含义 | 典型场景 |
| --- | --- | --- | --- |
| `REQUEST_VALIDATION_ERROR` | `422` | 请求参数校验失败 | 缺字段、类型不匹配、空白字符串不合法 |
| `TASK_NOT_FOUND` | `404` | 任务不存在 | 根据 `task_id` 查不到任务 |
| `TASK_ALREADY_COMPLETED` | `409` | 任务已完成，不能重复完成 | 对已完成任务再次调用完成接口 |
| `DOMAIN_ERROR` | `400` | 领域规则错误 | 请求通过了 HTTP 校验，但进入领域层后触发业务规则 |

## 任务对象结构

任务相关接口中的 `data` 对象结构如下：

```json
{
  "id": "task_1234567890abcdef",
  "title": "实现 API 文档",
  "description": "补齐契约说明与示例",
  "assignee_id": "user_001",
  "status": "assigned",
  "created_at": "2026-03-26T16:00:00Z",
  "updated_at": "2026-03-26T16:05:00Z",
  "completed_at": null
}
```

字段语义：

- `id`：任务标识，服务端生成，格式上以 `task_` 前缀开头
- `title`：任务标题，创建时必填，服务端会自动去掉首尾空白
- `description`：任务描述，可为空
- `assignee_id`：指派人标识，可为空
- `status`：任务状态，当前支持：
  - `pending`：未指派、未完成
  - `assigned`：已指派、未完成
  - `completed`：已完成
- `created_at`：创建时间
- `updated_at`：最近更新时间
- `completed_at`：完成时间；未完成时为 `null`

## description 空值归一化规则

创建任务时，`description` 字段采用“空值归一化”策略，避免把没有实际意义的空白字符串写入领域对象或数据库。

规则如下：

| 输入情况 | 归一化结果 |
| --- | --- |
| 字段未传 | `null` |
| 显式传 `null` | `null` |
| 传入 `"   "` 这类仅空白字符串 | `null` |
| 传入带首尾空白的非空字符串 | 去掉首尾空白后保存 |

示例：

请求：

```json
{
  "title": "编写文档",
  "description": "   "
}
```

响应中的 `description`：

```json
null
```

## 接口列表

### 1. 健康检查

#### `GET /health`

用于确认服务进程是否正常运行。

成功响应示例：

```json
{
  "data": {
    "status": "ok"
  }
}
```

---

### 2. 创建任务

#### `POST /api/v1/tasks`

创建一个新任务。

请求体：

```json
{
  "title": "实现 API 文档",
  "description": "补齐请求与响应示例"
}
```

请求字段说明：

- `title`：必填，去掉首尾空白后不能为空，最大长度 200
- `description`：可选，可为 `null`，归一化后最大长度 2000

成功响应：`201 Created`

```json
{
  "data": {
    "id": "task_1234567890abcdef",
    "title": "实现 API 文档",
    "description": "补齐请求与响应示例",
    "assignee_id": null,
    "status": "pending",
    "created_at": "2026-03-26T16:00:00Z",
    "updated_at": "2026-03-26T16:00:00Z",
    "completed_at": null
  }
}
```

校验失败示例：`422 Unprocessable Entity`

```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "请求参数校验失败",
    "details": [
      {
        "field": "title",
        "message": "Value error, 标题不能为空",
        "type": "value_error"
      }
    ]
  }
}
```

说明：

- 当 `title` 缺失时，也会返回 `422`
- 当 `description` 仅包含空白字符时，不会报错，而是归一化为 `null`

---

### 3. 获取单个任务

#### `GET /api/v1/tasks/{task_id}`

根据任务 ID 获取任务详情。

成功响应：`200 OK`

```json
{
  "data": {
    "id": "task_1234567890abcdef",
    "title": "实现 API 文档",
    "description": "补齐请求与响应示例",
    "assignee_id": null,
    "status": "pending",
    "created_at": "2026-03-26T16:00:00Z",
    "updated_at": "2026-03-26T16:00:00Z",
    "completed_at": null
  }
}
```

任务不存在示例：`404 Not Found`

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "任务不存在：task_missing",
    "details": []
  }
}
```

---

### 4. 查询任务列表

#### `GET /api/v1/tasks`

返回任务列表，默认按 `created_at` 倒序排列，即新创建的任务排在前面。

当前支持的查询参数：

- `status`：按任务状态过滤
- `assignee_id`：按指派人过滤

示例请求：

```text
GET /api/v1/tasks?status=assigned&assignee_id=user_001
```

成功响应：`200 OK`

```json
{
  "data": [
    {
      "id": "task_1234567890abcdef",
      "title": "实现 API 文档",
      "description": "补齐请求与响应示例",
      "assignee_id": "user_001",
      "status": "assigned",
      "created_at": "2026-03-26T16:00:00Z",
      "updated_at": "2026-03-26T16:05:00Z",
      "completed_at": null
    }
  ]
}
```

说明：

- 当前 `status` 查询参数本身没有额外枚举校验，调用方应传入已知状态值
- 若没有匹配结果，返回空数组，而不是报错

---

### 5. 指派任务

#### `POST /api/v1/tasks/{task_id}/assignments`

给指定任务设置指派人。

请求体：

```json
{
  "assignee_id": "user_001"
}
```

请求字段说明：

- `assignee_id`：必填，去掉首尾空白后不能为空，最大长度 128

成功响应：`200 OK`

```json
{
  "data": {
    "id": "task_1234567890abcdef",
    "title": "实现 API 文档",
    "description": "补齐请求与响应示例",
    "assignee_id": "user_001",
    "status": "assigned",
    "created_at": "2026-03-26T16:00:00Z",
    "updated_at": "2026-03-26T16:05:00Z",
    "completed_at": null
  }
}
```

校验失败示例：`422 Unprocessable Entity`

```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "请求参数校验失败",
    "details": [
      {
        "field": "assignee_id",
        "message": "Value error, 指派人不能为空",
        "type": "value_error"
      }
    ]
  }
}
```

任务不存在示例：`404 Not Found`

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "任务不存在：task_missing",
    "details": []
  }
}
```

说明：

- 若任务已经完成，当前实现仍允许写入 `assignee_id`，但状态会保持 `completed`
- 这体现的是当前示例代码的既有契约，不代表所有真实业务都应这样设计

---

### 6. 完成任务

#### `POST /api/v1/tasks/{task_id}/completion`

把指定任务标记为已完成。

请求体：无

成功响应：`200 OK`

```json
{
  "data": {
    "id": "task_1234567890abcdef",
    "title": "实现 API 文档",
    "description": "补齐请求与响应示例",
    "assignee_id": "user_001",
    "status": "completed",
    "created_at": "2026-03-26T16:00:00Z",
    "updated_at": "2026-03-26T16:10:00Z",
    "completed_at": "2026-03-26T16:10:00Z"
  }
}
```

重复完成示例：`409 Conflict`

```json
{
  "error": {
    "code": "TASK_ALREADY_COMPLETED",
    "message": "任务已完成，不能重复完成。",
    "details": []
  }
}
```

任务不存在示例：`404 Not Found`

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "任务不存在：task_missing",
    "details": []
  }
}
```

## 调用建议

对接方可按以下方式理解当前契约：

- 把 `error.code` 作为稳定分支条件
- 把 `error.message` 作为日志或调试信息，而不是唯一判定依据
- 把 `details` 用于表单字段级提示
- 把 `description` 和 `completed_at` 当作可空字段处理

## 与源码对应关系

若需要继续深入阅读实现，可优先关注以下文件：

- `src/task_management/interfaces/http/api.py`：路由与异常映射
- `src/task_management/interfaces/http/schemas.py`：请求/响应模型与输入归一化
- `src/task_management/domain/models.py`：领域规则与状态变化
- `tests/test_api.py`：HTTP 契约测试
