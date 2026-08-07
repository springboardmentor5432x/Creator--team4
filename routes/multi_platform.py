"""
routes/multi_platform.py — Multi-Platform Analytics Dashboard Endpoints

Provides endpoints for cross-platform analytics aggregation and comparison.
Data is sourced from the platform_analytics_raw MongoDB collection which
is populated by the SyncService.

Permission matrix:
  analytics:view — Admin ✅, Agency ✅, Creator Own, Marketing ✅

Endpoints:
  GET  /api/analytics/overview           → Latest snapshot per connected platform + totals
  GET  /api/analytics/compare            → Side-by-side metric comparison
  GET  /api/analytics/{platform}/history → Time-series for one platform (last N days)
"""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from repositories.platform_analytics_repository import PlatformAnalyticsRepository
from schemas.platform_analytics import (
    MultiPlatformOverview,
    MultiPlatformTotals,
    PlatformSnapshot,
    MultiPlatformComparison,
    MetricComparison,
    PlatformAnalyticsHistory,
    PlatformHistoryPoint,
)
from schemas.social_media import PlatformEnum

router = APIRouter(prefix="/api/analytics", tags=["Multi-Platform Analytics"])


def _get_creator_id(current_user: UserModel) -> str:
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    raise HTTPException(status_code=403, detail="Not authorized as a creator")


def _get_analytics_repo() -> PlatformAnalyticsRepository:
    return PlatformAnalyticsRepository()


# ── Multi-Platform Overview ───────────────────────────────────────────────


@router.get("/overview", response_model=MultiPlatformOverview)
async def get_analytics_overview(
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    repo: PlatformAnalyticsRepository = Depends(_get_analytics_repo),
):
    """
    Return the latest analytics snapshot for every connected platform.

    This is the primary data source for the multi-platform analytics
    dashboard card row. Each card shows followers, views, engagement
    rate, and last-synced time for one platform.

    Also returns aggregated totals (total followers across all platforms,
    total views, average engagement rate, etc.) for the dashboard header.

    If no snapshots have been synced yet, returns empty lists/zero totals.
    Connect a platform and trigger a sync first.
    """
    creator_id = _get_creator_id(current_user)

    raw_snapshots = await repo.get_latest_all_platforms(creator_id)
    raw_totals    = await repo.get_multi_platform_totals(creator_id)

    platforms: List[PlatformSnapshot] = []
    for snap in raw_snapshots:
        platforms.append(PlatformSnapshot(
            platform=snap.get("platform", ""),
            accountId=snap.get("accountId", ""),
            accountName=snap.get("accountName"),
            profileUrl=snap.get("profileUrl"),
            profilePicture=snap.get("profilePicture"),
            followers=snap.get("followers", 0) or 0,
            views=snap.get("views", 0) or 0,
            likes=snap.get("likes", 0) or 0,
            comments=snap.get("comments", 0) or 0,
            shares=snap.get("shares", 0) or 0,
            reach=snap.get("reach"),
            impressions=snap.get("impressions"),
            engagementRate=snap.get("engagementRate", 0.0) or 0.0,
            watchTime=snap.get("watchTime"),
            totalVideos=snap.get("totalVideos"),
            profileVisits=snap.get("profileVisits"),
            reelPlays=snap.get("reelPlays"),
            storyViews=snap.get("storyViews"),
            pageLikes=snap.get("pageLikes"),
            postImpressions=snap.get("postImpressions"),
            reactions=snap.get("reactions"),
            tweetImpressions=snap.get("tweetImpressions"),
            reposts=snap.get("reposts"),
            replies=snap.get("replies"),
            periodDays=snap.get("periodDays", 30),
            snapshotDate=snap.get("snapshotDate"),
            lastSyncedAt=snap.get("recordedAt"),
            isSampleData=snap.get("isSampleData", False),
        ))

    totals = MultiPlatformTotals(
        totalFollowers=raw_totals.get("totalFollowers", 0),
        totalViews=raw_totals.get("totalViews", 0),
        totalLikes=raw_totals.get("totalLikes", 0),
        totalComments=raw_totals.get("totalComments", 0),
        totalShares=raw_totals.get("totalShares", 0),
        totalReach=raw_totals.get("totalReach", 0),
        totalImpressions=raw_totals.get("totalImpressions", 0),
        averageEngagementRate=raw_totals.get("averageEngagementRate", 0.0),
        connectedPlatforms=raw_totals.get("connectedPlatforms", 0),
    )

    return MultiPlatformOverview(
        creatorId=creator_id,
        platforms=platforms,
        totals=totals,
        generatedAt=datetime.utcnow(),
    )


