"""
schemas/trend.py — Trend Detection Schemas

Request parameters and response models for the /api/trend/* endpoints.
"""

from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Query Parameters
# ---------------------------------------------------------------------------

class TrendQueryParams(BaseModel):
    """
    Filters for the GET /api/trend/top endpoint.
    """
    platform: Optional[str] = Field(
        default=None,
        description="Filter by platform (e.g. youtube, instagram)"
    )
    date_from: Optional[date] = Field(
        default=None,
        description="Start date for trend window"
    )
    date_to: Optional[date] = Field(
        default=None,
        description="End date for trend window"
    )
    content_type: Optional[str] = Field(
        default=None,
        description="Filter by content type (e.g. video, reel, post)"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of trending items to return"
    )


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class TrendScoreResponse(BaseModel):
    """A single trending content item."""
    rank: int = Field(description="Position in the trending list (1-indexed)")
    content_id: str
    title: Optional[str] = None
    platform: Optional[str] = None
    trend_score: float = Field(description="Normalized trend score (0–100)")
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    generated_at: Optional[datetime] = None


class TrendingContentResponse(BaseModel):
    """Aggregate response for GET /api/trend/top."""
    trending: List[TrendScoreResponse]
    total_count: int = Field(description="Number of items returned")
    generated_at: datetime = Field(description="Timestamp of trend calculation")
