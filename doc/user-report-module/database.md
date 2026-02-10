# 用户报告模块 数据库设计文档

> **文档版本**: v1.0  
> **创建日期**: 2026-02-09  
> **关联文档**: `design.md`, `api.md`

---

## 一、ER图

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    用户报告模块 ER图                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   ┌──────────────────┐         ┌────────────────────┐         ┌──────────────────┐     │
│   │   user_reports   │         │  report_chapters   │         │ generation_tasks │     │
│   │   (报告元数据)    │◄────────┤   (报告章节)        │         │  (生成任务)       │     │
│   └────────┬─────────┘    1:N  └────────────────────┘         └────────┬─────────┘     │
│            │                                                           │               │
│            │ N:1                                                       │ N:1           │
│            ▼                                                           ▼               │
│   ┌──────────────────┐                                         ┌──────────────────┐     │
│   │  user_profiles   │                                         │  user_profiles   │     │
│   │   (用户画像)      │                                         │   (用户画像)      │     │
│   └──────────────────┘                                         └──────────────────┘     │
│                                                                                         │
│   ┌──────────────────┐         ┌────────────────────┐                                   │
│   │ report_snapshots │         │   report_exports   │                                   │
│   │ (报告数据快照)    │         │   (导出记录)        │                                   │
│   └──────────────────┘         └────────────────────┘                                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、表结构设计

### 2.1 报告元数据表 (user_reports)

存储报告的基本信息和生成元数据。

**表名**: `user_reports`

| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |
|-------|------|-----|-----|-------|-----|
| id | VARCHAR | 64 | PK | - | 报告ID，格式: `report_{uuid}` |
| user_id | VARCHAR | 64 | FK | - | 用户ID，关联user_profiles表 |
| title | VARCHAR | 200 | YES | - | 报告标题 |
| report_type | VARCHAR | 30 | YES | - | 报告类型枚举 |
| status | VARCHAR | 20 | YES | `draft` | 报告状态 |
| word_count | INTEGER | - | NO | 0 | 总字数 |
| chapter_count | INTEGER | - | NO | 0 | 章节数量 |
| detail_level | VARCHAR | 20 | NO | `detailed` | 详细程度 |
| include_charts | BOOLEAN | - | NO | TRUE | 是否包含图表 |
| language | VARCHAR | 10 | NO | `zh-CN` | 语言 |
| generation_time | INTEGER | - | NO | 0 | 生成耗时(秒) |
| created_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 更新时间 |
| completed_at | DATETIME | - | NO | NULL | 完成时间 |
| deleted_at | DATETIME | - | NO | NULL | 删除时间(软删除) |
| version | INTEGER | - | NO | 1 | 版本号 |

**索引**:

```sql
CREATE INDEX idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX idx_user_reports_type ON user_reports(report_type);
CREATE INDEX idx_user_reports_status ON user_reports(status);
CREATE INDEX idx_user_reports_created_at ON user_reports(created_at);
CREATE INDEX idx_user_reports_user_type ON user_reports(user_id, report_type);
```

**报告类型枚举 (report_type)**:

| 值 | 说明 |
|---|-----|
| `SUB_REPORT_A` | 用户画像深度分析报告 |
| `SUB_REPORT_B` | 用户表单分析报告 |
| `SUB_REPORT_C` | 三层职业规划建模报告 |
| `SUB_REPORT_D` | 分层递进行动体系报告 |
| `FULL_REPORT` | 职业规划完整报告 |

**报告状态枚举 (status)**:

| 值 | 说明 |
|---|-----|
| `draft` | 草稿 |
| `generating` | 生成中 |
| `completed` | 已完成 |
| `failed` | 失败 |
| `cancelled` | 已取消 |
| `archived` | 已归档 |

**建表语句**:

