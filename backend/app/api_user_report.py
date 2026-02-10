# -*- coding: utf-8 -*-
"""
用户报告模块 - API路由
FastAPI路由实现
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import json

from .database import get_db
from .models_user_report import GenerationTask
from .schemas_user_report import (
    ReportType, ReportStatus, TaskStatus, ExportFormat,
    UserReportCreate, UserReportUpdate, UserReportResponse, UserReportDetail,
    UserReportContent, ReportChapterContent, ChapterNavigation,
    GenerationTaskCreate, GenerationTaskResponse, GenerationOptions,
    PrerequisitesResult, PrerequisitesValidation, PrerequisitesValidationResponse,
    ExportRequest, ExportOptions,
    ReportListParams, ReportListResponse,
    GenerationHistoryParams, GenerationHistoryResponse,
    ReportCenterInit, ActiveTask, UserStats, PrerequisitesSummary
)
from .crud_user_report import (
    create_user_report, get_user_report, get_user_reports, update_user_report, delete_user_report,
    create_report_chapter, get_report_chapter, get_report_chapters,
    get_generation_task, get_active_generation_task, update_generation_task, cancel_generation_task,
    get_generation_history, create_export_record, update_export_download,
    get_export_records, create_generation_log, create_report_snapshot
)
from .crud_user_profile import get_user_profile, get_user_profile_logs
from .report_prerequisites import check_report_prerequisites, can_generate_report, ReportPrerequisitesChecker
from .report_generation_service import ReportGenerationService

# 创建路由
router = APIRouter(prefix="/user-reports", tags=["User Reports"])


# ==================== 辅助函数 ====================

def get_current_user_id() -> str:
    """获取当前用户ID (简化版，实际应从JWT token解析)"""
    # TODO: 从JWT token中解析用户ID
    return "test_user"  # 临时返回测试用户


# ==================== 条件检查接口 ====================

@router.get("/prerequisites", response_model=PrerequisitesResult)
async def get_prerequisites(
    report_type: ReportType = Query(..., description="报告类型"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取报告生成条件清单
    
    返回指定报告类型的所有生成条件及其当前状态
    """
    # 获取用户画像
    profile = get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    # 获取表单提交次数
    logs = get_user_profile_logs(db, user_id, limit=100)
    form_submission_count = len([log for log in logs if log.update_type == "form_input"])
    
    # 检查条件
    result = check_report_prerequisites(profile, report_type, form_submission_count)
    
    return PrerequisitesResult(**result)


