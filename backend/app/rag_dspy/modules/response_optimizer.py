# -*- coding: utf-8 -*-
"""回复优化模块"""

from typing import Dict, Any, List
import dspy

from ..signatures.generate_signature import ResponseOptimization, FollowUpQuestionGeneration


class ResponseOptimizer(dspy.Module):
    """
    回复优化器
    检测并移除重复内容，增强个性化
    """
    
    def __init__(self):
        super().__init__()
        self.optimize = dspy.ChainOfThought(ResponseOptimization)
    
    def forward(self,
                raw_response: str,
                user_message: str,
                conversation_history: list,
                extracted_info: dict) -> Dict[str, Any]:
        """
        优化LLM生成的回复
        
        Args:
            raw_response: LLM原始回复
            user_message: 用户消息
            conversation_history: 对话历史
            extracted_info: 提取的信息
            
        Returns:
            优化后的回复和修改说明
        """
        history_str = self._format_history(conversation_history)
        extract_str = self._format_extracted(extracted_info)
        
        result = self.optimize(
            raw_response=raw_response,
            user_message=user_message,
            conversation_history=history_str,
            extracted_info=extract_str
        )
        
        return {
            'optimized_response': result.optimized_response,
            'changes': result.changes_made,
            'repetition_detected': result.repetition_detected,
            'personalization': result.personalization_added
        }
    
    def _format_history(self, history: list) -> str:
        """格式化历史"""
        if not history:
            return "（无）"
        
        # 只取AI的回复
        ai_responses = [h for h in history if h.get('role') == 'assistant'][-3:]
        return "\n".join([f"AI: {h.get('content', '')[:100]}" for h in ai_responses])
    
    def _format_extracted(self, extracted: dict) -> str:
        """格式化提取的信息"""
        parts = []
        if extracted.get('interests'):
            parts.append(f"兴趣: {extracted['interests']}")
        if extracted.get('values'):
            parts.append(f"价值观: {extracted['values']}")
        return "; ".join(parts) if parts else "（无）"


class QuestionGenerator(dspy.Module):
    """
    追问生成器
    生成与上下文高度相关的追问
    """
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(FollowUpQuestionGeneration)
    
    def forward(self,
                user_message: str,
                extracted_info: dict,
                conversation_stage: str,
                asked_questions: list = None) -> List[str]:
        """
        生成追问
        
        Args:
            user_message: 用户消息
            extracted_info: 提取的信息
            conversation_stage: 对话阶段
            asked_questions: 已经问过的问题（避免重复）
            
        Returns:
            建议问题列表
        """
        extract_str = self._format_extracted(extracted_info)
        asked_str = "\n".join(asked_questions[-10:]) if asked_questions else "（无）"
        
        result = self.generate(
            user_message=user_message,
            extracted_info=extract_str,
            conversation_stage=conversation_stage,
            asked_questions=asked_str
        )
        
        questions = []
        for q in [result.question_1, result.question_2, result.question_3]:
            if q and q.strip():
                questions.append(q.strip())
        
        return questions[:2]  # 最多返回2个
    
    def _format_extracted(self, extracted: dict) -> str:
        """格式化提取的信息"""
        parts = []
        
        if extracted.get('interests'):
            interests = extracted['interests']
            if isinstance(interests, list) and interests:
                for i in interests[:2]:
                    domain = i.get('domain', '') if isinstance(i, dict) else str(i)
                    specific = i.get('specific', '') if isinstance(i, dict) else ''
                    parts.append(f"{domain}/{specific}")
        
        if extracted.get('constraints'):
            constraints = extracted['constraints']
            if isinstance(constraints, list):
                parts.append(f"约束: {len(constraints)}项")
        
        return "; ".join(parts) if parts else "（未提取到具体信息）"
