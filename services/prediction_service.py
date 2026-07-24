"""
services/prediction_service.py — Reach Prediction Business Logic

Predicts future reach using Simple Moving Average.
Designed as an independent, replaceable module — swap _predict()
with an ML model in the future without touching the router or repository.
"""

from typing import Optional
from datetime import datetime, timedelta

from repositories.growth_repository import GrowthRepository
from repositories.prediction_repository import PredictionRepository
from schemas.prediction import (
    ReachPredictionResponse,
    PredictionPeriod,
)
from utils.analytics import calculate_moving_average, calculate_confidence
from utils.exceptions import InsufficientDataError


class PredictionService:
    """
    Reach prediction using Simple Moving Average (SMA).

    Strategy:
        - Next day: SMA(7) — 7-day moving average
        - Next week: SMA(7) * 7
        - Next month: SMA(30) * 30

    The service stores each prediction in the predictions collection
    for audit trail and caching.
    """

    def __init__(self):
        self.growth_repo = GrowthRepository()
        self.prediction_repo = PredictionRepository()

    async def predict_reach(
        self,
        creator_id: str,
        platform: Optional[str] = None,
    ) -> ReachPredictionResponse:
        """
        Predict future reach for next day, week, and month.

        Args:
            creator_id: Creator ID.
            platform: Optional platform filter.

        Returns:
            ReachPredictionResponse with three time horizons.

        Raises:
            InsufficientDataError: If less than 7 days of data available.
        """
        # Fetch last 30 days of reach data
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        records = await self.growth_repo.get_metrics_by_date_range(
            creator_id, start, end, platform
        )

        reach_values = [r.get("reach", 0) for r in records]

        if len(reach_values) < 7:
            raise InsufficientDataError(
                f"Need at least 7 days of data for reach prediction. "
                f"Found {len(reach_values)} days."
            )

        # Current reach (most recent value)
        current_reach = reach_values[-1] if reach_values else 0

        # Next day: SMA(7)
        sma_7 = calculate_moving_average(reach_values, 7)
        next_day = self._build_period(sma_7, current_reach, reach_values[-7:])

        # Next week: SMA(7) * 7
        next_week_reach = sma_7 * 7
        weekly_values = reach_values[-7:] if len(reach_values) >= 7 else reach_values
        weekly_current = sum(weekly_values)
        next_week = self._build_period(
            next_week_reach, weekly_current, reach_values
        )

        # Next month: SMA(30) * 30
        sma_30 = calculate_moving_average(reach_values, 30)
        next_month_reach = sma_30 * 30
        monthly_current = sum(reach_values)
        next_month = self._build_period(
            next_month_reach, monthly_current, reach_values
        )

        response = ReachPredictionResponse(
            next_day=next_day,
            next_week=next_week,
            next_month=next_month,
        )

        # Store prediction for audit
        await self.prediction_repo.save_prediction(
            creator_id=creator_id,
            prediction_type="reach",
            data={
                "next_day": next_day.model_dump(),
                "next_week": next_week.model_dump(),
                "next_month": next_month.model_dump(),
                "platform": platform,
            },
        )

        return response

    @staticmethod
    def _build_period(
        predicted: float,
        current: float,
        values: list,
    ) -> PredictionPeriod:
        """Build a PredictionPeriod from predicted and current values."""
        if current > 0:
            growth_pct = ((predicted - current) / current) * 100
        else:
            growth_pct = 100.0 if predicted > 0 else 0.0

        confidence = calculate_confidence(values)

        return PredictionPeriod(
            predicted_reach=round(predicted, 2),
            growth_percent=round(growth_pct, 2),
            confidence=confidence,
        )
