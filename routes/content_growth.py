"""
routes/content_growth.py — Content Growth Tracking API Endpoint

Permission matrix:
    growth:view     — Admin ✅, Agency ✅, Marketing ✅
    growth:view:own — Creator ✅ (own content only)

Endpoints:
    GET /api/content/{content_id}/growth — Growth timeline for a specific content
"""

from fastapi import APIRouter, Depends

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from services.content_growth_service import ContentGrowthService
from schemas.content_growth import ContentGrowthResponse

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