```sql
CREATE TABLE user_reports (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    title VARCHAR(200) NOT NULL,
    report_type VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    word_count INTEGER DEFAULT 0,
    chapter_count INTEGER DEFAULT 0,
    detail_level VARCHAR(20) DEFAULT 'detailed',
    include_charts BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'zh-CN',
    generation_time INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    deleted_at DATETIME,
    version INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

### 2.2 报告章节表 (report_chapters)

存储报告的各个章节内容。

**表名**: `report_chapters`

| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |
|-------|------|-----|-----|-------|-----|
| id | VARCHAR | 64 | PK | - | 章节ID，格式: `ch_{chapter_code}_{uuid}` |
| report_id | VARCHAR | 64 | FK | - | 所属报告ID |
| chapter_code | VARCHAR | 20 | YES | - | 章节代码，如`2.1`, `4.2.1` |
| title | VARCHAR | 200 | YES | - | 章节标题 |
| parent_id | VARCHAR | 64 | FK | NO | NULL | 父章节ID(用于层级结构) |
| order_num | INTEGER | - | YES | 0 | 排序序号 |
| level | INTEGER | - | YES | 1 | 层级深度(1-4) |
| word_count | INTEGER | - | NO | 0 | 章节字数 |
| content_html | TEXT | - | NO | NULL | HTML格式内容 |
| content_markdown | TEXT | - | NO | NULL | Markdown格式内容 |
| content_plain | TEXT | - | NO | NULL | 纯文本内容 |
| status | VARCHAR | 20 | YES | `pending` | 章节状态 |
| generated_at | DATETIME | - | NO | NULL | 生成时间 |
| generation_time | INTEGER | - | NO | 0 | 生成耗时(秒) |
| llm_model | VARCHAR | 50 | NO | NULL | 使用的LLM模型 |
| prompt_tokens | INTEGER | - | NO | 0 | Prompt tokens数 |
| completion_tokens | INTEGER | - | NO | 0 | 生成tokens数 |
| created_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 更新时间 |

**索引**:

```sql
CREATE INDEX idx_report_chapters_report_id ON report_chapters(report_id);
CREATE INDEX idx_report_chapters_parent_id ON report_chapters(parent_id);
CREATE INDEX idx_report_chapters_code ON report_chapters(chapter_code);
CREATE INDEX idx_report_chapters_order ON report_chapters(report_id, order_num);
CREATE INDEX idx_report_chapters_status ON report_chapters(status);
```

**章节状态枚举 (status)**:

| 值 | 说明 |
|---|-----|
| `pending` | 等待生成 |
| `generating` | 生成中 |
| `completed` | 已完成 |
| `failed` | 失败 |
| `retrying` | 重试中 |

**章节代码规范**:

| 代码 | 章节名称 | 所属报告 |
|-----|---------|---------|
| `1` | 执行摘要 | 完整报告 |
| `2` | 用户画像深度分析 | 子报告A/完整报告 |
| `2.1` | 接口层画像解析 | 子报告A/完整报告 |
| `2.1.1` | Holland职业兴趣分析 | 子报告A/完整报告 |
| `2.1.2` | MBTI性格类型分析 | 子报告A/完整报告 |
| `2.1.3` | 价值观优先级分析 | 子报告A/完整报告 |
| `2.1.4` | 能力评估矩阵 | 子报告A/完整报告 |
| `2.2` | 可变层画像解析 | 子报告A/完整报告 |
| `2.3` | 三层画像综合解读 | 子报告A/完整报告 |
| `3` | 用户表单与交互分析 | 子报告B/完整报告 |
| `4` | 三层职业规划结构化建模 | 子报告C/完整报告 |
| `5` | 分层递进行动体系设计 | 子报告D/完整报告 |
| `6` | 职业发展路径推荐 | 完整报告 |
| `7` | 风险评估与应对策略 | 完整报告 |
| `8` | 附录 | 完整报告 |

**建表语句**:

```sql
CREATE TABLE report_chapters (
    id VARCHAR(64) PRIMARY KEY,
    report_id VARCHAR(64) NOT NULL,
    chapter_code VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    parent_id VARCHAR(64),
    order_num INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    word_count INTEGER DEFAULT 0,
    content_html TEXT,
    content_markdown TEXT,
    content_plain TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    generated_at DATETIME,
    generation_time INTEGER DEFAULT 0,
    llm_model VARCHAR(50),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES report_chapters(id) ON DELETE SET NULL
);
```

---

### 2.3 生成任务表 (generation_tasks)

存储报告生成任务的状态和进度。

**表名**: `generation_tasks`

| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |
|-------|------|-----|-----|-------|-----|
| id | VARCHAR | 64 | PK | - | 任务ID，格式: `task_{uuid}` |
| user_id | VARCHAR | 64 | FK | - | 用户ID |
| report_id | VARCHAR | 64 | FK | NO | NULL | 关联的报告ID |
| report_type | VARCHAR | 30 | YES | - | 报告类型 |
| status | VARCHAR | 20 | YES | `pending` | 任务状态 |
| progress | INTEGER | - | NO | 0 | 总体进度(0-100) |
| current_stage | VARCHAR | 30 | NO | NULL | 当前阶段 |
| current_chapter_id | VARCHAR | 64 | FK | NO | NULL | 当前正在生成的章节 |
| total_chapters | INTEGER | - | NO | 0 | 总章节数 |
| completed_chapters | INTEGER | - | NO | 0 | 已完成章节数 |
| error_code | VARCHAR | 50 | NO | NULL | 错误代码 |
| error_message | TEXT | - | NO | NULL | 错误信息 |
| retry_count | INTEGER | - | NO | 0 | 重试次数 |
| options | JSON | - | NO | NULL | 生成选项 |
| started_at | DATETIME | - | NO | NULL | 开始时间 |
| completed_at | DATETIME | - | NO | NULL | 完成时间 |
| cancelled_at | DATETIME | - | NO | NULL | 取消时间 |
| created_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 更新时间 |

**索引**:

```sql
CREATE INDEX idx_generation_tasks_user_id ON generation_tasks(user_id);
CREATE INDEX idx_generation_tasks_report_id ON generation_tasks(report_id);
CREATE INDEX idx_generation_tasks_status ON generation_tasks(status);
CREATE INDEX idx_generation_tasks_user_status ON generation_tasks(user_id, status);
```

**任务状态枚举 (status)**:

| 值 | 说明 |
|---|-----|
| `pending` | 等待中 |
| `validating` | 条件验证中 |
| `generating` | 生成中 |
| `quality_checking` | 质量检查中 |
| `assembling` | 组装中 |
| `completed` | 已完成 |
| `failed` | 失败 |
| `cancelled` | 已取消 |
| `timeout` | 超时 |

**当前阶段枚举 (current_stage)**:

| 值 | 说明 |
|---|-----|
| `prerequisites_check` | 前置条件检查 |
| `data_preparation` | 数据准备 |
| `chapter_generation` | 章节生成 |
| `quality_validation` | 质量校验 |
| `content_assembly` | 内容组装 |
| `metadata_update` | 元数据更新 |

**建表语句**:

```sql
CREATE TABLE generation_tasks (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    report_id VARCHAR(64),
    report_type VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    current_stage VARCHAR(30),
    current_chapter_id VARCHAR(64),
    total_chapters INTEGER DEFAULT 0,
    completed_chapters INTEGER DEFAULT 0,
    error_code VARCHAR(50),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    options JSON,
    started_at DATETIME,
    completed_at DATETIME,
    cancelled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE SET NULL,
    FOREIGN KEY (current_chapter_id) REFERENCES report_chapters(id) ON DELETE SET NULL
);
```

---

### 2.4 报告数据快照表 (report_snapshots)

存储报告生成时的用户数据快照，用于追溯报告依据。

**表名**: `report_snapshots`

| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |
|-------|------|-----|-----|-------|-----|
| id | VARCHAR | 64 | PK | - | 快照ID |
| report_id | VARCHAR | 64 | FK | - | 关联报告ID |
| user_id | VARCHAR | 64 | FK | - | 用户ID |
| snapshot_type | VARCHAR | 30 | YES | - | 快照类型 |
| snapshot_data | JSON | - | YES | - | 快照数据 |
| created_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 创建时间 |

**快照类型枚举 (snapshot_type)**:

| 值 | 说明 |
|---|-----|
| `user_profile` | 用户画像完整数据 |
| `interface_layer` | 接口层数据 |
| `variable_layer` | 可变层数据 |
| `core_layer` | 核心层数据 |
| `form_history` | 表单历史数据 |
| `major_preferences` | 专业偏好数据 |

**建表语句**:

```sql
CREATE TABLE report_snapshots (
    id VARCHAR(64) PRIMARY KEY,
    report_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    snapshot_type VARCHAR(30) NOT NULL,
    snapshot_data JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_report_snapshots_report_id ON report_snapshots(report_id);
CREATE INDEX idx_report_snapshots_type ON report_snapshots(snapshot_type);
```

---

### 2.5 报告导出记录表 (report_exports)

存储报告导出操作的历史记录。

**表名**: `report_exports`

| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |
|-------|------|-----|-----|-------|-----|
| id | VARCHAR | 64 | PK | - | 导出记录ID |
| report_id | VARCHAR | 64 | FK | - | 报告ID |
| user_id | VARCHAR(64) | - | FK | - | 用户ID |
| format | VARCHAR | 20 | YES | - | 导出格式 |
| file_size | INTEGER | - | NO | 0 | 文件大小(字节) |
| file_path | VARCHAR | 500 | NO | NULL | 文件存储路径 |
| export_options | JSON | - | NO | NULL | 导出选项 |
| downloaded_at | DATETIME | - | NO | NULL | 下载时间 |
| ip_address | VARCHAR | 45 | NO | NULL | 下载IP地址 |
| user_agent | TEXT | - | NO | NULL | 用户代理 |
| created_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 创建时间 |

**导出格式枚举 (format)**:

| 值 | 说明 |
|---|-----|
| `pdf` | PDF格式 |
| `word` | Word格式(.docx) |
| `markdown` | Markdown格式 |
| `txt` | 纯文本格式 |

**建表语句**:

```sql
CREATE TABLE report_exports (
    id VARCHAR(64) PRIMARY KEY,
    report_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    format VARCHAR(20) NOT NULL,
    file_size INTEGER DEFAULT 0,
    file_path VARCHAR(500),
    export_options JSON,
    downloaded_at DATETIME,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_report_exports_report_id ON report_exports(report_id);
CREATE INDEX idx_report_exports_format ON report_exports(format);
CREATE INDEX idx_report_exports_created_at ON report_exports(created_at);
```

---

### 2.6 生成日志表 (generation_logs)

存储报告生成的详细日志，用于调试和审计。

**表名**: `generation_logs`

| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |
|-------|------|-----|-----|-------|-----|
| id | INTEGER | - | PK AUTO | - | 日志ID |
| task_id | VARCHAR | 64 | FK | - | 任务ID |
| log_level | VARCHAR | 20 | YES | `info` | 日志级别 |
| stage | VARCHAR | 30 | NO | NULL | 生成阶段 |
| chapter_id | VARCHAR | 64 | FK | NO | NULL | 章节ID |
| message | TEXT | - | YES | - | 日志消息 |
| details | JSON | - | NO | NULL | 详细数据 |
| created_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 创建时间 |

**日志级别枚举 (log_level)**:

| 值 | 说明 |
|---|-----|
| `debug` | 调试 |
| `info` | 信息 |
| `warning` | 警告 |
| `error` | 错误 |
| `critical` | 严重错误 |

**建表语句**:

```sql
CREATE TABLE generation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(64) NOT NULL,
    log_level VARCHAR(20) NOT NULL DEFAULT 'info',
    stage VARCHAR(30),
    chapter_id VARCHAR(64),
    message TEXT NOT NULL,
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES generation_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES report_chapters(id) ON DELETE SET NULL
);

CREATE INDEX idx_generation_logs_task_id ON generation_logs(task_id);
CREATE INDEX idx_generation_logs_level ON generation_logs(log_level);
CREATE INDEX idx_generation_logs_created_at ON generation_logs(created_at);
```

---

## 三、完整建表脚本

```sql
-- =============================================
-- 用户报告模块数据库初始化脚本
-- 版本: v1.0
-- 创建日期: 2026-02-09
-- =============================================

-- 报告元数据表
CREATE TABLE IF NOT EXISTS user_reports (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    title VARCHAR(200) NOT NULL,
    report_type VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    word_count INTEGER DEFAULT 0,
    chapter_count INTEGER DEFAULT 0,
    detail_level VARCHAR(20) DEFAULT 'detailed',
    include_charts BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'zh-CN',
    generation_time INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    deleted_at DATETIME,
    version INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 报告章节表
CREATE TABLE IF NOT EXISTS report_chapters (
    id VARCHAR(64) PRIMARY KEY,
    report_id VARCHAR(64) NOT NULL,
    chapter_code VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    parent_id VARCHAR(64),
    order_num INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    word_count INTEGER DEFAULT 0,
    content_html TEXT,
    content_markdown TEXT,
    content_plain TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    generated_at DATETIME,
    generation_time INTEGER DEFAULT 0,
    llm_model VARCHAR(50),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES report_chapters(id) ON DELETE SET NULL
);

-- 生成任务表
CREATE TABLE IF NOT EXISTS generation_tasks (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    report_id VARCHAR(64),
    report_type VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    current_stage VARCHAR(30),
    current_chapter_id VARCHAR(64),
    total_chapters INTEGER DEFAULT 0,
    completed_chapters INTEGER DEFAULT 0,
    error_code VARCHAR(50),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    options JSON,
    started_at DATETIME,
    completed_at DATETIME,
    cancelled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE SET NULL,
    FOREIGN KEY (current_chapter_id) REFERENCES report_chapters(id) ON DELETE SET NULL
);

-- 报告数据快照表
CREATE TABLE IF NOT EXISTS report_snapshots (
    id VARCHAR(64) PRIMARY KEY,
    report_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    snapshot_type VARCHAR(30) NOT NULL,
    snapshot_data JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 报告导出记录表
CREATE TABLE IF NOT EXISTS report_exports (
    id VARCHAR(64) PRIMARY KEY,
    report_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    format VARCHAR(20) NOT NULL,
    file_size INTEGER DEFAULT 0,
    file_path VARCHAR(500),
    export_options JSON,
    downloaded_at DATETIME,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES user_reports(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 生成日志表
CREATE TABLE IF NOT EXISTS generation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(64) NOT NULL,
    log_level VARCHAR(20) NOT NULL DEFAULT 'info',
    stage VARCHAR(30),
    chapter_id VARCHAR(64),
    message TEXT NOT NULL,
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES generation_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES report_chapters(id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_type ON user_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_user_reports_status ON user_reports(status);
CREATE INDEX IF NOT EXISTS idx_user_reports_created_at ON user_reports(created_at);

CREATE INDEX IF NOT EXISTS idx_report_chapters_report_id ON report_chapters(report_id);
CREATE INDEX IF NOT EXISTS idx_report_chapters_parent_id ON report_chapters(parent_id);
CREATE INDEX IF NOT EXISTS idx_report_chapters_code ON report_chapters(chapter_code);
CREATE INDEX IF NOT EXISTS idx_report_chapters_order ON report_chapters(report_id, order_num);

CREATE INDEX IF NOT EXISTS idx_generation_tasks_user_id ON generation_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_generation_tasks_report_id ON generation_tasks(report_id);
CREATE INDEX IF NOT EXISTS idx_generation_tasks_status ON generation_tasks(status);

CREATE INDEX IF NOT EXISTS idx_report_snapshots_report_id ON report_snapshots(report_id);
CREATE INDEX IF NOT EXISTS idx_report_snapshots_type ON report_snapshots(snapshot_type);

CREATE INDEX IF NOT EXISTS idx_report_exports_report_id ON report_exports(report_id);
CREATE INDEX IF NOT EXISTS idx_report_exports_format ON report_exports(format);

CREATE INDEX IF NOT EXISTS idx_generation_logs_task_id ON generation_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_generation_logs_level ON generation_logs(log_level);
```

---

## 四、数据关系说明

### 4.1 表间关系

| 主表 | 从表 | 关系类型 | 级联操作 |
|-----|-----|---------|---------|
| users | user_reports | 1:N | ON DELETE CASCADE |
| users | generation_tasks | 1:N | ON DELETE CASCADE |
| user_reports | report_chapters | 1:N | ON DELETE CASCADE |
| user_reports | report_snapshots | 1:N | ON DELETE CASCADE |
| user_reports | report_exports | 1:N | ON DELETE CASCADE |
| generation_tasks | generation_logs | 1:N | ON DELETE CASCADE |
| report_chapters | report_chapters | 1:N (自引用) | ON DELETE SET NULL |

### 4.2 数据生命周期

```
用户删除账号
    │
    ├──► user_reports 级联删除
    │       ├──► report_chapters 级联删除
    │       ├──► report_snapshots 级联删除
    │       └──► report_exports 级联删除
    │
    ├──► generation_tasks 级联删除
    │       └──► generation_logs 级联删除
    │
    └──► 其他模块数据级联删除

报告删除
    │
    ├──► report_chapters 级联删除
    ├──► report_snapshots 级联删除
    ├──► report_exports 级联删除
    └──► generation_tasks 设为 NULL
```

---

**文档结束**
