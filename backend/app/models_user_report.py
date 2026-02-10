# -*- coding: utf-8 -*-
"""
用户报告模块 - 数据模型
基于 Career-Planning SKILL 三层模型架构设计
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class UserReport(Base):
    """
    用户报告元数据表
    存储报告的基本信息和生成元数据
    """
    __tablename__ = "user_reports"
    
    id = Column(String(64), primary_key=True, index=True)  # report_{uuid}
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    
    # 报告类型: SUB_REPORT_A/B/C/D, FULL_REPORT
    report_type = Column(String(30), nullable=False, index=True)
    
    # 报告状态: draft/generating/completed/failed/cancelled/archived
    status = Column(String(20), nullable=False, default='draft', index=True)
    
    # 报告统计
    word_count = Column(Integer, default=0)
    chapter_count = Column(Integer, default=0)
    generation_time = Column(Integer, default=0)  # 生成耗时(秒)
    
    # 生成选项
    detail_level = Column(String(20), default='detailed')  # brief/standard/detailed
    include_charts = Column(Boolean, default=True)
    language = Column(String(10), default='zh-CN')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # 软删除
    
    version = Column(Integer, default=1)
    
    # 关系
    chapters = relationship("ReportChapter", back_populates="report", cascade="all, delete-orphan")
    snapshots = relationship("ReportSnapshot", back_populates="report", cascade="all, delete-orphan")
    exports = relationship("ReportExport", back_populates="report", cascade="all, delete-orphan")
    generation_task = relationship("GenerationTask", back_populates="report", uselist=False)


class ReportChapter(Base):
    """
    报告章节表
    存储报告的各个章节内容
    """
    __tablename__ = "report_chapters"
    
    id = Column(String(64), primary_key=True, index=True)  # ch_{code}_{uuid}
    report_id = Column(String(64), ForeignKey("user_reports.id"), nullable=False, index=True)
    
    # 章节标识
    chapter_code = Column(String(20), nullable=False, index=True)  # 如: 2.1, 4.2.1
    title = Column(String(200), nullable=False)
    parent_id = Column(String(64), ForeignKey("report_chapters.id"), nullable=True)
    order_num = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)  # 层级深度 1-4
    
    # 章节内容 (多格式存储)
    word_count = Column(Integer, default=0)
    content_html = Column(Text, nullable=True)
    content_markdown = Column(Text, nullable=True)
    content_plain = Column(Text, nullable=True)
    
    # 生成状态: pending/generating/completed/failed/retrying
    status = Column(String(20), nullable=False, default='pending', index=True)
    
    # 生成元数据
    generated_at = Column(DateTime, nullable=True)
    generation_time = Column(Integer, default=0)  # 生成耗时(秒)
    llm_model = Column(String(50), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    report = relationship("UserReport", back_populates="chapters")
    parent = relationship("ReportChapter", remote_side="ReportChapter.id", backref="children")
    generation_logs = relationship("GenerationLog", back_populates="chapter")


class GenerationTask(Base):
    """
    报告生成任务表
    存储报告生成任务的状态和进度
    """
    __tablename__ = "generation_tasks"
    
    id = Column(String(64), primary_key=True, index=True)  # task_{uuid}
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    report_id = Column(String(64), ForeignKey("user_reports.id"), nullable=True, unique=True)
    
    report_type = Column(String(30), nullable=False)
    
    # 任务状态: pending/validating/generating/quality_checking/assembling/completed/failed/cancelled/timeout
    status = Column(String(20), nullable=False, default='pending', index=True)
    progress = Column(Integer, default=0)  # 总体进度 0-100
    
    # 当前阶段
    current_stage = Column(String(30), nullable=True)  # prerequisites_check/data_preparation/chapter_generation/...
    current_chapter_id = Column(String(64), ForeignKey("report_chapters.id"), nullable=True)
    
    # 章节统计
    total_chapters = Column(Integer, default=0)
    completed_chapters = Column(Integer, default=0)
    
    # 错误信息
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # 生成选项
    options = Column(JSON, nullable=True)
    
    # 时间戳
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    report = relationship("UserReport", back_populates="generation_task")
    logs = relationship("GenerationLog", back_populates="task", cascade="all, delete-orphan")
    current_chapter = relationship("ReportChapter")


class ReportSnapshot(Base):
    """
    报告数据快照表
    存储报告生成时的用户数据快照，用于追溯报告依据
    """
    __tablename__ = "report_snapshots"
    
    id = Column(String(64), primary_key=True, index=True)
    report_id = Column(String(64), ForeignKey("user_reports.id"), nullable=False, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    
    # 快照类型: user_profile/interface_layer/variable_layer/core_layer/form_history/major_preferences
    snapshot_type = Column(String(30), nullable=False, index=True)
    snapshot_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    report = relationship("UserReport", back_populates="snapshots")


class ReportExport(Base):
    """
    报告导出记录表
    存储报告导出操作的历史记录
    """
    __tablename__ = "report_exports"
    
    id = Column(String(64), primary_key=True, index=True)
    report_id = Column(String(64), ForeignKey("user_reports.id"), nullable=False, index=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    
    # 导出格式: pdf/word/markdown/txt
    format = Column(String(20), nullable=False, index=True)
    file_size = Column(Integer, default=0)  # 文件大小(字节)
    file_path = Column(String(500), nullable=True)
    export_options = Column(JSON, nullable=True)
    
    # 下载记录
    downloaded_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    report = relationship("UserReport", back_populates="exports")


class GenerationLog(Base):
    """
    生成日志表
    存储报告生成的详细日志，用于调试和审计
    """
    __tablename__ = "generation_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String(64), ForeignKey("generation_tasks.id"), nullable=False, index=True)
    
    # 日志级别: debug/info/warning/error/critical
    log_level = Column(String(20), nullable=False, default='info', index=True)
    
    stage = Column(String(30), nullable=True)  # 生成阶段
    chapter_id = Column(String(64), ForeignKey("report_chapters.id"), nullable=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    task = relationship("GenerationTask", back_populates="logs")
    chapter = relationship("ReportChapter", back_populates="generation_logs")


# 导出所有模型
__all__ = [
    'UserReport',
    'ReportChapter',
    'GenerationTask',
    'ReportSnapshot',
    'ReportExport',
    'GenerationLog'
]
