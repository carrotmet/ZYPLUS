# -*- coding: utf-8 -*-
"""
用户画像模块 - API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from . import database
from . import schemas_user_profile as schemas
from . import crud_user_profile as crud
from .services.rag_service import get_rag_service
# 导入新的DSPy服务（如果可用）
try:
    from .rag_dspy import get_dspy_rag_service
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    print("[API] DSPy not available, using legacy RAG service")

# 创建路由
router = APIRouter(prefix="/api/user-profiles", tags=["用户画像"])

# 数据库依赖
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== 基础CRUD接口 ====================

@router.get("/{user_id}", response_model=schemas.UserProfileResponse)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """获取用户画像"""
    profile = crud.get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    return profile


@router.post("", response_model=schemas.UserProfileResponse)
def create_user_profile(profile: schemas.UserProfileCreate, db: Session = Depends(get_db)):
    """创建用户画像"""
    # 检查是否已存在
    existing = crud.get_user_profile(db, profile.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="用户画像已存在")
    
    return crud.create_user_profile(db, profile)


@router.put("/{user_id}", response_model=schemas.UserProfileResponse)
def update_user_profile(
    user_id: str,
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """更新用户画像"""
    profile = crud.update_user_profile(db, user_id, profile_update)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    return profile


@router.delete("/{user_id}")
def delete_user_profile(user_id: str, db: Session = Depends(get_db)):
    """删除用户画像"""
    success = crud.delete_user_profile(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    return {"success": True, "message": "用户画像已删除"}


# ==================== 完整度接口 ====================

@router.get("/{user_id}/completeness", response_model=schemas.ProfileCompletenessResponse)
def get_profile_completeness(user_id: str, db: Session = Depends(get_db)):
    """获取用户画像完整度"""
    result = crud.get_profile_completeness_detail(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    return result


# ==================== RAG对话接口 ====================

@router.post("/{user_id}/chat", response_model=schemas.ChatMessageResponse)
def chat_with_profile(
    user_id: str,
    request: schemas.ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    与用户画像进行RAG对话（DSPy增强版）
    自动提取信息并更新画像
    支持前端TypeChat预处理结果
    """
    # 获取或创建用户画像
    profile = crud.get_or_create_user_profile(db, user_id)
    
    # 将画像转换为字典
    profile_dict = {
        "holland_code": profile.holland_code,
        "mbti_type": profile.mbti_type,
        "value_priorities": profile.value_priorities,
        "ability_assessment": profile.ability_assessment,
        "career_path_preference": profile.career_path_preference,
        "current_casve_stage": profile.current_casve_stage,
        "universal_skills": profile.universal_skills,
        "completeness_score": profile.completeness_score
    }
    
    # 处理消息 - 从context中获取history（如果是字典格式）
    conversation_history = None
    if request.context:
        if isinstance(request.context, dict) and 'history' in request.context:
            conversation_history = request.context['history']
        else:
            conversation_history = request.context
    
    # 选择RAG服务：优先使用DSPy（如果可用）
    if DSPY_AVAILABLE:
        rag_service = get_dspy_rag_service()
        print(f"[API] Using DSPy RAG service for user {user_id}")
    else:
        rag_service = get_rag_service()
        print(f"[API] Using legacy RAG service for user {user_id}")
    
    # 调用RAG服务处理消息
    result = rag_service.process_message(
        user_message=request.message,
        user_profile=profile_dict,
        conversation_history=conversation_history,
        preprocessed=request.preprocessed  # 传递前端预处理结果
    )
    
    # 创建对话记录（用户消息）
    conversation = crud.create_conversation(
        db=db,
        user_id=user_id,
        session_id=profile.rag_session_id or f"session_{user_id}",
        message_role="user",
        message_content=request.message,
        intent_type=result.get("intent", "general_chat")
    )
    
    # 如果有提取到信息，更新画像
    updated_fields = []
    extracted_info_list = []
    
    # 处理提取的信息（兼容新旧格式）
    extracted_data = result.get("extracted_info", [])
    profile_updates = result.get("profile_updates", {})
    
    # 构建更新数据
    update_data = {}
    
    # 处理提取的信息列表
    if isinstance(extracted_data, list):
        for item in extracted_data:
            if isinstance(item, dict):
                field = item.get("field")
                value = item.get("value")
                if field and hasattr(schemas.UserProfileUpdate, field):
                    update_data[field] = value
                    updated_fields.append(field)
                    extracted_info_list.append(schemas.ExtractedInfo(
                        field=field,
                        value=value,
                        confidence=item.get("confidence", 1.0)
                    ))
    
    # 处理profile_updates（从DSPy返回的更新建议）
    if isinstance(profile_updates, dict):
        for field, value in profile_updates.items():
            if value and hasattr(schemas.UserProfileUpdate, field):
                if field not in update_data:  # 避免重复
                    update_data[field] = value
                    updated_fields.append(field)
    
    # 执行画像更新
    if update_data:
        crud.update_user_profile(
            db=db,
            user_id=user_id,
            profile_update=schemas.UserProfileUpdate(**update_data),
            update_type="conversation_extract",
            source_message_id=conversation.id
        )
    
    # 记录AI回复
    crud.create_conversation(
        db=db,
        user_id=user_id,
        session_id=profile.rag_session_id or f"session_{user_id}",
        message_role="assistant",
        message_content=result.get("reply", ""),
        intent_type=result.get("intent", "general_chat")
    )
    
    # 重新获取更新后的画像
    updated_profile = crud.get_user_profile(db, user_id)
    
    # 构建当前画像状态
    current_profile_state = {
        "holland_code": updated_profile.holland_code,
        "mbti_type": updated_profile.mbti_type,
        "value_priorities": updated_profile.value_priorities,
        "ability_assessment": updated_profile.ability_assessment,
        "career_path_preference": updated_profile.career_path_preference,
        "current_casve_stage": updated_profile.current_casve_stage,
        "universal_skills": updated_profile.universal_skills,
        "completeness_score": updated_profile.completeness_score
    }
    
    # 构建响应
    return schemas.ChatMessageResponse(
        reply=result.get("reply", ""),
        extracted_info=extracted_info_list if extracted_info_list else [
            schemas.ExtractedInfo(field=k, value=v, confidence=1.0)
            for k, v in (profile_updates if isinstance(profile_updates, dict) else {}).items()
        ],
        updated_fields=updated_fields,
        suggested_questions=result.get("suggested_questions", []),
        current_casve_stage=updated_profile.current_casve_stage,
        profile_updates=current_profile_state
    )


