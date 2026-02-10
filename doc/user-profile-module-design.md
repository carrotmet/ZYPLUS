# 用户画像模块设计文档

## 1. 设计依据：Career-Planning SKILL 三层模型

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 接口层 (Interface Layer) - 个性化输入                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ 数据实体: UserProfileInterface                                            │
│ ├── 基础信息: user_id, nickname, avatar, created_at                       │
│ ├── 兴趣价值观: holland_code, mbti_type, value_priorities (JSON)          │
│ ├── 能力评估: ability_assessment (JSON)                                   │
│ └── 约束条件: family_bg, life_constraints (JSON)                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│ 可变层 (Variable Layer) - 专业适配要素                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ 数据实体: UserProfileVariable                                             │
│ ├── 专业偏好: preferred_majors (JSON数组), preferred_disciplines          │
│ ├── 路径偏好: career_path_preference (技术/管理/第三路径)                  │
│ ├── 实践经历: practice_experiences (JSON: 竞赛/项目/实习/学术)             │
│ └── 学习记录: learning_records (JSON)                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────────────┐
│ 核心层 (Core Layer) - 跨专业不变要素                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 数据实体: UserProfileCore                                                 │
│ ├── CASVE状态: casve_stage (C/A/S/V/E), decision_history (JSON)           │
│ ├── 通用技能: universal_skills (JSON: 沟通/协作/思维/创造评分)             │
│ ├── 职业弹性: resilience_score, adaptability_index                        │
│ └── 对话上下文: rag_conversation_history (JSON, 用于LazyLLM)               │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. 数据表设计

