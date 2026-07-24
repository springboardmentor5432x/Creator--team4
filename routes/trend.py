"""
routes/trend.py — Trend Detection API Endpoints

Permission matrix:
    growth:view     — Admin ✅, Agency ✅, Marketing ✅
    growth:view:own — Creator ✅ (own content only)

Endpoints:
    GET /api/trend/top — Top N trending content with optional filters
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date, datetime

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from services.trend_service import TrendService
from schemas.trend import TrendingContentResponse

router = APIRouter(prefix="/api/trend", tags=["Trend Detection"])


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

def get_trend_service() -> TrendService:
    return TrendService()


def get_creator_id(current_user: UserModel) -> str:
    """Extract creator_id from the authenticated user."""
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    return current_user.id


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/top", response_model=TrendingContentResponse)
async def get_top_trending(
    platform: Optional[str] = Query(default=None, description="Filter by platform"),
    date_from: Optional[date] = Query(default=None, description="Start date for trend window"),
    date_to: Optional[date] = Query(default=None, description="End date for trend window"),
    content_type: Optional[str] = Query(default=None, description="Filter by content type (video, reel, post)"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of trending items"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: TrendService = Depends(get_trend_service),
):
    """
    Return the top N trending content items, ranked by trend score.

    Trend Score Formula:
        trend_score = 0.30×views + 0.20×likes + 0.20×shares
                    + 0.15×comments + 0.15×engagement_rate

    Scores are normalized to a 0–100 scale using min-max scaling.
    Results are cached in the trend_scores collection.

    Optional filters: platform, date range, content type.
    """
    creator_id = get_creator_id(current_user)

    # Convert date to datetime if provided
    dt_from = datetime.combine(date_from, datetime.min.time()) if date_from else None
    dt_to = datetime.combine(date_to, datetime.max.time()) if date_to else None

    return await service.get_top_trending(
        creator_id=creator_id,
        limit=limit,
        platform=platform,
        date_from=dt_from,
        date_to=dt_to,
        content_type=content_type,
    )
