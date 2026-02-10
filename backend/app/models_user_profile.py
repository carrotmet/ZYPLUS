# -*- coding: utf-8 -*-
"""
用户画像模块 - 数据模型
基于 Career-Planning SKILL 三层模型架构设计
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class UserProfile(Base):
    """
    用户画像主表
    对应SKILL三层模型: 接口层 + 可变层 + 核心层
    """
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    nickname = Column(String(100))
    avatar_url = Column(String(500))
    
    # ==================== 接口层 (Interface Layer) ====================
    # 兴趣与价值观
    holland_code = Column(String(10))  # 如: RIA, SEC
    mbti_type = Column(String(10))     # 如: INTJ, ENFP
    value_priorities = Column(JSON)    # ["成就感", "工作稳定", "创新空间"]
    
    # 能力评估
    ability_assessment = Column(JSON)  # {"逻辑推理": 8, "创造力": 7, ...}
    
    # 约束条件
    constraints = Column(JSON)         # {"family_bg": "...", "location_pref": "..."}
    
    # ==================== 可变层 (Variable Layer) ====================
    # 专业偏好
    preferred_disciplines = Column(JSON)  # [1, 2, 8] 学科ID列表
    preferred_majors = Column(JSON)       # [101, 102, 801] 专业ID列表
    
    # 路径偏好
    career_path_preference = Column(String(50))  # technical/management/professional/public
    
    # 实践经历
    practice_experiences = Column(JSON)  # [{"type": "internship", "desc": "..."}, ...]
    
    # ==================== 核心层 (Core Layer) ====================
    # CASVE决策状态
    current_casve_stage = Column(String(20), default='communication')  # C/A/S/V/E
    casve_history = Column(JSON)         # [{"stage": "C", "timestamp": "...", "notes": "..."}]
    
    # 通用技能
    universal_skills = Column(JSON)      # {"communication": 7, "teamwork": 8, ...}
    resilience_score = Column(Integer)   # 1-10
    
    # RAG对话上下文
    rag_session_id = Column(String(100))  # LazyLLM会话ID
    conversation_summary = Column(Text)   # 对话摘要
    
    # ==================== 元数据 ====================
    completeness_score = Column(Integer, default=0)  # 画像完整度 0-100
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    conversations = relationship("UserConversation", back_populates="user_profile", cascade="all, delete-orphan")
    update_logs = relationship("UserProfileLog", back_populates="user_profile", cascade="all, delete-orphan")


class UserConversation(Base):
    """
    用户对话记录表
    存储RAG对话历史，用于LazyLLM上下文管理
    """
    __tablename__ = "user_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    session_id = Column(String(100), index=True)  # LazyLLM会话ID
    message_role = Column(String(20))  # user/assistant/system
    message_content = Column(Text)
    intent_type = Column(String(50))   # interest_explore/ability_assess/value_clarify/career_advice/...
    extracted_entities = Column(JSON)  # 提取的实体信息
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user_profile = relationship("UserProfile", back_populates="conversations")


class UserProfileLog(Base):
    """
    用户画像更新日志
    追踪画像数据来源和变更历史
    """
    __tablename__ = "user_profile_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    update_type = Column(String(50))   # conversation_extract/form_input/manual_edit/system_infer
    field_name = Column(String(100))   # 更新的字段
    old_value = Column(Text)
    new_value = Column(Text)
    source_message_id = Column(Integer, ForeignKey("user_conversations.id"))  # 关联的对话记录
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user_profile = relationship("UserProfile", back_populates="update_logs")


class UserCareerPathRecommendation(Base):
    """
    用户职业路径推荐记录
    存储系统推荐的职业路径及匹配度
    """
    __tablename__ = "user_career_path_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=False)
    match_score = Column(Integer)      # 匹配度 0-100
    match_reason = Column(Text)        # 匹配理由
    recommendation_rank = Column(Integer)  # 推荐排名
    user_feedback = Column(String(20)) # like/dislike/neutral
    created_at = Column(DateTime, default=datetime.utcnow)


# 导出所有模型
__all__ = [
    'UserProfile',
    'UserConversation', 
    'UserProfileLog',
    'UserCareerPathRecommendation'
]
