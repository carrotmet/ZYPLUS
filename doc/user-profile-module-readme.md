# 用户画像模块开发文档

## 模块概述

基于 **Career-Planning SKILL 三层模型** 开发的智能用户画像系统，支持通过RAG对话（主要）和表单填写（次要）收集用户信息。

## 架构设计

### 三层模型映射

```
┌────────────────────────────────────────────────────────────┐
│ 接口层 (Interface Layer) - 个性化输入                       │
│ 数据表: user_profiles.interface_*                          │
│ ├── holland_code: 霍兰德代码                               │
│ ├── mbti_type: MBTI类型                                    │
│ ├── value_priorities: 价值观优先级 (JSON)                  │
│ ├── ability_assessment: 能力评估 (JSON)                    │
│ └── constraints: 约束条件 (JSON)                           │
├────────────────────────────────────────────────────────────┤
│ 可变层 (Variable Layer) - 专业适配要素                      │
│ 数据表: user_profiles.variable_*                           │
│ ├── preferred_disciplines: 偏好学科 (JSON)                 │
│ ├── preferred_majors: 偏好专业 (JSON)                      │
│ ├── career_path_preference: 路径偏好                       │
│ └── practice_experiences: 实践经历 (JSON)                  │
├────────────────────────────────────────────────────────────┤
│ 核心层 (Core Layer) - 跨专业不变要素                        │
│ 数据表: user_profiles.core_*                               │
│ ├── current_casve_stage: CASVE决策阶段                     │
│ ├── casve_history: CASVE历史 (JSON)                        │
│ ├── universal_skills: 通用技能 (JSON)                      │
│ ├── resilience_score: 职业弹性分数                         │
│ └── rag_session_id: LazyLLM会话ID                          │
└────────────────────────────────────────────────────────────┘
```

## 文件结构

### 后端文件

```
backend/app/
├── models_user_profile.py        # 数据模型 (SQLAlchemy)
├── schemas_user_profile.py       # Pydantic Schema
├── crud_user_profile.py          # CRUD操作
├── api_user_profile.py           # API路由
├── services/
│   ├── __init__.py
│   └── rag_service.py            # RAG服务 (LazyLLM集成)
└── database.py                   # 数据库初始化 (已更新)

backend/app/main.py               # FastAPI主应用 (已更新)
```

### 前端文件

```
user-profile.html                 # 用户画像页面
user-profile.js                   # 前端逻辑
```

### 文档

```
doc/user-profile-module-design.md    # 设计文档
doc/user-profile-module-readme.md    # 本文件
```

## API 接口列表

### 基础CRUD

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/user-profiles/{user_id}` | 获取用户画像 |
| POST | `/api/user-profiles` | 创建用户画像 |
| PUT | `/api/user-profiles/{user_id}` | 更新用户画像 |
| DELETE | `/api/user-profiles/{user_id}` | 删除用户画像 |

### RAG对话

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/user-profiles/{user_id}/chat` | 发送对话消息 |
| GET | `/api/user-profiles/{user_id}/chat/history` | 获取对话历史 |
| DELETE | `/api/user-profiles/{user_id}/chat/session` | 清除会话 |

### 分析推荐

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/user-profiles/{user_id}/completeness` | 获取完整度 |
| POST | `/api/user-profiles/{user_id}/analyze` | 分析画像 |
| GET | `/api/user-profiles/{user_id}/career-paths` | 推荐职业路径 |
| POST | `/api/user-profiles/{user_id}/casve/advance` | 推进CASVE阶段 |
| GET | `/api/user-profiles/{user_id}/visualization` | 分层可视化数据 |
| POST | `/api/user-profiles/{user_id}/batch-update` | 批量更新 |

## RAG对话流程

```
用户输入消息
    ↓
[Intent识别] → 确定对话意图 (interest_explore/ability_assess/...)
    ↓
[知识检索] → 从SKILL文档检索相关知识
    ↓
[LazyLLM生成] → 生成个性化回复
    ↓
[信息提取] → 提取结构化画像信息
    ↓
[画像更新] → 自动更新user_profiles表
    ↓
返回: 回复内容 + 提取信息 + 建议问题
```

## 数据库表结构

### user_profiles (主表)

```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    
    -- 接口层
    holland_code VARCHAR(10),
    mbti_type VARCHAR(10),
    value_priorities JSON,
    ability_assessment JSON,
    constraints JSON,
    
    -- 可变层
    preferred_disciplines JSON,
    preferred_majors JSON,
    career_path_preference VARCHAR(50),
    practice_experiences JSON,
    
    -- 核心层
    current_casve_stage VARCHAR(20) DEFAULT 'communication',
    casve_history JSON,
    universal_skills JSON,
    resilience_score INTEGER,
    rag_session_id VARCHAR(100),
    conversation_summary TEXT,
    
    -- 元数据
    completeness_score INTEGER DEFAULT 0,
    last_updated DATETIME,
    created_at DATETIME
);
```

### user_conversations (对话记录)

```sql
CREATE TABLE user_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    message_role VARCHAR(20),
    message_content TEXT,
    intent_type VARCHAR(50),
    extracted_entities JSON,
    timestamp DATETIME
);
```

### user_profile_logs (更新日志)

```sql
CREATE TABLE user_profile_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    update_type VARCHAR(50),
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    source_message_id INTEGER,
    timestamp DATETIME
);
```

## 前端组件

### 左侧: AI对话区
- 聊天历史展示
- 消息输入框
- 快捷意图按钮 (兴趣/能力/价值观/职业建议)
- 加载指示器

### 右侧: 画像可视化
- 完整度进度条 (三层分别显示)
- CASVE阶段指示器
- 接口层卡片 (兴趣/性格/价值观/能力)
- 可变层卡片 (专业偏好/路径选择/实践经历)
- 核心层卡片 (通用技能/职业弹性)

## 使用方式

### 1. 启动后端

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. 访问前端页面

打开 `user-profile.html` 文件，或部署到Web服务器访问。

### 3. 开始对话

- 用户首次访问会自动创建画像
- 通过对话框与AI助手交流
- AI会自动提取信息并更新画像
- 可以在右侧查看画像完善进度

## 扩展指南

### 添加新的画像维度

1. **模型层**: 在 `models_user_profile.py` 添加字段
2. **Schema层**: 在 `schemas_user_profile.py` 添加字段
3. **CRUD层**: 更新完整度计算逻辑
4. **RAG层**: 在 `rag_service.py` 添加信息提取规则

### 自定义RAG知识库

在 `rag_service.py` 中修改 `knowledge_base_path` 指向新的SKILL文档目录。

### 对接真实LazyLLM

取消 `rag_service.py` 中的模拟代码，启用真实的LazyLLM调用:

```python
from lazyllm import OnlineChatModule, Retrieval, Pipeline

# 构建真实RAG流水线
llm = OnlineChatModule(source="openai", model="gpt-3.5-turbo")
retriever = Retrieval(documents=skill_docs)
pipeline = Pipeline([retriever, llm])
```

## 关键特性

1. **智能信息提取**: 自动从对话中提取画像信息
2. **三层模型可视化**: 直观展示SKILL三层架构
3. **CASVE决策支持**: 引导用户完成系统决策流程
4. **完整度追踪**: 实时显示画像完善进度
5. **知识驱动**: 基于职业规划SKILL提供专业建议
6. **可扩展设计**: 易于添加新的评估维度

## 与项目其他模块的关系

```
用户画像模块
    ↓ 提供用户偏好
专业推荐系统 ← 数据库中的专业/职业数据
    ↓ 生成推荐
职业路径图 ← 使用三层模型可视化
```
