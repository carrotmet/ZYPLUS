# AGENTS.md - 职业规划导航平台

> 本文档供 AI 编程助手阅读，用于快速了解项目架构和开发规范。
> 最后更新：2026-02-10

---

## 项目概述

**职业规划导航平台**是一个专为高中生和大学生设计的职业规划网站，帮助用户了解专业选择与职业发展的对应关系，打通专业学习与未来职业的信息壁垒。

### 核心功能

| 功能模块 | 说明 |
|---------|------|
| 专业树形导航 | 基于普通高等学校本科专业目录的层级结构（学科门类→专业类→专业） |
| 职业路径可视化 | 清晰的职业发展方向和薪资趋势图表（ECharts） |
| 智能推荐系统 | 根据专业推荐相关职业，显示匹配度 |
| 用户画像与RAG对话 | 基于三层模型（接口层/可变层/核心层）的智能职业规划助手 |
| 经历分享 | 用户可添加和分享个人职业经历 |
| 报告生成 | 基于用户画像生成个性化职业规划报告 |

### 技术栈

| 层级 | 技术 | 版本/说明 |
|------|------|----------|
| 后端 | Python + FastAPI | 3.9+ / 0.104.1 |
| 数据库 | SQLite + SQLAlchemy | 2.0+ |
| ORM | SQLAlchemy | 2.0.23 |
| 数据验证 | Pydantic | 2.5.0 |
| 前端 | HTML5 + CSS3 + JavaScript (ES6+) | 无框架 |
| UI | Tailwind CSS | 原子化CSS框架 |
| 图表 | ECharts.js | 数据可视化 |
| 动画 | Anime.js | 交互动画 |
| AI/RAG | DSPy + TypeChat | 意图识别与回复优化 |
| 部署 | Nginx + Docker | 容器化部署 |

---

## 项目结构

```
D:\github.com\carrotmet\zyplusv2\                    # 项目根目录
│
├── index.html                  # 主页 - 专业树形导航
├── major-detail.html           # 专业详情页 - 职业信息展示
├── add-info.html               # 信息管理页 - 添加专业/职业/经历
├── experience-sharing.html     # 经历分享页面
├── user-profile.html           # 用户画像与RAG对话页面
├── report-center.html          # 报告中心页面
├── report-generation.html      # 报告生成页面
├── report-viewer.html          # 报告查看页面
├── main.js                     # 主页JavaScript逻辑
├── add-info.js                 # 信息管理页逻辑
├── user-profile.js             # 用户画像模块前端逻辑
├── profile-form.js             # 画像表单逻辑
├── api-service.js              # 前端API服务封装（含Mock数据）
├── Dockerfile                  # 前端Nginx容器配置
├── docker-compose.yml          # 多容器编排配置
├── nginx.conf                  # Nginx服务器配置
│
├── backend/                    # 后端代码目录
│   ├── requirements.txt        # Python依赖清单
│   ├── Dockerfile              # 后端容器配置
│   ├── .env                    # 环境变量配置（LLM API Key）
│   └── app/                    # 主应用代码
│       ├── main.py             # FastAPI主应用入口
│       ├── database.py         # 数据库连接和初始化
│       ├── models.py           # SQLAlchemy数据模型（专业/职业/经历）
│       ├── schemas.py          # Pydantic数据验证模式
│       ├── crud.py             # 数据库CRUD操作
│       ├── api_auth.py         # 用户认证API
│       ├── api_user_profile.py # 用户画像API路由
│       ├── api_user_report.py  # 用户报告API路由
│       ├── models_user_profile.py   # 用户画像数据模型（三层模型）
│       ├── schemas_user_profile.py  # 用户画像模式
│       ├── crud_user_profile.py     # 用户画像CRUD
│       ├── models_user_report.py    # 用户报告数据模型
│       ├── schemas_user_report.py   # 用户报告模式
│       ├── crud_user_report.py      # 用户报告CRUD
│       ├── report_generation_service.py  # 报告生成服务
│       ├── report_prerequisites.py       # 报告前置条件检查
│       ├── services/           # 业务服务层
│       │   └── rag_service.py  # 旧版LazyLLM RAG服务（fallback）
│       ├── rag_dspy/           # DSPy RAG模块
│       │   ├── __init__.py
│       │   ├── dspy_rag_service.py    # DSPy主服务
│       │   ├── signatures/            # DSPy签名定义
│       │   │   ├── intent_signature.py
│       │   │   ├── extract_signature.py
│       │   │   └── generate_signature.py
│       │   └── modules/               # DSPy模块实现
│       │       ├── intent_classifier.py
│       │       ├── info_extractor.py
│       │       ├── prompt_generator.py
│       │       └── response_optimizer.py
│       └── init_*.py           # 学科数据初始化脚本（14个）
│
├── frontend/                   # 前端TypeScript代码
│   └── src/
│       ├── types/careerChat.ts       # TypeChat类型定义
│       └── services/typechatProcessor.ts  # TypeChat预处理器
│
├── doc/                        # 项目文档目录
│   ├── design.md               # 后端API设计文档
│   ├── interaction.md          # 交互设计文档
│   ├── WINDOWS_DEVELOPMENT.md  # Windows开发指南
│   ├── RAG_REFACTOR_PLAN.md    # RAG重构规划
│   ├── DATABASE_SETUP.md       # 数据库设置说明
│   ├── user-profile-module-design.md  # 用户画像模块设计
│   └── *.md                    # 其他设计文档和更新日志
│
├── .agents/skills/Career-Planning/  # 职业规划领域知识
│   └── SKILL.md                # 三层模型理论基础
│
├── tests/                      # 测试脚本目录
│   ├── test_api.py             # API测试脚本
│   ├── test_dspy_intent.py     # DSPy意图测试
│   ├── test_dspy_simple.py     # DSPy简单测试
│   └── test_ai_profile_update.py  # AI画像更新测试
│
├── resources/                  # 静态资源（图片等）
├── data/                       # SQLite数据库文件存储
└── logs/                       # 日志文件
```

---

## 构建与启动

### 方法一：一键启动（Windows推荐）

```cmd
# 在项目根目录双击运行
start-dev.bat

# 选择选项 [1] 启动完整开发环境
# 前端: http://localhost:8001
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方法二：手动启动

```cmd
# 1. 安装Python依赖（首次）
cd backend
pip install -r requirements.txt

# 2. 启动后端（端口8000）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 启动前端（端口8001，新终端）
cd <项目根目录>
python -m http.server 8001
```

### 方法三：独立启动脚本

```cmd
# 仅启动后端
start-backend.bat

# 仅启动前端
start-frontend.bat

# 启动DSPy模式后端
start-backend-dspy.bat
```

### 方法四：Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 前端访问: http://localhost
# 后端API: http://localhost:8000
```

---

## 配置说明

### LLM API Key 配置（必需，用于AI对话功能）

**方式1：环境变量（推荐）**
```powershell
# Windows PowerShell
$env:LAZYLLM_KIMI_API_KEY="your_api_key_here"

# Windows CMD
set LAZYLLM_KIMI_API_KEY=your_api_key_here
```

**方式2：.env文件**
编辑 `backend/.env` 文件：
```
LAZYLLM_KIMI_API_KEY=sk-your-actual-api-key-here
```

**支持的LLM服务商：**

| 服务商 | 环境变量名 | 注册地址 |
|--------|-----------|----------|
| Kimi (推荐) | `LAZYLLM_KIMI_API_KEY` | https://platform.moonshot.cn/ |
| DeepSeek | `LAZYLLM_DEEPSEEK_API_KEY` | https://platform.deepseek.com/ |
| OpenAI | `LAZYLLM_OPENAI_API_KEY` / `OPENAI_API_KEY` | https://platform.openai.com/ |
| 智谱GLM | `LAZYLLM_GLM_API_KEY` | https://open.bigmodel.cn/ |
| 通义千问 | `LAZYLLM_QWEN_API_KEY` | https://dashscope.aliyun.com/ |

---

## 代码组织

### 后端架构

**FastAPI应用结构：**
```
backend/app/
├── main.py              # FastAPI应用入口，路由注册
├── database.py          # SQLAlchemy引擎、会话、基类
├── models*.py           # 数据库模型定义
├── schemas*.py          # Pydantic数据验证模式
├── crud*.py             # 数据库CRUD操作
├── api_*.py             # API路由处理
├── services/            # 业务逻辑服务层
└── rag_dspy/            # DSPy RAG实现
```

