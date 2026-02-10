# 用户报告模块 API 接口设计文档

> **文档版本**: v1.0  
> **创建日期**: 2026-02-09  
> **关联文档**: `design.md`, `database.md`

---

## 一、接口概览

### 1.1 接口分类

| 分类 | 接口数量 | 说明 |
|-----|---------|-----|
| **条件检查接口** | 2个 | 报告生成条件查询与验证 |
| **报告生成接口** | 4个 | 生成任务启动、状态查询、取消、回调 |
| **报告查询接口** | 4个 | 报告列表、详情、章节、历史 |
| **报告导出接口** | 3个 | PDF、Word、Markdown导出 |
| **管理接口** | 2个 | 报告删除、归档 |

### 1.2 基础信息

- **基础URL**: `/api/user-reports`
- **认证方式**: JWT Token (Authorization: Bearer {token})
- **请求格式**: JSON
- **响应格式**: JSON
- **字符编码**: UTF-8

### 1.3 通用响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误码定义**:

| 错误码 | 说明 | HTTP状态码 |
|-------|-----|-----------|
| 200 | 成功 | 200 |
| 400 | 请求参数错误 | 400 |
| 401 | 未授权 | 401 |
| 403 | 禁止访问 | 403 |
| 404 | 资源不存在 | 404 |
| 409 | 资源冲突 (如报告正在生成中) | 409 |
| 422 | 业务逻辑错误 (如条件不满足) | 422 |
| 500 | 服务器内部错误 | 500 |
| 503 | 服务暂时不可用 | 503 |

---

## 二、条件检查接口

### 2.1 获取报告生成条件清单

获取指定报告类型的所有生成条件及其当前状态。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/prerequisites`
- **Auth**: Required

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_type | string | 是 | 报告类型: `SUB_REPORT_A`/`SUB_REPORT_B`/`SUB_REPORT_C`/`SUB_REPORT_D`/`FULL_REPORT` |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "report_type": "FULL_REPORT",
    "can_generate": false,
    "overall_progress": 65,
    "prerequisites": [
      {
        "id": "A1",
        "name": "接口层基础信息",
        "description": "需要完成Holland职业兴趣测评和MBTI性格测试",
        "status": "passed",
        "current_value": "RIA, ENFP",
        "required_value": "非空",
        "weight": 10
      },
      {
        "id": "A2",
        "name": "接口层完整度",
        "description": "接口层完整度需要达到60%以上",
        "status": "passed",
        "current_value": 75,
        "required_value": ">= 60",
        "weight": 10
      },
      {
        "id": "B1",
        "name": "表单填写次数",
        "description": "需要至少完成3次表单更新",
        "status": "failed",
        "current_value": 2,
        "required_value": ">= 3",
        "weight": 10,
        "recommendation": "请前往用户画像页面完善更多信息"
      },
      {
        "id": "C1",
        "name": "可变层路径偏好",
        "description": "需要设置职业路径偏好",
        "status": "passed",
        "current_value": "technical",
        "required_value": "非空",
        "weight": 10
      },
      {
        "id": "D1",
        "name": "核心层通用技能",
        "description": "需要进行通用技能评估",
        "status": "passed",
        "current_value": {"communication": 8, "teamwork": 7},
        "required_value": "非空",
        "weight": 10
      },
      {
        "id": "F1",
        "name": "总完整度",
        "description": "整体画像完整度需要达到70%以上",
        "status": "failed",
        "current_value": 65,
        "required_value": ">= 70",
        "weight": 20,
        "recommendation": "当前完整度为65%，建议完善价值观优先级和能力评估"
      }
    ],
    "next_steps": [
      "完成表单填写至少1次",
      "完善价值观优先级评估",
      "补充能力评估信息"
    ]
  }
}
```

---

### 2.2 验证特定条件

验证用户是否满足指定报告类型的生成条件。

**请求信息**:
- **Method**: POST
- **Path**: `/api/user-reports/prerequisites/validate`
- **Auth**: Required

**请求体**:

```json
{
  "report_type": "FULL_REPORT"
}
```

