"""
routes/ad_revenue.py — Ad Revenue Endpoints

Endpoints:
    POST /api/revenue/ad         → Record ad revenue from platforms (YouTube, IG, TikTok, FB, LinkedIn)
    GET  /api/revenue/ad/summary → Get today, weekly, monthly, platform-wise earnings breakdown
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, require_any_permission
from permissions import Permission
from models import UserModel
from schemas.revenue import (
    AdRevenueCreate,
    AdRevenueSummaryResponse,
    RevenueTransactionResponse,
)
from services.revenue_service import RevenueService

router = APIRouter(prefix="/api/revenue/ad", tags=["Ad Revenue Monitoring"])


def get_service(db: AsyncSession = Depends(get_db)) -> RevenueService:
    return RevenueService(db.sync_session if hasattr(db, "sync_session") else db)


@router.post(
    "",
    response_model=RevenueTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record ad revenue",
    description="Records ad revenue from supported platforms (YouTube, Instagram, TikTok, Facebook, LinkedIn).",
)
async def record_ad_revenue(
    payload: AdRevenueCreate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_CREATE, Permission.REVENUE_CREATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.record_ad_revenue(current_user, payload.model_dump())


@router.get(
    "/summary",
    response_model=AdRevenueSummaryResponse,
    summary="Ad revenue earnings summary",
    description="Returns today's, weekly, monthly, and platform-wise ad revenue totals.",
)
async def get_ad_revenue_summary(
    creator_id: str = Query(..., description="Target creator profile ID"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_ad_revenue_summary(current_user, creator_id)
