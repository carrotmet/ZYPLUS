# RAG模块重构完成说明

## 架构变更

### 新架构图

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
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      数据存储层                                   │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐     │
│  │ user_profiles│  │ user_conversations│  │ users        │     │
│  │ （保持不变）  │  │ （保持不变）       │  │ （保持不变）  │     │
│  └──────────────┘  └──────────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 文件变更清单

### 后端文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `backend/app/rag_dspy/__init__.py` | 新增 | DSPy模块入口 |
| `backend/app/rag_dspy/signatures/*.py` | 新增 | DSPy签名定义（意图/提取/生成） |
| `backend/app/rag_dspy/modules/*.py` | 新增 | DSPy模块实现 |
| `backend/app/rag_dspy/dspy_rag_service.py` | 新增 | DSPy主服务 |
| `backend/app/api_user_profile.py` | 修改 | 集成DSPy服务 |
| `backend/app/schemas_user_profile.py` | 修改 | 添加preprocessed字段 |
| `backend/requirements.txt` | 修改 | 添加dspy-ai依赖 |

### 前端文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `frontend/src/types/careerChat.ts` | 新增 | TypeScript类型定义 |
| `frontend/src/services/typechatProcessor.ts` | 新增 | TypeChat处理器 |
| `user-profile.js` | 修改 | 集成快速意图检测和TypeChat |

## 配置方法

### 1. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 或者只安装新增依赖
pip install dspy-ai openai
```

### 2. 配置API Key

**后端DSPy配置：**
```bash
# .env文件
OPENAI_API_KEY=your_openai_key
# 或
LAZYLLM_KIMI_API_KEY=your_kimi_key
```

**前端TypeChat配置：**
```javascript
// 在浏览器控制台或通过UI配置
localStorage.setItem('openai_api_key', 'your_key');
// 然后刷新页面启用TypeChat
```

### 3. 启动服务

```bash
# 开发模式
./start-dev.bat

# 后端会自动检测DSPy是否可用
# 如果不可用，自动回退到旧版RAG服务
```

## API兼容性

### 请求格式（向后兼容）

```json
{
    "message": "用户输入",
    "context": {
        "history": [...]
    },
    "preprocessed": {  // 新增，可选
        "intent": {...},
        "entities": {...}
    }
}
```

### 响应格式（向后兼容）

```json
{
    "reply": "AI回复",
    "extracted_info": [...],
    "updated_fields": [...],
    "suggested_questions": [...],
    "current_casve_stage": "...",
    "profile_updates": {...},  // 新增
    // 以下字段为DSPy新增，可选使用
    "sub_intents": [...],
    "reasoning": "...",
    "confidence": 0.95,
    "emotional_state": "neutral"
}
```

## 数据表兼容性

**所有现有数据表完全保留：**

- ✅ `user_profiles` - 用户画像主表
- ✅ `user_conversations` - 对话历史表
- ✅ `users` - 用户账号表
- ✅ 其他所有表...

**新增数据表：** 无（保持零迁移成本）

## 降级方案

如果DSPy服务出现故障，系统会自动回退到旧版RAG服务：

```python
# 自动降级逻辑
if DSPY_AVAILABLE:
    rag_service = get_dspy_rag_service()
else:
    rag_service = get_rag_service()  # 回退
```

## 测试方法

### 后端测试

```bash
cd backend
python -c "from app.rag_dspy import get_dspy_rag_service; print('DSPy OK')"
```

### 前端测试

```javascript
// 浏览器控制台
await sendMessage(); // 发送测试消息
// 观察控制台输出的意图检测结果
```

### API测试

```bash
curl -X POST http://localhost:8000/api/user-profiles/test_user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "我喜欢羽毛球", "context": {"history": []}}'
```

## 性能优化建议

1. **TypeChat异步加载** - 前端预处理不阻塞用户发送
2. **快速意图检测** - 本地关键词匹配，零延迟
3. **服务降级** - DSPy故障自动回退，保证可用性
4. **缓存机制** - 可考虑缓存常见意图的预处理结果

## 后续优化方向

1. **BootstrapFewShot优化**
   - 收集20-50条标注数据
   - 运行DSPy自动优化提示词

2. **多模型融合**
   - 前端TypeChat用轻量级模型
   - 后端DSPy用强力模型

3. **A/B测试**
   - 对比新旧RAG效果
   - 基于数据持续优化

## 注意事项

1. **API Key安全** - 前端TypeChat需要用户自己配置API key
2. **网络延迟** - TypeChat会增加一次LLM调用，可选择关闭
3. **错误处理** - 所有模块都有fallback，保证服务可用

---

**重构完成时间**: 2026-02-04  
**文档版本**: v1.0
