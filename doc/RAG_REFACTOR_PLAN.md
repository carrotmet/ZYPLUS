# RAG模块重构方案：引入 TypeChat + DSPy

## 一、现状问题分析

### 1.1 核心问题（基于生产数据）

从 `user_conversations` 表数据分析，当前系统存在以下系统性问题：

#### 问题1：意图识别不准确
```
用户: "我日常没时间练习唱歌"  →  识别为: general_chat (错误)
正确意图: interest_explore (兴趣探索) 或 ability_assess (能力评估)
```

**根因分析**:
- 当前基于关键词匹配的意图识别过于简单
- 缺乏上下文语境理解
- 无法识别隐含意图（"没时间练习"暗示对唱歌有兴趣但遇到困难）

#### 问题2：提示词缺乏上下文感知
```
用户: "我喜欢古典音乐"
AI回复: "音乐是很好的表达方式！你喜欢什么类型的音乐呢？" (重复且无效)
正确回复应针对: "古典音乐" 展开（如作曲家偏好、乐器类型等）
```

**根因分析**:
- LLM prompt 缺乏对话历史上下文的深度整合
- 没有针对用户具体输入做动态提示词优化
- 建议问题与当前话题关联度低

#### 问题3：结构化信息提取粒度粗
- 只能提取显式信息（如"我喜欢羽毛球"→提取"羽毛球"）
- 无法提取隐式信息（如"没时间练习"→时间管理能力差、兴趣与现实的冲突）
- 缺乏信息置信度和多轮累积机制

---

## 二、技术方案概述

### 2.1 选型理由

| 框架 | 职责 | 选型理由 |
|------|------|----------|
| **TypeChat** | 前端结构化输出 | 1. TypeScript/JavaScript原生支持<br>2. 将自然语言转为结构化类型<br>3. 前端预处理减轻后端压力<br>4. 提供运行时类型安全 |
| **DSPy** | 后端提示词优化 | 1. 程序化Prompt工程<br>2. 自动提示词优化（BootstrapFewShot）<br>3. 模块化LLM调用链<br>4. 支持多阶段推理（意图→提取→回复） |

### 2.2 架构目标

```
用户输入
    ↓
[前端: TypeChat] 预处理 → 结构化意图对象
    ↓
[后端: DSPy] 多阶段处理
    ├─ 阶段1: 意图分类器 (IntentClassifier)
    ├─ 阶段2: 信息提取器 (InfoExtractor)  
    ├─ 阶段3: 提示词生成器 (PromptGenerator)
    └─ 阶段4: 回复优化器 (ResponseOptimizer)
    ↓
LLM调用 → 个性化回复
    ↓
结构化存储 → user_profiles / user_conversations
```

---

## 三、详细设计

### 3.1 前端层：TypeChat 设计

#### 3.1.1 安装与配置

```bash
# 前端安装 TypeChat
npm install typechat
# 或使用CDN
<script src="https://cdn.jsdelivr.net/npm/typechat@0.0.10/dist/index.js"></script>
```

#### 3.1.2 Schema 定义

创建 `frontend/src/types/careerChat.ts`:

```typescript
// 意图类型定义
export interface Intent {
    type: 'interest_explore' | 'ability_assess' | 'value_clarify' 
          | 'career_advice' | 'path_planning' | 'casve_guidance' 
          | 'general_chat' | 'emotional_support';
    confidence: number;  // 0-1
    subType?: string;    // 子类型，如 interest_explore.music
    contextSignals: string[];  // 上下文信号
}

// 实体提取定义
export interface ExtractedEntities {
    interests: Array<{
        domain: string;      // 领域，如 "音乐"
        specific: string;    // 具体，如 "古典音乐"
        sentiment: 'positive' | 'negative' | 'neutral';
        constraints?: string[];  // 限制条件，如 ["没时间"]
    }>;
    abilities: Array<{
        skill: string;
        level: 'beginner' | 'intermediate' | 'advanced';
        evidence: string;    // 证据原文
    }>;
    values: string[];
    constraints: Array<{
        type: 'time' | 'resource' | 'skill' | 'other';
        description: string;
    }>;
}

// 预处理结果
export interface PreprocessedInput {
    rawText: string;
    cleanedText: string;
    intent: Intent;
    entities: ExtractedEntities;
    contextSummary: string;  // 上下文摘要
    suggestedApproach: string;  // 建议处理方式
}
```

#### 3.1.3 TypeChat 转换器

