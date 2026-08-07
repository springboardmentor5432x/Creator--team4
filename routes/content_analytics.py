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
from datetime import datetime

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
    search: Optional[str] = Query(None, description="Search by content title (case-insensitive)"),
    platform: Optional[str] = Query(None, description="Filter by platform name (e.g. youtube, instagram)"),
    date_from: Optional[datetime] = Query(None, description="Filter: published on or after this date (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Filter: published on or before this date (ISO 8601)"),
    sort_by: str = Query("publishedAt", description="Sort field: publishedAt | title | platform"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction: asc or desc"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return all creator content with optional search, filter, and sort. Requires analytics:view."""
    creator_id = get_creator_id(current_user)
    return await service.get_all_content(
        creator_id,
        search=search,
        platform=platform,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )

@router.get("/top-performing", response_model=List[Dict])
async def get_top_performing_content(
    limit: int = Query(10, ge=1, le=100),
    platform: Optional[str] = Query(None, description="Filter by platform name"),
    sort_by: str = Query(
        "performanceScore",
        description="Rank by: performanceScore | views | likes | comments | shares | watchTime | engagementRate",
    ),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Return top content ranked by a specific metric. Requires analytics:view."""
    valid_sort = {"performanceScore", "views", "likes", "comments", "shares", "watchTime", "engagementRate"}
    if sort_by not in valid_sort:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by value. Choose from: {', '.join(sorted(valid_sort))}"
        )
    creator_id = get_creator_id(current_user)
    return await service.get_top_performing_content(creator_id, limit, platform, sort_by)

@router.get("/compare", response_model=Dict)
async def compare_posts(
    post_ids: List[str] = Query(
        ...,
        description="List of 2 or more post IDs to compare (repeat param: ?post_ids=id1&post_ids=id2)",
        min_length=2,
    ),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service)
):
    """Compare 2 or more content posts side by side. Requires analytics:view."""
    if len(post_ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 post_ids for comparison")
    creator_id = get_creator_id(current_user)
    return await service.compare_posts(creator_id, post_ids)

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
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
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


# ── Content-Analytics Linkage ─────────────────────────────────────────────


@router.get("/{postId}/analytics", response_model=Dict)
async def get_content_full_analytics(
    postId: str,
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service),
):
    """
    Return full analytics for a specific content item (video, reel, or post).

    Combines:
      - Content metadata (title, type, platform, published date, thumbnail)
      - Latest metrics snapshot (views, likes, comments, shares, reach, watchTime)
      - Historical metric snapshots for trend analysis

    Use this when a user selects a specific piece of content to view
    its detailed performance data.
    """
    creator_id = get_creator_id(current_user)
    post       = await service.get_content(creator_id, postId)
    metrics    = await service.get_content_metrics(creator_id, postId)
    history    = await service.get_content_history(creator_id, postId)

    # Serialize MongoDB ObjectIds
    post["_id"]     = str(post.get("_id", ""))
    metrics["_id"]  = str(metrics.get("_id", ""))
    for h in history:
        h["_id"] = str(h.get("_id", ""))

    return {
        "content": post,
        "latestMetrics": metrics,
        "metricsHistory": history,
        "fetchedAt": datetime.utcnow().isoformat(),
    }


@router.get("/platform/{platform}", response_model=Dict)
async def get_platform_content_with_metrics(
    platform: str,
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    sort_by: str = Query(
        "views",
        description="Sort metric: views | likes | comments | shares | engagementRate",
    ),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: ContentAnalyticsService = Depends(get_content_service),
):
    """
    List all content posts for a given platform, each enriched with its latest metrics.

    This endpoint powers the content management integration view — a table
    or grid showing every piece of content published on a platform with
    its performance numbers directly alongside.

    Supported platforms: youtube, instagram, facebook, linkedin, x

    Metrics included per post:
      - Views, Likes, Comments, Shares, Saves
      - Watch Time (YouTube), Reach, Impressions
      - Engagement Rate
    """
    creator_id = get_creator_id(current_user)

    # Fetch posts for the platform
    posts = await service.get_all_content(
        creator_id,
        platform=platform,
        sort_by="publishedAt",
        sort_order="desc",
    )

    # Enrich each post with its latest metrics
    enriched = []
    for post in posts[:limit]:
        post_id = str(post.get("_id", ""))
        post["_id"] = post_id
        post.pop("accessToken", None)   # safety strip

        try:
            metrics = await service.get_content_metrics(creator_id, post_id)
            metrics["_id"] = str(metrics.get("_id", ""))
        except Exception:
            metrics = {}

        enriched.append({
            "content": post,
            "metrics": metrics,
        })

    return {
        "platform": platform,
        "creatorId": creator_id,
        "posts": enriched,
        "total": len(enriched),
        "fetchedAt": datetime.utcnow().isoformat(),
    }
