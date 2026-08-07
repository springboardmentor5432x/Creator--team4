"""
schemas/growth.py — Growth Monitoring Schemas

Request parameters and response models for the /api/growth/* endpoints.
"""

from typing import Dict, List, Optional, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Base / DB Models
# ---------------------------------------------------------------------------

class GrowthMetricBase(BaseModel):
    """Core metric fields stored per day in growth_metrics collection."""
    followers: int = Field(default=0, ge=0)
    subscribers: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    watch_time: int = Field(default=0, ge=0, description="Watch time in seconds")
    engagement_rate: float = Field(default=0.0, ge=0.0)
    reach: int = Field(default=0, ge=0)
    revenue: float = Field(default=0.0, ge=0.0, description="Revenue in currency units")


class GrowthMetricResponse(GrowthMetricBase):
    """Single day growth metric record returned to clients."""
    id: Optional[str] = Field(default=None, alias="_id")
    creator_id: str
    platform: str
    date: date

    class Config:
        populate_by_name = True


# ---------------------------------------------------------------------------
# Query Parameters
# ---------------------------------------------------------------------------

class GrowthQueryParams(BaseModel):
    """
    Common query parameters for growth endpoints.

    Usage in routes:
        async def get_daily(params: GrowthQueryParams = Depends()):
    """
    platform: Optional[str] = Field(
        default=None,
        description="Filter by platform (e.g. youtube, instagram)"
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Start date (inclusive) — defaults to 30 days ago"
    )
    end_date: Optional[date] = Field(
        default=None,
        description="End date (inclusive) — defaults to today"
    )


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class GrowthSnapshotResponse(BaseModel):
    """A single time-bucketed growth snapshot (used in growth_history list)."""
    date: str = Field(description="Date or period label (e.g. '2026-07-01', 'Week 28')")
    followers: int = 0
    subscribers: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    watch_time: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    revenue: float = 0.0


class GrowthSummaryResponse(BaseModel):
    """
    Aggregated growth summary returned by all /api/growth/* endpoints.

    Contains total values, percentage changes, historical snapshots,
    and an overall trend indicator.
    """
    total_growth: Dict[str, float] = Field(
        description="Sum/latest of each metric over the period"
    )
    percentage_growth: Dict[str, float] = Field(
        description="Percentage change from start to end of the period"
    )
    growth_history: List[GrowthSnapshotResponse] = Field(
        description="Time-bucketed snapshots (daily/weekly/monthly/yearly)"
    )
    trend: str = Field(
        description="Overall trend: 'increasing', 'decreasing', or 'stable'"
    )


# ---------------------------------------------------------------------------
# Feature 7 & 8 Response Models
# ---------------------------------------------------------------------------

class GrowthPeriodHighlight(BaseModel):
    """Highlights for highest/lowest growth periods."""
    period_label: str
    metric: str
    growth_value: float
    growth_percentage: float


class HistoricalPerformanceResponse(BaseModel):
    """Response model for Historical Performance Analysis."""
    daily_performance: GrowthSummaryResponse
    weekly_performance: GrowthSummaryResponse
    monthly_performance: GrowthSummaryResponse
    highest_growth_period: Optional[GrowthPeriodHighlight] = None
    lowest_growth_period: Optional[GrowthPeriodHighlight] = None
    performance_comparison: Dict[str, Any] = Field(
        default_factory=dict,
        description="Side-by-side performance delta between recent and previous periods"
    )


class GrowthInsightsResponse(BaseModel):
    """Response model for Growth Insights & Recommendations."""
    best_performing_category: Optional[str] = None
    best_time_period_for_growth: Optional[str] = None
    fastest_growing_content: Optional[Dict[str, Any]] = None
    most_effective_hashtags: List[str] = Field(default_factory=list)
    audience_growth_pattern: str = Field(
        description="Identified growth pattern (e.g. 'Accelerating', 'Steady', 'Fluctuating')"
    )
    overall_growth_trend: str = Field(
        description="Overall growth direction ('increasing', 'decreasing', 'stable')"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable strategy suggestions based on analyzed historical data"
    )

