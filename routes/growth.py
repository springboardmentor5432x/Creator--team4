"""
routes/growth.py — Growth Monitoring API Endpoints

Permission matrix:
    growth:view     — Admin ✅, Agency ✅, Marketing ✅
    growth:view:own — Creator ✅ (own data only)

Endpoints:
    GET /api/growth/daily    — Daily growth summary
    GET /api/growth/weekly   — Weekly aggregated growth
    GET /api/growth/monthly  — Monthly aggregated growth
    GET /api/growth/yearly   — Yearly aggregated growth
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from datetime import date

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from services.growth_service import GrowthService
from schemas.growth import GrowthSummaryResponse, GrowthQueryParams

router = APIRouter(prefix="/api/growth", tags=["Growth Monitoring"])


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

def get_growth_service() -> GrowthService:
    return GrowthService()


def get_creator_id(current_user: UserModel) -> str:
    """Extract creator_id from the authenticated user."""
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    # Admin/Agency/Marketing may pass creator_id as query param
    # For now, fallback to user id
    return current_user.id


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/daily", response_model=GrowthSummaryResponse)
async def get_daily_growth(
    platform: Optional[str] = Query(default=None, description="Filter by platform"),
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: GrowthService = Depends(get_growth_service),
):
    """
    Get daily growth metrics with total growth, percentage changes,
    day-by-day history, and trend direction.

    Defaults to the last 30 days if no date range is specified.
    """
    creator_id = get_creator_id(current_user)
    params = GrowthQueryParams(
        platform=platform, start_date=start_date, end_date=end_date
    )
    return await service.get_daily_growth(creator_id, params)


@router.get("/weekly", response_model=GrowthSummaryResponse)
async def get_weekly_growth(
    platform: Optional[str] = Query(default=None, description="Filter by platform"),
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: GrowthService = Depends(get_growth_service),
):
    """
    Get weekly aggregated growth metrics.

    Groups daily data by ISO week. Defaults to the last 90 days.
    """
    creator_id = get_creator_id(current_user)
    params = GrowthQueryParams(
        platform=platform, start_date=start_date, end_date=end_date
    )
    return await service.get_weekly_growth(creator_id, params)


@router.get("/monthly", response_model=GrowthSummaryResponse)
async def get_monthly_growth(
    platform: Optional[str] = Query(default=None, description="Filter by platform"),
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: GrowthService = Depends(get_growth_service),
):
    """
    Get monthly aggregated growth metrics.

    Groups daily data by calendar month. Defaults to the last 365 days.
    """
    creator_id = get_creator_id(current_user)
    params = GrowthQueryParams(
        platform=platform, start_date=start_date, end_date=end_date
    )
    return await service.get_monthly_growth(creator_id, params)


@router.get("/yearly", response_model=GrowthSummaryResponse)
async def get_yearly_growth(
    platform: Optional[str] = Query(default=None, description="Filter by platform"),
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: GrowthService = Depends(get_growth_service),
):
    """
    Get yearly aggregated growth metrics.

    Groups daily data by calendar year. Defaults to the last 5 years.
    """
    creator_id = get_creator_id(current_user)
    params = GrowthQueryParams(
        platform=platform, start_date=start_date, end_date=end_date
    )
    return await service.get_yearly_growth(creator_id, params)