**模型分层：**
- `models.py` - 核心数据模型（学科、专业、职业、经历）
- `models_user_profile.py` - 用户画像三层模型
- `models_user_report.py` - 用户报告模型

**API分层：**
- `main.py` - 核心学科/专业/职业API
- `api_user_profile.py` - 用户画像API（前缀 `/api/user-profiles`）
- `api_user_report.py` - 用户报告API（前缀 `/user-reports`）
- `api_auth.py` - 用户认证API

### 前端架构

**纯HTML+JS架构：**
- 每个`.html`文件对应一个独立页面
- `.js`文件与HTML文件同名，处理该页面逻辑
- `api-service.js` - 全局API服务，提供Mock数据回退

**TypeScript模块：**
- `frontend/src/types/careerChat.ts` - TypeChat类型定义
- `frontend/src/services/typechatProcessor.ts` - 前端预处理逻辑

---

## 数据库模型

### 核心表结构

**学科专业类：**
- `disciplines` - 学科门类（工学、理学等）
- `major_categories` - 专业类（计算机类、电子信息类等）
- `majors` - 具体专业（计算机科学与技术等）

**职业类：**
- `occupations` - 职业信息
- `career_paths` - 职业发展路径
- `major_occupations` - 专业-职业关联表

**用户类：**
- `users` - 用户账号
- `user_profiles` - 用户画像（三层模型）
- `user_conversations` - RAG对话历史
- `user_profile_logs` - 画像更新日志
- `user_career_path_recommendations` - 职业路径推荐记录

**报告类：**
- `user_reports` - 用户报告
- `report_chapters` - 报告章节
- `generation_tasks` - 生成任务
- `export_records` - 导出记录

**经历类：**
- `personal_experiences` - 个人职业经历
- `experience_shares` - 经验分享

### 用户画像三层模型

```
┌─────────────────────────────────────────────────────────────┐
│ 接口层 (Interface Layer) - 个性化输入                        │
├── holland_code: 霍兰德代码                                   │
├── mbti_type: MBTI性格类型                                    │
├── value_priorities: 价值观优先级（JSON）                     │
├── ability_assessment: 能力评估（JSON）                       │
└── constraints: 约束条件（JSON）                              │
├─────────────────────────────────────────────────────────────┤
│ 可变层 (Variable Layer) - 专业适配要素                       │
├── preferred_disciplines: 偏好学科（JSON）                    │
├── preferred_majors: 偏好专业（JSON）                         │
├── career_path_preference: 路径偏好                           │
└── practice_experiences: 实践经历（JSON）                     │
├─────────────────────────────────────────────────────────────┤
│ 核心层 (Core Layer) - 跨专业不变要素                         │
├── current_casve_stage: CASVE决策阶段                         │
├── casve_history: CASVE历史（JSON）                           │
├── universal_skills: 通用技能（JSON）                         │
└── resilience_score: 职业弹性评分                             │
└─────────────────────────────────────────────────────────────┘
```

---

## API 接口规范

### 响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 主要接口

**学科专业：**
- `GET /api/disciplines` - 获取学科门类树形结构
- `GET /api/majors` - 获取专业列表
- `GET /api/majors/{id}` - 获取专业详情
- `GET /api/majors/search?q={keyword}` - 搜索专业
- `POST /api/majors` - 创建专业

**职业：**
- `GET /api/occupations` - 获取职业列表
- `GET /api/occupations/{id}` - 获取职业详情
- `GET /api/career-paths/{occupation_id}` - 获取职业路径
- `POST /api/career-paths` - 创建职业路径

**用户画像：**
- `GET /api/user-profiles/{user_id}` - 获取用户画像
- `POST /api/user-profiles` - 创建用户画像
- `PUT /api/user-profiles/{user_id}` - 更新用户画像
- `POST /api/user-profiles/{user_id}/chat` - RAG对话
- `GET /api/user-profiles/{user_id}/completeness` - 画像完整度
- `GET /api/user-profiles/{user_id}/visualization` - 分层可视化
- `POST /api/user-profiles/{user_id}/casve/advance` - 推进CASVE阶段
- `POST /api/user-profiles/{user_id}/form-update` - 表单更新画像

