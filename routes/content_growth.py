"""
routes/content_growth.py — Content Growth Tracking API Endpoint

Permission matrix:
    growth:view     — Admin ✅, Agency ✅, Marketing ✅
    growth:view:own — Creator ✅ (own content only)

Endpoints:
    GET /api/content/{content_id}/growth — Growth timeline for a specific content
"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from services.content_growth_service import ContentGrowthService
from schemas.content_growth import ContentGrowthResponse, ContentGrowthComparisonResponse

router = APIRouter(prefix="/api/content", tags=["Content Growth Tracking"])


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

def get_content_growth_service() -> ContentGrowthService:
    return ContentGrowthService()


def get_creator_id(current_user: UserModel) -> str:
    """Extract creator_id from the authenticated user."""
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    return current_user.id


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/growth/compare", response_model=ContentGrowthComparisonResponse)
async def compare_content_growth(
    content_ids: List[str] = Query(..., description="List of content IDs to compare (repeat query param: ?content_ids=id1&content_ids=id2)"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: ContentGrowthService = Depends(get_content_growth_service),
):
    """
    Feature 5 — Content Growth Velocity Comparison.
    Compare growth velocity and milestone metrics (7-day views, 30-day likes, 60-day watch time) across content items.
    """
    creator_id = get_creator_id(current_user)
    return await service.compare_content_growth(content_ids, creator_id)


@router.get("/{content_id}/growth", response_model=ContentGrowthResponse)
async def get_content_growth(
    content_id: str,
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: ContentGrowthService = Depends(get_content_growth_service),
):
    """
    Get the complete growth analysis for a specific content item.

    Returns:
        - Views after 7 Days, Likes after 30 Days, Watch Time after 60 Days
        - Growth timeline (daily snapshots)
        - Growth percentage per metric
        - Highest growth day
        - Lowest growth day
        - Graph data for charting (per-metric time series)
    """
    creator_id = get_creator_id(current_user)
    return await service.get_content_growth(
        content_id=content_id,
        creator_id=creator_id,
    )

