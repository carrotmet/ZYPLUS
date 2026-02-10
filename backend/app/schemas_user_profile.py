# -*- coding: utf-8 -*-
"""
用户画像模块 - Pydantic Schema
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== 枚举类型 ====================

class CasveStage(str, Enum):
    """CASVE决策阶段"""
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"
    EXECUTION = "execution"


class CareerPathType(str, Enum):
    """职业路径类型"""
    TECHNICAL = "technical"
    MANAGEMENT = "management"
    PROFESSIONAL = "professional"
    PUBLIC_WELFARE = "public_welfare"


class ConversationIntent(str, Enum):
    """对话意图类型"""
    INTEREST_EXPLORE = "interest_explore"      # 兴趣探索
    ABILITY_ASSESS = "ability_assess"          # 能力评估
    VALUE_CLARIFY = "value_clarify"            # 价值观澄清
    CAREER_ADVICE = "career_advice"            # 职业建议
    PATH_PLANNING = "path_planning"            # 路径规划
    CASVE_GUIDANCE = "casve_guidance"          # CASVE指导
    GENERAL_CHAT = "general_chat"              # 一般对话


# ==================== 基础模型 ====================

class UserProfileBase(BaseModel):
    """用户画像基础模型 - 接口层"""
    nickname: Optional[str] = Field(None, description="用户昵称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    
    # 接口层: 兴趣价值观
    holland_code: Optional[str] = Field(None, description="霍兰德代码,如RIA")
    mbti_type: Optional[str] = Field(None, description="MBTI类型,如INTJ")
    value_priorities: Optional[List[str]] = Field(None, description="价值观优先级列表")
    
    # 接口层: 能力评估
    ability_assessment: Optional[Dict[str, int]] = Field(None, description="能力评估字典")
    
    # 接口层: 约束条件
    constraints: Optional[Dict[str, Any]] = Field(None, description="约束条件")


class UserProfileVariable(BaseModel):
    """用户画像可变层模型"""
    # 专业偏好
    preferred_disciplines: Optional[List[int]] = Field(None, description="偏好学科ID列表")
    preferred_majors: Optional[List[int]] = Field(None, description="偏好专业ID列表")
    
    # 路径偏好
    career_path_preference: Optional[CareerPathType] = Field(None, description="职业路径偏好")
    
    # 实践经历
    practice_experiences: Optional[List[Dict[str, Any]]] = Field(None, description="实践经历列表")


class UserProfileCore(BaseModel):
    """用户画像核心层模型"""
    # CASVE状态
    current_casve_stage: Optional[CasveStage] = Field(CasveStage.COMMUNICATION, description="当前CASVE阶段")
    casve_history: Optional[List[Dict[str, Any]]] = Field(None, description="CASVE历史")
    
    # 通用技能
    universal_skills: Optional[Dict[str, int]] = Field(None, description="通用技能评分")
    resilience_score: Optional[int] = Field(None, ge=1, le=10, description="职业弹性分数1-10")


# ==================== CRUD模型 ====================

class UserProfileCreate(UserProfileBase):
    """创建用户画像"""
    user_id: str = Field(..., description="用户唯一标识")


class UserProfileUpdate(BaseModel):
    """更新用户画像 - 支持部分更新"""
    # 接口层
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    holland_code: Optional[str] = None
    mbti_type: Optional[str] = None
    value_priorities: Optional[List[str]] = None
    ability_assessment: Optional[Dict[str, int]] = None
    constraints: Optional[Dict[str, Any]] = None
    
    # 可变层
    preferred_disciplines: Optional[List[int]] = None
    preferred_majors: Optional[List[int]] = None
    career_path_preference: Optional[CareerPathType] = None
    practice_experiences: Optional[List[Dict[str, Any]]] = None
    
    # 核心层
    current_casve_stage: Optional[CasveStage] = None
    casve_history: Optional[List[Dict[str, Any]]] = None
    universal_skills: Optional[Dict[str, int]] = None
    resilience_score: Optional[int] = None


class UserProfileResponse(UserProfileBase, UserProfileVariable, UserProfileCore):
    """用户画像完整响应"""
    id: int
    user_id: str
    completeness_score: int = Field(0, description="画像完整度0-100")
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 对话相关模型 ====================

class ChatMessageRequest(BaseModel):
    """聊天消息请求"""
    message: str = Field(..., description="用户消息内容")
    context: Optional[Dict[str, Any]] = Field(None, description="额外上下文")
    preprocessed: Optional[Dict[str, Any]] = Field(None, description="前端TypeChat预处理结果（可选）")


class ExtractedInfo(BaseModel):
    """从对话中提取的信息"""
    field: str = Field(..., description="字段名")
    value: Any = Field(..., description="提取的值")
    confidence: float = Field(1.0, ge=0, le=1, description="置信度")


class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    reply: str = Field(..., description="AI回复内容")
    extracted_info: List[ExtractedInfo] = Field([], description="本次提取的信息列表")
    updated_fields: List[str] = Field([], description="更新的字段列表")
    suggested_questions: List[str] = Field([], description="建议的后续问题")
    current_casve_stage: Optional[CasveStage] = None
    profile_updates: Optional[Dict[str, Any]] = Field(None, description="更新后的完整画像状态")


class ConversationHistoryItem(BaseModel):
    """对话历史项"""
    id: int
    message_role: str
    message_content: str
    intent_type: Optional[ConversationIntent] = None
    extracted_entities: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ==================== 分析相关模型 ====================

class ProfileCompletenessResponse(BaseModel):
    """画像完整度响应"""
    score: int = Field(..., ge=0, le=100, description="完整度分数")
    interface_layer_score: int = Field(..., description="接口层完整度")
    variable_layer_score: int = Field(..., description="可变层完整度")
    core_layer_score: int = Field(..., description="核心层完整度")
    missing_fields: List[str] = Field([], description="缺失的字段")
    suggestions: List[str] = Field([], description="完善建议")


class CareerPathRecommendation(BaseModel):
    """职业路径推荐"""
    occupation_id: int
    occupation_name: str
    match_score: int = Field(..., ge=0, le=100)
    match_reason: str
    key_requirements: List[str] = []
    salary_range: Optional[str] = None


class ProfileAnalysisResponse(BaseModel):
    """画像分析响应"""
    insights: List[str] = Field([], description="洞察点")
    recommendations: List[str] = Field([], description="建议")
    career_paths: List[CareerPathRecommendation] = Field([], description="推荐的职业路径")
    suggested_next_steps: List[str] = Field([], description="建议的下一步行动")


class CasveAdvanceRequest(BaseModel):
    """推进CASVE阶段请求"""
    target_stage: Optional[CasveStage] = None
    notes: Optional[str] = None


class CasveAdvanceResponse(BaseModel):
    """推进CASVE阶段响应"""
    previous_stage: CasveStage
    current_stage: CasveStage
    stage_description: str
    suggested_actions: List[str]


# ==================== 三层模型可视化 ====================

class ProfileLayerVisualization(BaseModel):
    """用户画像分层可视化"""
    user_id: str
    nickname: Optional[str]
    
    # 接口层
    interface_layer: Dict[str, Any] = Field({}, description="接口层数据")
    interface_completeness: int = Field(0, ge=0, le=100)
    
    # 可变层
    variable_layer: Dict[str, Any] = Field({}, description="可变层数据")
    variable_completeness: int = Field(0, ge=0, le=100)
    
    # 核心层
    core_layer: Dict[str, Any] = Field({}, description="核心层数据")
    core_completeness: int = Field(0, ge=0, le=100)
    
    # 总体
    total_completeness: int = Field(0, ge=0, le=100)
    layer_status: str = Field("", description="分层状态描述")


# ==================== 批量操作模型 ====================

class ProfileBatchUpdateItem(BaseModel):
    """批量更新项"""
    field: str
    value: Any
    source: str = "conversation"  # conversation/form/system


class ProfileBatchUpdateRequest(BaseModel):
    """批量更新请求"""
    updates: List[ProfileBatchUpdateItem]


class ProfileSummary(BaseModel):
    """用户画像摘要 - 用于RAG上下文"""
    user_id: str
    nickname: Optional[str]
    
    # 关键信息摘要
    interest_summary: Optional[str] = None
    ability_summary: Optional[str] = None
    value_summary: Optional[str] = None
    
    # 当前状态
    current_stage: Optional[str] = None
    career_direction: Optional[str] = None
    
    # 对话上下文
    recent_topics: List[str] = []
    open_questions: List[str] = []
