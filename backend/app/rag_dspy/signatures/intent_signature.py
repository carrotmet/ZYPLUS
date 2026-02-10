# -*- coding: utf-8 -*-
"""意图识别签名定义"""

import dspy


class IntentClassification(dspy.Signature):
    """
    分析用户输入的意图类型，考虑上下文和隐含意图。
    需要判断用户是在表达兴趣、评估能力、澄清价值观，
    还是寻求职业建议、规划路径、解决决策困难，或只是闲聊。
    """
    
    user_message = dspy.InputField(
        desc="用户的原始输入文本"
    )
    conversation_history = dspy.InputField(
        desc="最近5轮对话历史，格式为 [{'role': 'user'|'assistant', 'content': '...'}, ...]"
    )
    current_profile = dspy.InputField(
        desc="当前用户画像状态，包含已知的兴趣、能力、价值观等信息"
    )
    
    intent_type = dspy.OutputField(
        desc="主要意图类型，必须是以下之一: interest_explore(兴趣探索), ability_assess(能力评估), "
             "value_clarify(价值观澄清), career_advice(职业建议), path_planning(路径规划), "
             "casve_guidance(CASVE决策指导), general_chat(一般对话), emotional_support(情感支持)"
    )
    confidence = dspy.OutputField(
        desc="意图判断的置信度，0-1之间的小数"
    )
    reasoning = dspy.OutputField(
        desc="判断该意图的详细理由，解释为什么这样判断"
    )
    sub_intents = dspy.OutputField(
        desc="子意图列表，用逗号分隔，如'interest_explore.music,constraint.time'"
    )
    emotional_state = dspy.OutputField(
        desc="用户情感状态: anxious(焦虑), confident(自信), curious(好奇), frustrated(沮丧), neutral(中性)"
    )


class IntentRefinement(dspy.Signature):
    """
    结合前端TypeChat预处理结果，优化意图判断。
    当前端已经提供了初步意图分析时，使用此签名进行综合判断。
    """
    
    user_message = dspy.InputField(desc="用户原始输入")
    frontend_intent = dspy.InputField(desc="前端TypeChat识别的意图")
    backend_analysis = dspy.InputField(desc="后端初步分析结果")
    
    final_intent = dspy.OutputField(desc="最终确定的意图类型")
    final_confidence = dspy.OutputField(desc="最终置信度")
    merge_reasoning = dspy.OutputField(desc="融合前后端判断的理由")