```typescript
// frontend/src/services/typechatProcessor.ts

import { createLanguageModel, createJsonTranslator } from 'typechat';
import { PreprocessedInput } from '../types/careerChat';

// 使用轻量级本地模型或云端小模型做预处理
const model = createLanguageModel({
    apiKey: 'your-api-key',
    model: 'gpt-3.5-turbo',  // 或更小的模型
    temperature: 0.2  // 低温度确保输出稳定
});

const schema = `
interface Intent {
    type: "interest_explore" | "ability_assess" | "value_clarify" | 
          "career_advice" | "path_planning" | "casve_guidance" | 
          "general_chat" | "emotional_support";
    confidence: number;
    subType?: string;
    contextSignals: string[];
}

interface ExtractedEntities {
    interests: Array<{
        domain: string;
        specific: string;
        sentiment: "positive" | "negative" | "neutral";
        constraints?: string[];
    }>;
    constraints: Array<{
        type: "time" | "resource" | "skill" | "other";
        description: string;
    }>;
}

interface PreprocessedInput {
    rawText: string;
    intent: Intent;
    entities: ExtractedEntities;
    contextSummary: string;
}
`;

const translator = createJsonTranslator<PreprocessedInput>(model, schema, 'PreprocessedInput');

export async function preprocessUserInput(
    rawText: string, 
    conversationHistory: any[]
): Promise<PreprocessedInput> {
    
    const prompt = `
分析用户的职业规划咨询输入，提取结构化信息。

对话历史:
${formatHistory(conversationHistory)}

用户输入: "${rawText}"

请分析:
1. 主要意图类型（考虑上下文语境）
2. 提到的兴趣领域及具体描述
3. 隐含的约束条件（如时间、资源限制）
4. 情感倾向（积极/消极/中性）
`;

    const result = await translator.translate(prompt);
    return result.data;
}
```

#### 3.1.4 前端集成

```typescript
// user-profile.js 修改

async function sendMessage() {
    const message = getInputValue();
    
    // Step 1: TypeChat 前端预处理
    const preprocessed = await preprocessUserInput(message, state.chatHistory);
    console.log('[TypeChat] Preprocessed:', preprocessed);
    
    // Step 2: 发送到后端（携带结构化信息）
    const response = await fetch(`${CONFIG.API_BASE_URL}/user-profiles/${CONFIG.USER_ID}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            preprocessed: preprocessed,  // TypeChat处理结果
            context: { history: state.chatHistory }
        })
    });
    
    // ...
}
```

---

### 3.2 后端层：DSPy 设计

#### 3.2.1 安装配置

```bash
pip install dspy-ai
```

#### 3.2.2 模块架构

```
backend/app/rag_dspy/
├── __init__.py
├── modules/
│   ├── __init__.py
│   ├── intent_classifier.py      # 意图分类模块
│   ├── info_extractor.py         # 信息提取模块
│   ├── prompt_generator.py       # 提示词生成模块
│   └── response_optimizer.py     # 回复优化模块
├── signatures/
│   ├── __init__.py
│   ├── intent_signature.py       # 签名定义
│   ├── extract_signature.py
│   └── generate_signature.py
├── optimizers/
│   ├── __init__.py
│   └── bootstrap_optimizer.py    # 自动优化器
├── examples/
│   └── training_examples.json    # 训练样本
└── dspy_rag_service.py           # 主服务入口
```

#### 3.2.3 DSPy Signatures 定义

```python
# backend/app/rag_dspy/signatures/intent_signature.py

import dspy

class IntentClassification(dspy.Signature):
    """分析用户输入的意图类型，考虑上下文和隐含意图"""
    
    user_message = dspy.InputField(desc="用户原始输入")
    conversation_history = dspy.InputField(desc="对话历史JSON")
    current_profile = dspy.InputField(desc="当前用户画像状态")
    
    intent_type = dspy.OutputField(
        desc="意图类型: interest_explore/ability_assess/value_clarify/career_advice/path_planning/casve_guidance/general_chat/emotional_support"
    )
    confidence = dspy.OutputField(desc="置信度 0-1")
    reasoning = dspy.OutputField(desc="判断理由")
    sub_intents = dspy.OutputField(desc="子意图列表，如['interest_explore.music', 'constraint.time']")


