# LLM 配置指南

## 问题说明

如果你发现AI对话出现以下情况，说明**没有配置LLM API Key**：

1. ⚠️ AI重复同样的固定回复（如"探索兴趣是职业规划的重要起点..."）
2. ⚠️ 建议问题与上下文无关（用户说"我喜欢浇花"，但建议问题是通用的"你平时喜欢做什么？"）
3. ⚠️ 回复中带有 "当前决策阶段: communication" 等模板化内容

## 配置方法

### 方法一：设置环境变量（推荐）

在Windows PowerShell中执行：

```powershell
# Kimi (推荐，国内访问稳定)
$env:LAZYLLM_KIMI_API_KEY="your_api_key_here"

# 或 DeepSeek
$env:LAZYLLM_DEEPSEEK_API_KEY="your_api_key_here"

# 或 OpenAI
$env:LAZYLLM_OPENAI_API_KEY="your_api_key_here"
```

在CMD中执行：

```cmd
set LAZYLLM_KIMI_API_KEY=your_api_key_here
```

### 方法二：创建 .env 文件

1. 复制 `backend/.env.example` 为 `backend/.env`
2. 编辑 `.env` 文件，填入你的API Key：

```
LAZYLLM_KIMI_API_KEY=sk-your-actual-api-key-here
```

### 方法三：使用 Python 加载 .env

修改 `backend/app/services/rag_service.py`，在文件开头添加：

```python
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
```

然后安装依赖：

```bash
pip install python-dotenv
```

## API Key 获取

| 服务商 | 注册地址 | 特点 |
|--------|----------|------|
| Kimi (Moonshot) | https://platform.moonshot.cn/ | 国内稳定，支持长文本 |
| DeepSeek | https://platform.deepseek.com/ | 性价比高，推理能力强 |
| OpenAI | https://platform.openai.com/ | 原版GPT，需翻墙 |

## 验证配置

配置完成后，运行测试脚本验证：

```bash
cd backend
python test_llm.py
```

如果显示以下信息，说明配置成功：

```
✓ API Key配置: ✓
✓ LLM调用: ✓
✓ RAG服务: ✓
✓ 所有测试通过！对话功能正常工作。
```

## 修复效果对比

### 配置前（Fallback模式）

用户: "我喜欢浇花"
AI: "探索兴趣是职业规划的重要起点。根据你的情况，新用户，暂无画像信息。我们可以从你喜欢做什么开始深入探讨。"
建议问题: ["你平时喜欢做什么？", "什么事情让你忘记时间？"]（与"浇花"无关）

### 配置后（LLM模式）

用户: "我喜欢浇花"
AI: "喜欢浇花说明你有耐心和细致的特质，这在园艺、植物研究、景观设计等领域都是优势。园艺相关的爱好能培养观察力和责任感，你可以考虑是否与这些职业方向相关。"
建议问题: ["你喜欢浇花多久了？", "除了浇花，你还喜欢其他园艺活动吗？"]（与"浇花"相关）

## 其他问题排查

如果配置后仍有问题，请检查：

1. **网络连接**：能否访问对应的API服务
2. **API Key有效性**：在服务商平台测试Key是否可用
3. **依赖版本**：确保LazyLLM版本 >= 0.7.0

```bash
python -c "import lazyllm; print(lazyllm.__version__)"
```
