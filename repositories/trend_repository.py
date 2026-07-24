"""
repositories/trend_repository.py — Trend Scores Data Access Layer

Handles CRUD operations against the trend_scores MongoDB collection
and $lookup joins with content_posts / content_metrics for trend ranking.
"""

from typing import Dict, List, Optional
from datetime import datetime
from mongo.mongodb import get_database
from models.mongo import TREND_SCORES, CONTENT_POSTS, CONTENT_METRICS
import pymongo


class TrendRepository:
    """
    Data access layer for the trend_scores collection.

    Document schema:
        {
            content_id: str,
            trend_score: float,
            views: int,
            likes: int,
            shares: int,
            comments: int,
            engagement_rate: float,
            platform: str,
            content_type: str,
            generated_at: datetime,
        }
    """

    async def get_top_trending(
        self,
        limit: int = 10,
        platform: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        content_type: Optional[str] = None,
    ) -> List[Dict]:
        """
        Fetch top trending content sorted by trend_score descending.

        Args:
            limit: Max items to return.
            platform: Optional platform filter.
            date_from: Optional start date filter.
            date_to: Optional end date filter.
            content_type: Optional content type filter.

        Returns:
            List of trend score documents with content metadata.
        """
        db = get_database()
        query: Dict = {}

        if platform:
            query["platform"] = platform
        if content_type:
            query["content_type"] = content_type
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = date_from
            if date_to:
                date_filter["$lte"] = date_to
            query["generated_at"] = date_filter

        cursor = (
            db[TREND_SCORES]
            .find(query)
            .sort("trend_score", pymongo.DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def upsert_trend_score(self, content_id: str, score_data: Dict) -> str:
        """Insert or update a single trend score."""
        db = get_database()
        score_data["content_id"] = content_id
        score_data["generated_at"] = datetime.utcnow()

        result = await db[TREND_SCORES].update_one(
            {"content_id": content_id},
            {"$set": score_data},
            upsert=True,
        )
        if result.upserted_id:
            return str(result.upserted_id)
        return content_id

    async def bulk_upsert_trend_scores(self, scores: List[Dict]) -> int:
        """
        Batch upsert multiple trend scores.

        Args:
            scores: List of dicts, each with 'content_id' and score fields.

        Returns:
            Number of documents affected.
        """
        if not scores:
            return 0

        db = get_database()
        from pymongo import UpdateOne

        operations = [
            UpdateOne(
                {"content_id": s["content_id"]},
                {"$set": {**s, "generated_at": datetime.utcnow()}},
                upsert=True,
            )
            for s in scores
        ]
        result = await db[TREND_SCORES].bulk_write(operations)
        return result.modified_count + result.upserted_count

    async def get_content_with_metrics(self, content_ids: List[str]) -> List[Dict]:
        """
        Fetch content posts with their latest metrics via $lookup.

        Args:
            content_ids: List of content post IDs.

        Returns:
            List of content documents enriched with metrics.
        """
        db = get_database()
        pipeline = [
            {"$match": {"_id": {"$in": content_ids}}},
            {
                "$lookup": {
                    "from": CONTENT_METRICS,
                    "localField": "_id",
                    "foreignField": "postId",
                    "as": "metrics",
                }
            },
            {
                "$addFields": {
                    "latest_metrics": {"$arrayElemAt": ["$metrics", -1]}
                }
            },
            {"$project": {"metrics": 0}},
        ]
        cursor = db[CONTENT_POSTS].aggregate(pipeline)
        return await cursor.to_list(length=len(content_ids))
