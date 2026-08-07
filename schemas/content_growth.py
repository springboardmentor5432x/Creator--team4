"""
schemas/content_growth.py — Content Growth Tracking Schemas

Response models for GET /api/content/{content_id}/growth.
"""

from typing import Dict, List, Optional
from datetime import date
from pydantic import BaseModel, Field


class ContentGrowthDayResponse(BaseModel):
    """A single day's metrics for a content item."""
    date: date
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    reach: int = 0
    engagement_rate: float = 0.0


class GrowthDayHighlight(BaseModel):
    """Identifies the highest or lowest growth day."""
    date: date
    metric: str = Field(description="The metric with the highest/lowest growth")
    value: float = Field(description="The absolute change on that day")
    percent: float = Field(description="The percentage change on that day")


class GraphDataPoint(BaseModel):
    """A single point in a graph data series."""
    date: str
    value: float


class ContentGrowthResponse(BaseModel):
    """
    Complete growth analysis for a specific content item.

    Returned by GET /api/content/{content_id}/growth.
    """
    content_id: str
    views_after_7_days: int = Field(default=0, description="Cumulative views after 7 days of publishing")
    likes_after_30_days: int = Field(default=0, description="Cumulative likes after 30 days of publishing")
    watch_time_after_60_days: int = Field(default=0, description="Cumulative watch time in seconds after 60 days")
    growth_timeline: List[ContentGrowthDayResponse] = Field(
        description="Chronological list of daily metric snapshots"
    )
    growth_percentage: Dict[str, float] = Field(
        description="Overall % change per metric (first day → last day)"
    )
    highest_growth_day: Optional[GrowthDayHighlight] = Field(
        default=None,
        description="Day with the largest positive growth"
    )
    lowest_growth_day: Optional[GrowthDayHighlight] = Field(
        default=None,
        description="Day with the smallest / most negative growth"
    )
    graph_data: Dict[str, List[GraphDataPoint]] = Field(
        description="Per-metric time series for charting"
    )


class ContentGrowthComparisonItem(BaseModel):
    """Growth metrics summary for a content item in comparison."""
    content_id: str
    title: Optional[str] = None
    published_at: Optional[date] = None
    views_after_7_days: int = 0
    likes_after_30_days: int = 0
    watch_time_after_60_days: int = 0
    growth_percentage: Dict[str, float] = Field(default_factory=dict)
    growth_velocity_score: float = Field(default=0.0, description="Velocity score evaluating how quickly engagement was gained")


class ContentGrowthComparisonResponse(BaseModel):
    """Response model for content growth comparison."""
    comparison: List[ContentGrowthComparisonItem]

