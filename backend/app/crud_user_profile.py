# -*- coding: utf-8 -*-
"""
用户画像模块 - CRUD操作
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from . import models_user_profile as models
from . import schemas_user_profile as schemas


# ==================== 用户画像 CRUD ====================

def get_user_profile(db: Session, user_id: str) -> Optional[models.UserProfile]:
    """获取用户画像"""
    return db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()


def get_user_profile_by_id(db: Session, profile_id: int) -> Optional[models.UserProfile]:
    """通过ID获取用户画像"""
    return db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()


def create_user_profile(db: Session, profile: schemas.UserProfileCreate) -> models.UserProfile:
    """创建用户画像"""
    db_profile = models.UserProfile(
        user_id=profile.user_id,
        nickname=profile.nickname,
        avatar_url=profile.avatar_url,
        holland_code=profile.holland_code,
        mbti_type=profile.mbti_type,
        value_priorities=profile.value_priorities,
        ability_assessment=profile.ability_assessment,
        constraints=profile.constraints,
        preferred_disciplines=profile.preferred_disciplines,
        preferred_majors=profile.preferred_majors,
        career_path_preference=profile.career_path_preference,
        practice_experiences=profile.practice_experiences,
        current_casve_stage=profile.current_casve_stage or "communication",
        casve_history=profile.casve_history or [],
        universal_skills=profile.universal_skills,
        resilience_score=profile.resilience_score,
        completeness_score=calculate_completeness_score_from_data(profile),
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_user_profile(db: Session, user_id: str, updates: schemas.UserProfileUpdate) -> Optional[models.UserProfile]:
    """更新用户画像"""
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        return None
    
    # 更新字段
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(db_profile, field):
            setattr(db_profile, field, value)
    
    # 重新计算完整度
    db_profile.completeness_score = calculate_completeness_score(db_profile)
    db_profile.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


def batch_update_profile(db: Session, user_id: str, items: List[schemas.ProfileBatchUpdateItem]) -> Optional[models.UserProfile]:
    """批量更新用户画像字段"""
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        return None
    
    # 记录日志
    for item in items:
        old_value = getattr(db_profile, item.field, None)
        create_profile_log(
            db, user_id,
            update_type=item.source or "batch_update",
            field_name=item.field,
            old_value=str(old_value) if old_value else None,
            new_value=str(item.value) if item.value else None
        )
        
        # 特殊处理JSON字段
        if item.field in ['value_priorities', 'ability_assessment', 'preferred_disciplines', 
                          'preferred_majors', 'practice_experiences', 'universal_skills', 
                          'constraints', 'casve_history']:
            if isinstance(item.value, str):
                try:
                    item.value = json.loads(item.value)
                except:
                    pass
        
        # 更新字段
        setattr(db_profile, item.field, item.value)
    
    db_profile.completeness_score = calculate_completeness_score(db_profile)
    db_profile.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


def delete_user_profile(db: Session, user_id: str) -> bool:
    """删除用户画像"""
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        return False
    
    db.delete(db_profile)
    db.commit()
    return True


# ==================== 更新日志 CRUD ====================

def create_profile_log(
    db: Session,
    user_id: str,
    update_type: str,
    field_name: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    source_message_id: Optional[int] = None
) -> models.UserProfileLog:
    """创建画像更新日志"""
    db_log = models.UserProfileLog(
        user_id=user_id,
        update_type=update_type,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        source_message_id=source_message_id,
        timestamp=datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_user_profile_logs(
    db: Session,
    user_id: str,
    update_type: Optional[str] = None,
    limit: int = 50
) -> List[models.UserProfileLog]:
    """获取用户画像更新日志"""
    query = db.query(models.UserProfileLog).filter(
        models.UserProfileLog.user_id == user_id
    )
    
    if update_type:
        query = query.filter(models.UserProfileLog.update_type == update_type)
    
    return query.order_by(desc(models.UserProfileLog.timestamp)).limit(limit).all()


# ==================== 完整度计算 ====================

def calculate_completeness_score_from_data(profile_data) -> int:
    """从数据计算完整度分数"""
    score = 0
    
    # 接口层字段 (40分)
    interface_fields = [
        (profile_data.holland_code, 10),
        (profile_data.mbti_type, 10),
        (profile_data.value_priorities, 10),
        (profile_data.ability_assessment, 10)
    ]
    for value, points in interface_fields:
        if value:
            score += points
    
    # 可变层字段 (30分)
    variable_fields = [
        (profile_data.preferred_disciplines or profile_data.preferred_majors, 10),
        (profile_data.career_path_preference, 10),
        (profile_data.practice_experiences, 10)
    ]
    for value, points in variable_fields:
        if value and len(value) > 0:
            score += points
    
    # 核心层字段 (30分)
    core_fields = [
        (profile_data.universal_skills, 15),
        (profile_data.resilience_score, 10),
        (profile_data.casve_history and len(profile_data.casve_history) > 0, 5)
    ]
    for value, points in core_fields:
        if value:
            score += points
    
    return min(score, 100)


def calculate_completeness_score(profile: models.UserProfile) -> int:
    """计算用户画像完整度分数"""
    score = 0
    
    # 接口层字段 (40分)
    interface_fields = [
        (profile.holland_code, 10),
        (profile.mbti_type, 10),
        (profile.value_priorities, 10),
        (profile.ability_assessment, 10)
    ]
    for value, points in interface_fields:
        if value:
            score += points
    
    # 可变层字段 (30分)
    variable_fields = [
        (profile.preferred_disciplines or profile.preferred_majors, 10),
        (profile.career_path_preference, 10),
        (profile.practice_experiences, 10)
    ]
    for value, points in variable_fields:
        if value and len(value) > 0:
            score += points
    
    # 核心层字段 (30分)
    core_fields = [
        (profile.universal_skills, 15),
        (profile.resilience_score, 10),
        (profile.casve_history and len(profile.casve_history) > 0, 5)
    ]
    for value, points in core_fields:
        if value:
            score += points
    
    return min(score, 100)


def get_profile_completeness_detail(db: Session, user_id: str) -> Optional[schemas.ProfileCompletenessResponse]:
    """获取画像完整度详细信息"""
    profile = get_user_profile(db, user_id)
    if not profile:
        return None
    
    # 计算各层完整度
    interface_score = 0
    if profile.holland_code: interface_score += 10
    if profile.mbti_type: interface_score += 10
    if profile.value_priorities: interface_score += 10
    if profile.ability_assessment: interface_score += 10
    
    variable_score = 0
    if profile.preferred_disciplines or profile.preferred_majors: variable_score += 10
    if profile.career_path_preference: variable_score += 10
    if profile.practice_experiences and len(profile.practice_experiences) > 0: variable_score += 10
    
    core_score = 0
    if profile.universal_skills: core_score += 15
    if profile.resilience_score: core_score += 10
    if profile.casve_history and len(profile.casve_history) > 0: core_score += 5
    
    # 缺失字段
    missing = []
    if not profile.holland_code: missing.append("holland_code")
    if not profile.mbti_type: missing.append("mbti_type")
    if not profile.value_priorities: missing.append("value_priorities")
    if not profile.ability_assessment: missing.append("ability_assessment")
    if not (profile.preferred_disciplines or profile.preferred_majors): missing.append("preferred_majors")
    if not profile.career_path_preference: missing.append("career_path_preference")
    
    # 建议
    suggestions = []
    if interface_score < 40:
        suggestions.append("建议完成兴趣和性格测评，完善接口层信息")
    if variable_score < 30:
        suggestions.append("建议探索专业方向，明确职业路径偏好")
    if core_score < 30:
        suggestions.append("建议进行通用技能自评，了解自身能力优势")
    
    return schemas.ProfileCompletenessResponse(
        score=calculate_completeness_score(profile),
        interface_layer_score=interface_score,
        variable_layer_score=variable_score,
        core_layer_score=core_score,
        missing_fields=missing,
        suggestions=suggestions
    )


# ==================== 对话记录 CRUD ====================

def create_conversation(
    db: Session,
    user_id: str,
    session_id: str,
    message_role: str,
    message_content: str,
    intent_type: Optional[str] = None,
    extracted_entities: Optional[Dict] = None
) -> models.UserConversation:
    """创建对话记录"""
    db_conv = models.UserConversation(
        user_id=user_id,
        session_id=session_id,
        message_role=message_role,
        message_content=message_content,
        intent_type=intent_type,
        extracted_entities=extracted_entities
    )
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    return db_conv


def get_conversation_history(
    db: Session,
    user_id: str,
    session_id: Optional[str] = None,
    limit: int = 50
) -> List[models.UserConversation]:
    """获取对话历史"""
    query = db.query(models.UserConversation).filter(
        models.UserConversation.user_id == user_id
    )
    if session_id:
        query = query.filter(models.UserConversation.session_id == session_id)
    
    return query.order_by(desc(models.UserConversation.timestamp)).limit(limit).all()


def get_recent_conversation_summary(db: Session, user_id: str, limit: int = 10) -> str:
    """获取近期对话摘要"""
    conversations = get_conversation_history(db, user_id, limit=limit)
    if not conversations:
        return ""
    
    # 简单的摘要生成
    user_messages = [c.message_content for c in conversations if c.message_role == "user"]
    return "; ".join(user_messages[:5]) if user_messages else ""


# ==================== CASVE 操作 ====================

def advance_casve_stage(
    db: Session,
    user_id: str,
    target_stage: Optional[schemas.CasveStage] = None,
    notes: Optional[str] = None
) -> Optional[models.UserProfile]:
    """推进CASVE阶段"""
    profile = get_user_profile(db, user_id)
    if not profile:
        return None
    
    stage_order = ["communication", "analysis", "synthesis", "evaluation", "execution"]
    current = profile.current_casve_stage or "communication"
    
    if target_stage:
        new_stage = target_stage.value
    else:
        # 自动推进到下一阶段
        current_idx = stage_order.index(current)
        if current_idx < len(stage_order) - 1:
            new_stage = stage_order[current_idx + 1]
        else:
            new_stage = current
    
    # 更新历史
    history = profile.casve_history or []
    history.append({
        "stage": new_stage,
        "timestamp": datetime.utcnow().isoformat(),
        "notes": notes or f"从 {current} 推进到 {new_stage}"
    })
    
    profile.current_casve_stage = new_stage
    profile.casve_history = history
    profile.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    return profile


# ==================== 辅助函数 ====================

def get_or_create_user_profile(db: Session, user_id: str, nickname: Optional[str] = None) -> models.UserProfile:
    """获取或创建用户画像"""
    profile = get_user_profile(db, user_id)
    if not profile:
        profile = create_user_profile(db, schemas.UserProfileCreate(
            user_id=user_id,
            nickname=nickname or f"用户{user_id[:8]}"
        ))
    return profile


def get_profile_summary_for_rag(db: Session, user_id: str) -> schemas.ProfileSummary:
    """生成用于RAG上下文的画像摘要"""
    profile = get_user_profile(db, user_id)
    if not profile:
        return schemas.ProfileSummary(user_id=user_id)
    
    # 生成兴趣摘要
    interest_parts = []
    if profile.holland_code:
        interest_parts.append(f"霍兰德代码: {profile.holland_code}")
    if profile.mbti_type:
        interest_parts.append(f"MBTI: {profile.mbti_type}")
    if profile.value_priorities:
        interest_parts.append(f"重视: {', '.join(profile.value_priorities[:3])}")
    
    # 能力摘要
    ability_parts = []
    if profile.ability_assessment:
        top_abilities = sorted(profile.ability_assessment.items(), key=lambda x: x[1], reverse=True)[:3]
        ability_parts.append(f"优势能力: {', '.join([k for k, v in top_abilities])}")
    
    # 当前状态
    career_direction = None
    if profile.career_path_preference:
        career_direction = profile.career_path_preference
    
    return schemas.ProfileSummary(
        user_id=user_id,
        nickname=profile.nickname,
        interest_summary="; ".join(interest_parts) if interest_parts else None,
        ability_summary="; ".join(ability_parts) if ability_parts else None,
        value_summary=", ".join(profile.value_priorities[:3]) if profile.value_priorities else None,
        current_stage=profile.current_casve_stage,
        career_direction=career_direction,
        recent_topics=[],  # 可从对话历史提取
        open_questions=[]
    )
