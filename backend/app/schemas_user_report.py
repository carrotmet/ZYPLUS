# -*- coding: utf-8 -*-
"""
用户报告模块 - Pydantic数据验证模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== 枚举定义 ====================

class ReportType(str, Enum):
    """报告类型枚举"""
    SUB_REPORT_A = "SUB_REPORT_A"  # 用户画像深度分析报告
    SUB_REPORT_B = "SUB_REPORT_B"  # 用户表单分析报告
    SUB_REPORT_C = "SUB_REPORT_C"  # 三层职业规划建模报告
    SUB_REPORT_D = "SUB_REPORT_D"  # 分层递进行动体系报告
    FULL_REPORT = "FULL_REPORT"      # 职业规划完整报告


class ReportStatus(str, Enum):
    """报告状态枚举"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    VALIDATING = "validating"
    GENERATING = "generating"
    QUALITY_CHECKING = "quality_checking"
    ASSEMBLING = "assembling"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ChapterStatus(str, Enum):
    """章节状态枚举"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ExportFormat(str, Enum):
    """导出格式枚举"""
    PDF = "pdf"
    WORD = "word"
    MARKDOWN = "markdown"
    TXT = "txt"


class DetailLevel(str, Enum):
    """详细程度枚举"""
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"


# ==================== 基础模型 ====================

class ReportChapterBase(BaseModel):
    """章节基础模型"""
    chapter_code: str = Field(..., description="章节代码，如2.1, 4.2.1")
    title: str = Field(..., description="章节标题")
    parent_id: Optional[str] = Field(None, description="父章节ID")
    order_num: int = Field(0, description="排序序号")
    level: int = Field(1, description="层级深度 1-4")


class ReportChapterCreate(ReportChapterBase):
    """章节创建模型"""
    report_id: str
    word_count: int = 0
    status: ChapterStatus = ChapterStatus.PENDING


class ReportChapterResponse(ReportChapterBase):
    """章节响应模型"""
    id: str
    report_id: str
    word_count: int
    status: ChapterStatus
    generated_at: Optional[datetime] = None
    generation_time: int = 0
    llm_model: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReportChapterContent(BaseModel):
    """章节内容模型"""
    id: str
    report_id: str
    chapter_code: str
    title: str
    content_html: Optional[str] = None
    content_markdown: Optional[str] = None
    content_plain: Optional[str] = None
    word_count: int
    generated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChapterNavigation(BaseModel):
    """章节导航模型"""
    prev: Optional[Dict[str, str]] = None
    next: Optional[Dict[str, str]] = None


# ==================== 报告模型 ====================

class UserReportBase(BaseModel):
    """报告基础模型"""
    title: str = Field(..., description="报告标题")
    report_type: ReportType
    detail_level: DetailLevel = DetailLevel.DETAILED
    include_charts: bool = True
    language: str = "zh-CN"


class UserReportCreate(UserReportBase):
    """报告创建模型"""
    user_id: str
    id: Optional[str] = None
    status: ReportStatus = ReportStatus.DRAFT


class UserReportUpdate(BaseModel):
    """报告更新模型"""
    title: Optional[str] = None
    status: Optional[ReportStatus] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    generation_time: Optional[int] = None
    completed_at: Optional[datetime] = None


class UserReportMetadata(BaseModel):
    """报告元数据模型"""
    word_count: int
    chapter_count: int
    generation_time: int
    detail_level: DetailLevel
    include_charts: bool


class UserReportResponse(BaseModel):
    """报告列表响应模型"""
    id: str
    title: str
    report_type: ReportType
    status: ReportStatus
    word_count: int
    chapter_count: int
    created_at: datetime
    thumbnail_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserReportDetail(BaseModel):
    """报告详情响应模型"""
    id: str
    title: str
    report_type: ReportType
    status: ReportStatus
    metadata: UserReportMetadata
    chapters: List[ReportChapterResponse]
    created_at: datetime
    data_snapshot: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class UserReportContent(BaseModel):
    """报告内容响应模型"""
    report_id: str
    chapter_id: Optional[str] = None
    format: str
    content: str
    word_count: int
    toc: List[Dict[str, Any]] = []


# ==================== 生成任务模型 ====================

class GenerationOptions(BaseModel):
    """生成选项模型"""
    include_charts: bool = True
    detail_level: DetailLevel = DetailLevel.DETAILED
    language: str = "zh-CN"


class GenerationTaskCreate(BaseModel):
    """生成任务创建模型"""
    user_id: str
    report_type: ReportType
    report_id: Optional[str] = None
    options: Optional[GenerationOptions] = None


class GenerationProgress(BaseModel):
    """生成进度模型"""
    overall: int = Field(0, description="总体进度 0-100")
    current_stage: Optional[str] = None
    completed_chapters: int = 0
    total_chapters: int = 0
    current_chapter: Optional[Dict[str, Any]] = None


class GenerationTaskResponse(BaseModel):
    """生成任务响应模型"""
    task_id: str
    report_id: Optional[str] = None
    report_type: ReportType
    status: TaskStatus
    progress: GenerationProgress
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    elapsed_seconds: Optional[int] = None
    error: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class GenerationTaskResult(BaseModel):
    """生成任务结果模型"""
    report_url: str
    word_count: int
    generation_time: int


# ==================== 条件检查模型 ====================

class PrerequisiteItem(BaseModel):
    """条件检查项模型"""
    id: str
    name: str
    description: str
    status: str  # passed/failed
    current_value: Optional[Any] = None
    required_value: Optional[str] = None
    weight: int
    recommendation: Optional[str] = None


class PrerequisitesResult(BaseModel):
    """条件检查结果模型"""
    report_type: ReportType
    can_generate: bool
    overall_progress: int
    prerequisites: List[PrerequisiteItem]
    next_steps: List[str] = []


class PrerequisitesValidation(BaseModel):
    """条件验证请求模型"""
    report_type: ReportType


class PrerequisitesValidationResponse(BaseModel):
    """条件验证响应模型"""
    can_generate: bool
    estimated_time: Optional[int] = None  # 预估生成时间(秒)
    estimated_words: Optional[int] = None  # 预估字数
    failed_conditions: Optional[List[Dict[str, Any]]] = None


# ==================== 导出模型 ====================

class ExportOptions(BaseModel):
    """导出选项模型"""
    include_toc: bool = True
    include_cover: bool = True
    page_size: str = "A4"
    watermark: Optional[Dict[str, Any]] = None
    template: Optional[str] = "default"


class ExportRequest(BaseModel):
    """导出请求模型"""
    options: Optional[ExportOptions] = None


class ExportResponse(BaseModel):
    """导出响应模型"""
    export_id: str
    format: ExportFormat
    file_url: str
    file_size: int
    expires_at: datetime


# ==================== 列表与分页模型 ====================

class ReportListParams(BaseModel):
    """报告列表查询参数"""
    page: int = 1
    page_size: int = 10
    report_type: Optional[ReportType] = None
    sort_by: str = "created_at"  # created_at/word_count
    sort_order: str = "desc"  # asc/desc


class ReportListResponse(BaseModel):
    """报告列表响应模型"""
    total: int
    page: int
    page_size: int
    reports: List[UserReportResponse]


class GenerationHistoryParams(BaseModel):
    """生成历史查询参数"""
    page: int = 1
    page_size: int = 20
    status: Optional[str] = None  # 多个状态用逗号分隔


class GenerationHistoryItem(BaseModel):
    """生成历史项模型"""
    task_id: str
    report_id: Optional[str] = None
    report_type: ReportType
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    generation_time: Optional[int] = None
    error: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class GenerationHistoryResponse(BaseModel):
    """生成历史响应模型"""
    total: int
    page: int
    page_size: int
    history: List[GenerationHistoryItem]


# ==================== 报告中心模型 ====================

class UserStats(BaseModel):
    """用户统计模型"""
    total_reports: int
    last_generated_at: Optional[datetime] = None
    profile_completeness: int


class PrerequisitesSummary(BaseModel):
    """条件摘要模型"""
    can_generate: bool
    progress: int


class ActiveTask(BaseModel):
    """进行中的任务模型"""
    task_id: str
    status: TaskStatus
    progress: int


class ReportCenterInit(BaseModel):
    """报告中心初始化数据模型"""
    user_stats: UserStats
    prerequisites_summary: Dict[str, PrerequisitesSummary]
    recent_reports: List[UserReportResponse]
    active_task: Optional[ActiveTask] = None


# ==================== WebSocket消息模型 ====================

class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""
    type: str  # progress_update/chapter_complete/stage_change/completed/error/cancelled
    timestamp: datetime
    data: Dict[str, Any]


class ChapterProgressUpdate(BaseModel):
    """章节进度更新模型"""
    id: str
    title: str
    status: ChapterStatus
    progress: int
    word_count: int


class GenerationProgressUpdate(BaseModel):
    """生成进度更新模型"""
    overall_progress: int
    current_stage: str
    chapter_update: Optional[ChapterProgressUpdate] = None