@router.post("/prerequisites/validate", response_model=PrerequisitesValidationResponse)
async def validate_prerequisites(
    validation: PrerequisitesValidation,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    验证特定报告的生成条件
    
    返回是否可以生成报告，以及预估时间和字数
    """
    # 获取用户画像
    profile = get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    # 获取表单提交次数
    logs = get_user_profile_logs(db, user_id, limit=100)
    form_submission_count = len([log for log in logs if log.update_type == "form_input"])
    
    # 检查条件
    result = check_report_prerequisites(profile, validation.report_type, form_submission_count)
    
    if result["can_generate"]:
        checker = ReportPrerequisitesChecker(profile, form_submission_count)
        return PrerequisitesValidationResponse(
            can_generate=True,
            estimated_time=checker.get_estimated_time(validation.report_type),
            estimated_words=checker.get_estimated_words(validation.report_type)
        )
    else:
        failed_conditions = [
            {
                "id": p.id,
                "name": p.name,
                "message": p.description,
                "current": p.current_value,
                "required": p.required_value,
                "recommendation": p.recommendation
            }
            for p in result["prerequisites"]
            if p.status == "failed"
        ]
        return PrerequisitesValidationResponse(
            can_generate=False,
            failed_conditions=failed_conditions
        )


# ==================== 前端集成接口 ====================
# 注意：静态路由必须在动态路由 `/{report_id}` 之前定义

@router.get("/center/init", response_model=ReportCenterInit)
async def get_report_center_init(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取报告中心初始化数据
    
    为报告中心页面提供一站式数据加载
    """
    # 获取用户统计
    reports, total = get_user_reports(db, user_id, limit=1)
    last_generated = reports[0].created_at if reports else None
    
    profile = get_user_profile(db, user_id)
    completeness = profile.completeness_score if profile else 0
    
    user_stats = UserStats(
        total_reports=total,
        last_generated_at=last_generated,
        profile_completeness=completeness
    )
    
    # 获取各报告类型的条件摘要
    logs = get_user_profile_logs(db, user_id, limit=100)
    form_submission_count = len([log for log in logs if log.update_type == "form_input"])
    
    prerequisites_summary = {}
    for report_type in ReportType:
        result = check_report_prerequisites(profile, report_type, form_submission_count) if profile else {
            "can_generate": False,
            "overall_progress": 0
        }
        prerequisites_summary[report_type.value] = PrerequisitesSummary(
            can_generate=result["can_generate"],
            progress=result["overall_progress"]
        )
    
    # 获取最近报告
    recent_reports_data, _ = get_user_reports(db, user_id, limit=5)
    recent_reports = [
        UserReportResponse(
            id=r.id,
            title=r.title,
            report_type=r.report_type,
            status=r.status,
            word_count=r.word_count,
            chapter_count=r.chapter_count,
            created_at=r.created_at
        )
        for r in recent_reports_data
    ]
    
    # 获取进行中的任务
    active_task_obj = get_active_generation_task(db, user_id)
    active_task = None
    if active_task_obj:
        active_task = ActiveTask(
            task_id=active_task_obj.id,
            status=active_task_obj.status,
            progress=active_task_obj.progress
        )
    
    return ReportCenterInit(
        user_stats=user_stats,
        prerequisites_summary=prerequisites_summary,
        recent_reports=recent_reports,
        active_task=active_task
    )


# ==================== 报告生成接口 ====================

@router.post("/generation", response_model=GenerationTaskResponse)
async def start_generation(
    report_type: ReportType = Query(..., description="报告类型"),
    options: Optional[GenerationOptions] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    启动报告生成任务
    
    创建新的报告生成任务，返回任务ID和WebSocket连接URL
    """
    # 检查是否已有进行中的任务
    active_task = get_active_generation_task(db, user_id)
    if active_task:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "已有进行中的生成任务",
                "existing_task_id": active_task.id,
                "status": active_task.status,
                "progress": active_task.progress
            }
        )
    
    # 检查生成条件
    profile = get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    logs = get_user_profile_logs(db, user_id, limit=100)
    form_submission_count = len([log for log in logs if log.update_type == "form_input"])
    
    if not can_generate_report(profile, report_type, form_submission_count):
        raise HTTPException(
            status_code=422,
            detail={
                "message": "生成条件不满足",
                "prerequisites_url": f"/api/user-reports/prerequisites?report_type={report_type}"
            }
        )
    
    # 启动生成
    service = ReportGenerationService(db)
    task_id = await service.generate_report(user_id, report_type, options)
    
    # 获取任务信息
    task = get_generation_task(db, task_id)
    
    return GenerationTaskResponse(
        task_id=task.id,
        report_id=task.report_id,
        report_type=task.report_type,
        status=task.status,
        progress={
            "overall": task.progress,
            "current_stage": task.current_stage,
            "completed_chapters": task.completed_chapters,
            "total_chapters": task.total_chapters
        },
        started_at=task.started_at,
        estimated_completion=None,  # TODO: 计算预估完成时间
        websocket_url=f"/api/user-reports/generation/{task_id}/stream"
    )


@router.get("/generation/history", response_model=GenerationHistoryResponse)
async def get_generation_history_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取生成历史
    
    获取用户报告生成的历史记录
    """
    skip = (page - 1) * page_size
    tasks, total = get_generation_history(
        db, user_id,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    history_list = []
    for task in tasks:
        error = None
        if task.status == TaskStatus.FAILED:
            error = {
                "code": task.error_code,
                "message": task.error_message
            }
        
        history_list.append({
            "task_id": task.id,
            "report_id": task.report_id,
            "report_type": task.report_type,
            "status": task.status,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
            "failed_at": task.completed_at if task.status == TaskStatus.FAILED else None,
            "generation_time": task.generation_time if hasattr(task, 'generation_time') else None,
            "error": error
        })
    
    return GenerationHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        history=history_list
    )


@router.get("/generation/{task_id}", response_model=GenerationTaskResponse)
async def get_generation_status(
    task_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取生成任务状态
    
    返回任务的当前状态、进度和结果
    """
    task = get_generation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此任务")
    
    # 计算已用时间
    elapsed_seconds = None
    if task.started_at:
        from datetime import datetime
        elapsed_seconds = int((datetime.utcnow() - task.started_at).total_seconds())
    
    # 构建错误信息
    error = None
    if task.status == TaskStatus.FAILED:
        error = {
            "code": task.error_code,
            "message": task.error_message,
            "retryable": task.retry_count < 3
        }
    
    # 构建结果信息
    result = None
    if task.status == TaskStatus.COMPLETED and task.report_id:
        result = {
            "report_url": f"/api/user-reports/{task.report_id}",
            "word_count": 0,  # TODO: 从报告获取
            "generation_time": task.generation_time if hasattr(task, 'generation_time') else 0
        }
    
    return GenerationTaskResponse(
        task_id=task.id,
        report_id=task.report_id,
        report_type=task.report_type,
        status=task.status,
        progress={
            "overall": task.progress,
            "current_stage": task.current_stage,
            "completed_chapters": task.completed_chapters,
            "total_chapters": task.total_chapters,
            "current_chapter": {
                "id": task.current_chapter_id,
                "title": None  # TODO: 获取章节标题
            } if task.current_chapter_id else None
        },
        started_at=task.started_at,
        estimated_completion=None,
        elapsed_seconds=elapsed_seconds,
        error=error,
        result=result
    )


@router.post("/generation/{task_id}/cancel")
async def cancel_generation(
    task_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    取消生成任务
    
    取消正在进行的报告生成任务
    """
    task = get_generation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此任务")
    
    # 检查是否可以取消
    if task.status not in [TaskStatus.PENDING, TaskStatus.VALIDATING, TaskStatus.GENERATING]:
        raise HTTPException(status_code=409, detail="任务无法取消")
    
    # 更新任务状态
    from datetime import datetime
    update_generation_task(
        db, task_id,
        status=TaskStatus.CANCELLED,
        cancelled_at=datetime.utcnow()
    )
    
    # 如果有报告，也更新报告状态
    if task.report_id:
        update_user_report(db, task.report_id, UserReportUpdate(
            status=ReportStatus.CANCELLED
        ))
    
    return {
        "code": 200,
        "message": "任务已取消",
        "data": {
            "task_id": task_id,
            "status": TaskStatus.CANCELLED,
            "cancelled_at": datetime.utcnow().isoformat()
        }
    }


@router.websocket("/generation/{task_id}/stream")
async def generation_stream(
    websocket: WebSocket,
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket实时进度流
    
    通过WebSocket连接实时接收生成进度更新
    """
    await websocket.accept()
    
    try:
        task = get_generation_task(db, task_id)
        if not task:
            await websocket.send_json({
                "type": "error",
                "message": "任务不存在"
            })
            await websocket.close()
            return
        
        # TODO: 验证用户权限 (从WebSocket连接中获取token)
        
        # 发送初始状态
        await websocket.send_json({
            "type": "init",
            "data": {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress
            }
        })
        
        # 模拟实时推送 (实际应使用pub/sub或类似机制)
        import asyncio
        while True:
            await asyncio.sleep(2)  # 每2秒检查一次
            
            # 刷新任务状态
            db.refresh(task)
            
            await websocket.send_json({
                "type": "progress_update",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "overall_progress": task.progress,
                    "current_stage": task.current_stage,
                    "completed_chapters": task.completed_chapters,
                    "total_chapters": task.total_chapters
                }
            })
            
            # 如果任务完成或失败，关闭连接
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                await websocket.send_json({
                    "type": task.status.value,
                    "data": {"task_id": task_id, "status": task.status}
                })
                await websocket.close()
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()


# ==================== 报告查询接口 ====================

@router.get("", response_model=ReportListResponse)
async def get_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    report_type: Optional[ReportType] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|word_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取报告列表
    
    返回当前用户的所有报告列表，支持分页和筛选
    """
    skip = (page - 1) * page_size
    reports, total = get_user_reports(
        db, user_id,
        report_type=report_type,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    report_list = [
        UserReportResponse(
            id=r.id,
            title=r.title,
            report_type=r.report_type,
            status=r.status,
            word_count=r.word_count,
            chapter_count=r.chapter_count,
            created_at=r.created_at,
            thumbnail_url=None  # TODO: 生成缩略图
        )
        for r in reports
    ]
    
    return ReportListResponse(
        total=total,
        page=page,
        page_size=page_size,
        reports=report_list
    )


@router.get("/{report_id}", response_model=UserReportDetail)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取报告详情
    
    返回指定报告的详细信息和元数据
    """
    report = get_user_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此报告")
    
    # 获取章节列表
    chapters = get_report_chapters(db, report_id)
    chapter_list = [
        ReportChapterResponse(
            id=c.id,
            report_id=c.report_id,
            chapter_code=c.chapter_code,
            title=c.title,
            parent_id=c.parent_id,
            order_num=c.order_num,
            level=c.level,
            word_count=c.word_count,
            status=c.status,
            generated_at=c.generated_at,
            generation_time=c.generation_time,
            llm_model=c.llm_model,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in chapters
    ]
    
    # 获取数据快照
    from .crud_user_report import get_report_snapshots
    snapshots = get_report_snapshots(db, report_id)
    data_snapshot = {
        s.snapshot_type: s.snapshot_data
        for s in snapshots
    }
    
    return UserReportDetail(
        id=report.id,
        title=report.title,
        report_type=report.report_type,
        status=report.status,
        metadata={
            "word_count": report.word_count,
            "chapter_count": report.chapter_count,
            "generation_time": report.generation_time,
            "detail_level": report.detail_level,
            "include_charts": report.include_charts
        },
        chapters=chapter_list,
        created_at=report.created_at,
        data_snapshot=data_snapshot
    )


@router.get("/{report_id}/content")
async def get_report_content(
    report_id: str,
    chapter_id: Optional[str] = None,
    format: str = Query("html", pattern="^(html|markdown|text)$"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取报告内容
    
    返回报告的完整内容或指定章节内容
    """
    report = get_user_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此报告")
    
    if chapter_id:
        # 获取指定章节
        chapter = get_report_chapter(db, chapter_id)
        if not chapter or chapter.report_id != report_id:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        if format == "html":
            content = chapter.content_html or ""
        elif format == "markdown":
            content = chapter.content_markdown or ""
        else:
            content = chapter.content_plain or ""
        
        return UserReportContent(
            report_id=report_id,
            chapter_id=chapter_id,
            format=format,
            content=content,
            word_count=chapter.word_count,
            toc=[]
        )
    else:
        # 获取完整报告内容
        chapters = get_report_chapters(db, report_id)
        
        # 组装目录
        toc = [
            {
                "id": c.id,
                "title": c.title,
                "level": c.level,
                "word_count": c.word_count
            }
            for c in sorted(chapters, key=lambda x: x.order_num)
        ]
        
        # 组装内容
        if format == "html":
            contents = [c.content_html or "" for c in sorted(chapters, key=lambda x: x.order_num)]
            content = "\n".join(contents)
        elif format == "markdown":
            contents = [c.content_markdown or "" for c in sorted(chapters, key=lambda x: x.order_num)]
            content = "\n\n---\n\n".join(contents)
        else:
            contents = [c.content_plain or "" for c in sorted(chapters, key=lambda x: x.order_num)]
            content = "\n\n".join(contents)
        
        return UserReportContent(
            report_id=report_id,
            chapter_id=None,
            format=format,
            content=content,
            word_count=report.word_count,
            toc=toc
        )


@router.get("/{report_id}/chapters/{chapter_id}")
async def get_chapter(
    report_id: str,
    chapter_id: str,
    format: str = Query("html", pattern="^(html|markdown|text)$"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取章节内容
    
    返回指定章节的详细内容，包含前后导航
    """
    report = get_user_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此报告")
    
    chapter = get_report_chapter(db, chapter_id)
    if not chapter or chapter.report_id != report_id:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    # 获取格式内容
    if format == "html":
        content = chapter.content_html
    elif format == "markdown":
        content = chapter.content_markdown
    else:
        content = chapter.content_plain
    
    # 获取导航
    chapters = get_report_chapters(db, report_id)
    sorted_chapters = sorted(chapters, key=lambda x: x.order_num)
    current_index = next((i for i, c in enumerate(sorted_chapters) if c.id == chapter_id), -1)
    
    navigation = ChapterNavigation()
    if current_index > 0:
        prev_chapter = sorted_chapters[current_index - 1]
        navigation.prev = {"id": prev_chapter.id, "title": prev_chapter.title}
    if current_index < len(sorted_chapters) - 1:
        next_chapter = sorted_chapters[current_index + 1]
        navigation.next = {"id": next_chapter.id, "title": next_chapter.title}
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "report_id": report_id,
            "chapter": {
                "id": chapter.id,
                "chapter_code": chapter.chapter_code,
                "title": chapter.title,
                "order": chapter.order_num,
                "parent_id": chapter.parent_id,
                "level": chapter.level,
                "word_count": chapter.word_count,
                "content": content,
                "format": format,
                "generated_at": chapter.generated_at.isoformat() if chapter.generated_at else None
            },
            "navigation": navigation
        }
    }


# ==================== 报告导出接口 ====================

@router.post("/{report_id}/export/pdf")
async def export_pdf(
    report_id: str,
    request: ExportRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    导出PDF
    
    将报告导出为PDF格式
    """
    report = get_user_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此报告")
    
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(status_code=422, detail="报告尚未完成生成")
    
    # TODO: 实现PDF导出
    # 这里返回模拟响应
    
    return {
        "code": 200,
        "message": "PDF导出成功",
        "data": {
            "export_id": f"exp_{report_id}_pdf",
            "format": "pdf",
            "file_url": f"/api/user-reports/{report_id}/download/pdf",
            "file_size": 1024000,
            "expires_at": "2026-02-10T14:30:00Z"
        }
    }


@router.post("/{report_id}/export/word")
async def export_word(
    report_id: str,
    request: ExportRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    导出Word
    
    将报告导出为Word格式(.docx)
    """
    report = get_user_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此报告")
    
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(status_code=422, detail="报告尚未完成生成")
    
    # TODO: 实现Word导出
    
    return {
        "code": 200,
        "message": "Word导出成功",
        "data": {
            "export_id": f"exp_{report_id}_word",
            "format": "word",
            "file_url": f"/api/user-reports/{report_id}/download/word",
            "file_size": 512000,
            "expires_at": "2026-02-10T14:30:00Z"
        }
    }


@router.get("/{report_id}/export/markdown")
async def export_markdown(
    report_id: str,
    include_metadata: bool = Query(True),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    导出Markdown
    
    将报告导出为Markdown格式
    """
    report = get_user_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此报告")
    
    # 获取Markdown内容
    result = await get_report_content(
        report_id=report_id,
        format="markdown",
        db=db,
        user_id=user_id
    )
    
    content = result.content
    
    # 添加元数据头部
    if include_metadata:
        metadata = f"""---
title: {report.title}
created_at: {report.created_at.isoformat()}
word_count: {report.word_count}
report_type: {report.report_type}
---

"""
        content = metadata + content
    
    # 创建导出记录
    create_export_record(db, report_id, user_id, ExportFormat.MARKDOWN)
    
    # 返回文件
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=\"{report.title}_{report.created_at.strftime('%Y%m%d')}.md\""
        }
    )


# ==================== 管理接口 ====================

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    删除报告
    
    软删除指定的报告及其所有相关数据
    """
    report = get_user_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此报告")
    
    delete_user_report(db, report_id)
    
    return {
        "code": 200,
        "message": "报告已删除",
        "data": {
            "report_id": report_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
    }


# 导出路由
__all__ = ["router"]
