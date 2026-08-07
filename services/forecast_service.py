"""
services/forecast_service.py — Audience Growth Forecasting Business Logic

Predicts future followers and subscribers using Simple Moving Average.
Designed as an independent, replaceable module.
"""

from typing import Optional
from datetime import datetime, timedelta

from repositories.growth_repository import GrowthRepository
from repositories.prediction_repository import PredictionRepository
from schemas.prediction import AudienceForecastResponse
from utils.analytics import (
    calculate_moving_average,
    calculate_confidence,
    calculate_growth_percentage,
)
from utils.exceptions import InsufficientDataError


class ForecastService:
    """
    Audience growth forecasting using Simple Moving Average.

    Calculates expected followers and subscribers by:
        1. Computing average daily growth from historical data.
        2. Extrapolating linearly for the forecast period.
        3. Providing confidence based on data consistency.
    """

    def __init__(self):
        self.growth_repo = GrowthRepository()
        self.prediction_repo = PredictionRepository()

    async def forecast_audience(
        self,
        creator_id: str,
        platform: Optional[str] = None,
        forecast_days: int = 30,
    ) -> AudienceForecastResponse:
        """
        Forecast audience growth (followers and subscribers).

        Args:
            creator_id: Creator ID.
            platform: Optional platform filter.
            forecast_days: Number of days to forecast (default 30).

        Returns:
            AudienceForecastResponse with expected values and confidence.

        Raises:
            InsufficientDataError: If less than 7 days of data.
        """
        # Fetch historical data
        end = datetime.utcnow()
        start = end - timedelta(days=90)  # Use up to 90 days of history
        records = await self.growth_repo.get_metrics_by_date_range(
            creator_id, start, end, platform
        )

        if len(records) < 7:
            raise InsufficientDataError(
                f"Need at least 7 days of data for audience forecasting. "
                f"Found {len(records)} days."
            )

        # Extract follower and subscriber series
        follower_values = [r.get("followers", 0) for r in records]
        subscriber_values = [r.get("subscribers", 0) for r in records]

        # Calculate daily growth rates
        follower_daily_growth = self._calculate_daily_growth(follower_values)
        subscriber_daily_growth = self._calculate_daily_growth(subscriber_values)

        # SMA of daily growth
        window = min(30, len(follower_daily_growth))
        avg_follower_growth = calculate_moving_average(
            follower_daily_growth, window
        )
        avg_subscriber_growth = calculate_moving_average(
            subscriber_daily_growth, window
        )

        # Current values
        current_followers = follower_values[-1] if follower_values else 0
        current_subscribers = subscriber_values[-1] if subscriber_values else 0

        # Forecast
        expected_followers = current_followers + (avg_follower_growth * forecast_days)
        expected_subscribers = current_subscribers + (avg_subscriber_growth * forecast_days)

        # Overall growth %
        growth_pct = calculate_growth_percentage(expected_followers, current_followers)

        # Confidence based on consistency of daily growth
        confidence = calculate_confidence(follower_daily_growth) if follower_daily_growth else 0.0

        # Average monthly growth (30 days)
        avg_monthly_growth = avg_follower_growth * 30

        response = AudienceForecastResponse(
            current_followers=float(current_followers),
            current_subscribers=float(current_subscribers),
            average_monthly_growth=round(avg_monthly_growth, 2),
            expected_followers=round(max(0, expected_followers), 2),
            expected_subscribers=round(max(0, expected_subscribers), 2),
            expected_growth_percent=round(growth_pct, 2),
            forecast_period=f"{forecast_days}_days",
            method_used="moving_average",
            confidence=confidence,
        )

        # Store prediction
        await self.prediction_repo.save_prediction(
            creator_id=creator_id,
            prediction_type="audience",
            data={
                **response.model_dump(),
                "platform": platform,
                "forecast_days": forecast_days,
            },
        )

        return response

    @staticmethod
    def _calculate_daily_growth(values: list) -> list:
        """
        Calculate day-over-day absolute growth from a time series.

        Args:
            values: List of daily values (chronologically ordered).

        Returns:
            List of daily deltas (length = len(values) - 1).
        """
        if len(values) < 2:
            return []
        return [values[i] - values[i - 1] for i in range(1, len(values))]
