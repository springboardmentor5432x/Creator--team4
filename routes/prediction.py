"""
routes/prediction.py — Reach Prediction & Audience Forecast API Endpoints

Permission matrix:
    growth:view     — Admin ✅, Agency ✅, Marketing ✅
    growth:view:own — Creator ✅ (own data only)

Endpoints:
    POST /api/prediction/reach   — Predict future reach
    POST /api/forecast/audience  — Forecast audience growth
"""

from fastapi import APIRouter, Depends

from authorization import require_any_permission
from permissions import Permission
from models import UserModel
from services.prediction_service import PredictionService
from services.forecast_service import ForecastService
from schemas.prediction import (
    ReachPredictionRequest,
    ReachPredictionResponse,
    AudienceForecastRequest,
    AudienceForecastResponse,
)

# Use two separate routers since the endpoints have different prefixes
prediction_router = APIRouter(prefix="/api/prediction", tags=["Reach Prediction"])
forecast_router = APIRouter(prefix="/api/forecast", tags=["Audience Forecast"])


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------

def get_prediction_service() -> PredictionService:
    return PredictionService()


def get_forecast_service() -> ForecastService:
    return ForecastService()


def get_creator_id(current_user: UserModel) -> str:
    """Extract creator_id from the authenticated user."""
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    return current_user.id


# ---------------------------------------------------------------------------
# Reach Prediction Endpoint
# ---------------------------------------------------------------------------

@prediction_router.post("/reach", response_model=ReachPredictionResponse)
async def predict_reach(
    request: ReachPredictionRequest,
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: PredictionService = Depends(get_prediction_service),
):
    """
    Predict future reach for next day, next week, and next month.

    Uses Simple Moving Average on the last 30 days of reach data.
    Requires at least 7 days of historical data.

    Returns predicted reach values, growth percentages, and confidence levels.
    """
    creator_id = get_creator_id(current_user)
    return await service.predict_reach(
        creator_id=creator_id,
        platform=request.platform,
    )


# ---------------------------------------------------------------------------
# Audience Forecast Endpoint
# ---------------------------------------------------------------------------

@forecast_router.post("/audience", response_model=AudienceForecastResponse)
async def forecast_audience(
    request: AudienceForecastRequest,
    current_user: UserModel = Depends(
        require_any_permission(Permission.GROWTH_VIEW, Permission.GROWTH_VIEW_OWN)
    ),
    service: ForecastService = Depends(get_forecast_service),
):
    """
    Forecast future followers and subscribers growth.

    Uses Simple Moving Average on historical follower/subscriber data.
    Requires at least 7 days of historical data.

    Returns expected followers, subscribers, growth %, and confidence level.
    """
    creator_id = get_creator_id(current_user)
    return await service.forecast_audience(
        creator_id=creator_id,
        platform=request.platform,
        forecast_days=request.forecast_days,
    )