**响应示例** (条件不满足):

```json
{
  "code": 422,
  "message": "生成条件不满足",
  "data": {
    "can_generate": false,
    "failed_conditions": [
      {
        "id": "B1",
        "name": "表单填写次数",
        "message": "表单填写次数不足",
        "current": 2,
        "required": ">= 3",
        "recommendation": "请前往用户画像页面完善更多信息"
      }
    ]
  }
}
```

**响应示例** (条件满足):

```json
{
  "code": 200,
  "message": "条件验证通过",
  "data": {
    "can_generate": true,
    "estimated_time": "300",
    "estimated_words": 50000
  }
}
```

---

## 三、报告生成接口

### 3.1 启动报告生成任务

启动一个新的报告生成任务。

**请求信息**:
- **Method**: POST
- **Path**: `/api/user-reports/generation`
- **Auth**: Required

**请求体**:

```json
{
  "report_type": "FULL_REPORT",
  "options": {
    "include_charts": true,
    "detail_level": "detailed",
    "language": "zh-CN"
  }
}
```

**参数说明**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_type | string | 是 | 报告类型 |
| options.include_charts | boolean | 否 | 是否包含图表，默认true |
| options.detail_level | string | 否 | 详细程度: `brief`/`standard`/`detailed`，默认`detailed` |
| options.language | string | 否 | 语言: `zh-CN`/`zh-TW`/`en-US`，默认`zh-CN` |

**响应示例** (成功):

```json
{
  "code": 200,
  "message": "生成任务已启动",
  "data": {
    "task_id": "task_abc123xyz",
    "report_id": "report_def456uvw",
    "status": "pending",
    "created_at": "2026-02-09T14:30:00Z",
    "estimated_completion": "2026-02-09T14:35:00Z",
    "websocket_url": "ws://localhost:8000/api/user-reports/generation/task_abc123xyz/stream"
  }
}
```

**响应示例** (条件不满足):

```json
{
  "code": 422,
  "message": "生成条件不满足，无法启动任务",
  "data": {
    "prerequisites_url": "/api/user-reports/prerequisites?report_type=FULL_REPORT"
  }
}
```

**响应示例** (已有进行中的任务):

```json
{
  "code": 409,
  "message": "已有进行中的生成任务",
  "data": {
    "existing_task_id": "task_previous123",
    "status": "generating",
    "progress": 45
  }
}
```

---

### 3.2 获取生成任务状态

查询报告生成任务的当前状态和进度。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/generation/{task_id}`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| task_id | string | 是 | 生成任务ID |

**响应示例** (生成中):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "task_abc123xyz",
    "report_id": "report_def456uvw",
    "report_type": "FULL_REPORT",
    "status": "generating",
    "progress": {
      "overall": 65,
      "current_stage": "chapter_generation",
      "completed_chapters": 5,
      "total_chapters": 12,
      "current_chapter": {
        "id": "ch_4_2",
        "title": "4.2 可变层建模: 专业适配系统",
        "progress": 80
      }
    },
    "started_at": "2026-02-09T14:30:00Z",
    "estimated_completion": "2026-02-09T14:35:00Z",
    "elapsed_seconds": 180
  }
}
```

**响应示例** (已完成):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "task_abc123xyz",
    "report_id": "report_def456uvw",
    "report_type": "FULL_REPORT",
    "status": "completed",
    "progress": {
      "overall": 100,
      "completed_chapters": 12,
      "total_chapters": 12
    },
    "result": {
      "report_url": "/api/user-reports/report_def456uvw",
      "word_count": 52340,
      "generation_time": 298
    },
    "started_at": "2026-02-09T14:30:00Z",
    "completed_at": "2026-02-09T14:35:28Z"
  }
}
```

**响应示例** (失败):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "task_abc123xyz",
    "report_id": "report_def456uvw",
    "report_type": "FULL_REPORT",
    "status": "failed",
    "error": {
      "code": "LLM_SERVICE_ERROR",
      "message": "LLM服务暂时不可用",
      "failed_chapter": "ch_5_3",
      "retryable": true
    },
    "started_at": "2026-02-09T14:30:00Z",
    "failed_at": "2026-02-09T14:32:15Z"
  }
}
```

