"""
routes/content_analytics.py — Content & Analytics Endpoints

Permission matrix applied:
    content:create  — Admin ✅, Agency ✅, Creator ✅
    content:update  — Admin ✅, Agency ✅, Creator Own
    content:delete  — Admin ✅, Agency ✅, Creator Own
    analytics:view  — Admin ✅, Agency ✅, Creator Own, Marketing ✅
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional

from authorization import (
    require_any_permission,
    require_permission,
    get_access_level,
    verify_ownership,
)
from permissions import Permission
from models import UserModel
from services.content_analytics_service import ContentAnalyticsService
from schemas.metrics import MetricSyncRequest

router = APIRouter(prefix="/api/content", tags=["Content Analytics"])

def get_content_service() -> ContentAnalyticsService:
    return ContentAnalyticsService()

def get_creator_id(current_user: UserModel) -> str:
    # Based on the PostgreSQL schema, users with creator profile will have it loaded
    # However, since `creator_profile` is a relationship, we should fetch it or query it.
    # To keep it simple, we assume `current_user.creator_profile.id` is accessible if role is Creator.
    if hasattr(current_user, 'creator_profile') and current_user.creator_profile:
        return current_user.creator_profile.id
    # Fallback to agency logic or admin if necessary
    raise HTTPException(status_code=403, detail="Not authorized as a creator")

@router.get("", response_model=List[Dict])
async def get_all_content(
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return all creator content. Requires analytics:view or analytics:view:own."""
    creator_id = get_creator_id(current_user)
    return await service.get_all_content(creator_id)

@router.get("/top-performing", response_model=List[Dict])
async def get_top_performing_content(
    limit: int = Query(10, ge=1, le=100),
    platform: Optional[str] = None,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return top content based on performance score. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.get_top_performing_content(creator_id, limit, platform)

@router.get("/compare", response_model=Dict)
async def compare_posts(
    post1: str,
    post2: str,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Compare two content posts. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.compare_posts(creator_id, post1, post2)

@router.get("/reach-analysis", response_model=Dict)
async def reach_analysis(
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return reach analysis metrics. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.reach_analysis(creator_id)

@router.get("/performance-trends", response_model=List[Dict])
async def get_performance_trends(
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return performance trends. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.get_performance_trends(creator_id, period)

@router.get("/dashboard-summary", response_model=Dict)
async def get_dashboard_summary(
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return dashboard summary metrics. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.get_dashboard_summary(creator_id)

@router.get("/{postId}", response_model=Dict)
async def get_single_content(
    postId: str,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return single content. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.get_content(creator_id, postId)

@router.get("/{postId}/metrics", response_model=Dict)
async def get_content_metrics(
    postId: str,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return latest metrics for a post. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.get_content_metrics(creator_id, postId)

@router.get("/{postId}/history", response_model=List[Dict])
async def get_content_history(
    postId: str,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return all historical snapshots for a post. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.get_content_history(creator_id, postId)

@router.post("/sync", response_model=Dict)
async def sync_metrics(
    request: MetricSyncRequest,
    current_user: UserModel = Depends(require_permission(Permission.CONTENT_CREATE)),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Accept analytics data and store new snapshot. Requires content:create."""
    creator_id = get_creator_id(current_user)
    snapshot_id = await service.sync_metrics(creator_id, request)
    return {"message": "Metrics synced successfully", "snapshotId": snapshot_id}

