"""
routes/financial_insights.py — Financial Insights & Loss Detection Endpoints

Endpoints:
    GET /api/revenue/financial-insights → Returns highest earning month/platform/creator, revenue distribution, monthly average, top source, and loss detection.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, require_any_permission
from permissions import Permission
from models import UserModel
from schemas.revenue import FinancialInsightsResponse
from services.revenue_service import RevenueService

router = APIRouter(prefix="/api/revenue/financial-insights", tags=["Financial Insights"])


def get_service(db: AsyncSession = Depends(get_db)) -> RevenueService:
    return RevenueService(db.sync_session if hasattr(db, "sync_session") else db)


@router.get(
    "",
    response_model=FinancialInsightsResponse,
    summary="Financial insights & loss detection",
    description="Computes highest earning month, highest earning platform, highest earning creator, revenue distribution percentage, average monthly revenue, top revenue source, and loss detection alerts.",
)
async def get_financial_insights(
    creator_id: str = Query(..., description="Target creator profile ID"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_financial_insights(current_user, creator_id)