class StructuredInfoExtraction(dspy.Signature):
    """从用户输入中提取结构化信息，包括显式和隐式信息"""
    
    user_message = dspy.InputField(desc="用户原始输入")
    intent_type = dspy.InputField(desc="已识别的意图类型")
    profile_context = dspy.InputField(desc="当前画像上下文")
    
    interests = dspy.OutputField(desc="兴趣列表，每项包含domain, specific, sentiment, constraints")
    abilities = dspy.OutputField(desc="能力列表，每项包含skill, level, evidence")
    values = dspy.OutputField(desc="价值观关键词列表")
    constraints = dspy.OutputField(desc="约束条件列表，每项包含type, description")
    emotional_state = dspy.OutputField(desc="情感状态: anxious/confident/curious/frustrated/neutral")
    update_suggestions = dspy.OutputField(desc="建议更新的画像字段")


class DynamicPromptGeneration(dspy.Signature):
    """根据上下文生成优化的LLM提示词"""
    
    user_message = dspy.InputField(desc="用户输入")
    intent_info = dspy.InputField(desc="意图分析结果")
    extracted_info = dspy.InputField(desc="提取的结构化信息")
    profile_summary = dspy.InputField(desc="用户画像摘要")
    conversation_stage = dspy.InputField(desc="对话阶段: initial/exploring/deepening/concluding")
    
    system_prompt = dspy.OutputField(desc="系统级提示词")
    user_context = dspy.OutputField(desc="用户上下文注入")
    response_guidelines = dspy.OutputField(desc="回复指导原则")
    suggested_questions = dspy.OutputField(desc="2-3个建议追问")


class ResponseOptimization(dspy.Signature):
    """优化LLM生成的回复"""
    
    raw_response = dspy.InputField(desc="LLM原始回复")
    user_message = dspy.InputField(desc="用户输入")
    conversation_history = dspy.InputField(desc="对话历史")
    
    optimized_response = dspy.OutputField(desc="优化后的回复")
    removed_redundancy = dspy.OutputField(desc="移除的重复内容")
    added_context = dspy.OutputField(desc="增加的上下文关联")
    tone_adjustment = dspy.OutputField(desc="语气调整说明")
```

#### 3.2.4 DSPy Modules 实现

```python
# backend/app/rag_dspy/modules/intent_classifier.py

import dspy
from typing import Dict, Any

class IntentClassifier(dspy.Module):
    """多阶段意图分类器"""
    
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(IntentClassification)
        
    def forward(self, 
                user_message: str, 
                conversation_history: list,
                current_profile: dict) -> Dict[str, Any]:
        
        # 使用CoT进行意图分类
        result = self.classify(
            user_message=user_message,
            conversation_history=str(conversation_history[-5:]),  # 最近5轮
            current_profile=str(current_profile)
        )
        
        return {
            'intent_type': result.intent_type,
            'confidence': float(result.confidence),
            'reasoning': result.reasoning,
            'sub_intents': result.sub_intents.split(',') if result.sub_intents else []
        }


# backend/app/rag_dspy/modules/info_extractor.py

class StructuredInfoExtractor(dspy.Module):
    """结构化信息提取器"""
    
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(StructuredInfoExtraction)
        
    def forward(self, 
                user_message: str,
                intent_type: str,
                profile_context: dict) -> Dict[str, Any]:
        
        result = self.extract(
            user_message=user_message,
            intent_type=intent_type,
            profile_context=str(profile_context)
        )
        
        # 解析结构化输出
        import json
        try:
            interests = json.loads(result.interests) if result.interests else []
        except:
            interests = []
            
        return {
            'interests': interests,
            'abilities': result.abilities,
            'values': result.values.split(',') if result.values else [],
            'constraints': result.constraints,
            'emotional_state': result.emotional_state,
            'update_suggestions': result.update_suggestions
        }


# backend/app/rag_dspy/modules/prompt_generator.py

class ContextualPromptGenerator(dspy.Module):
    """上下文感知提示词生成器"""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(DynamicPromptGeneration)
        
    def forward(self,
                user_message: str,
                intent_info: dict,
                extracted_info: dict,
                profile_summary: str,
                conversation_stage: str) -> Dict[str, Any]:
        
        result = self.generate(
            user_message=user_message,
            intent_info=str(intent_info),
            extracted_info=str(extracted_info),
            profile_summary=profile_summary,
            conversation_stage=conversation_stage
        )
        
        return {
            'system_prompt': result.system_prompt,
            'user_context': result.user_context,
            'guidelines': result.response_guidelines,
            'suggested_questions': result.suggested_questions.split('\n')[:3]
        }
```

#### 3.2.5 主服务集成

```python
# backend/app/rag_dspy/dspy_rag_service.py

