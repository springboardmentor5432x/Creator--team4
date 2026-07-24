"""
routes/hashtag.py — Hashtag Analysis API Endpoints

Permission matrix:
    growth:view     — Admin ✅, Agency ✅, Marketing ✅
    growth:view:own — Creator ✅

Endpoints:
    GET /api/hashtags           — List all hashtags (paginated)
    GET /api/hashtags/top       — Top hashtags by frequency
    GET /api/hashtags/trending  — Fastest growing hashtags
    GET /api/hashtags/{hashtag} — Detail for a specific hashtag

Note: /top and /trending are registered BEFORE /{hashtag} to prevent
FastAPI from matching "top" and "trending" as hashtag path parameters.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from services.hashtag_service import HashtagService
from schemas.hashtag import HashtagListResponse, HashtagDetailResponse, HashtagResponse

router = APIRouter(prefix="/api/hashtags", tags=["Hashtag Analysis"])


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

def get_hashtag_service() -> HashtagService:
    return HashtagService()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=HashtagListResponse)
async def list_hashtags(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(
        default=None,
        description="Sort by: frequency, average_reach, average_engagement, growth_percentage"
    ),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort direction"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: HashtagService = Depends(get_hashtag_service),
):
    """
    Return a paginated list of all hashtags with their statistics.

    Sortable by frequency, average_reach, average_engagement, or growth_percentage.
    """
    return await service.get_all_hashtags(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/top", response_model=List[HashtagResponse])
async def get_top_hashtags(
    limit: int = Query(default=10, ge=1, le=50, description="Number of items"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: HashtagService = Depends(get_hashtag_service),
):
    """
    Return the top N hashtags ranked by usage frequency.
    """
    return await service.get_top_hashtags(limit=limit)


@router.get("/trending", response_model=List[HashtagResponse])
async def get_trending_hashtags(
    limit: int = Query(default=10, ge=1, le=50, description="Number of items"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: HashtagService = Depends(get_hashtag_service),
):
    """
    Return the fastest growing hashtags, ranked by growth percentage.
    """
    return await service.get_trending_hashtags(limit=limit)


@router.get("/{hashtag}", response_model=HashtagDetailResponse)
async def get_hashtag_detail(
    hashtag: str,
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: HashtagService = Depends(get_hashtag_service),
):
    """
    Return detailed analytics for a specific hashtag.

    Includes: frequency, average reach, average engagement,
    associated content IDs, and related hashtags.
    """
    return await service.get_hashtag_detail(hashtag)