### 2.1 主表: user_profiles
```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) UNIQUE NOT NULL,  -- 用户唯一标识
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    
    -- 接口层: 兴趣价值观 (JSON存储)
    holland_code VARCHAR(10),  -- 如: RIA, SEC
    mbti_type VARCHAR(10),     -- 如: INTJ, ENFP
    value_priorities TEXT,     -- JSON: ["成就感", "工作稳定", "创新空间"]
    
    -- 接口层: 能力评估
    ability_assessment TEXT,   -- JSON: {"逻辑推理": 8, "创造力": 7, ...}
    
    -- 接口层: 约束条件
    constraints TEXT,          -- JSON: {"family_bg": "...", "location_pref": "..."}
    
    -- 可变层: 专业偏好
    preferred_disciplines TEXT, -- JSON: [1, 2, 8] 学科ID列表
    preferred_majors TEXT,      -- JSON: [101, 102, 801] 专业ID列表
    
    -- 可变层: 路径偏好
    career_path_preference VARCHAR(50), -- technical/management/professional/public
    
    -- 可变层: 实践经历
    practice_experiences TEXT,  -- JSON: [{"type": "internship", "desc": "..."}, ...]
    
    -- 核心层: CASVE状态
    current_casve_stage VARCHAR(20) DEFAULT 'communication', -- C/A/S/V/E
    casve_history TEXT,         -- JSON: [{"stage": "C", "timestamp": "...", "notes": "..."}]
    
    -- 核心层: 通用技能
    universal_skills TEXT,      -- JSON: {"communication": 7, "teamwork": 8, ...}
    resilience_score INTEGER,   -- 1-10
    
    -- 核心层: RAG对话上下文 (LazyLLM使用)
    rag_session_id VARCHAR(100), -- LazyLLM会话ID
    conversation_summary TEXT,   -- 对话摘要
    
    -- 元数据
    completeness_score INTEGER DEFAULT 0, -- 画像完整度 0-100
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 对话记录表: user_conversations
```sql
CREATE TABLE user_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,  -- LazyLLM会话ID
    message_role VARCHAR(20),          -- user/assistant/system
    message_content TEXT,
    intent_type VARCHAR(50),           -- 消息意图: interest_explore/ability_assess/value_clarify/...
    extracted_entities TEXT,           -- JSON: 提取的实体信息
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 画像更新日志: user_profile_logs
```sql
CREATE TABLE user_profile_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    update_type VARCHAR(50),      -- conversation_extract/form_input/manual_edit
    field_name VARCHAR(100),      -- 更新的字段
    old_value TEXT,
    new_value TEXT,
    source_message_id INTEGER,    -- 关联的对话记录
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 3. API 设计

### 3.1 用户画像管理 API

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/user-profiles/{user_id} | 获取用户画像 | - | UserProfile |
| POST | /api/user-profiles | 创建用户画像 | UserProfileCreate | UserProfile |
| PUT | /api/user-profiles/{user_id} | 更新用户画像 | UserProfileUpdate | UserProfile |
| GET | /api/user-profiles/{user_id}/completeness | 获取画像完整度 | - | {score, missing_fields} |

### 3.2 RAG对话 API

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | /api/user-profiles/{user_id}/chat | 发送对话消息 | {message, context} | {reply, extracted_info, updated_fields} |
| GET | /api/user-profiles/{user_id}/chat/history | 获取对话历史 | - | Conversation[] |
| DELETE | /api/user-profiles/{user_id}/chat/session | 清除对话会话 | - | {success} |

### 3.3 智能分析 API

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | /api/user-profiles/{user_id}/analyze | 分析用户画像 | - | {insights, recommendations, career_matches} |
| GET | /api/user-profiles/{user_id}/career-paths | 推荐职业路径 | - | CareerPathRecommendation[] |
| POST | /api/user-profiles/{user_id}/casve/advance | 推进CASVE阶段 | {stage, notes} | {new_stage, actions} |

## 4. 前端页面设计

### 4.1 页面结构
```
/user-profile.html
├── Header (导航)
├── Main Content
│   ├── 左侧: AI对话区 (RAG)
│   │   ├── 对话历史展示
│   │   ├── 消息输入框
│   │   └── 快捷意图按钮 (兴趣/能力/价值观/路径)
│   │
│   └── 右侧: 画像可视化
│       ├── 接口层卡片 (兴趣/性格/价值观)
│       ├── 可变层卡片 (专业偏好/路径选择)
│       ├── 核心层卡片 (技能/CASVE状态)
│       └── 完整度进度条
│
└── Footer
```

### 4.2 关键组件
- **AIChatWidget**: RAG对话组件，集成LazyLLM
- **ProfileCard**: 分层画像卡片组件
- **CASVEProgress**: CASVE阶段可视化
- **CompletenessIndicator**: 画像完整度指示器
- **QuickIntentButtons**: 快捷意图选择按钮

## 5. RAG集成设计 (LazyLLM)

### 5.1 知识库构建
```python
# 将SKILL文档向量化存储
knowledge_base = [
    "SKILL.md - 三层模型架构",
    "01-theoretical-foundations.md - 职业规划理论",
    "02-lifelong-learning.md - 终身学习",
    "03-career-path-selection.md - 道路选择模式",
    "04-career-progression.md - 路径分化进阶",
    "05-action-plan.md - 行动计划",
    "06-industry-trends.md - 行业趋势"
]
```

### 5.2 对话流程设计
```
用户输入 → Intent识别 → 知识检索 → 回答生成 → 信息提取 → 画像更新
    │           │            │            │           │
    └───────────┴────────────┴────────────┘           │
                    LazyLLM RAG                        │
                                                      ↓
                                              更新user_profiles表
```

### 5.3 Prompt模板
```
你是一位专业的职业规划顾问，基于以下知识为用户提供服务：

{retrieved_knowledge}

当前用户画像状态：
{user_profile_summary}

用户消息：{user_message}

请：
1. 根据知识库提供专业建议
2. 识别用户提到的兴趣、能力、价值观等信息
3. 以JSON格式返回需要更新的画像字段
4. 保持对话的连贯性和个性化

返回格式：
{
    "reply": "给用户的专业回复",
    "extracted_info": {
        "field": "value"
    },
    "suggested_questions": ["问题1", "问题2"]
}
```

## 6. 实现步骤

1. **数据模型** (models.py, schemas.py)
2. **RAG服务** (services/rag_service.py - LazyLLM集成)
3. **CRUD操作** (crud.py)
4. **API路由** (main.py)
5. **前端页面** (user-profile.html + user-profile.js)
6. **组件封装** (components/)

## 7. 可扩展性设计

- **多维度评估**: 支持添加新的评估维度（如情商、领导力等）
- **多轮对话策略**: 支持配置不同的对话收集策略
- **A/B测试**: 支持对比不同RAG策略的效果
- **数据导出**: 支持画像数据导出用于分析