**用户报告：**
- `GET /user-reports/prerequisites` - 获取报告生成条件
- `POST /user-reports` - 创建报告
- `GET /user-reports/{report_id}` - 获取报告
- `GET /user-reports` - 获取报告列表
- `POST /user-reports/{report_id}/generate` - 生成报告内容

**推荐系统：**
- `GET /api/recommendations/majors/{major_id}/occupations` - 专业推荐职业

**经历分享：**
- `GET /api/experiences` - 获取个人经历列表
- `POST /api/experiences` - 添加个人经历
- `GET /api/experiences/{id}/shares` - 获取经验分享
- `POST /api/experiences/{id}/shares` - 添加经验分享

完整API文档：`http://localhost:8000/docs`

---

## RAG 架构说明

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                          前端层                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  TypeChat 预处理器 (可选)                                │   │
│  │  - 快速意图检测（本地关键词）                             │   │
│  │  - 深度意图分析（LLM调用，可选）                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          API层                                    │
│  POST /api/user-profiles/{user_id}/chat                          │
│  - 接收 message + preprocessed(可选)                            │
│  - 优先使用DSPy服务，fallback到旧版RAG                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          DSPy服务层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ 意图分类器   │→│ 信息提取器   │→│ 动态提示词生成器     │   │
│  │ Intent      │  │ Info        │  │ Prompt Generator    │   │
│  │ Classifier  │  │ Extractor   │  └─────────────────────┘   │
│  └─────────────┘  └─────────────┘             ↓                │
│                                               ↓                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                    LLM调用                             │   │
│  └───────────────────────────────────────────────────────┘   │
│                                               ↓                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 回复优化器  →  追问生成器                              │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 降级机制

如果 DSPy 服务不可用，系统会自动回退到旧版 LazyLLM RAG 服务，确保服务可用性：

```python
# backend/app/api_user_profile.py
if DSPY_AVAILABLE:
    rag_service = get_dspy_rag_service()
else:
    rag_service = get_rag_service()  # 回退
```

---

## 代码风格指南

### Python 后端

- 遵循 PEP 8 规范
- 使用 Type Hints 进行类型注解
- 函数和类需添加文档字符串（docstring）
- 文件编码：UTF-8
- 换行符：LF（Unix风格）

**示例：**
```python
def process_message(
    user_message: str,
    user_profile: Dict[str, Any],
    conversation_history: List[Dict] = None
) -> Dict[str, Any]:
    """
    处理用户消息的完整流程
    
    Args:
        user_message: 用户原始输入
        user_profile: 当前用户画像
        conversation_history: 对话历史
        
    Returns:
        包含回复、提取信息、意图等的字典
    """
    ...
```

### JavaScript 前端

- 使用 ES6+ 语法
- 变量使用 `const` / `let`，避免 `var`
- 异步操作使用 `async/await`
- 文件编码：UTF-8

**示例：**
```javascript
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch failed:', error);
        throw error;
    }
}
```

### 注释规范

- 中文注释为主（项目主要面向中文用户）
- 关键逻辑必须添加注释
- API接口需注明入参和出参

---

## 测试

### 后端测试

```bash
# 运行API测试
cd backend
python -m pytest

# 测试DSPy服务
python -c "from app.rag_dspy import get_dspy_rag_service; print('DSPy OK')"

# 测试用户画像API
python tests/test_api.py

# 测试DSPy意图识别
python tests/test_dspy_intent.py
```

### 前端测试

```javascript
// 浏览器控制台测试TypeChat
await window.typeChatProcessor.preprocess("我喜欢编程");

// 测试API连接
await window.apiService.checkAPI();
```

### 手动测试端点

```bash
# 测试后端是否运行
curl http://localhost:8000/

# 测试RAG对话
curl -X POST http://localhost:8000/api/user-profiles/test_user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "我喜欢编程", "context": {"history": []}}'
```

---

## 数据初始化

### 学科数据初始化

项目包含14个初始化脚本，用于导入普通高等学校本科专业目录数据：

