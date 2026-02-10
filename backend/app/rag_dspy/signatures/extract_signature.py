# -*- coding: utf-8 -*-
"""结构化信息提取签名定义"""

import dspy


class StructuredInfoExtraction(dspy.Signature):
    """
    从用户输入中提取结构化信息，包括显式和隐式信息。
    显式信息是用户直接陈述的，隐式信息需要从语境中推断。
    """
    
    user_message = dspy.InputField(
        desc="用户的原始输入文本"
    )
    intent_type = dspy.InputField(
        desc="已识别的意图类型"
    )
    profile_context = dspy.InputField(
        desc="当前已知的用户画像信息，用于避免重复提取"
    )
    conversation_context = dspy.InputField(
        desc="对话上下文，帮助理解隐含信息"
    )
    
    # 兴趣相关信息
    interests = dspy.OutputField(
        desc="兴趣列表，JSON格式。每个兴趣包含: domain(领域，如'音乐'), "
             "specific(具体描述，如'古典音乐'), sentiment(情感:positive/negative/neutral), "
             "constraints(限制条件列表，如['没时间练习'])"
    )
    
    # 能力相关信息
    abilities = dspy.OutputField(
        desc="能力列表，JSON格式。每个能力包含: skill(技能名称), "
             "level(水平:beginner/intermediate/advanced), evidence(证据原文)"
    )
    
    # 价值观
    values = dspy.OutputField(
        desc="价值观关键词列表，用逗号分隔，如'成就感,自由,创新'"
    )
    
    # 约束条件
    constraints = dspy.OutputField(
        desc="约束条件列表，JSON格式。每个约束包含: type(类型:time/resource/skill/other), "
             "description(描述)"
    )
    
    # 职业相关信息
    career_hints = dspy.OutputField(
        desc="职业偏好线索，JSON格式。包含: preferred_industries(偏好行业), "
             "preferred_roles(偏好角色), avoided_things(回避的事物)"
    )
    
    # 更新建议
    profile_updates = dspy.OutputField(
        desc="建议更新的画像字段，JSON格式，如{'holland_code': 'RIA', 'mbti_type': 'INTJ'}"
    )
    
    # 提取置信度
    extraction_confidence = dspy.OutputField(
        desc="信息提取的整体置信度，0-1之间"
    )


class ContextUnderstanding(dspy.Signature):
    """
    理解对话上下文，识别话题转换和深层含义。
    """
    
    current_message = dspy.InputField(desc="当前用户消息")
    previous_messages = dspy.InputField(desc="之前的多轮对话")
    
    topic_transition = dspy.OutputField(
        desc="话题转换类型: continuation(延续), shift(转移), return(回归之前话题), new(全新话题)"
    )
    implicit_needs = dspy.OutputField(
        desc="识别出的隐含需求，如'希望得到认可','需要具体建议'等"
    )
    suggested_response_tone = dspy.OutputField(
        desc="建议的回复语气: encouraging(鼓励型), exploratory(探索型), directive(指导型), "
             "empathetic(共情型)"
    )