import dspy
from typing import Dict, Any, List

class DSPyCareerRAGService:
    """基于DSPy的职业规划RAG服务"""
    
    def __init__(self):
        # 配置LLM
        self.lm = dspy.OpenAI(
            model='gpt-3.5-turbo',
            api_key=os.environ.get('OPENAI_API_KEY'),
            temperature=0.7
        )
        dspy.settings.configure(lm=self.lm)
        
        # 初始化模块
        self.intent_classifier = IntentClassifier()
        self.info_extractor = StructuredInfoExtractor()
        self.prompt_generator = ContextualPromptGenerator()
        
        # 加载优化后的提示词（如果有）
        self._load_optimized_prompts()
        
    def process_message(self,
                       user_message: str,
                       user_profile: Dict[str, Any],
                       conversation_history: List[Dict] = None,
                       preprocessed: Dict = None) -> Dict[str, Any]:
        """
        处理用户消息的多阶段流水线
        
        Args:
            user_message: 用户原始输入
            user_profile: 当前用户画像
            conversation_history: 对话历史
            preprocessed: TypeChat前端预处理结果（可选）
        """
        
        # Stage 1: 意图分类
        if preprocessed and preprocessed.get('intent'):
            # 使用前端预处理结果作为参考
            intent_info = self._merge_intent(preprocessed['intent'], user_message)
        else:
            intent_info = self.intent_classifier(
                user_message=user_message,
                conversation_history=conversation_history or [],
                current_profile=user_profile
            )
        
        # Stage 2: 结构化信息提取
        extracted_info = self.info_extractor(
            user_message=user_message,
            intent_type=intent_info['intent_type'],
            profile_context=user_profile
        )
        
        # Stage 3: 确定对话阶段
        conversation_stage = self._determine_stage(
            conversation_history, 
            user_profile.get('completeness_score', 0)
        )
        
        # Stage 4: 生成动态提示词
        prompt_config = self.prompt_generator(
            user_message=user_message,
            intent_info=intent_info,
            extracted_info=extracted_info,
            profile_summary=self._format_profile(user_profile),
            conversation_stage=conversation_stage
        )
        
        # Stage 5: 调用LLM生成回复
        llm_response = self._call_llm(prompt_config)
        
        # Stage 6: 构建返回结果
        return {
            'reply': llm_response['content'],
            'extracted_info': self._convert_to_api_format(extracted_info),
            'intent': intent_info['intent_type'],
            'sub_intents': intent_info.get('sub_intents', []),
            'suggested_questions': prompt_config['suggested_questions'],
            'reasoning': intent_info.get('reasoning', ''),
            'conversation_stage': conversation_stage,
            'confidence': intent_info.get('confidence', 0.5)
        }
        
    def _determine_stage(self, history: List[Dict], completeness: int) -> str:
        """确定当前对话阶段"""
        if not history:
            return 'initial'
        if completeness < 30:
            return 'exploring'
        elif completeness < 70:
            return 'deepening'
        else:
            return 'concluding'
            
    def _load_optimized_prompts(self):
        """加载DSPy BootstrapFewShot优化的提示词"""
        optimizer_path = os.path.join(os.path.dirname(__file__), 'optimizers', 'compiled.json')
        if os.path.exists(optimizer_path):
            # 加载优化后的参数
            pass
            
    def optimize_with_examples(self, examples: List[Dict]):
        """
        使用示例数据优化模块
        
        运行一次即可生成优化后的提示词模板
        """
        from dspy.teleprompt import BootstrapFewShot
        
        # 转换示例格式
        trainset = [dspy.Example(**ex) for ex in examples]
        
        # 定义验证指标
        def validate(example, pred, trace=None):
            return pred.intent_type == example.intent_type
        
        # 编译优化
        teleprompter = BootstrapFewShot(metric=validate)
        compiled = teleprompter.compile(self.intent_classifier, trainset=trainset)
        
        # 保存优化结果
        compiled.save(os.path.join('optimizers', 'compiled.json'))