```bash
cd backend

# 批量运行所有初始化脚本
python -m app.run_all_init

# 单独运行某个学科
python -m app.init_08_engineering_a  # 工学-A
python -m app.init_10_medicine       # 医学
```

**初始化脚本清单：**

| 序号 | 文件名 | 学科门类 |
|------|--------|----------|
| 1 | `init_03_law.py` | 03 法学 |
| 2 | `init_04_education.py` | 04 教育学 |
| 3 | `init_05_literature_chinese.py` | 05 文学-中文与新闻 |
| 4 | `init_05_literature_foreign_a.py` | 05 文学-外语A |
| 5 | `init_05_literature_foreign_b.py` | 05 文学-外语B |
| 6 | `init_06_history.py` | 06 历史学 |
| 7 | `init_07_science.py` | 07 理学 |
| 8 | `init_08_engineering_a.py` | 08 工学-A |
| 9 | `init_08_engineering_b.py` | 08 工学-B |
| 10 | `init_09_agriculture.py` | 09 农学 |
| 11 | `init_10_medicine.py` | 10 医学 |
| 12 | `init_12_management.py` | 12 管理学 |
| 13 | `init_13_art.py` | 13 艺术学 |

---

## 安全注意事项

1. **API Key 保护**：`.env` 文件包含敏感 API Key，请勿提交到版本控制（已添加至 `.dockerignore`）
2. **CORS 配置**：开发环境允许所有来源（`allow_origins=["*"]`），生产环境需限制
3. **用户认证**：使用 JWT Token 进行身份验证，存储在 localStorage
4. **输入验证**：所有 API 入参都经过 Pydantic 模式验证
5. **SQL注入防护**：使用 SQLAlchemy ORM，参数化查询

---

## 故障排查

### 端口被占用

```cmd
# 查找占用8000端口的进程
netstat -ano | findstr :8000
# 结束进程
taskkill /PID <PID> /F
```

### 数据库问题

```cmd
# 检查数据库状态
cd backend
python check_db.py

# 手动创建表
python -c "from app.database import create_tables; create_tables()"
```

### 前端无法连接后端

- 检查后端服务是否运行：`curl http://localhost:8000/`
- 检查浏览器控制台是否有 CORS 错误
- 确认 `api-service.js` 中的 `baseURL` 配置正确

### DSPy服务无法启动

- 检查 `dspy-ai` 是否安装：`pip list | findstr dspy`
- 检查 API Key 是否配置：`echo %LAZYLLM_KIMI_API_KEY%`
- 查看后端启动日志中的 DSPy 初始化信息

---

## 关键配置文件

### requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
dspy-ai>=2.0.0
openai>=1.0.0
```

### docker-compose.yml
- 定义3个服务：backend（端口8000）、frontend（端口80）、database（开发用）
- 使用volume持久化data和logs目录
- 创建bridge网络连接各服务

### nginx.conf
- 提供静态文件服务
- Gzip压缩优化
- 单页应用路由处理（try_files）
- 安全头配置

---

## 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目README | `README.md` | 项目介绍和快速开始 |
| API设计 | `doc/design.md` | 后端API设计文档 |
| 交互设计 | `doc/interaction.md` | 前端交互设计 |
| RAG重构 | `RAG_REFACTOR_README.md` | RAG模块重构说明 |
| Windows开发 | `doc/WINDOWS_DEVELOPMENT.md` | Windows环境详细指南 |
| LLM配置 | `LLM_CONFIG_GUIDE.md` | API Key配置指南 |
| 用户画像设计 | `doc/user-profile-module-design.md` | 用户画像模块详细设计 |
| 职业规划Skill | `.agents/skills/Career-Planning/SKILL.md` | 三层模型理论基础 |

---

## 更新日志

- **2026-02-10**: 重写AGENTS.md，完善项目架构和配置说明
- **2026-02-08**: 更新AGENTS.md，完善项目架构文档
- **2026-02-04**: 完成RAG模块DSPy重构，添加TypeChat前端预处理
- **2026-02-03**: 用户画像模块验证完成，LazyLLM服务可用
- **2026-01-28 ~ 01-30**: 专业数据初始化、用户画像模块开发

---

**维护者**: AI Assistant  
**项目语言**: 中文  
**最后更新**: 2026-02-10
