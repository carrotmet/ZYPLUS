# -*- coding: utf-8 -*-
"""意图分类模块"""

import json
from typing import Dict, Any, Optional
import dspy

from ..signatures.intent_signature import IntentClassification, IntentRefinement


class IntentClassifier(dspy.Module):
    """
    多阶段意图分类器
    使用ChainOfThought进行推理，输出详细的意图分析
    """
    
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(IntentClassification)
    
    def forward(self,
                user_message: str,
                conversation_history: list,
                current_profile: dict) -> Dict[str, Any]:
        """
        执行意图分类
        
        Args:
            user_message: 用户原始消息
            conversation_history: 对话历史列表
            current_profile: 当前用户画像
            
        Returns:
            包含intent_type, confidence, reasoning, sub_intents, emotional_state的字典
        """
        # 格式化输入
        history_str = self._format_history(conversation_history)
        profile_str = self._format_profile(current_profile)
        
        # 执行分类
        result = self.classify(
            user_message=user_message,
            conversation_history=history_str,
            current_profile=profile_str
        )
        
        # 解析子意图
        sub_intents = []
        if result.sub_intents:
            sub_intents = [s.strip() for s in result.sub_intents.split(',')]
        
        return {
            'intent_type': result.intent_type,
            'confidence': float(result.confidence) if result.confidence else 0.5,
            'reasoning': result.reasoning,
            'sub_intents': sub_intents,
            'emotional_state': result.emotional_state or 'neutral'
        }
    
    def _format_history(self, history: list) -> str:
        """格式化对话历史"""
        if not history:
            return "（新对话）"
        
        # 只取最近5轮
        recent = history[-5:]
        formatted = []
        for item in recent:
            role = "用户" if item.get('role') == 'user' else "助手"
            content = item.get('content', '')
            # 截断过长的内容
            if len(content) > 100:
                content = content[:100] + "..."
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _format_profile(self, profile: dict) -> str:
        """格式化用户画像"""
        if not profile:
            return "（新用户，暂无画像）"
        
        parts = []
        if profile.get('holland_code'):
            parts.append(f"霍兰德代码: {profile['holland_code']}")
        if profile.get('mbti_type'):
            parts.append(f"MBTI: {profile['mbti_type']}")
        if profile.get('career_path_preference'):
            parts.append(f"路径偏好: {profile['career_path_preference']}")
        if profile.get('value_priorities'):
            values = profile['value_priorities']
            if isinstance(values, list):
                parts.append(f"价值观: {', '.join(values[:3])}")
        
        return "; ".join(parts) if parts else "（画像信息较少）"


class IntentMerger(dspy.Module):
    """
    意图融合器
    结合前端TypeChat和后端DSPy的意图分析结果
    """
    
    def __init__(self):
        super().__init__()
        self.merge = dspy.ChainOfThought(IntentRefinement)
    
    def forward(self,
                user_message: str,
                frontend_intent: Optional[dict],
                backend_intent: dict) -> Dict[str, Any]:
        """
        融合前后端意图分析结果
        
        Args:
            user_message: 用户消息
            frontend_intent: 前端TypeChat结果（可能为None）
            backend_intent: 后端DSPy结果
            
        Returns:
            融合后的最终意图
        """
        if not frontend_intent:
            # 没有前端结果，直接使用后端
            return backend_intent
        
        # 格式化前端意图
        frontend_str = json.dumps(frontend_intent, ensure_ascii=False)
        backend_str = json.dumps(backend_intent, ensure_ascii=False)
        
        # 执行融合
        result = self.merge(
            user_message=user_message,
            frontend_intent=frontend_str,
            backend_analysis=backend_str
        )
        
        return {
            'intent_type': result.final_intent,
            'confidence': float(result.final_confidence) if result.final_confidence else 0.5,
            'reasoning': result.merge_reasoning,
            'sub_intents': backend_intent.get('sub_intents', []),
            'emotional_state': backend_intent.get('emotional_state', 'neutral'),
            'merged': True
        }
