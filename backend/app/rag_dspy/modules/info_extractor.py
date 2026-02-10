# -*- coding: utf-8 -*-
"""结构化信息提取模块"""

import json
from typing import Dict, Any, List
import dspy

from ..signatures.extract_signature import StructuredInfoExtraction, ContextUnderstanding


class StructuredInfoExtractor(dspy.Module):
    """
    结构化信息提取器
    从用户输入中提取兴趣、能力、价值观、约束等信息
    """
    
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(StructuredInfoExtraction)
    
    def forward(self,
                user_message: str,
                intent_type: str,
                profile_context: dict,
                conversation_context: list = None) -> Dict[str, Any]:
        """
        执行信息提取
        
        Args:
            user_message: 用户消息
            intent_type: 意图类型
            profile_context: 当前画像
            conversation_context: 对话上下文
            
        Returns:
            提取的结构化信息
        """
        # 格式化输入
        profile_str = self._format_profile(profile_context)
        conv_str = self._format_conversation(conversation_context or [])
        
        # 执行提取
        result = self.extract(
            user_message=user_message,
            intent_type=intent_type,
            profile_context=profile_str,
            conversation_context=conv_str
        )
        
        # 解析JSON字段
        interests = self._parse_json(result.interests, [])
        abilities = self._parse_json(result.abilities, [])
        constraints = self._parse_json(result.constraints, [])
        career_hints = self._parse_json(result.career_hints, {})
        profile_updates = self._parse_json(result.profile_updates, {})
        
        # 解析价值观
        values = []
        if result.values:
            values = [v.strip() for v in result.values.split(',')]
        
        return {
            'interests': interests,
            'abilities': abilities,
            'values': values,
            'constraints': constraints,
            'career_hints': career_hints,
            'profile_updates': profile_updates,
            'confidence': float(result.extraction_confidence) if result.extraction_confidence else 0.5
        }
    
    def _format_profile(self, profile: dict) -> str:
        """格式化画像"""
        if not profile:
            return "（新用户）"
        
        known_fields = []
        empty_fields = []
        
        fields_map = {
            'holland_code': '霍兰德代码',
            'mbti_type': 'MBTI类型',
            'value_priorities': '价值观',
            'ability_assessment': '能力评估',
            'career_path_preference': '路径偏好',
            'practice_experiences': '实践经历'
        }
        
        for field, label in fields_map.items():
            if profile.get(field):
                known_fields.append(label)
            else:
                empty_fields.append(label)
        
        result = []
        if known_fields:
            result.append(f"已知: {', '.join(known_fields)}")
        if empty_fields:
            result.append(f"待补充: {', '.join(empty_fields[:3])}")
        
        return "; ".join(result) if result else "（画像信息较少）"
    
    def _format_conversation(self, history: list) -> str:
        """格式化对话上下文"""
        if not history:
            return "（当前对话）"
        
        # 取最近3轮
        recent = history[-3:]
        return "\n".join([f"{'用户' if h.get('role') == 'user' else 'AI'}: {h.get('content', '')[:50]}" 
                         for h in recent])
    
    def _parse_json(self, text: str, default: Any) -> Any:
        """安全解析JSON"""
        if not text:
            return default
        try:
            return json.loads(text)
        except:
            # 尝试修复常见的JSON格式问题
            try:
                # 单引号改双引号
                fixed = text.replace("'", '"')
                return json.loads(fixed)
            except:
                return default


class ContextAnalyzer(dspy.Module):
    """
    上下文分析器
    分析话题转换、识别隐含需求
    """
    
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(ContextUnderstanding)
    
    def forward(self,
                current_message: str,
                previous_messages: list) -> Dict[str, Any]:
        """
        分析对话上下文
        
        Args:
            current_message: 当前消息
            previous_messages: 之前的消息
            
        Returns:
            上下文分析结果
        """
        prev_str = self._format_previous(previous_messages[-3:] if previous_messages else [])
        
        result = self.analyze(
            current_message=current_message,
            previous_messages=prev_str
        )
        
        return {
            'topic_transition': result.topic_transition,
            'implicit_needs': result.implicit_needs,
            'suggested_tone': result.suggested_response_tone
        }
    
    def _format_previous(self, messages: list) -> str:
        """格式化历史消息"""
        if not messages:
            return "（无）"
        return "\n".join([f"{'用户' if m.get('role') == 'user' else 'AI'}: {m.get('content', '')[:80]}" 
                         for m in messages])
