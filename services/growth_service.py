"""
services/growth_service.py — Growth Monitoring Business Logic

Provides daily, weekly, monthly, and yearly growth summaries
with total values, percentage changes, historical snapshots, and trend detection.
"""

from typing import Optional
from datetime import datetime, timedelta, date

from repositories.growth_repository import GrowthRepository
from schemas.growth import (
    GrowthSummaryResponse,
    GrowthSnapshotResponse,
    GrowthQueryParams,
)
from utils.analytics import calculate_growth_percentage, determine_trend


# Metrics fields tracked in growth_metrics documents
METRIC_FIELDS = [
    "followers", "subscribers", "views", "likes",
    "comments", "shares", "watch_time", "engagement_rate", "reach",
]


class GrowthService:
    """
    Handles all growth monitoring logic for /api/growth/* endpoints.

    Each method returns a GrowthSummaryResponse containing:
        - total_growth: Latest/sum values per metric
        - percentage_growth: % change from start to end of period
        - growth_history: Time-bucketed snapshots
        - trend: 'increasing' | 'decreasing' | 'stable'
    """

    def __init__(self):
        self.repository = GrowthRepository()

    async def get_daily_growth(
        self,
        creator_id: str,
        params: GrowthQueryParams,
    ) -> GrowthSummaryResponse:
        """Daily growth — fetches raw daily records."""
        start, end = self._resolve_dates(params, default_days=30)
        records = await self.repository.get_metrics_by_date_range(
            creator_id, start, end, params.platform
        )
        return self._build_summary(records, date_format="day")

    async def get_weekly_growth(
        self,
        creator_id: str,
        params: GrowthQueryParams,
    ) -> GrowthSummaryResponse:
        """Weekly growth — aggregates by ISO week."""
        start, end = self._resolve_dates(params, default_days=90)
        records = await self.repository.aggregate_metrics(
            creator_id, "week", start, end, params.platform
        )
        return self._build_summary(records, date_format="week")

    async def get_monthly_growth(
        self,
        creator_id: str,
        params: GrowthQueryParams,
    ) -> GrowthSummaryResponse:
        """Monthly growth — aggregates by month."""
        start, end = self._resolve_dates(params, default_days=365)
        records = await self.repository.aggregate_metrics(
            creator_id, "month", start, end, params.platform
        )
        return self._build_summary(records, date_format="month")

    async def get_yearly_growth(
        self,
        creator_id: str,
        params: GrowthQueryParams,
    ) -> GrowthSummaryResponse:
        """Yearly growth — aggregates by year."""
        start, end = self._resolve_dates(params, default_days=1825)  # ~5 years
        records = await self.repository.aggregate_metrics(
            creator_id, "year", start, end, params.platform
        )
        return self._build_summary(records, date_format="year")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_dates(
        params: GrowthQueryParams, default_days: int
    ) -> tuple:
        """Resolve start/end dates, applying defaults if not provided."""
        end = (
            datetime.combine(params.end_date, datetime.max.time())
            if params.end_date
            else datetime.utcnow()
        )
        start = (
            datetime.combine(params.start_date, datetime.min.time())
            if params.start_date
            else end - timedelta(days=default_days)
        )
        return start, end

    def _build_summary(
        self, records: list, date_format: str
    ) -> GrowthSummaryResponse:
        """
        Build a GrowthSummaryResponse from a list of metric records.

        Args:
            records: List of dicts from the repository.
            date_format: How to label each snapshot ('day', 'week', 'month', 'year').

        Returns:
            Fully populated GrowthSummaryResponse.
        """
        if not records:
            return GrowthSummaryResponse(
                total_growth={f: 0 for f in METRIC_FIELDS},
                percentage_growth={f: 0.0 for f in METRIC_FIELDS},
                growth_history=[],
                trend="stable",
            )

        # Build history
        history = []
        for r in records:
            label = self._format_date_label(r, date_format)
            snapshot = GrowthSnapshotResponse(
                date=label,
                **{f: r.get(f, 0) for f in METRIC_FIELDS},
            )
            history.append(snapshot)

        # Total growth = latest record values (followers/subscribers are cumulative)
        # For sum-based metrics (views, likes, etc.), sum them
        latest = records[-1]
        total_growth = {}
        for f in METRIC_FIELDS:
            if f in ("followers", "subscribers"):
                total_growth[f] = latest.get(f, 0)
            else:
                total_growth[f] = sum(r.get(f, 0) for r in records)

        # Percentage growth = first vs last
        first = records[0]
        percentage_growth = {}
        for f in METRIC_FIELDS:
            first_val = first.get(f, 0)
            last_val = latest.get(f, 0)
            percentage_growth[f] = round(
                calculate_growth_percentage(last_val, first_val), 2
            )

        # Trend based on a key metric (views)
        view_values = [r.get("views", 0) for r in records]
        trend = determine_trend(view_values)

        return GrowthSummaryResponse(
            total_growth=total_growth,
            percentage_growth=percentage_growth,
            growth_history=history,
            trend=trend,
        )

    @staticmethod
    def _format_date_label(record: dict, date_format: str) -> str:
        """Convert a record to a human-readable date label."""
        if date_format == "day":
            d = record.get("date")
            if isinstance(d, datetime):
                return d.strftime("%Y-%m-%d")
            return str(d)

        # Aggregated records have _id with year/month/week/day
        group_id = record.get("_id", {})
        if date_format == "week":
            return f"{group_id.get('year', '')}-W{group_id.get('week', ''):02d}"
        elif date_format == "month":
            return f"{group_id.get('year', '')}-{group_id.get('month', ''):02d}"
        elif date_format == "year":
            return str(group_id.get("year", ""))

        return str(record.get("period_start", ""))
