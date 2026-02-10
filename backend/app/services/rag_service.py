# -*- coding: utf-8 -*-
"""
用户画像模块 - RAG服务
集成LazyLLM进行智能对话和画像信息提取
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

# 加载 .env 文件中的环境变量
try:
    from dotenv import load_dotenv
    # 尝试从多个位置加载 .env
    env_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
        '.env',
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            print(f"[RAG] Loaded .env from: {env_path}")
            break
except ImportError:
    print("[RAG] python-dotenv not installed, .env file will not be loaded")

# LazyLLM导入
try:
    import lazyllm
    from lazyllm import OnlineChatModule, TrainableModule
    LAZYLLM_AVAILABLE = True
    print(f"[RAG] LazyLLM loaded, version: {lazyllm.__version__}")
except ImportError:
    LAZYLLM_AVAILABLE = False
    print("[RAG] Warning: LazyLLM not available, using mock implementation")

# 检查API Key是否配置
def _check_api_key_configured() -> bool:
    """检查是否有配置任何LLM的API Key"""
    api_key_vars = [
        'LAZYLLM_KIMI_API_KEY',
        'LAZYLLM_DEEPSEEK_API_KEY',
        'LAZYLLM_OPENAI_API_KEY',
        'LAZYLLM_GLM_API_KEY',
        'LAZYLLM_QWEN_API_KEY',
        'LAZYLLM_DOUBAO_API_KEY',
    ]
    for var in api_key_vars:
        if os.environ.get(var):
            return True
    return False


class CareerPlanningRAGService:
    """
    职业规划RAG服务
    基于SKILL文档提供智能对话和画像信息提取
    """
    
    def __init__(self, knowledge_base_path: str = ".agents/skills/Career-Planning"):
        self.knowledge_base_path = knowledge_base_path
        self.skill_docs = self._load_skill_documents()
        self.llm = None
        self.llm_available = False
        
        # 初始化LazyLLM
        if LAZYLLM_AVAILABLE:
            if not _check_api_key_configured():
                print("[RAG] Warning: No LLM API Key configured.")
            else:
                try:
                    self.llm = OnlineChatModule()
                    self.llm_available = True
                    print("[RAG] LazyLLM OnlineChatModule initialized")
                except Exception as e:
                    print(f"[RAG] Failed to initialize LLM: {e}")

    def _load_skill_documents(self) -> Dict[str, str]:
        """加载SKILL文档作为知识库"""
        docs = {}
        files = [
            ("SKILL.md", "核心架构"),
            ("references/01-theoretical-foundations.md", "理论基础"),
            ("references/02-lifelong-learning.md", "终身学习"),
            ("references/03-career-path-selection.md", "道路选择"),
            ("references/04-career-progression.md", "路径进阶"),
            ("references/05-action-plan.md", "行动计划"),
            ("references/06-industry-trends.md", "行业趋势")
        ]
        
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        base_path = os.path.join(project_root, self.knowledge_base_path)
        
        for filename, category in files:
            filepath = os.path.join(base_path, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        docs[category] = f.read()
                except Exception as e:
                    print(f"[RAG] Error loading {filename}: {e}")
        
        return docs

    def process_message(
        self,
        user_message: str,
        user_profile: Dict[str, Any],
        conversation_history: List[Dict] = None,
        preprocessed: Dict[str, Any] = None  # 新增：兼容API接口，但旧版会忽略
    ) -> Dict[str, Any]:
        """
        处理用户消息
        返回: {
            "reply": "AI自然回复",
            "extracted_info": {提取的结构化信息},
            "intent": "意图类型",
            "suggested_questions": [建议问题],
            "profile_updates": {需要更新的画像字段}
        }
        
        注意: preprocessed参数用于兼容新的API接口，旧版服务会忽略该参数
        """
        # 1. 识别意图
        intent = self._recognize_intent(user_message)
        
        # 2. 提取结构化信息（从用户消息中）
        extracted_info = self._extract_information(user_message, intent)
        
        # 3. 生成AI回复（自然对话，不包含结构化信息）
        reply_result = self._generate_reply(
            message=user_message,
            intent=intent,
            conversation_history=conversation_history
        )
        
        return {
            "reply": reply_result["reply"],
            "extracted_info": extracted_info,
            "intent": intent,
            "suggested_questions": reply_result.get("suggested_questions", []),
            "profile_updates": extracted_info  # 提取的信息直接用于更新画像
        }

    def _recognize_intent(self, message: str) -> str:
        """识别用户意图"""
        message_lower = message.lower()
        
        intent_keywords = {
            "interest_explore": ["兴趣", "喜欢", "爱好", "热爱", "享受", "感兴趣", "想做什么", "热情"],
            "ability_assess": ["能力", "技能", "擅长", "优势", "会什么", "能做", "强", "厉害"],
            "value_clarify": ["价值", "意义", "重要", "在乎", "追求", "想要", "重视", "看重"],
            "career_advice": ["职业", "工作", "行业", "前景", "发展", "建议", "推荐", "怎么样"],
            "path_planning": ["路径", "规划", "方向", "怎么选", "怎么走", "未来", "计划"],
            "casve_guidance": ["决策", "选择", "犹豫", "纠结", "casve", "选哪个", "怎么办"]
        }
        
        scores = {intent: 0 for intent in intent_keywords}
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[intent] += 1
        
        best_intent = max(scores, key=scores.get)
        return best_intent if scores[best_intent] > 0 else "general_chat"

    def _extract_information(self, message: str, intent: str) -> Dict[str, Any]:
        """
        从消息中提取结构化信息
        宽松的提取逻辑，尽可能多地获取信息
        """
        extracted = {}
        message_upper = message.upper()
        message_lower = message.lower()
        
        # 提取霍兰德代码 (如: RIA, SEC)
        holland_match = re.search(r'\b([RIASEC]{3})\b', message_upper)
        if holland_match:
            extracted["holland_code"] = holland_match.group(1)
        
        # 提取MBTI类型 (如: INTJ, ENFP)
        mbti_match = re.search(r'\b([EI][NS][FT][JP])\b', message_upper)
        if mbti_match:
            extracted["mbti_type"] = mbti_match.group(1)
        
        # 提取职业路径偏好（宽松匹配）
        path_keywords = {
            "technical": ["技术", "工程师", "编程", "开发", "算法", "架构", "代码", "程序员"],
            "management": ["管理", "领导", "团队", "经理", "主管", "总监", "带人", "管人"],
            "professional": ["产品", "设计", "咨询", "专业", "运营", "市场", "销售"],
            "public_welfare": ["公益", "社会", "帮助", "服务", "志愿", "教育", "老师"]
        }
        for path, keywords in path_keywords.items():
            if any(kw in message_lower for kw in keywords):
                extracted["career_path_preference"] = path
                break
        
        # 提取价值观关键词
        value_keywords = {
            "成就感": ["成就感", "成就", "成功", "实现价值"],
            "稳定": ["稳定", "安稳", "安全", "踏实"],
            "创新": ["创新", "创造", "新鲜", "有趣"],
            "自由": ["自由", "灵活", "自主", "不受约束"],
            "收入": ["收入", "薪资", "工资", "钱", "待遇"],
            "平衡": ["平衡", "生活", "家庭", "健康"],
            "成长": ["成长", "学习", "进步", "提升"],
            "影响": ["影响", "改变", "贡献", "意义"],
            "帮助": ["帮助", "助人", "服务", "关怀"]
        }
        values = []
        for value_name, keywords in value_keywords.items():
            if any(kw in message for kw in keywords):
                values.append(value_name)
        if values:
            extracted["value_priorities"] = values
        
        # 提取能力关键词
        ability_keywords = {
            "逻辑思维": ["逻辑", "推理", "分析", "思考"],
            "沟通能力": ["沟通", "表达", "交流", "说服"],
            "编程能力": ["编程", "代码", "开发"],
            "设计能力": ["设计", "审美", "创意"],
            "分析能力": ["分析", "数据", "研究"],
            "创意能力": ["创意", "创新", "想法"],
            "组织能力": ["组织", "协调", "安排"],
            "领导能力": ["领导", "带领", "管理"]
        }
        abilities = {}
        for ability_name, keywords in ability_keywords.items():
            if any(kw in message for kw in keywords):
                # 默认给中等评分
                abilities[ability_name] = 6
        if abilities:
            extracted["ability_assessment"] = abilities
        
        # 提取昵称（如果用户自我介绍）
        nickname_patterns = [
            r'(?:我叫|我是|我的名字是)\s*([^，。,.]+)',
            r'(?:可以叫我)\s*([^，。,.]+)',
        ]
        for pattern in nickname_patterns:
            match = re.search(pattern, message)
            if match:
                extracted["nickname"] = match.group(1).strip()
                break
        
        # 提取兴趣爱好（从兴趣探索意图的消息中）
        if intent == "interest_explore":
            # 提取"我喜欢/热爱XXX"中的XXX
            interest_patterns = [
                r'(?:我喜欢|我热爱|我爱|我享受|我喜欢做)\s*([^，。,.]+)',
                r'(?:我的兴趣是|我的爱好是)\s*([^，。,.]+)',
            ]
            for pattern in interest_patterns:
                match = re.search(pattern, message)
                if match:
                    interest = match.group(1).strip()
                    # 存入可变层的偏好专业或实践经历
                    if "practice_experiences" not in extracted:
                        extracted["practice_experiences"] = []
                    extracted["practice_experiences"].append({
                        "type": "兴趣爱好",
                        "desc": interest
                    })
                    break
        
        return extracted

    def _generate_reply(
        self,
        message: str,
        intent: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        生成自然对话回复
        不包含任何结构化信息，只生成亲切自然的对话
        """
        
        # 使用LLM生成回复
        if self.llm_available and self.llm:
            try:
                # 简化的prompt，不要求JSON格式，让回复更自然
                history_text = ""
                if conversation_history:
                    recent = conversation_history[-3:]  # 最近3轮
                    for item in recent:
                        role = "用户" if item.get("role") == "user" else "助手"
                        history_text += f"{role}: {item.get('content', '')}\n"
                
                prompt = f"""你是一位亲切的职业规划顾问，正在与用户进行自然对话。

对话历史:
{history_text if history_text else "（新对话）"}

用户说: {message}

请用自然、亲切的语气回复，就像朋友聊天一样。不要提及任何结构化信息（如霍兰德代码、MBTI、CASVE阶段等）。回复控制在100字以内。

然后提供2个与当前话题相关的追问，帮助用户深入思考。格式:
回复: (你的自然回复)
问题1: (第一个追问)
问题2: (第二个追问)"""

                response = self.llm(prompt)
                
                # 解析回复
                reply, questions = self._parse_llm_response(response)
                
                return {
                    "reply": reply,
                    "suggested_questions": questions
                }
                
            except Exception as e:
                print(f"[RAG] LLM generation failed: {e}")
        
        # Fallback: 使用模板回复（但仍然自然）
        return self._fallback_reply(message, intent)

    def _parse_llm_response(self, response: str) -> tuple:
        """解析LLM回复，提取回复内容和建议问题"""
        response = response.strip()
        questions = []
        reply = ""
        
        # 尝试提取问题和回复
        lines = response.split('\n')
        reply_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 提取问题1
            if line.startswith('问题1:') or line.startswith('问题1：'):
                q = line.split(':', 1)[-1].strip()
                if q:
                    questions.append(q)
            # 提取问题2
            elif line.startswith('问题2:') or line.startswith('问题2：'):
                q = line.split(':', 1)[-1].strip()
                if q:
                    questions.append(q)
            # 提取回复
            elif line.startswith('回复:') or line.startswith('回复：'):
                reply = line.split(':', 1)[-1].strip()
            # 忽略其他标记行
            elif line.startswith('问题3:') or line.startswith('追问:') or line.startswith('建议:'):
                continue
            else:
                reply_lines.append(line)
        
        # 如果没有解析到回复，使用第一行或清理后的内容
        if not reply:
            if reply_lines:
                reply = reply_lines[0]
            else:
                reply = response.split('\n')[0] if response else "能多说一些吗？"
        
        # 清理回复中的常见前缀
        reply = re.sub(r'^(回复[:：]|AI[:：]|助手[:：])\s*', '', reply).strip()
        
        # 确保有建议问题
        if len(questions) < 2:
            questions = self._generate_contextual_questions(reply)
        
        return reply, questions[:2]

    def _generate_contextual_questions(self, message: str) -> List[str]:
        """根据消息内容生成上下文相关问题"""
        message_lower = message.lower()
        
        # 关键词到问题的映射
        keyword_questions = {
            "羽毛球": ["你打羽毛球多久了？", "羽毛球带给你什么收获？"],
            "篮球": ["你打什么位置？", "篮球对你意味着什么？"],
            "足球": ["你喜欢哪个位置？", "足球教会了你什么？"],
            "跑步": ["你一般跑多远？", "跑步时你在想什么？"],
            "游泳": ["你擅长哪种泳姿？", "游泳让你感觉怎么样？"],
            "健身": ["你最喜欢练哪个部位？", "健身改变了你什么？"],
            "瑜伽": ["你练瑜伽多久了？", "瑜伽给你带来了什么？"],
            "舞蹈": ["你跳什么舞种？", "舞蹈对你意味着什么？"],
            "音乐": ["你喜欢什么类型的音乐？", "会演奏乐器吗？"],
            "画画": ["你擅长什么画风？", "画画时是什么感觉？"],
            "摄影": ["你喜欢拍什么主题？", "摄影对你意味着什么？"],
            "读书": ["最近在读什么书？", "你喜欢什么类型的书？"],
            "旅行": ["最喜欢去哪里旅行？", "旅行中最难忘的经历？"],
            "游戏": ["你喜欢什么类型的游戏？", "游戏带给你什么？"],
            "编程": ["你用哪些编程语言？", "编程中最有成就感的事？"],
            "浇花": ["你喜欢什么花？", "浇花时是什么感觉？"],
            "烹饪": ["你擅长做什么菜？", "烹饪对你意味着什么？"],
        }
        
        # 检查关键词匹配
        for keyword, questions in keyword_questions.items():
            if keyword in message_lower:
                return questions
        
        # 通用追问
        return ["能多说一些吗？", "这对你意味着什么？"]

    def _fallback_reply(self, message: str, intent: str) -> Dict[str, Any]:
        """备用回复 - 自然亲切，避免重复"""
        import random
        message_lower = message.lower()
        
        # 短消息多样化处理（避免重复回复）
        short_responses = {
            "没有": [
                "没关系，我们可以从其他角度聊聊。你平时有什么放松的方式吗？",
                "了解，那我们换个话题。你对未来有什么期待吗？",
                "没关系，不是每个人都想好了。你现在最享受做的事情是什么？"
            ],
            "不能": [
                "理解，那我们可以从其他角度聊聊。最近有什么让你开心的事吗？",
                "没问题，那我们换个方向。你有什么好奇或想了解的事情吗？",
                "好的，那先不聊这个。你平时空闲时间喜欢做什么？"
            ],
            "不知道": [
                "这种感觉很正常，很多人一开始也不太确定。我们先聊聊你的日常生活？",
                "没关系，探索本身就是一个过程。有什么事情是让你感到快乐的吗？",
                "了解，那我们慢慢摸索。你能想到的最开心的时刻是什么时候？"
            ],
            "嗯": [
                "看来你在思考呢。能具体说说你在想什么吗？",
                "我在听，你继续说。",
                "理解，那我们继续深入。还有什么想分享的吗？"
            ],
            "好吧": [
                "感觉你有些犹豫，没关系。有什么让你纠结的事情吗？",
                "好的，那我们轻松一点聊。最近有什么新鲜事吗？",
                "明白，不急。我们可以慢慢聊。有什么想聊的话题吗？"
            ],
            "随便": [
                "哈哈，'随便'也是一种态度呢。那我们来聊点有趣的，你最近有什么新发现吗？",
                "了解，那我提几个方向，你看看哪个感兴趣：兴趣爱好、擅长的事、或者对未来的想象？",
                "好的，那我换个方式问：如果现在可以做任何事情，你会选择做什么？"
            ]
        }
        
        # 检查是否是短消息
        for keyword, replies in short_responses.items():
            if keyword in message_lower:
                reply = random.choice(replies)
                questions = [
                    "能具体说说吗？",
                    "为什么是这样呢？",
                    "还有其他想法吗？"
                ]
                random.shuffle(questions)
                return {"reply": reply, "suggested_questions": questions[:2]}
        
        # 根据关键词生成个性化回复
        if any(kw in message_lower for kw in ["羽毛球", "篮球", "足球", "运动"]):
            reply = "喜欢运动很棒！运动能培养很多优秀的品质。你喜欢这项运动多久了？"
            questions = ["你一般多久运动一次？", "运动带给你最大的收获是什么？"]
        elif any(kw in message_lower for kw in ["音乐", "唱歌", "乐器"]):
            reply = "音乐是很好的表达方式！你喜欢什么类型的音乐呢？"
            questions = ["你会演奏乐器吗？", "音乐对你意味着什么？"]
        elif any(kw in message_lower for kw in ["读书", "阅读", "看书"]):
            reply = "阅读是很好的习惯！你最近在读什么书？"
            questions = ["你喜欢什么类型的书？", "阅读给你带来了什么改变？"]
        elif any(kw in message_lower for kw in ["游戏", "电竞"]):
            reply = "游戏也是个很有意思的领域！你喜欢什么类型的游戏？"
            questions = ["你觉得游戏带给你什么？", "有没有想过往游戏行业发展？"]
        elif any(kw in message_lower for kw in ["编程", "代码", "开发"]):
            reply = "有技术背景很不错！你用哪些技术栈？"
            questions = ["你最擅长什么语言？", "有没有特别感兴趣的技术方向？"]
        elif intent == "interest_explore":
            reply = "听起来你对此很有热情！能多说一些吗？"
            questions = ["你是什么时候开始感兴趣的？", "这对你意味着什么？"]
        elif intent == "ability_assess":
            reply = "了解自己的优势很重要！你能举个例子吗？"
            questions = ["别人经常夸你什么？", "你觉得最自豪的能力是什么？"]
        elif intent == "career_advice":
            reply = "职业选择确实需要认真思考。你现在有什么想法吗？"
            questions = ["你最看重工作的什么方面？", "有什么感兴趣的方向吗？"]
        else:
            # 默认回复也多样化
            default_replies = [
                "明白了，能再多分享一些吗？",
                "了解，我们可以深入聊聊这个话题。",
                "好的，那我们从另一个角度看看？",
                "明白，有什么具体的例子吗？"
            ]
            reply = random.choice(default_replies)
            questions = ["能具体说说吗？", "这对你有什么特别的意义？"]
        
        return {
            "reply": reply,
            "suggested_questions": questions
        }


# 全局RAG服务实例
_rag_service = None

def get_rag_service() -> CareerPlanningRAGService:
    """获取RAG服务单例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = CareerPlanningRAGService()
    return _rag_service