# ── Multi-Platform Comparison ─────────────────────────────────────────────


@router.get("/compare", response_model=MultiPlatformComparison)
async def compare_platforms(
    metrics: str = Query(
        "followers,views,likes,comments,shares,engagementRate",
        description="Comma-separated metrics to compare across platforms",
    ),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    repo: PlatformAnalyticsRepository = Depends(_get_analytics_repo),
):
    """
    Side-by-side metric comparison across all connected platforms.

    Returns a list of metrics, each with values per platform. This
    powers comparison bar charts and tables in the dashboard.

    Example response:
    {
      "metrics": [
        {"metric": "followers", "values": {"youtube": 12500, "instagram": 8400}},
        {"metric": "views",     "values": {"youtube": 85000, "instagram": 24000}}
      ]
    }
    """
    creator_id = _get_creator_id(current_user)
    raw_snapshots = await repo.get_latest_all_platforms(creator_id)

    requested_metrics = [m.strip() for m in metrics.split(",") if m.strip()]
    comparison: List[MetricComparison] = []

    for metric_name in requested_metrics:
        values: Dict[str, int] = {}
        for snap in raw_snapshots:
            platform = snap.get("platform", "")
            raw_val  = snap.get(metric_name)
            if raw_val is not None:
                values[platform] = int(raw_val) if isinstance(raw_val, float) else (raw_val or 0)
        if values:
            comparison.append(MetricComparison(metric=metric_name, values=values))

    return MultiPlatformComparison(
        creatorId=creator_id,
        metrics=comparison,
        snapshotDate=datetime.utcnow(),
    )


# ── Platform History (time-series) ────────────────────────────────────────


@router.get("/{platform}/history", response_model=PlatformAnalyticsHistory)
async def get_platform_history(
    platform: PlatformEnum,
    days: int = Query(30, ge=7, le=90, description="Number of days of history to return"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    repo: PlatformAnalyticsRepository = Depends(_get_analytics_repo),
):
    """
    Return time-series analytics history for a specific platform.

    Returns one data point per day synced, sorted ascending by date.
    Use this to power line/area charts showing growth trends over time.

    Note: Data points only exist for days when a sync was performed.
    If the scheduler has been running for 7 days, you will get 7 points.
    """
    creator_id = _get_creator_id(current_user)
    history = await repo.get_history(creator_id, platform.value, days=days)

    data_points: List[PlatformHistoryPoint] = []
    for snap in history:
        data_points.append(PlatformHistoryPoint(
            date=snap.get("snapshotDate", snap.get("recordedAt", datetime.utcnow())),
            followers=snap.get("followers", 0) or 0,
            views=snap.get("views", 0) or 0,
            likes=snap.get("likes", 0) or 0,
            comments=snap.get("comments", 0) or 0,
            shares=snap.get("shares", 0) or 0,
            reach=snap.get("reach"),
            impressions=snap.get("impressions"),
            engagementRate=snap.get("engagementRate", 0.0) or 0.0,
        ))

    return PlatformAnalyticsHistory(
        creatorId=creator_id,
        platform=platform.value,
        periodDays=days,
        dataPoints=data_points,
    )
