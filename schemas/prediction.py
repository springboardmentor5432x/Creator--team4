"""
schemas/prediction.py — Reach Prediction & Audience Forecast Schemas

Request bodies and response models for:
  - POST /api/prediction/reach
  - POST /api/forecast/audience
"""

from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Reach Prediction
# ---------------------------------------------------------------------------

class ReachPredictionRequest(BaseModel):
    """Request body for POST /api/prediction/reach."""
    platform: Optional[str] = Field(
        default=None,
        description="Filter historical data by platform"
    )


class PredictionPeriod(BaseModel):
    """A single prediction for one time horizon."""
    previous_reach: float = Field(default=0.0, description="Previous period reach value")
    average_reach: float = Field(default=0.0, description="Average historical reach")
    predicted_reach: float = Field(ge=0, description="Predicted reach value")
    estimated_views: float = Field(default=0.0, description="Estimated future views")
    estimated_engagement: float = Field(default=0.0, description="Estimated engagement rate %")
    growth_percent: float = Field(description="Expected growth %")
    confidence: float = Field(
        ge=0, le=100,
        description="Confidence level (0–100%)"
    )


class ReachPredictionResponse(BaseModel):
    """Response for POST /api/prediction/reach."""
    previous_reach: float = 0.0
    average_reach: float = 0.0
    predicted_reach: float = 0.0
    estimated_views: float = 0.0
    estimated_engagement: float = 0.0
    next_day: PredictionPeriod
    next_week: PredictionPeriod
    next_month: PredictionPeriod


# ---------------------------------------------------------------------------
# Audience Forecast
# ---------------------------------------------------------------------------

class AudienceForecastRequest(BaseModel):
    """Request body for POST /api/forecast/audience."""
    platform: Optional[str] = Field(
        default=None,
        description="Filter historical data by platform"
    )
    forecast_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to forecast into the future"
    )


class AudienceForecastResponse(BaseModel):
    """Response for POST /api/forecast/audience."""
    current_followers: float = Field(default=0.0, ge=0)
    current_subscribers: float = Field(default=0.0, ge=0)
    average_monthly_growth: float = Field(default=0.0, description="Average monthly growth rate or delta")
    expected_followers: float = Field(ge=0, alias="expected_future_followers", default=0.0)
    expected_subscribers: float = Field(ge=0, default=0.0)
    expected_growth_percent: float = Field(default=0.0, alias="growth_percentage")
    forecast_period: str = Field(default="30_days", description="Period label for forecast")
    method_used: str = Field(
        default="moving_average",
        description="Algorithm used: 'moving_average'"
    )
    confidence: float = Field(
        default=0.0, ge=0, le=100,
        description="Confidence level (0–100%)"
    )

    class Config:
        populate_by_name = True

