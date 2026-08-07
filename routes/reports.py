"""
routes/reports.py — Report Generation & Download Endpoints

Provides endpoints for:
  - Generating reports on-demand (weekly, monthly, quarterly, annual, custom)
  - Viewing report history
  - Previewing report data JSON
  - Downloading PDF and Excel files
"""

import os
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from services.report_service import ReportService
from schemas.reports import (
    GenerateReportRequest,
    ReportHistoryResponse,
    ReportDetailResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Reports & Export"])


def _get_creator_id(current_user: UserModel) -> str:
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    raise HTTPException(status_code=403, detail="Not authorized as a creator")


def _get_report_service() -> ReportService:
    return ReportService()


# ── Report Generation ───────────────────────────────────────────────────


@router.post("/generate", response_model=Dict[str, Any])
async def generate_report(
    payload: GenerateReportRequest,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ReportService = Depends(_get_report_service),
):
    """
    Generate a performance report on-demand.

    Supported types: weekly, monthly, quarterly, annual, custom.
    Generates PDF & Excel files, stores PostgreSQL history record + MongoDB snapshot.
    Optionally sends an email notification with attached PDF if sendEmail=true.
    """
    creator_id = _get_creator_id(current_user)
    creator_name = getattr(current_user, "full_name", "Creator")
    user_email = getattr(current_user, "email", None)

    report_result = await service.generate_report(
        creator_id=creator_id,
        report_type=payload.reportType.value,
        start_date=payload.startDate,
        end_date=payload.endDate,
        send_email=payload.sendEmail,
        user_email=user_email,
        creator_name=creator_name,
    )
    return report_result


# ── Report History ───────────────────────────────────────────────────────


@router.get("/history", response_model=ReportHistoryResponse)
async def get_report_history(
    report_type: Optional[str] = Query(None, description="Filter by report type (weekly/monthly/quarterly/annual)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ReportService = Depends(_get_report_service),
):
    """Fetch history of generated reports for the current creator."""
    creator_id = _get_creator_id(current_user)
    return await service.get_report_history(
        creator_id=creator_id,
        report_type=report_type,
        limit=limit,
        offset=offset,
    )


# ── Report Preview / Details ─────────────────────────────────────────────


@router.get("/{report_id}", response_model=Dict[str, Any])
async def get_report_detail(
    report_id: int,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ReportService = Depends(_get_report_service),
):
    """Fetch single report details and JSON snapshot for UI rendering."""
    creator_id = _get_creator_id(current_user)
    report = await service.get_report_preview(report_id, creator_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or access denied")
    return report


# ── Report Downloads (PDF & Excel) ──────────────────────────────────────


@router.get("/{report_id}/download/pdf")
async def download_report_pdf(
    report_id: int,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ReportService = Depends(_get_report_service),
):
    """Download the PDF report file."""
    creator_id = _get_creator_id(current_user)
    metadata = await service.report_repo.get_report_by_id(report_id)

    if not metadata or metadata.get("creatorId") != creator_id:
        raise HTTPException(status_code=404, detail="Report not found or access denied")

    pdf_path = metadata.get("pdfPath")
    if not pdf_path or not os.path.exists(pdf_path):
        # Re-generate on demand if missing from disk
        preview = await service.get_report_preview(report_id, creator_id)
        if preview and preview.get("data"):
            pdf_path = service.pdf_generator.generate_pdf(report_id, preview["data"])
            await service.report_repo.update_report_files(report_id, pdf_path=pdf_path)
        else:
            raise HTTPException(status_code=404, detail="PDF file not available")

    filename = os.path.basename(pdf_path)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )


@router.get("/{report_id}/download/excel")
async def download_report_excel(
    report_id: int,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ReportService = Depends(_get_report_service),
):
    """Download the Excel report file (.xlsx)."""
    creator_id = _get_creator_id(current_user)
    metadata = await service.report_repo.get_report_by_id(report_id)

    if not metadata or metadata.get("creatorId") != creator_id:
        raise HTTPException(status_code=404, detail="Report not found or access denied")

    excel_path = metadata.get("excelPath")
    if not excel_path or not os.path.exists(excel_path):
        # Re-generate on demand if missing from disk
        preview = await service.get_report_preview(report_id, creator_id)
        if preview and preview.get("data"):
            excel_path = service.excel_generator.generate_excel(report_id, preview["data"])
            await service.report_repo.update_report_files(report_id, excel_path=excel_path)
        else:
            raise HTTPException(status_code=404, detail="Excel file not available")

    filename = os.path.basename(excel_path)
    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )
