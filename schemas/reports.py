"""
schemas/reports.py — Pydantic schemas for Report Generation, Export, and History.

Models for:
  - Report generation request
  - Report summary / preview (weekly, monthly, quarterly, annual)
  - Report history item & paginated response
  - File download link response
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class ReportTypeEnum(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"


class GenerateReportRequest(BaseModel):
    """Request payload to generate a report on-demand."""
    reportType: ReportTypeEnum
    startDate: Optional[date] = Field(None, description="Start date for custom range (YYYY-MM-DD)")
    endDate: Optional[date] = Field(None, description="End date for custom range (YYYY-MM-DD)")
    sendEmail: bool = Field(False, description="Whether to email the report to the user")


class ReportSummaryMetrics(BaseModel):
    """Core KPI metrics summary."""
    totalViews: int = 0
    newFollowers: int = 0
    engagementRate: float = 0.0
    totalRevenue: float = 0.0
    totalPosts: int = 0


class BestContentItem(BaseModel):
    """Top performing post details."""
    postId: Optional[str] = None
    title: Optional[str] = None
    platform: Optional[str] = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    engagementRate: float = 0.0


class TopPlatformItem(BaseModel):
    """Highest performing platform summary."""
    platform: str
    views: int = 0
    followers: int = 0
    revenue: float = 0.0
    engagementRate: float = 0.0


class ReportDataPayload(BaseModel):
    """Full aggregated report data payload."""
    reportType: str
    periodLabel: str
    startDate: str
    endDate: str
    creatorName: str
    creatorId: str
    summaryMetrics: ReportSummaryMetrics
    bestContent: Optional[BestContentItem] = None
    topPlatform: Optional[TopPlatformItem] = None
    platformBreakdown: List[Dict[str, Any]] = []
    revenueSummary: Dict[str, Any] = {}
    audienceSummary: Dict[str, Any] = {}
    growthComparison: Dict[str, Any] = {}


class GeneratedReportRecord(BaseModel):
    """Metadata for a report row in PostgreSQL generated_reports."""
    id: int
    creatorId: str
    reportName: str
    reportType: str
    periodLabel: str
    startDate: date
    endDate: date
    pdfUrl: Optional[str] = None
    excelUrl: Optional[str] = None
    status: str
    createdAt: datetime


class ReportHistoryResponse(BaseModel):
    """Paginated list of generated reports."""
    creatorId: str
    reports: List[GeneratedReportRecord]
    total: int


class ReportDetailResponse(BaseModel):
    """Detailed report preview containing metadata + full snapshot payload."""
    metadata: GeneratedReportRecord
    data: ReportDataPayload
