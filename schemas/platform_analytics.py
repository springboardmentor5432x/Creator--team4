"""
schemas/platform_analytics.py — Pydantic schemas for platform analytics snapshots.

Defines normalized response models for:
  - Per-platform analytics snapshots stored in platform_analytics_raw
  - Multi-platform aggregated overview
  - Per-content analytics enriched response
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ---------------------------------------------------------------------------
# Per-Platform Snapshot (normalized across all 5 platforms)
# ---------------------------------------------------------------------------

class PlatformSnapshot(BaseModel):
    """
    Normalized analytics snapshot for one connected platform.

    Fields that are platform-specific are Optional and will be None
    when not applicable (e.g. watchTime is only for YouTube).
    """
    platform: str                               # "youtube" | "instagram" | "facebook" | "linkedin" | "x"
    accountId: str
    accountName: Optional[str] = None
    profileUrl: Optional[str] = None
    profilePicture: Optional[str] = None

    # Universal metrics (available on all or most platforms)
    followers: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    reach: Optional[int] = None
    impressions: Optional[int] = None
    engagementRate: float = 0.0

    # YouTube-specific
    watchTime: Optional[float] = None          # minutes watched
    totalVideos: Optional[int] = None

    # Instagram-specific
    profileVisits: Optional[int] = None
    reelPlays: Optional[int] = None
    storyViews: Optional[int] = None

    # Facebook-specific
    pageLikes: Optional[int] = None

    # LinkedIn-specific
    postImpressions: Optional[int] = None
    reactions: Optional[int] = None

    # X (Twitter)-specific
    tweetImpressions: Optional[int] = None
    reposts: Optional[int] = None
    replies: Optional[int] = None

    # Metadata
    periodDays: int = 30
    snapshotDate: Optional[datetime] = None
    lastSyncedAt: Optional[datetime] = None
    isSampleData: bool = False                 # True when API is unavailable and mock data is used


# ---------------------------------------------------------------------------
# Multi-Platform Overview (aggregated across all connected platforms)
# ---------------------------------------------------------------------------

class MultiPlatformTotals(BaseModel):
    """Aggregated cross-platform totals for the dashboard header."""
    totalFollowers: int = 0
    totalViews: int = 0
    totalLikes: int = 0
    totalComments: int = 0
    totalShares: int = 0
    totalReach: int = 0
    totalImpressions: int = 0
    averageEngagementRate: float = 0.0
    connectedPlatforms: int = 0


class MultiPlatformOverview(BaseModel):
    """
    Response for GET /api/analytics/overview.

    Contains one snapshot per connected platform plus aggregated totals.
    """
    creatorId: str
    platforms: List[PlatformSnapshot]
    totals: MultiPlatformTotals
    generatedAt: datetime


# ---------------------------------------------------------------------------
# Platform Comparison (side-by-side by metric)
# ---------------------------------------------------------------------------

class MetricComparison(BaseModel):
    """One row in a side-by-side metric comparison across platforms."""
    metric: str                                # e.g. "followers", "views"
    values: Dict[str, int]                     # {"youtube": 12500, "instagram": 8400}


class MultiPlatformComparison(BaseModel):
    """Response for GET /api/analytics/compare."""
    creatorId: str
    metrics: List[MetricComparison]
    snapshotDate: datetime


# ---------------------------------------------------------------------------
# Platform Analytics History (time-series for one platform)
# ---------------------------------------------------------------------------

class PlatformHistoryPoint(BaseModel):
    """One data point in a time-series response."""
    date: datetime
    followers: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    reach: Optional[int] = None
    impressions: Optional[int] = None
    engagementRate: float = 0.0


class PlatformAnalyticsHistory(BaseModel):
    """Response for GET /api/analytics/{platform}/history."""
    creatorId: str
    platform: str
    periodDays: int
    dataPoints: List[PlatformHistoryPoint]


# ---------------------------------------------------------------------------
# Content-Linked Analytics
# ---------------------------------------------------------------------------

class ContentWithMetrics(BaseModel):
    """A content post enriched with its latest performance metrics."""
    postId: str
    platform: str
    contentType: str                           # "video" | "reel" | "post"
    title: Optional[str] = None
    contentUrl: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    publishedAt: Optional[datetime] = None

    # Metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    watchTime: Optional[float] = None
    reach: Optional[int] = None
    impressions: Optional[int] = None
    engagementRate: float = 0.0

    recordedAt: Optional[datetime] = None


class PlatformContentResponse(BaseModel):
    """Response for GET /api/content/platform/{platform}."""
    platform: str
    creatorId: str
    posts: List[ContentWithMetrics]
    total: int
