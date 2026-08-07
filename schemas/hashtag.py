"""
schemas/hashtag.py — Hashtag Analysis Schemas

Request parameters and response models for the /api/hashtags/* endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class HashtagResponse(BaseModel):
    """Summary-level hashtag returned in lists."""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    frequency: int = Field(default=0, ge=0, description="Number of times this hashtag was used")
    average_reach: float = Field(default=0.0, ge=0.0)
    average_impressions: float = Field(default=0.0, ge=0.0)
    average_engagement: float = Field(default=0.0, ge=0.0)
    growth_percentage: float = Field(default=0.0, description="Growth % over the analysis period")

    class Config:
        populate_by_name = True


class HashtagDetailResponse(BaseModel):
    """Detailed view for a single hashtag (GET /api/hashtags/{hashtag})."""
    name: str
    frequency: int = 0
    average_reach: float = 0.0
    average_impressions: float = 0.0
    average_engagement: float = 0.0
    growth_percentage: float = 0.0
    content_ids: List[str] = Field(
        default_factory=list,
        description="IDs of content using this hashtag"
    )
    daily_usage: List[dict] = Field(
        default_factory=list,
        description="List of {date, count} showing daily usage history"
    )
    related_hashtags: List[str] = Field(
        default_factory=list,
        description="Other hashtags frequently co-occurring with this one"
    )


class HashtagListResponse(BaseModel):
    """Paginated hashtag list response."""
    hashtags: List[HashtagResponse]
    total: int
    page: int
    page_size: int