**状态枚举值**:

| 状态值 | 说明 |
|-------|-----|
| `pending` | 等待中 |
| `validating` | 条件验证中 |
| `generating` | 生成中 |
| `quality_checking` | 质量检查中 |
| `assembling` | 组装中 |
| `completed` | 已完成 |
| `failed` | 失败 |
| `cancelled` | 已取消 |

---

### 3.3 取消生成任务

取消正在进行的报告生成任务。

**请求信息**:
- **Method**: POST
- **Path**: `/api/user-reports/generation/{task_id}/cancel`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| task_id | string | 是 | 生成任务ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "任务已取消",
  "data": {
    "task_id": "task_abc123xyz",
    "status": "cancelled",
    "cancelled_at": "2026-02-09T14:33:00Z"
  }
}
```

---

### 3.4 WebSocket 实时进度流

通过WebSocket连接实时接收生成进度更新。

**连接信息**:
- **URL**: `ws://{host}/api/user-reports/generation/{task_id}/stream`
- **Auth**: JWT Token (通过query参数或header传递)

**消息格式**:

```json
{
  "type": "progress_update",
  "timestamp": "2026-02-09T14:31:30Z",
  "data": {
    "overall_progress": 65,
    "current_stage": "chapter_generation",
    "chapter_update": {
      "id": "ch_4_2",
      "title": "4.2 可变层建模: 专业适配系统",
      "status": "generating",
      "progress": 80,
      "word_count": 4200
    }
  }
}
```

**消息类型**:

| 类型 | 说明 |
|-----|-----|
| `progress_update` | 进度更新 |
| `chapter_complete` | 章节完成 |
| `stage_change` | 阶段变更 |
| `completed` | 全部完成 |
| `error` | 错误发生 |
| `cancelled` | 任务取消 |

---

## 四、报告查询接口

### 4.1 获取报告列表

获取当前用户的所有报告列表。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports`
- **Auth**: Required

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认10，最大50 |
| report_type | string | 否 | 筛选报告类型 |
| sort_by | string | 否 | 排序字段: `created_at`/`word_count`，默认`created_at` |
| sort_order | string | 否 | 排序方向: `asc`/`desc`，默认`desc` |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "page": 1,
    "page_size": 10,
    "reports": [
      {
        "id": "report_def456uvw",
        "title": "职业规划完整报告",
        "report_type": "FULL_REPORT",
        "status": "completed",
        "word_count": 52340,
        "chapter_count": 12,
        "created_at": "2026-02-09T14:35:28Z",
        "thumbnail_url": "/api/user-reports/report_def456uvw/thumbnail"
      },
      {
        "id": "report_sub_a_001",
        "title": "用户画像深度分析报告",
        "report_type": "SUB_REPORT_A",
        "status": "completed",
        "word_count": 8520,
        "chapter_count": 4,
        "created_at": "2026-02-08T10:20:15Z"
      }
    ]
  }
}
```

---

### 4.2 获取报告详情

获取指定报告的详细信息和元数据。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/{report_id}`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_id | string | 是 | 报告ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "report_def456uvw",
    "title": "职业规划完整报告",
    "report_type": "FULL_REPORT",
    "status": "completed",
    "metadata": {
      "word_count": 52340,
      "chapter_count": 12,
      "generation_time": 298,
      "detail_level": "detailed",
      "include_charts": true
    },
    "chapters": [
      {
        "id": "ch_1",
        "title": "第一章: 执行摘要",
        "word_count": 2100,
        "order": 1
      },
      {
        "id": "ch_2",
        "title": "第二章: 用户画像深度分析",
        "word_count": 8200,
        "order": 2
      }
    ],
    "created_at": "2026-02-09T14:35:28Z",
    "data_snapshot": {
      "profile_completeness": 75,
      "interface_layer": {
        "holland_code": "RIA",
        "mbti_type": "ENFP"
      },
      "variable_layer": {
        "career_path_preference": "technical"
      },
      "core_layer": {
        "casve_stage": "analysis"
      }
    }
  }
}
```