@router.get("/{user_id}/chat/history", response_model=List[schemas.ConversationHistoryItem])
def get_chat_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    conversations = crud.get_conversation_history(db, user_id, limit=limit)
    return conversations


@router.delete("/{user_id}/chat/session")
def clear_chat_session(user_id: str, db: Session = Depends(get_db)):
    """清除对话会话"""
    # 这里可以实现会话重置逻辑
    return {"success": True, "message": "会话已清除"}


# ==================== 分析推荐接口 ====================

@router.post("/{user_id}/analyze", response_model=schemas.ProfileAnalysisResponse)
def analyze_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    分析用户画像
    提供洞察、建议和职业路径推荐
    """
    profile = crud.get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    # 生成分析结果
    insights = []
    recommendations = []
    
    # 基于接口层分析
    if profile.holland_code:
        insights.append(f"你的霍兰德代码是{profile.holland_code}，这表明你可能适合相关类型的职业")
    
    # 基于可变层分析
    if profile.career_path_preference:
        path_names = {
            "technical": "技术专家",
            "management": "管理领导",
            "professional": "专业方向",
            "public_welfare": "公益方向"
        }
        insights.append(f"你偏好{path_names.get(profile.career_path_preference, '综合')}发展路径")
    
    # 完善建议
    completeness = crud.get_profile_completeness_detail(db, user_id)
    if completeness.score < 50:
        recommendations.append("建议继续完善基础信息，完成兴趣和能力测评")
    elif completeness.score < 80:
        recommendations.append("可以探索更多职业方向，积累实践经验")
    else:
        recommendations.append("画像较为完整，可以开始制定具体的职业行动计划")
    
    return schemas.ProfileAnalysisResponse(
        insights=insights,
        recommendations=recommendations,
        career_paths=[],  # TODO: 实现职业匹配算法
        suggested_next_steps=completeness.suggestions
    )


@router.get("/{user_id}/career-paths", response_model=List[schemas.CareerPathRecommendation])
def get_career_path_recommendations(user_id: str, db: Session = Depends(get_db)):
    """获取职业路径推荐"""
    profile = crud.get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    # TODO: 实现基于画像的职业匹配算法
    return []


# ==================== CASVE接口 ====================

@router.post("/{user_id}/casve/advance", response_model=schemas.CasveAdvanceResponse)
def advance_casve_stage(
    user_id: str,
    request: schemas.CasveAdvanceRequest,
    db: Session = Depends(get_db)
):
    """推进CASVE决策阶段"""
    profile = crud.get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    previous_stage = profile.current_casve_stage
    
    # 更新阶段
    updated_profile = crud.advance_casve_stage(
        db=db,
        user_id=user_id,
        target_stage=request.target_stage,
        notes=request.notes
    )
    
    # 阶段描述和建议
    stage_descriptions = {
        "communication": "识别决策需求，感知理想与现实差距",
        "analysis": "系统梳理自我认知与选项信息",
        "synthesis": "生成可能的解决方案",
        "evaluation": "权衡各选项的优劣后果",
        "execution": "将选择转化为行动计划"
    }
    
    stage_actions = {
        "communication": ["识别不满来源", "明确需要做出的选择", "列出待解决的问题"],
        "analysis": ["梳理自我知识", "搜集职业信息", "进行SWOT分析"],
        "synthesis": ["头脑风暴可能选项", "扩展创造性方案", "避免过早收敛"],
        "evaluation": ["建立评估标准", "分析各选项后果", "进行多标准决策分析"],
        "execution": ["制定行动计划", "设定时间表", "采取第一步行动"]
    }
    
    return schemas.CasveAdvanceResponse(
        previous_stage=previous_stage,
        current_stage=updated_profile.current_casve_stage,
        stage_description=stage_descriptions.get(updated_profile.current_casve_stage, ""),
        suggested_actions=stage_actions.get(updated_profile.current_casve_stage, [])
    )


# ==================== 分层可视化接口 ====================

@router.get("/{user_id}/visualization", response_model=schemas.ProfileLayerVisualization)
def get_profile_visualization(user_id: str, db: Session = Depends(get_db)):
    """获取用户画像分层可视化数据"""
    profile = crud.get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    completeness = crud.get_profile_completeness_detail(db, user_id)
    
    # 构建各层数据
    interface_data = {
        "holland_code": profile.holland_code,
        "mbti_type": profile.mbti_type,
        "value_priorities": profile.value_priorities,
        "ability_assessment": profile.ability_assessment
    }
    
    variable_data = {
        "preferred_disciplines": profile.preferred_disciplines,
        "preferred_majors": profile.preferred_majors,
        "career_path_preference": profile.career_path_preference,
        "practice_experiences": profile.practice_experiences
    }
    
    core_data = {
        "current_casve_stage": profile.current_casve_stage,
        "universal_skills": profile.universal_skills,
        "resilience_score": profile.resilience_score,
        "casve_history": profile.casve_history
    }
    
    return schemas.ProfileLayerVisualization(
        user_id=user_id,
        nickname=profile.nickname,
        interface_layer=interface_data,
        interface_completeness=completeness.interface_layer_score,
        variable_layer=variable_data,
        variable_completeness=completeness.variable_layer_score,
        core_layer=core_data,
        core_completeness=completeness.core_layer_score,
        total_completeness=completeness.score,
        layer_status=f"接口层{completeness.interface_layer_score}% | 可变层{completeness.variable_layer_score}% | 核心层{completeness.core_layer_score}%"
    )


# ==================== 批量操作接口 ====================

@router.post("/{user_id}/batch-update")
def batch_update_profile(
    user_id: str,
    request: schemas.ProfileBatchUpdateRequest,
    db: Session = Depends(get_db)
):
    """批量更新用户画像"""
    profile = crud.batch_update_profile(db, user_id, request.updates)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    return {
        "success": True,
        "updated_fields": [u.field for u in request.updates],
        "completeness_score": profile.completeness_score
    }


# ==================== 表单更新接口 ====================

class ProfileFormUpdateRequest(BaseModel):
    """表单更新请求 - 用户主动填写"""
    updates: Dict[str, Any] = Field(..., description="更新的字段和值")


class ProfileAIUpdateRequest(BaseModel):
    """AI更新请求 - AI隐式调用"""
    updates: Dict[str, Any] = Field(..., description="更新的字段和值")
    reason: Optional[str] = Field(None, description="更新原因")
    source: Optional[str] = Field("ai_extraction", description="数据来源")


class ProfileFormUpdateResponse(BaseModel):
    """表单更新响应"""
    success: bool
    message: str
    data: Dict[str, Any]


@router.post("/{user_id}/form-update", response_model=ProfileFormUpdateResponse)
def update_profile_by_form(
    user_id: str,
    request: ProfileFormUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    通过表单更新用户画像
    支持的字段：holland_code, mbti_type, value_priorities, ability_assessment,
                   career_path_preference, current_casve_stage, universal_skills, resilience_score
    """
    # 获取或创建用户画像
    profile = crud.get_or_create_user_profile(db, user_id)
    
    # 过滤有效的字段
    valid_fields = [
        'holland_code', 'mbti_type', 'value_priorities', 'ability_assessment',
        'constraints', 'preferred_disciplines', 'preferred_majors',
        'career_path_preference', 'practice_experiences',
        'current_casve_stage', 'casve_history', 'universal_skills', 'resilience_score',
        'nickname', 'avatar_url'
    ]
    
    update_data = {}
    for field, value in request.updates.items():
        if field in valid_fields and value is not None and value != '':
            # 特殊处理某些字段
            if field in ['value_priorities', 'preferred_disciplines', 'preferred_majors']:
                if isinstance(value, list) and len(value) > 0:
                    update_data[field] = value
            elif field in ['ability_assessment', 'universal_skills', 'constraints']:
                if isinstance(value, dict) and len(value) > 0:
                    update_data[field] = value
            elif field == 'resilience_score':
                if isinstance(value, int) and 1 <= value <= 10:
                    update_data[field] = value
            else:
                update_data[field] = value
    
    if not update_data:
        return ProfileFormUpdateResponse(
            success=True,
            message="没有需要更新的字段",
            data={"updated_fields": []}
        )
    
    # 执行更新
    try:
        updated_profile = crud.update_user_profile(
            db=db,
            user_id=user_id,
            profile_update=schemas.UserProfileUpdate(**update_data),
            update_type="form_input"
        )
        
        # 构建返回数据
        current_state = {
            "holland_code": updated_profile.holland_code,
            "mbti_type": updated_profile.mbti_type,
            "value_priorities": updated_profile.value_priorities,
            "ability_assessment": updated_profile.ability_assessment,
            "career_path_preference": updated_profile.career_path_preference,
            "current_casve_stage": updated_profile.current_casve_stage,
            "universal_skills": updated_profile.universal_skills,
            "resilience_score": updated_profile.resilience_score,
            "completeness_score": updated_profile.completeness_score
        }
        
        return ProfileFormUpdateResponse(
            success=True,
            message="画像更新成功",
            data={
                "updated_fields": list(update_data.keys()),
                "profile": current_state
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/{user_id}/ai-update", response_model=ProfileFormUpdateResponse)
def update_profile_by_ai(
    user_id: str,
    request: ProfileAIUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    AI隐式更新用户画像
    用于AI从对话中自动提取并更新画像字段
    """
    # 获取或创建用户画像
    profile = crud.get_or_create_user_profile(db, user_id)
    
    # 过滤有效字段
    valid_fields = [
        'holland_code', 'mbti_type', 'value_priorities', 'ability_assessment',
        'preferred_disciplines', 'preferred_majors', 'career_path_preference',
        'practice_experiences', 'current_casve_stage', 'universal_skills', 'resilience_score'
    ]
    
    update_data = {}
    for field, value in request.updates.items():
        if field in valid_fields and value is not None and value != '':
            if field in ['value_priorities', 'preferred_disciplines', 'preferred_majors']:
                if isinstance(value, list) and len(value) > 0:
                    update_data[field] = value
            elif field in ['ability_assessment', 'universal_skills']:
                if isinstance(value, dict) and len(value) > 0:
                    update_data[field] = value
            elif field == 'resilience_score':
                if isinstance(value, int) and 1 <= value <= 10:
                    update_data[field] = value
            else:
                update_data[field] = value
    
    if not update_data:
        return ProfileFormUpdateResponse(
            success=True,
            message="没有需要更新的字段",
            data={"updated_fields": []}
        )
    
    try:
        updated_profile = crud.update_user_profile(
            db=db,
            user_id=user_id,
            profile_update=schemas.UserProfileUpdate(**update_data),
            update_type=request.source or "ai_extraction"
        )
        
        current_state = {
            "holland_code": updated_profile.holland_code,
            "mbti_type": updated_profile.mbti_type,
            "value_priorities": updated_profile.value_priorities,
            "ability_assessment": updated_profile.ability_assessment,
            "career_path_preference": updated_profile.career_path_preference,
            "current_casve_stage": updated_profile.current_casve_stage,
            "universal_skills": updated_profile.universal_skills,
            "resilience_score": updated_profile.resilience_score,
            "completeness_score": updated_profile.completeness_score
        }
        
        return ProfileFormUpdateResponse(
            success=True,
            message=f"AI已更新: {', '.join(update_data.keys())}",
            data={
                "updated_fields": list(update_data.keys()),
                "profile": current_state,
                "reason": request.reason
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI更新失败: {str(e)}")
