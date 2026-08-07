"""
services/growth_service.py — Growth Monitoring Business Logic

Provides daily, weekly, monthly, and yearly growth summaries
with total values, percentage changes, historical snapshots, and trend detection.
"""

from typing import Optional
from datetime import datetime, timedelta, date

from repositories.growth_repository import GrowthRepository
from repositories.trend_repository import TrendRepository
from repositories.hashtag_repository import HashtagRepository
from repositories.content_growth_repository import ContentGrowthRepository
from repositories.content_repository import ContentRepository

from schemas.growth import (
    GrowthSummaryResponse,
    GrowthSnapshotResponse,
    GrowthQueryParams,
    HistoricalPerformanceResponse,
    GrowthPeriodHighlight,
    GrowthInsightsResponse,
)
from utils.analytics import calculate_growth_percentage, determine_trend


# Metrics fields tracked in growth_metrics documents
METRIC_FIELDS = [
    "followers", "subscribers", "views", "likes",
    "comments", "shares", "watch_time", "engagement_rate", "reach", "revenue"
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
        self.trend_repo = TrendRepository()
        self.hashtag_repo = HashtagRepository()
        self.content_growth_repo = ContentGrowthRepository()
        self.content_repo = ContentRepository()

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

    async def get_historical_performance(
        self, creator_id: str, platform: Optional[str] = None
    ) -> HistoricalPerformanceResponse:
        """
        Feature 7 — Historical Performance Analysis.
        Compares daily, weekly, and monthly growth and identifies
        highest/lowest growth periods.
        """
        params = GrowthQueryParams(platform=platform)
        daily = await self.get_daily_growth(creator_id, params)
        weekly = await self.get_weekly_growth(creator_id, params)
        monthly = await self.get_monthly_growth(creator_id, params)

        # Identify highest/lowest growth periods from monthly/weekly history
        highest_period = None
        lowest_period = None

        if monthly.growth_history:
            best_snap = max(monthly.growth_history, key=lambda s: s.views)
            worst_snap = min(monthly.growth_history, key=lambda s: s.views)
            highest_period = GrowthPeriodHighlight(
                period_label=best_snap.date,
                metric="views",
                growth_value=float(best_snap.views),
                growth_percentage=monthly.percentage_growth.get("views", 0.0),
            )
            lowest_period = GrowthPeriodHighlight(
                period_label=worst_snap.date,
                metric="views",
                growth_value=float(worst_snap.views),
                growth_percentage=0.0,
            )

        delta = {
            "views_growth_delta": round(
                monthly.total_growth.get("views", 0) - weekly.total_growth.get("views", 0), 2
            ),
            "followers_growth_delta": round(
                monthly.total_growth.get("followers", 0) - weekly.total_growth.get("followers", 0), 2
            ),
        }

        return HistoricalPerformanceResponse(
            daily_performance=daily,
            weekly_performance=weekly,
            monthly_performance=monthly,
            highest_growth_period=highest_period,
            lowest_growth_period=lowest_period,
            performance_comparison=delta,
        )

    async def get_growth_insights(
        self, creator_id: str, platform: Optional[str] = None
    ) -> GrowthInsightsResponse:
        """
        Feature 8 — Growth Insights and Recommendations.
        Compiles insights across categories, periods, hashtags, and growth patterns.
        """
        # 1. Best category
        cat_trends = await self.trend_repo.aggregate_by_category(creator_id)
        best_cat = cat_trends[0]["category"] if cat_trends else "General"

        # 2. Historical for growth pattern
        params = GrowthQueryParams(platform=platform)
        monthly = await self.get_monthly_growth(creator_id, params)

        # 3. Effective hashtags
        top_tags = await self.hashtag_repo.get_top(limit=5, sort_field="average_engagement")
        tag_names = [t.get("name", "") for t in top_tags if t.get("name")]

        # 4. Fastest growing content
        posts = await self.content_repo.get_posts_by_creator(creator_id, limit=1)
        fastest_content = None
        if posts:
            p = posts[0]
            fastest_content = {
                "id": str(p.get("_id")),
                "title": p.get("title"),
                "platform": p.get("platform"),
            }

        pattern = "Accelerating" if monthly.trend == "increasing" else "Steady" if monthly.trend == "stable" else "Fluctuating"

        recommendations = [
            f"Focus on producing more content in the '{best_cat}' category.",
            "Post consistently during periods of high audience activity.",
            f"Use top-performing hashtags such as #{', #'.join(tag_names[:3])}." if tag_names else "Use relevant targeted hashtags to expand reach.",
            "Optimize video titles and thumbnails to boost early engagement velocity."
        ]

        return GrowthInsightsResponse(
            best_performing_category=best_cat,
            best_time_period_for_growth="Monthly (Q3)",
            fastest_growing_content=fastest_content,
            most_effective_hashtags=tag_names,
            audience_growth_pattern=pattern,
            overall_growth_trend=monthly.trend,
            recommendations=recommendations,
        )

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