---

### 4.3 获取报告内容

获取报告的完整内容或指定章节内容。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/{report_id}/content`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_id | string | 是 | 报告ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| chapter_id | string | 否 | 章节ID，不提供则返回全部内容 |
| format | string | 否 | 格式: `html`/`markdown`/`text`，默认`html` |

**响应示例** (HTML格式):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "report_id": "report_def456uvw",
    "chapter_id": null,
    "format": "html",
    "content": "<div class=\"report-content\">...</div>",
    "word_count": 52340,
    "toc": [
      {"id": "ch_1", "title": "第一章: 执行摘要", "level": 1},
      {"id": "ch_2", "title": "第二章: 用户画像深度分析", "level": 1},
      {"id": "ch_2_1", "title": "2.1 接口层画像解析", "level": 2}
    ]
  }
}
```

---

### 4.4 获取章节内容

获取指定章节的详细内容。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/{report_id}/chapters/{chapter_id}`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_id | string | 是 | 报告ID |
| chapter_id | string | 是 | 章节ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| format | string | 否 | 格式: `html`/`markdown`/`text`，默认`html` |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "report_id": "report_def456uvw",
    "chapter": {
      "id": "ch_2_1",
      "title": "2.1 Holland职业兴趣分析",
      "order": 3,
      "parent_id": "ch_2",
      "word_count": 2150,
      "content": "<h3>2.1 Holland职业兴趣分析</h3><p>您的Holland代码为RIA...</p>...",
      "format": "html",
      "generated_at": "2026-02-09T14:32:15Z"
    },
    "navigation": {
      "prev": {"id": "ch_2", "title": "第二章: 用户画像深度分析"},
      "next": {"id": "ch_2_2", "title": "2.2 MBTI性格类型分析"}
    }
  }
}
```

---

## 五、报告导出接口

### 5.1 导出PDF

将报告导出为PDF格式。

**请求信息**:
- **Method**: POST
- **Path**: `/api/user-reports/{report_id}/export/pdf`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_id | string | 是 | 报告ID |

**请求体**:

```json
{
  "include_toc": true,
  "include_cover": true,
  "page_size": "A4",
  "watermark": {
    "enabled": true,
    "text": "用户ID: user_123"
  }
}
```

**响应**:
- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename="职业规划完整报告_20260209.pdf"`

---

### 5.2 导出Word

将报告导出为Word格式(.docx)。

**请求信息**:
- **Method**: POST
- **Path**: `/api/user-reports/{report_id}/export/word`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_id | string | 是 | 报告ID |

**请求体**:

```json
{
  "include_toc": true,
  "include_cover": true,
  "template": "default"
}
```

**响应**:
- **Content-Type**: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Content-Disposition**: `attachment; filename="职业规划完整报告_20260209.docx"`

---

### 5.3 导出Markdown

将报告导出为Markdown格式。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/{report_id}/export/markdown`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_id | string | 是 | 报告ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| include_metadata | boolean | 否 | 是否包含元数据头部，默认true |

**响应**:
- **Content-Type**: `text/markdown; charset=utf-8`
- **Content-Disposition**: `attachment; filename="职业规划完整报告_20260209.md"`

**响应示例**:

```markdown
---
title: 职业规划完整报告
created_at: 2026-02-09T14:35:28Z
word_count: 52340
---

# 职业规划完整报告

## 第一章: 执行摘要

...
```

---

## 六、管理接口

### 6.1 删除报告

删除指定的报告及其所有相关数据。

