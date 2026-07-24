"""
services/content_growth_service.py — Content Growth Tracking Business Logic

Tracks per-content growth over time and generates growth timelines,
percentage calculations, highest/lowest growth day identification,
and chart-ready graph data.
"""

from typing import Optional
from datetime import datetime

from repositories.content_growth_repository import ContentGrowthRepository
from repositories.content_repository import ContentRepository
from schemas.content_growth import (
    ContentGrowthResponse,
    ContentGrowthDayResponse,
    GrowthDayHighlight,
    GraphDataPoint,
)
from utils.analytics import calculate_growth_percentage
from utils.exceptions import ContentNotFoundError


# Metrics to track for per-content growth
CONTENT_METRICS = ["views", "likes", "comments", "shares", "reach", "engagement_rate"]


class ContentGrowthService:
    """
    Handles per-content growth tracking for
    GET /api/content/{content_id}/growth.
    """

    def __init__(self):
        self.growth_repo = ContentGrowthRepository()
        self.content_repo = ContentRepository()

    async def get_content_growth(
        self,
        content_id: str,
        creator_id: str,
    ) -> ContentGrowthResponse:
        """
        Build a complete growth analysis for a specific content item.

        Steps:
            1. Verify content exists and belongs to creator.
            2. Fetch all daily growth records.
            3. Build growth timeline.
            4. Calculate overall growth percentages.
            5. Identify highest and lowest growth days.
            6. Build graph data for charting.

        Args:
            content_id: The content item's ID.
            creator_id: Creator ID for ownership verification.

        Returns:
            ContentGrowthResponse with full analysis.

        Raises:
            ContentNotFoundError: If content_id doesn't exist or doesn't belong to creator.
        """
        # Step 1: Verify content
        post = await self.content_repo.get_post_by_id(content_id)
        if not post or post.get("creatorId") != creator_id:
            raise ContentNotFoundError(content_id)

        # Step 2: Fetch daily growth records
        records = await self.growth_repo.get_growth_by_content(content_id)

        if not records:
            return ContentGrowthResponse(
                content_id=content_id,
                growth_timeline=[],
                growth_percentage={m: 0.0 for m in CONTENT_METRICS},
                highest_growth_day=None,
                lowest_growth_day=None,
                graph_data={m: [] for m in CONTENT_METRICS},
            )

        # Step 3: Build growth timeline
        timeline = []
        for r in records:
            d = r.get("date")
            date_val = d.date() if isinstance(d, datetime) else d
            timeline.append(
                ContentGrowthDayResponse(
                    date=date_val,
                    **{m: r.get(m, 0) for m in CONTENT_METRICS},
                )
            )

        # Step 4: Calculate overall growth percentages
        first = records[0]
        last = records[-1]
        growth_pct = {}
        for m in CONTENT_METRICS:
            growth_pct[m] = round(
                calculate_growth_percentage(
                    last.get(m, 0), first.get(m, 0)
                ),
                2,
            )

        # Step 5: Identify highest and lowest growth days
        highest = self._find_extreme_day(records, "max")
        lowest = self._find_extreme_day(records, "min")

        # Step 6: Build graph data
        graph_data = {}
        for m in CONTENT_METRICS:
            points = []
            for r in records:
                d = r.get("date")
                date_str = d.strftime("%Y-%m-%d") if isinstance(d, datetime) else str(d)
                points.append(GraphDataPoint(date=date_str, value=r.get(m, 0)))
            graph_data[m] = points

        return ContentGrowthResponse(
            content_id=content_id,
            growth_timeline=timeline,
            growth_percentage=growth_pct,
            highest_growth_day=highest,
            lowest_growth_day=lowest,
            graph_data=graph_data,
        )

    def _find_extreme_day(
        self, records: list, extreme: str
    ) -> Optional[GrowthDayHighlight]:
        """
        Find the day with the highest or lowest day-over-day growth.

        Args:
            records: List of daily growth records.
            extreme: 'max' for highest, 'min' for lowest.

        Returns:
            GrowthDayHighlight or None if less than 2 records.
        """
        if len(records) < 2:
            return None

        best_day = None
        best_value = None
        best_metric = ""
        best_percent = 0.0

        for i in range(1, len(records)):
            prev = records[i - 1]
            curr = records[i]

            for m in CONTENT_METRICS:
                prev_val = prev.get(m, 0)
                curr_val = curr.get(m, 0)
                delta = curr_val - prev_val

                if best_value is None:
                    should_update = True
                elif extreme == "max":
                    should_update = delta > best_value
                else:
                    should_update = delta < best_value

                if should_update:
                    best_value = delta
                    best_metric = m
                    d = curr.get("date")
                    best_day = d.date() if isinstance(d, datetime) else d
                    best_percent = round(
                        calculate_growth_percentage(curr_val, prev_val), 2
                    )

        if best_day is None:
            return None

        return GrowthDayHighlight(
            date=best_day,
            metric=best_metric,
            value=best_value,
            percent=best_percent,
        )
