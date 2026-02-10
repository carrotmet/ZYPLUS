# -*- coding: utf-8 -*-
"""
用户报告模块 - CRUD操作
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from .models_user_report import (
    UserReport, ReportChapter, GenerationTask,
    ReportSnapshot, ReportExport, GenerationLog
)
from .schemas_user_report import (
    UserReportCreate, UserReportUpdate, ReportChapterCreate,
    GenerationTaskCreate, ReportType, ReportStatus, TaskStatus,
    ChapterStatus, ExportFormat
)


# ==================== 报告CRUD ====================

def create_user_report(db: Session, report: UserReportCreate) -> UserReport:
    """创建报告"""
    db_report = UserReport(
        id=report.id or f"report_{uuid.uuid4().hex[:16]}",
        user_id=report.user_id,
        title=report.title,
        report_type=report.report_type,
        status=report.status,
        detail_level=report.detail_level,
        include_charts=report.include_charts,
        language=report.language,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_user_report(db: Session, report_id: str) -> Optional[UserReport]:
    """获取报告详情"""
    return db.query(UserReport).filter(
        and_(UserReport.id == report_id, UserReport.deleted_at.is_(None))
    ).first()


def get_user_reports(
    db: Session,
    user_id: str,
    report_type: Optional[ReportType] = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> tuple[List[UserReport], int]:
    """获取用户报告列表"""
    query = db.query(UserReport).filter(
        and_(UserReport.user_id == user_id, UserReport.deleted_at.is_(None))
    )
    
    if report_type:
        query = query.filter(UserReport.report_type == report_type)
    
    # 排序
    sort_column = getattr(UserReport, sort_by, UserReport.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    total = query.count()
    reports = query.offset(skip).limit(limit).all()
    return reports, total


def update_user_report(
    db: Session,
    report_id: str,
    update_data: UserReportUpdate
) -> Optional[UserReport]:
    """更新报告"""
    db_report = get_user_report(db, report_id)
    if not db_report:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict['updated_at'] = datetime.utcnow()
    
    for key, value in update_dict.items():
        setattr(db_report, key, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


def delete_user_report(db: Session, report_id: str) -> bool:
    """软删除报告"""
    db_report = get_user_report(db, report_id)
    if not db_report:
        return False
    
    db_report.deleted_at = datetime.utcnow()
    db_report.status = ReportStatus.ARCHIVED
    db.commit()
    return True


def hard_delete_user_report(db: Session, report_id: str) -> bool:
    """硬删除报告（谨慎使用）"""
    db_report = db.query(UserReport).filter(UserReport.id == report_id).first()
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True


# ==================== 章节CRUD ====================

def create_report_chapter(db: Session, chapter: ReportChapterCreate) -> ReportChapter:
    """创建章节"""
    db_chapter = ReportChapter(
        id=f"ch_{chapter.chapter_code.replace('.', '_')}_{uuid.uuid4().hex[:8]}",
        report_id=chapter.report_id,
        chapter_code=chapter.chapter_code,
        title=chapter.title,
        parent_id=chapter.parent_id,
        order_num=chapter.order_num,
        level=chapter.level,
        word_count=chapter.word_count,
        status=chapter.status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


def get_report_chapter(db: Session, chapter_id: str) -> Optional[ReportChapter]:
    """获取章节详情"""
    return db.query(ReportChapter).filter(ReportChapter.id == chapter_id).first()


def get_report_chapters(
    db: Session,
    report_id: str,
    parent_id: Optional[str] = None
) -> List[ReportChapter]:
    """获取报告章节列表"""
    query = db.query(ReportChapter).filter(ReportChapter.report_id == report_id)
    
    if parent_id is not None:
        query = query.filter(ReportChapter.parent_id == parent_id)
    
    return query.order_by(ReportChapter.order_num).all()


def update_chapter_content(
    db: Session,
    chapter_id: str,
    content_html: Optional[str] = None,
    content_markdown: Optional[str] = None,
    content_plain: Optional[str] = None,
    word_count: Optional[int] = None,
    status: Optional[ChapterStatus] = None,
    generation_time: Optional[int] = None,
    llm_model: Optional[str] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None
) -> Optional[ReportChapter]:
    """更新章节内容"""
    db_chapter = get_report_chapter(db, chapter_id)
    if not db_chapter:
        return None
    
    if content_html is not None:
        db_chapter.content_html = content_html
    if content_markdown is not None:
        db_chapter.content_markdown = content_markdown
    if content_plain is not None:
        db_chapter.content_plain = content_plain
    if word_count is not None:
        db_chapter.word_count = word_count
    if status is not None:
        db_chapter.status = status
    if generation_time is not None:
        db_chapter.generation_time = generation_time
    if llm_model is not None:
        db_chapter.llm_model = llm_model
    if prompt_tokens is not None:
        db_chapter.prompt_tokens = prompt_tokens
    if completion_tokens is not None:
        db_chapter.completion_tokens = completion_tokens
    
    if status == ChapterStatus.COMPLETED:
        db_chapter.generated_at = datetime.utcnow()
    
    db_chapter.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


# ==================== 生成任务CRUD ====================

def create_generation_task(db: Session, task: GenerationTaskCreate) -> GenerationTask:
    """创建生成任务"""
    db_task = GenerationTask(
        id=f"task_{uuid.uuid4().hex[:16]}",
        user_id=task.user_id,
        report_id=task.report_id,
        report_type=task.report_type,
        status=TaskStatus.PENDING,
        options=task.options.model_dump() if task.options else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_generation_task(db: Session, task_id: str) -> Optional[GenerationTask]:
    """获取生成任务"""
    return db.query(GenerationTask).filter(GenerationTask.id == task_id).first()


def get_active_generation_task(db: Session, user_id: str) -> Optional[GenerationTask]:
    """获取用户进行中的生成任务"""
    active_statuses = [
        TaskStatus.PENDING,
        TaskStatus.VALIDATING,
        TaskStatus.GENERATING,
        TaskStatus.QUALITY_CHECKING,
        TaskStatus.ASSEMBLING
    ]
    return db.query(GenerationTask).filter(
        and_(
            GenerationTask.user_id == user_id,
            GenerationTask.status.in_(active_statuses)
        )
    ).first()


def update_generation_task(
    db: Session,
    task_id: str,
    status: Optional[TaskStatus] = None,
    progress: Optional[int] = None,
    current_stage: Optional[str] = None,
    current_chapter_id: Optional[str] = None,
    completed_chapters: Optional[int] = None,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    cancelled_at: Optional[datetime] = None
) -> Optional[GenerationTask]:
    """更新生成任务"""
    db_task = get_generation_task(db, task_id)
    if not db_task:
        return None
    
    if status is not None:
        db_task.status = status
    if progress is not None:
        db_task.progress = progress
    if current_stage is not None:
        db_task.current_stage = current_stage
    if current_chapter_id is not None:
        db_task.current_chapter_id = current_chapter_id
    if completed_chapters is not None:
        db_task.completed_chapters = completed_chapters
    if error_code is not None:
        db_task.error_code = error_code
    if error_message is not None:
        db_task.error_message = error_message
    if started_at is not None:
        db_task.started_at = started_at
    if completed_at is not None:
        db_task.completed_at = completed_at
    if cancelled_at is not None:
        db_task.cancelled_at = cancelled_at
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task


def increment_task_retry(db: Session, task_id: str) -> Optional[GenerationTask]:
    """增加任务重试次数"""
    db_task = get_generation_task(db, task_id)
    if not db_task:
        return None
    
    db_task.retry_count += 1
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task


def get_generation_history(
    db: Session,
    user_id: str,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[GenerationTask], int]:
    """获取生成历史"""
    query = db.query(GenerationTask).filter(GenerationTask.user_id == user_id)
    
    if status:
        status_list = status.split(',')
        query = query.filter(GenerationTask.status.in_(status_list))
    
    total = query.count()
    tasks = query.order_by(desc(GenerationTask.created_at)).offset(skip).limit(limit).all()
    return tasks, total


# ==================== 数据快照CRUD ====================

def create_report_snapshot(
    db: Session,
    report_id: str,
    user_id: str,
    snapshot_type: str,
    snapshot_data: Dict[str, Any]
) -> ReportSnapshot:
    """创建数据快照"""
    db_snapshot = ReportSnapshot(
        id=f"snap_{uuid.uuid4().hex[:16]}",
        report_id=report_id,
        user_id=user_id,
        snapshot_type=snapshot_type,
        snapshot_data=snapshot_data,
        created_at=datetime.utcnow()
    )
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)
    return db_snapshot


def get_report_snapshots(db: Session, report_id: str) -> List[ReportSnapshot]:
    """获取报告的所有快照"""
    return db.query(ReportSnapshot).filter(ReportSnapshot.report_id == report_id).all()


def get_report_snapshot_by_type(
    db: Session,
    report_id: str,
    snapshot_type: str
) -> Optional[ReportSnapshot]:
    """获取指定类型的快照"""
    return db.query(ReportSnapshot).filter(
        and_(
            ReportSnapshot.report_id == report_id,
            ReportSnapshot.snapshot_type == snapshot_type
        )
    ).first()


# ==================== 导出记录CRUD ====================

def create_export_record(
    db: Session,
    report_id: str,
    user_id: str,
    format: ExportFormat,
    file_size: int = 0,
    file_path: Optional[str] = None,
    export_options: Optional[Dict] = None
) -> ReportExport:
    """创建导出记录"""
    db_export = ReportExport(
        id=f"exp_{uuid.uuid4().hex[:16]}",
        report_id=report_id,
        user_id=user_id,
        format=format,
        file_size=file_size,
        file_path=file_path,
        export_options=export_options,
        created_at=datetime.utcnow()
    )
    db.add(db_export)
    db.commit()
    db.refresh(db_export)
    return db_export


def update_export_download(
    db: Session,
    export_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[ReportExport]:
    """更新导出下载记录"""
    db_export = db.query(ReportExport).filter(ReportExport.id == export_id).first()
    if not db_export:
        return None
    
    db_export.downloaded_at = datetime.utcnow()
    db_export.ip_address = ip_address
    db_export.user_agent = user_agent
    db.commit()
    db.refresh(db_export)
    return db_export


def get_export_records(
    db: Session,
    report_id: str,
    limit: int = 10
) -> List[ReportExport]:
    """获取报告的导出记录"""
    return db.query(ReportExport).filter(
        ReportExport.report_id == report_id
    ).order_by(desc(ReportExport.created_at)).limit(limit).all()


# ==================== 生成日志CRUD ====================

def create_generation_log(
    db: Session,
    task_id: str,
    message: str,
    log_level: str = "info",
    stage: Optional[str] = None,
    chapter_id: Optional[str] = None,
    details: Optional[Dict] = None
) -> GenerationLog:
    """创建生成日志"""
    db_log = GenerationLog(
        task_id=task_id,
        log_level=log_level,
        stage=stage,
        chapter_id=chapter_id,
        message=message,
        details=details,
        created_at=datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_generation_logs(
    db: Session,
    task_id: str,
    log_level: Optional[str] = None,
    limit: int = 100
) -> List[GenerationLog]:
    """获取生成日志"""
    query = db.query(GenerationLog).filter(GenerationLog.task_id == task_id)
    
    if log_level:
        query = query.filter(GenerationLog.log_level == log_level)
    
    return query.order_by(desc(GenerationLog.created_at)).limit(limit).all()


def cancel_generation_task(db: Session, task_id: str) -> Optional[GenerationTask]:
    """取消生成任务"""
    db_task = get_generation_task(db, task_id)
    if not db_task:
        return None
    
    from datetime import datetime
    db_task.status = "cancelled"
    db_task.cancelled_at = datetime.utcnow()
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_old_generation_logs(db: Session, days: int = 30) -> int:
    """删除旧的生成日志"""
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    result = db.query(GenerationLog).filter(GenerationLog.created_at < cutoff_date).delete()
    db.commit()
    return result