**请求信息**:
- **Method**: DELETE
- **Path**: `/api/user-reports/{report_id}`
- **Auth**: Required

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| report_id | string | 是 | 报告ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "报告已删除",
  "data": {
    "report_id": "report_def456uvw",
    "deleted_at": "2026-02-09T16:00:00Z"
  }
}
```

---

### 6.2 获取报告生成历史

获取用户报告生成的历史记录（包含失败和取消的任务）。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/generation/history`
- **Auth**: Required

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|-----|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |
| status | string | 否 | 筛选状态，多个用逗号分隔 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 12,
    "page": 1,
    "page_size": 20,
    "history": [
      {
        "task_id": "task_abc123xyz",
        "report_id": "report_def456uvw",
        "report_type": "FULL_REPORT",
        "status": "completed",
        "created_at": "2026-02-09T14:30:00Z",
        "completed_at": "2026-02-09T14:35:28Z",
        "generation_time": 298
      },
      {
        "task_id": "task_failed_001",
        "report_id": null,
        "report_type": "SUB_REPORT_C",
        "status": "failed",
        "created_at": "2026-02-08T09:00:00Z",
        "failed_at": "2026-02-08T09:05:00Z",
        "error": {
          "code": "LLM_TIMEOUT",
          "message": "生成超时"
        }
      }
    ]
  }
}
```

---

## 七、前端集成接口

### 7.1 获取报告中心初始化数据

为报告中心页面提供一站式数据加载。

**请求信息**:
- **Method**: GET
- **Path**: `/api/user-reports/center/init`
- **Auth**: Required

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_stats": {
      "total_reports": 5,
      "last_generated_at": "2026-02-09T14:35:28Z",
      "profile_completeness": 75
    },
    "prerequisites_summary": {
      "FULL_REPORT": {
        "can_generate": false,
        "progress": 65
      },
      "SUB_REPORT_A": {
        "can_generate": true,
        "progress": 90
      }
    },
    "recent_reports": [
      {
        "id": "report_def456uvw",
        "title": "职业规划完整报告",
        "report_type": "FULL_REPORT",
        "created_at": "2026-02-09T14:35:28Z"
      }
    ],
    "active_task": {
      "task_id": "task_abc123xyz",
      "status": "generating",
      "progress": 65
    }
  }
}
```

---

## 八、错误处理规范

### 8.1 错误响应格式

```json
{
  "code": 422,
  "message": "生成条件不满足",
  "data": {
    "error_code": "PREREQUISITES_NOT_MET",
    "error_details": [...],
    "suggestions": [...]
  }
}
```

### 8.2 业务错误码

| 错误码 | 说明 | HTTP状态码 |
|-------|-----|-----------|
| `PREREQUISITES_NOT_MET` | 生成条件不满足 | 422 |
| `GENERATION_IN_PROGRESS` | 已有生成任务进行中 | 409 |
| `LLM_SERVICE_ERROR` | LLM服务错误 | 503 |
| `GENERATION_TIMEOUT` | 生成超时 | 504 |
| `QUALITY_CHECK_FAILED` | 质量检查失败 | 422 |
| `REPORT_NOT_FOUND` | 报告不存在 | 404 |
| `CHAPTER_NOT_FOUND` | 章节不存在 | 404 |
| `TASK_NOT_FOUND` | 任务不存在 | 404 |
| `EXPORT_FAILED` | 导出失败 | 500 |
| `INVALID_REPORT_TYPE` | 无效的报告类型 | 400 |

---

## 九、接口调用示例

### 9.1 完整生成流程示例

```javascript
// 1. 检查生成条件
const checkPrerequisites = async () => {
  const response = await fetch('/api/user-reports/prerequisites?report_type=FULL_REPORT', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const result = await response.json();
  
  if (result.data.can_generate) {
    return startGeneration();
  } else {
    showRecommendations(result.data.next_steps);
  }
};

// 2. 启动生成任务
const startGeneration = async () => {
  const response = await fetch('/api/user-reports/generation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      report_type: 'FULL_REPORT',
      options: { include_charts: true }
    })
  });
  const result = await response.json();
  
  // 3. 连接WebSocket监听进度
  connectWebSocket(result.data.websocket_url);
  
  return result.data.task_id;
};

// 3. WebSocket连接
const connectWebSocket = (wsUrl) => {
  const ws = new WebSocket(`${wsUrl}?token=${token}`);
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    updateProgress(message.data);
    
    if (message.type === 'completed') {
      showReport(message.data.report_id);
    }
  };
};
```

---

**文档结束**