```

---

## 四、实施路线图

### 4.1 第一阶段：TypeChat前端集成（Week 1）

| 任务 | 负责人 | 产出物 |
|------|--------|--------|
| TypeChat环境搭建 | 前端 | package.json更新 |
| Schema类型定义 | 前端/产品 | careerChat.ts |
| 预处理器开发 | 前端 | typechatProcessor.ts |
| 前端集成测试 | 前端 | 单元测试 |

**里程碑**: 前端能正确输出结构化意图对象

### 4.2 第二阶段：DSPy后端搭建（Week 2-3）

| 任务 | 负责人 | 产出物 |
|------|--------|--------|
| DSPy环境配置 | 后端 | requirements.txt |
| Signatures定义 | 后端 | signatures/*.py |
| Modules实现 | 后端 | modules/*.py |
| 基础Pipeline联调 | 后端 | dspy_rag_service.py |

**里程碑**: 后端Pipeline能跑通基础流程

### 4.3 第三阶段：数据准备与优化（Week 4）

| 任务 | 负责人 | 产出物 |
|------|--------|--------|
| 标注数据收集 | 产品/运营 | training_examples.json |
| DSPy Bootstrap优化 | 后端 | compiled优化参数 |
| A/B测试方案 | 产品 | 测试计划 |

**标注数据格式示例**:
```json
{
    "examples": [
        {
            "user_message": "我日常没时间练习唱歌",
            "conversation_history": [],
            "intent_type": "interest_explore",
            "reasoning": "用户提到唱歌且表达了时间约束，表明有潜在兴趣但遇困难",
            "sub_intents": ["interest_explore.music", "constraint.time"],
            "interests": [{"domain": "音乐", "specific": "唱歌", "sentiment": "positive", "constraints": ["没时间"]}]
        }
    ]
}
```

### 4.4 第四阶段：灰度与迭代（Week 5-6）

- 10%流量灰度测试
- 收集反馈数据
- 持续优化Few-shot示例

---

## 五、接口兼容性说明

### 5.1 保留接口

以下接口保持完全兼容：

| 接口 | 方法 | 兼容性 |
|------|------|--------|
| `/api/user-profiles/{user_id}/chat` | POST | ✅ 完全兼容，增加可选字段 |
| `/api/user-profiles/{user_id}` | GET/PUT | ✅ 完全兼容 |
| `/api/user-profiles/{user_id}/completeness` | GET | ✅ 完全兼容 |

### 5.2 向后兼容的请求格式

```json
{
    "message": "用户输入",
    "context": {
        "history": [...]
    },
    // 新增可选字段
    "preprocessed": {
        "intent": {...},
        "entities": {...}
    }
}
```

### 5.3 向后兼容的响应格式

```json
{
    "reply": "AI回复",
    "extracted_info": [...],
    "updated_fields": [...],
    "suggested_questions": [...],
    "current_casve_stage": "...",
    // 新增字段（前端可选使用）
    "sub_intents": [...],
    "reasoning": "...",
    "confidence": 0.95
}
```

---

## 六、数据表保留说明

重构期间以下数据表**完全保留**，仅优化写入逻辑：

| 表名 | 操作 | 说明 |
|------|------|------|
| `user_profiles` | 保留 | 继续使用，可能增加字段 |
| `user_conversations` | 保留 | 继续使用 |
| `users` | 保留 | 继续使用 |
| `conversation_history` | 保留 | 如有则继续使用 |

---

## 七、风险评估与回滚方案

### 7.1 风险点

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| TypeChat前端性能问题 | 延迟增加 | 使用轻量级模型，或改为后端调用 |
| DSPy优化效果不佳 | 提升不明显 | 准备规则引擎作为fallback |
| 标注数据不足 | 优化不充分 | 先上线基础版本，持续收集数据 |

### 7.2 回滚方案

如上线后出现问题，可立即回滚到当前版本：

```bash
# Git回滚
git revert HEAD
git push origin main

# 或切换分支
git checkout feature/old-rag
```

---

## 八、成功指标

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|----------|
| 意图识别准确率 | ~60% | >85% | 人工抽样评估 |
| 回复重复率 | ~40% | <10% | 对话记录分析 |
| 用户满意度 | N/A | >4.0/5 | 反馈收集 |
| 画像完整度提升速度 | 慢 | 提升50% | 平均会话数统计 |

---

## 九、附录

### 9.1 参考资源

- TypeChat GitHub: https://github.com/microsoft/TypeChat
- DSPy Documentation: https://dspy-docs.vercel.app/
- DSPy Paper: https://arxiv.org/abs/2310.03714

### 9.2 团队分工

- **前端**: TypeChat集成、UI反馈展示
- **后端**: DSPy模块开发、Pipeline搭建
- **产品**: 标注数据准备、效果评估
- **算法**: Few-shot优化、模型选型

---

**文档版本**: v1.0  
**创建日期**: 2026-02-03  
**下次评审**: 2026-02-10
