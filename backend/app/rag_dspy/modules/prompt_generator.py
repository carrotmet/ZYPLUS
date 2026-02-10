# -*- coding: utf-8 -*-
"""提示词生成模块"""

from typing import Dict, Any, List
import dspy

from ..signatures.generate_signature import DynamicPromptGeneration


class ContextualPromptGenerator(dspy.Module):
    """
    上下文感知提示词生成器
    根据用户画像、意图、对话阶段生成个性化提示词
    """
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(DynamicPromptGeneration)
    
    def forward(self,
                user_message: str,
                intent_info: dict,
                extracted_info: dict,
                profile_summary: str,
                conversation_stage: str,
                previous_responses: list = None) -> Dict[str, Any]:
        """
        生成动态提示词
        
        Args:
            user_message: 用户消息
            intent_info: 意图信息
            extracted_info: 提取的结构化信息
            profile_summary: 画像摘要
            conversation_stage: 对话阶段
            previous_responses: 之前的AI回复（用于避免重复）
            
        Returns:
            包含system_prompt, user_context, strategy, key_points, suggested_questions
        """
        # 格式化输入
        intent_str = self._format_intent(intent_info)
        extract_str = self._format_extracted(extracted_info)
        prev_str = self._format_previous(previous_responses or [])
        
        # 生成提示词
        result = self.generate(
            user_message=user_message,
            intent_info=intent_str,
            extracted_info=extract_str,
            profile_summary=profile_summary,
            conversation_stage=conversation_stage,
            previous_responses=prev_str
        )
        
        # 解析建议问题
        questions = []
        if result.suggested_questions:
            questions = [q.strip() for q in result.suggested_questions.split('\n') if q.strip()][:3]
        
        # 解析关键点
        key_points = []
        if result.key_points_to_address:
            key_points = [p.strip() for p in result.key_points_to_address.split('\n') if p.strip()]
        
        return {
            'system_prompt': result.system_prompt,
            'user_context': result.user_context,
            'response_strategy': result.response_strategy,
            'key_points': key_points,
            'suggested_questions': questions,
            'anti_repetition': result.anti_repetition_guidelines
        }
    
    def _format_intent(self, intent_info: dict) -> str:
        """格式化意图信息"""
        parts = [
            f"意图类型: {intent_info.get('intent_type', 'unknown')}",
            f"置信度: {intent_info.get('confidence', 0.5)}",
            f"判断理由: {intent_info.get('reasoning', '')}",
            f"情感状态: {intent_info.get('emotional_state', 'neutral')}"
        ]
        if intent_info.get('sub_intents'):
            parts.append(f"子意图: {', '.join(intent_info['sub_intents'])}")
        return "\n".join(parts)
    
    def _format_extracted(self, extracted: dict) -> str:
        """格式化提取的信息"""
        parts = []
        
        if extracted.get('interests'):
            interests = extracted['interests']
            if isinstance(interests, list):
                parts.append(f"兴趣: {len(interests)}项")
                for i in interests[:2]:  # 只显示前2个
                    domain = i.get('domain', '')
                    specific = i.get('specific', '')
                    parts.append(f"  - {domain}: {specific}")
        
        if extracted.get('constraints'):
            constraints = extracted['constraints']
            if isinstance(constraints, list):
                parts.append(f"约束: {len(constraints)}项")
        
        if extracted.get('values'):
            values = extracted['values']
            if isinstance(values, list):
                parts.append(f"价值观: {', '.join(values[:3])}")
        
        return "\n".join(parts) if parts else "（未提取到新信息）"
    
    def _format_previous(self, responses: list) -> str:
        """格式化之前的回复"""
        if not responses:
            return "（无）"
        
        # 取最近3条，截断
        recent = responses[-3:]
        formatted = []
        for i, resp in enumerate(recent, 1):
            content = resp if isinstance(resp, str) else resp.get('content', '')
            if len(content) > 60:
                content = content[:60] + "..."
            formatted.append(f"[{i}] {content}")
        return "\n".join(formatted)
    
    def build_final_prompt(self, config: dict, user_message: str) -> str:
        """
        构建最终的LLM提示词
        
        Args:
            config: 提示词配置
            user_message: 用户消息
            
        Returns:
            完整的提示词字符串
        """
        parts = []
        
        # 系统提示
        if config.get('system_prompt'):
            parts.append(f"【系统指令】\n{config['system_prompt']}")
        
        # 用户上下文
        if config.get('user_context'):
            parts.append(f"\n【用户背景】\n{config['user_context']}")
        
        # 回复策略
        if config.get('response_strategy'):
            parts.append(f"\n【回复策略】\n{config['response_strategy']}")
        
        # 关键点
        if config.get('key_points'):
            points = "\n".join([f"- {p}" for p in config['key_points']])
            parts.append(f"\n【需要涵盖】\n{points}")
        
        # 防重复
        if config.get('anti_repetition'):
            parts.append(f"\n【注意】\n{config['anti_repetition']}")
        
        # 用户输入
        parts.append(f"\n【用户说】\n{user_message}")
        parts.append("\n【你的回复】")
        
        return "\n".join(parts)
