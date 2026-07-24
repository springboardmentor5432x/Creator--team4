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
    predicted_reach: float = Field(ge=0, description="Predicted reach value")
    growth_percent: float = Field(description="Expected growth %")
    confidence: float = Field(
        ge=0, le=100,
        description="Confidence level (0–100%)"
    )


class ReachPredictionResponse(BaseModel):
    """Response for POST /api/prediction/reach."""
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
    expected_followers: float = Field(ge=0)
    expected_subscribers: float = Field(ge=0)
    expected_growth_percent: float
    method_used: str = Field(
        default="moving_average",
        description="Algorithm used: 'moving_average'"
    )
    confidence: float = Field(
        ge=0, le=100,
        description="Confidence level (0–100%)"
    )
