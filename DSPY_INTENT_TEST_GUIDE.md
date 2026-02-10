# DSPy意图识别与信息抽取模块测试指南

## 修改总结

### 1. 前端修改 (user-profile.js)

**新增：轻量级TypeChat预处理器**
- 添加了 `LightweightTypeChatProcessor` 类，实现浏览器端的意图识别和实体提取
- 支持8种意图类型：interest_explore, ability_assess, value_clarify, career_advice, path_planning, casve_guidance, emotional_support, general_chat
- 支持情感状态检测：anxious, confident, curious, frustrated, neutral
- 自动提取：兴趣、能力、价值观、约束条件

**修改：启用预处理功能**
- 将 `TYPECHAT_CONFIG.enabled` 从 `false` 改为 `true`
- 替换原有的简单正则匹配为新的预处理器
- 预处理结果会自动发送到后端

### 2. 后端修改 (backend/app/rag_dspy/)

**修复：DSPy 3.x兼容性**
- 修复了 `dspy_rag_service.py` 中的导入语句（使用 `dspy.LM` 替代 `dspy.OpenAI`）
- 修复了LLM配置方式（使用 `dspy.configure(lm=lm)`）
- 修复了LLM调用方式

**模块结构：**
- `intent_classifier.py`: 意图分类和融合
- `info_extractor.py`: 结构化信息提取
- `prompt_generator.py`: 动态提示词生成
- `response_optimizer.py`: 回复优化

## 测试步骤

### 前置条件

1. 安装依赖：
```bash
.venv\Scripts\python.exe -m pip install dspy-ai openai
```

2. 设置API Key（必需）：
```powershell
$env:LAZYLLM_KIMI_API_KEY="your-api-key-here"
# 或
$env:OPENAI_API_KEY="your-api-key-here"
```

### 测试1: 验证DSPy模块加载

```bash
.venv\Scripts\python.exe test_dspy_simple.py
```

预期输出：
```
[OK] DSPy module verification completed!
DSPy available: True
LLM configured: True
```

### 测试2: 启动后端服务

```bash
# 设置API Key
$env:LAZYLLM_KIMI_API_KEY="your-key"

# 启动后端
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

查看控制台输出，确认：
```
[DSPyRAG] Initialized successfully
```

### 测试3: 前端意图识别测试

1. 打开浏览器访问 `http://localhost:8001/user-profile.html`
2. 登录后进入AI对话页面
3. 在浏览器开发者工具中打开Console
4. 发送测试消息，观察日志输出：

测试消息示例：
- "我喜欢编程和计算机" -> 应识别为 interest_explore
- "我擅长数学分析" -> 应识别为 ability_assess
- "我追求稳定的工作环境" -> 应识别为 value_clarify
- "软件工程师前景怎么样" -> 应识别为 career_advice
- "我不知道该选什么专业" -> 应识别为 casve_guidance

Console中应显示：
```
[TypeChat] Preprocessed: {intent: {...}, entities: {...}, ...}
[Chat] Quick intent: interest_explore
```

### 测试4: 后端意图识别测试

```bash
curl -X POST http://localhost:8000/api/user-profiles/test_user/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "我喜欢编程", "context": {"history": []}}'
```

预期返回包含：
```json
{
  "reply": "...",
  "intent": "interest_explore",
  "extracted_info": [...],
  "suggested_questions": [...]
}
```

### 测试5: 完整流程测试

1. 前端发送带有预处理结果的请求：
```javascript
// 在浏览器Console中测试
const testMsg = "我喜欢弹钢琴，擅长音乐创作";
typeChatProcessor.preprocess(testMsg, []).then(result => {
    console.log('预处理结果:', result);
    // 结果应包含 intent.type = "interest_explore"
    // 结果应包含 entities.interests = [{domain: "art", specific: "弹钢琴", ...}]
});
```

2. 后端应接收预处理结果并融合：
```
[API] Using DSPy RAG service for user test_user
```

## 验证要点

### 意图识别验证

| 用户输入 | 期望意图 | 验证方式 |
|---------|---------|---------|
| 我喜欢编程 | interest_explore | Console日志 + API返回 |
| 我擅长数学 | ability_assess | Console日志 + API返回 |
| 工作稳定很重要 | value_clarify | Console日志 + API返回 |
| 软件工程师怎么样 | career_advice | Console日志 + API返回 |
| 不知道该选什么 | casve_guidance | Console日志 + API返回 |
| 很焦虑很迷茫 | emotional_support | Console日志 + API返回 |

### 信息抽取验证

检查API返回的 `extracted_info` 字段是否包含：
- interests: 兴趣列表
- abilities: 能力列表  
- values: 价值观列表
- constraints: 约束条件

### 画像更新验证

检查API返回的 `profile_updates` 字段：
- 应包含建议更新的画像字段
- 前端应显示"已自动记录"提示
- 侧边栏画像应实时更新

## 故障排查

### 问题1: DSPy服务不可用

**现象：** `[DSPy] Warning: dspy-ai not installed`

**解决：**
```bash
.venv\Scripts\python.exe -m pip install dspy-ai
```

### 问题2: API Key未设置

**现象：** `[DSPyRAG] Warning: No API key found, using fallback mode`

**解决：**
```powershell
$env:LAZYLLM_KIMI_API_KEY="your-key"
```

### 问题3: 前端预处理未生效

**现象：** Console中没有 `[TypeChat] Preprocessed:` 日志

**解决：**
1. 检查浏览器Console是否有错误
2. 确认 `TYPECHAT_CONFIG.enabled = true`
3. 刷新页面重试

### 问题4: 意图识别不准确

**现象：** 意图识别结果不符合预期

**解决：**
1. 检查Console中的预处理结果
2. 验证后端是否正确接收预处理结果
3. 调整后端DSPy模块的签名定义

## 后续优化建议

1. **添加更多意图模式**：根据实际使用数据扩展关键词和模式
2. **优化实体提取**：添加更多领域特定的实体识别规则
3. **集成LLM进行深度预处理**：当用户配置了API Key时，使用LLM进行更准确的预处理
4. **添加意图置信度阈值**：低置信度时提示用户澄清
5. **收集反馈优化模型**：记录用户纠正意图的行为，用于优化

## 相关文件

- `user-profile.js`: 前端预处理器
- `backend/app/rag_dspy/dspy_rag_service.py`: DSPy服务主入口
- `backend/app/rag_dspy/modules/intent_classifier.py`: 意图分类模块
- `backend/app/rag_dspy/modules/info_extractor.py`: 信息提取模块
- `test_dspy_simple.py`: 简单验证脚本
