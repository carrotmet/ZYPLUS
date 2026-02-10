# -*- coding: utf-8 -*-
"""提示词生成和回复优化签名定义"""

import dspy


class DynamicPromptGeneration(dspy.Signature):
    """
    根据上下文生成优化的LLM提示词。
    提示词需要个性化、上下文感知，并避免重复和模板化。
    """
    
    user_message = dspy.InputField(desc="用户原始输入")
    intent_info = dspy.InputField(desc="意图分析结果，包含intent_type, confidence, reasoning")
    extracted_info = dspy.InputField(desc="提取的结构化信息")
    profile_summary = dspy.InputField(desc="用户画像摘要")
    conversation_stage = dspy.InputField(
        desc="对话阶段: initial(初始), exploring(探索中), deepening(深入), concluding(收尾)"
    )
    previous_responses = dspy.InputField(desc="之前几轮的AI回复，用于避免重复")
    
    system_prompt = dspy.OutputField(
        desc="系统级提示词，定义AI角色和基本行为准则"
    )
    
    user_context = dspy.OutputField(
        desc="注入的用户上下文，包含画像信息和提取的新信息"
    )
    
    response_strategy = dspy.OutputField(
        desc="回复策略: ask_clarify(请求澄清), explore_deeper(深入探索), "
             "provide_info(提供信息), offer_suggestion(提供建议), acknowledge(认可)"
    )
    
    key_points_to_address = dspy.OutputField(
        desc="回复需要涵盖的关键点列表"
    )
    
    suggested_questions = dspy.OutputField(
        desc="2-3个建议追问，用换行分隔"
    )
    
    anti_repetition_guidelines = dspy.OutputField(
        desc="避免重复的指导原则，如'不要重复之前说过的内容'"
    )


class ResponseOptimization(dspy.Signature):
    """
    优化LLM生成的回复，去除重复内容，增强个性化。
    """
    
    raw_response = dspy.InputField(desc="LLM原始回复")
    user_message = dspy.InputField(desc="用户输入")
    conversation_history = dspy.InputField(desc="对话历史")
    extracted_info = dspy.InputField(desc="提取的结构化信息")
    
    optimized_response = dspy.OutputField(desc="优化后的最终回复")
    
    changes_made = dspy.OutputField(
        desc="所做的修改，如'移除了重复的开场白','增加了对古典音乐的具体回应'"
    )
    
    repetition_detected = dspy.OutputField(
        desc="检测到的重复内容"
    )
    
    personalization_added = dspy.OutputField(
        desc="增加的个性化内容"
    )


class FollowUpQuestionGeneration(dspy.Signature):
    """
    生成与上下文高度相关的追问。
    追问需要具体、开放，引导用户深入思考。
    """
    
    user_message = dspy.InputField(desc="用户消息")
    extracted_info = dspy.InputField(desc="提取的信息")
    conversation_stage = dspy.InputField(desc="对话阶段")
    asked_questions = dspy.InputField(desc="已经问过的问题列表，避免重复")
    
    question_1 = dspy.OutputField(
        desc="第一个追问，针对具体细节"
    )
    question_2 = dspy.OutputField(
        desc="第二个追问，引导深入思考"
    )
    question_3 = dspy.OutputField(
        desc="第三个追问（可选），探索关联话题"
    )
    
    questions_rationale = dspy.OutputField(
        desc="生成这些问题的理由"
    )
