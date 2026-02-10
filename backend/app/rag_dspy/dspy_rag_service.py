# -*- coding: utf-8 -*-
"""
基于DSPy的职业规划RAG服务主入口
整合所有模块，提供统一的对话处理接口
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 尝试导入dspy
try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    print("[DSPy] Warning: dspy-ai not installed, using fallback mode")

from .modules.intent_classifier import IntentClassifier, IntentMerger
from .modules.info_extractor import StructuredInfoExtractor, ContextAnalyzer
from .modules.prompt_generator import ContextualPromptGenerator
from .modules.response_optimizer import ResponseOptimizer, QuestionGenerator


class DSPyCareerRAGService:
    """
    职业规划RAG服务
    使用DSPy进行意图识别、信息提取和提示词优化
    """
    
    def __init__(self):
        self.dspy_available = DSPY_AVAILABLE
        self.llm = None
        self.modules = {}
        
        if self.dspy_available:
            self._init_dspy()
        else:
            print("[DSPyRAG] Running in fallback mode")
    
    def _init_dspy(self):
        """初始化DSPy配置和模块"""
        try:
            # 配置LLM
            api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('LAZYLLM_KIMI_API_KEY')
            if not api_key:
                print("[DSPyRAG] Warning: No API key found, using fallback mode")
                self.dspy_available = False
                return
            
            # 使用OpenAI兼容接口（Kimi/DeepSeek等）
            if os.environ.get('LAZYLLM_KIMI_API_KEY'):
                # Kimi配置 - DSPy 3.x使用LM类
                # Note: kimi-k2.5 only supports temperature=1
                self.llm = dspy.LM(
                    model='openai/kimi-k2.5',
                    api_key=api_key,
                    api_base='https://api.moonshot.cn/v1',
                    temperature=1.0,  # kimi-k2.5 only supports temperature=1
                    max_tokens=2000
                )
            else:
                # OpenAI配置 - DSPy 3.x使用LM类
                self.llm = dspy.LM(
                    model='openai/gpt-3.5-turbo',
                    api_key=api_key,
                    temperature=0.7,
                    max_tokens=2000
                )
            
            # 配置DSPy 3.x
            dspy.configure(lm=self.llm)
            
            # 初始化模块
            self.modules = {
                'intent_classifier': IntentClassifier(),
                'intent_merger': IntentMerger(),
                'info_extractor': StructuredInfoExtractor(),
                'context_analyzer': ContextAnalyzer(),
                'prompt_generator': ContextualPromptGenerator(),
                'response_optimizer': ResponseOptimizer(),
                'question_generator': QuestionGenerator()
            }
            
            # 加载优化后的提示词（如果有）
            self._load_optimized_prompts()
            
            print("[DSPyRAG] Initialized successfully")
            
        except Exception as e:
            print(f"[DSPyRAG] Initialization failed: {e}")
            self.dspy_available = False
    
    def process_message(self,
                       user_message: str,
                       user_profile: Dict[str, Any],
                       conversation_history: List[Dict] = None,
                       preprocessed: Dict = None) -> Dict[str, Any]:
        """
        处理用户消息的完整流程
        
        Args:
            user_message: 用户原始输入
            user_profile: 当前用户画像
            conversation_history: 对话历史
            preprocessed: 前端TypeChat预处理结果（可选）
            
        Returns:
            {
                'reply': str,  # AI回复
                'extracted_info': dict,  # 提取的结构化信息
                'intent': str,  # 意图类型
                'sub_intents': list,  # 子意图
                'suggested_questions': list,  # 建议问题
                'reasoning': str,  # 判断理由
                'conversation_stage': str,  # 对话阶段
                'confidence': float,  # 置信度
                'profile_updates': dict  # 建议的画像更新
            }
        """
        if not self.dspy_available:
            return self._fallback_process(user_message, user_profile, conversation_history)
        
        try:
            return self._dspy_process(user_message, user_profile, conversation_history, preprocessed)
        except Exception as e:
            print(f"[DSPyRAG] Process error: {e}")
            return self._fallback_process(user_message, user_profile, conversation_history)
    
    def _dspy_process(self,
                     user_message: str,
                     user_profile: Dict[str, Any],
                     conversation_history: List[Dict],
                     preprocessed: Optional[Dict]) -> Dict[str, Any]:
        """使用DSPy的处理流程"""
        
        # Stage 1: 意图分类
        intent_result = self.modules['intent_classifier'](
            user_message=user_message,
            conversation_history=conversation_history or [],
            current_profile=user_profile
        )
        
        # 如果有前端预处理结果，进行融合
        if preprocessed and preprocessed.get('intent'):
            intent_result = self.modules['intent_merger'](
                user_message=user_message,
                frontend_intent=preprocessed.get('intent'),
                backend_intent=intent_result
            )
        
        # Stage 2: 上下文分析
        context_analysis = self.modules['context_analyzer'](
            current_message=user_message,
            previous_messages=conversation_history or []
        )
        
        # Stage 3: 结构化信息提取
        extracted_info = self.modules['info_extractor'](
            user_message=user_message,
            intent_type=intent_result['intent_type'],
            profile_context=user_profile,
            conversation_context=conversation_history or []
        )
        
        # Stage 4: 确定对话阶段
        conversation_stage = self._determine_stage(
            conversation_history,
            user_profile.get('completeness_score', 0)
        )
        
        # Stage 5: 生成动态提示词
        previous_ai_responses = [
            h.get('content', '') for h in (conversation_history or [])
            if h.get('role') == 'assistant'
        ][-3:]  # 最近3条AI回复
        
        prompt_config = self.modules['prompt_generator'](
            user_message=user_message,
            intent_info=intent_result,
            extracted_info=extracted_info,
            profile_summary=self._format_profile_summary(user_profile),
            conversation_stage=conversation_stage,
            previous_responses=previous_ai_responses
        )
        
        # Stage 6: 调用LLM
        final_prompt = self.modules['prompt_generator'].build_final_prompt(
            prompt_config,
            user_message
        )
        
        # DSPy 3.x: LM返回列表
        llm_response = self.llm(final_prompt)
        raw_response = llm_response[0] if isinstance(llm_response, list) else str(llm_response)
        
        # Stage 7: 优化回复
        optimization = self.modules['response_optimizer'](
            raw_response=raw_response,
            user_message=user_message,
            conversation_history=conversation_history or [],
            extracted_info=extracted_info
        )
        
        # Stage 8: 生成追问（如果配置中没有）
        if not prompt_config.get('suggested_questions'):
            suggested_questions = self.modules['question_generator'](
                user_message=user_message,
                extracted_info=extracted_info,
                conversation_stage=conversation_stage,
                asked_questions=self._extract_previous_questions(conversation_history)
            )
        else:
            suggested_questions = prompt_config['suggested_questions']
        
        # 构建返回结果
        return {
            'reply': optimization['optimized_response'],
            'extracted_info': self._convert_to_api_format(extracted_info),
            'intent': intent_result['intent_type'],
            'sub_intents': intent_result.get('sub_intents', []),
            'suggested_questions': suggested_questions,
            'reasoning': intent_result.get('reasoning', ''),
            'conversation_stage': conversation_stage,
            'confidence': intent_result.get('confidence', 0.5),
            'emotional_state': intent_result.get('emotional_state', 'neutral'),
            'profile_updates': extracted_info.get('profile_updates', {}),
            'context_analysis': context_analysis,
            'optimization_notes': optimization.get('changes', '')
        }
    
    def _fallback_process(self,
                         user_message: str,
                         user_profile: Dict[str, Any],
                         conversation_history: List[Dict]) -> Dict[str, Any]:
        """Fallback处理（当DSPy不可用时）"""
        # 导入原有的fallback逻辑
        from ..services.rag_service import CareerPlanningRAGService
        fallback_service = CareerPlanningRAGService()
        
        result = fallback_service.process_message(
            user_message=user_message,
            user_profile=user_profile,
            conversation_history=conversation_history
        )
        
        # 确保返回格式一致
        return {
            'reply': result.get('reply', ''),
            'extracted_info': result.get('extracted_info', []),
            'intent': result.get('intent', 'general_chat'),
            'sub_intents': [],
            'suggested_questions': result.get('suggested_questions', []),
            'reasoning': '',
            'conversation_stage': 'initial',
            'confidence': 0.5,
            'emotional_state': 'neutral',
            'profile_updates': {},
            'context_analysis': {},
            'optimization_notes': 'fallback_mode'
        }
    
    def _determine_stage(self, history: List[Dict], completeness: int) -> str:
        """确定对话阶段"""
        if not history:
            return 'initial'
        
        user_messages = [h for h in history if h.get('role') == 'user']
        msg_count = len(user_messages)
        
        if msg_count <= 2:
            return 'initial'
        elif completeness < 30:
            return 'exploring'
        elif completeness < 70:
            return 'deepening'
        else:
            return 'concluding'
    
    def _format_profile_summary(self, profile: Dict) -> str:
        """格式化画像摘要"""
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
        if profile.get('completeness_score') is not None:
            parts.append(f"画像完整度: {profile['completeness_score']}%")
        
        return "; ".join(parts) if parts else "（新用户）"
    
    def _convert_to_api_format(self, extracted_info: Dict) -> List[Dict]:
        """转换为API返回格式"""
        result = []
        
        # 转换兴趣
        if extracted_info.get('interests'):
            for interest in extracted_info['interests']:
                if isinstance(interest, dict):
                    result.append({
                        'field': 'practice_experiences',
                        'value': interest,
                        'confidence': extracted_info.get('confidence', 0.5)
                    })
        
        # 转换价值观
        if extracted_info.get('values'):
            result.append({
                'field': 'value_priorities',
                'value': extracted_info['values'],
                'confidence': extracted_info.get('confidence', 0.5)
            })
        
        # 转换能力
        if extracted_info.get('abilities'):
            result.append({
                'field': 'ability_assessment',
                'value': {a.get('skill', ''): 6 for a in extracted_info['abilities'] if isinstance(a, dict)},
                'confidence': extracted_info.get('confidence', 0.5)
            })
        
        return result
    
    def _extract_previous_questions(self, history: List[Dict]) -> List[str]:
        """从历史中提取之前问过的问题"""
        if not history:
            return []
        
        questions = []
        for item in history:
            if item.get('role') == 'assistant':
                content = item.get('content', '')
                # 简单提取问句
                if '?' in content or '？' in content:
                    # 这里可以做得更精细
                    pass
        return questions
    
    def _load_optimized_prompts(self):
        """加载优化后的提示词"""
        optimizer_path = os.path.join(
            os.path.dirname(__file__),
            'optimizers',
            'compiled.json'
        )
        if os.path.exists(optimizer_path):
            try:
                # 加载优化后的参数
                print(f"[DSPyRAG] Loading optimized prompts from {optimizer_path}")
                # 这里可以加载编译后的模块
            except Exception as e:
                print(f"[DSPyRAG] Failed to load optimized prompts: {e}")


# 全局服务实例
_dspy_rag_service = None


def get_dspy_rag_service() -> DSPyCareerRAGService:
    """获取DSPy RAG服务单例"""
    global _dspy_rag_service
    if _dspy_rag_service is None:
        _dspy_rag_service = DSPyCareerRAGService()
    return _dspy_rag_service
