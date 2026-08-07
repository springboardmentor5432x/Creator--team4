"""
services/hashtag_service.py — Hashtag Analysis Business Logic

Provides aggregated hashtag statistics, top/trending hashtag lists,
and detailed per-hashtag analytics using MongoDB aggregation pipelines.
"""

from typing import List

from repositories.hashtag_repository import HashtagRepository
from schemas.hashtag import (
    HashtagResponse,
    HashtagDetailResponse,
    HashtagListResponse,
)
from utils.exceptions import HashtagNotFoundError


class HashtagService:
    """
    Handles all hashtag analysis logic for /api/hashtags/* endpoints.
    """

    def __init__(self):
        self.repository = HashtagRepository()

    async def get_all_hashtags(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = None,
        sort_order: str = "desc",
    ) -> HashtagListResponse:
        """
        Return a paginated list of all hashtags.

        Args:
            page: Page number (1-indexed).
            page_size: Items per page.
            sort_by: Field to sort by (frequency, average_reach, etc.).
            sort_order: 'asc' or 'desc'.

        Returns:
            HashtagListResponse with items and pagination info.
        """
        items, total = await self.repository.get_all(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        hashtags = [self._to_response(item) for item in items]

        return HashtagListResponse(
            hashtags=hashtags,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_hashtag_detail(self, name: str) -> HashtagDetailResponse:
        """
        Get detailed analytics for a specific hashtag.

        Runs a real-time aggregation across content_posts + content_metrics
        to compute average engagement, reach, and find related hashtags.

        Args:
            name: The hashtag name (without #).

        Returns:
            HashtagDetailResponse with full analytics.

        Raises:
            HashtagNotFoundError: If the hashtag has no associated content.
        """
        # Run live aggregation for up-to-date stats
        agg_result = await self.repository.aggregate_from_content(name)

        if agg_result["frequency"] == 0:
            # Also check the hashtags collection directly
            stored = await self.repository.get_by_name(name)
            if not stored:
                raise HashtagNotFoundError(name)
            return HashtagDetailResponse(
                name=name,
                frequency=stored.get("frequency", 0),
                average_reach=stored.get("average_reach", 0.0),
                average_impressions=stored.get("average_impressions", 0.0),
                average_engagement=stored.get("average_engagement", 0.0),
                growth_percentage=stored.get("growth_percentage", 0.0),
                content_ids=[],
                daily_usage=[],
                related_hashtags=[],
            )

        # Update the stored hashtag with fresh stats
        await self.repository.upsert_hashtag(name, {
            "frequency": agg_result["frequency"],
            "average_reach": round(agg_result.get("average_reach", 0.0), 2),
            "average_impressions": round(agg_result.get("average_impressions", 0.0), 2),
            "average_engagement": round(agg_result.get("average_engagement", 0.0), 2),
        })

        return HashtagDetailResponse(
            name=name,
            frequency=agg_result["frequency"],
            average_reach=round(agg_result.get("average_reach", 0.0), 2),
            average_impressions=round(agg_result.get("average_impressions", 0.0), 2),
            average_engagement=round(agg_result.get("average_engagement", 0.0), 2),
            growth_percentage=0.0,  # Calculated from historical snapshots
            content_ids=agg_result.get("content_ids", []),
            daily_usage=[],  # Would require time-series aggregation
            related_hashtags=agg_result.get("related_hashtags", []),
        )

    async def get_top_hashtags(self, limit: int = 10) -> List[HashtagResponse]:
        """Return top hashtags by frequency."""
        items = await self.repository.get_top(limit=limit, sort_field="frequency")
        return [self._to_response(item) for item in items]

    async def get_trending_hashtags(self, limit: int = 10) -> List[HashtagResponse]:
        """Return fastest growing hashtags by growth_percentage."""
        items = await self.repository.get_trending(limit=limit)
        return [self._to_response(item) for item in items]

    async def refresh_hashtag_stats(self) -> int:
        """
        Recalculate all hashtag stats from content_posts + content_metrics.
        Intended for background jobs.

        Returns:
            Number of hashtags updated.
        """
        # Get all unique hashtags from content_posts
        from mongo.mongodb import get_database
        from models.mongo import CONTENT_POSTS

        db = get_database()
        pipeline = [
            {"$unwind": "$hashtags"},
            {"$group": {"_id": {"$toLower": "$hashtags"}}},
        ]
        cursor = db[CONTENT_POSTS].aggregate(pipeline)
        unique_tags = await cursor.to_list(length=10000)

        count = 0
        for tag_doc in unique_tags:
            tag_name = tag_doc["_id"].lstrip("#")
            if not tag_name:
                continue
            agg = await self.repository.aggregate_from_content(tag_name)
            await self.repository.upsert_hashtag(tag_name, {
                "frequency": agg["frequency"],
                "average_reach": round(agg.get("average_reach", 0.0), 2),
                "average_impressions": round(agg.get("average_impressions", 0.0), 2),
                "average_engagement": round(agg.get("average_engagement", 0.0), 2),
            })
            count += 1

        return count

    @staticmethod
    def _to_response(item: dict) -> HashtagResponse:
        """Convert a raw MongoDB document to HashtagResponse."""
        return HashtagResponse(
            _id=str(item.get("_id", "")),
            name=item.get("name", ""),
            frequency=item.get("frequency", 0),
            average_reach=item.get("average_reach", 0.0),
            average_impressions=item.get("average_impressions", 0.0),
            average_engagement=item.get("average_engagement", 0.0),
            growth_percentage=item.get("growth_percentage", 0.0),
        )

