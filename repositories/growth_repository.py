"""
repositories/growth_repository.py — Growth Metrics Data Access Layer

Handles CRUD operations against the growth_metrics MongoDB collection.
One record per creator per day stores all high-level engagement metrics.
"""

from typing import Dict, List, Optional
from datetime import datetime, date
from bson import ObjectId
from mongo.mongodb import get_database
from models.mongo import GROWTH_METRICS
import pymongo


class GrowthRepository:
    """
    Data access layer for the growth_metrics collection.

    Document schema:
        {
            creator_id: str,
            platform: str,
            date: datetime,
            followers: int,
            subscribers: int,
            views: int,
            likes: int,
            comments: int,
            shares: int,
            watch_time: int,
            reach: int,
            engagement_rate: float,
        }
    """

    async def get_metrics_by_date_range(
        self,
        creator_id: str,
        start: datetime,
        end: datetime,
        platform: Optional[str] = None,
    ) -> List[Dict]:
        """
        Fetch daily growth metrics within a date range.

        Args:
            creator_id: The creator's ID.
            start: Start of the range (inclusive).
            end: End of the range (inclusive).
            platform: Optional platform filter.

        Returns:
            List of metric documents, sorted by date ascending.
        """
        db = get_database()
        query = {
            "creator_id": creator_id,
            "date": {"$gte": start, "$lte": end},
        }
        if platform:
            query["platform"] = platform

        cursor = db[GROWTH_METRICS].find(query).sort("date", pymongo.ASCENDING)
        return await cursor.to_list(length=1000)

    async def get_latest_metrics(
        self, creator_id: str, platform: Optional[str] = None
    ) -> Optional[Dict]:
        """Return the most recent daily metric snapshot."""
        db = get_database()
        query = {"creator_id": creator_id}
        if platform:
            query["platform"] = platform

        return await db[GROWTH_METRICS].find_one(
            query, sort=[("date", pymongo.DESCENDING)]
        )

    async def upsert_daily_metrics(
        self,
        creator_id: str,
        platform: str,
        metric_date: date,
        metrics: Dict,
    ) -> str:
        """
        Insert or update a daily metric record.

        Uses the unique index on (creator_id, date) for upsert.

        Returns:
            The document _id as a string.
        """
        db = get_database()
        dt = datetime.combine(metric_date, datetime.min.time())
        doc = {
            "creator_id": creator_id,
            "platform": platform,
            "date": dt,
            **metrics,
            "updated_at": datetime.utcnow(),
        }
        result = await db[GROWTH_METRICS].update_one(
            {"creator_id": creator_id, "date": dt},
            {"$set": doc},
            upsert=True,
        )
        if result.upserted_id:
            return str(result.upserted_id)
        # Find existing doc id
        existing = await db[GROWTH_METRICS].find_one(
            {"creator_id": creator_id, "date": dt}, {"_id": 1}
        )
        return str(existing["_id"]) if existing else ""

    async def aggregate_metrics(
        self,
        creator_id: str,
        group_by: str,
        start: datetime,
        end: datetime,
        platform: Optional[str] = None,
    ) -> List[Dict]:
        """
        Aggregate metrics using MongoDB $group.

        Args:
            creator_id: Creator ID.
            group_by: One of 'day', 'week', 'month', 'year'.
            start: Start of the range.
            end: End of the range.
            platform: Optional platform filter.

        Returns:
            List of aggregated metric buckets.
        """
        db = get_database()

        # Build match stage
        match = {
            "creator_id": creator_id,
            "date": {"$gte": start, "$lte": end},
        }
        if platform:
            match["platform"] = platform

        # Build group-by expression
        group_expr = self._build_group_expr(group_by)

        pipeline = [
            {"$match": match},
            {"$sort": {"date": 1}},
            {
                "$group": {
                    "_id": group_expr,
                    "followers": {"$last": "$followers"},
                    "subscribers": {"$last": "$subscribers"},
                    "views": {"$sum": "$views"},
                    "likes": {"$sum": "$likes"},
                    "comments": {"$sum": "$comments"},
                    "shares": {"$sum": "$shares"},
                    "watch_time": {"$sum": "$watch_time"},
                    "reach": {"$sum": "$reach"},
                    "revenue": {"$sum": "$revenue"},
                    "engagement_rate": {"$avg": "$engagement_rate"},
                    "period_start": {"$first": "$date"},
                }
            },
            {"$sort": {"period_start": 1}},
        ]

        cursor = db[GROWTH_METRICS].aggregate(pipeline)
        return await cursor.to_list(length=500)

    @staticmethod
    def _build_group_expr(group_by: str) -> dict:
        """Return MongoDB date grouping expression."""
        if group_by == "day":
            return {
                "year": {"$year": "$date"},
                "month": {"$month": "$date"},
                "day": {"$dayOfMonth": "$date"},
            }
        elif group_by == "week":
            return {
                "year": {"$isoWeekYear": "$date"},
                "week": {"$isoWeek": "$date"},
            }
        elif group_by == "month":
            return {
                "year": {"$year": "$date"},
                "month": {"$month": "$date"},
            }
        else:  # year
            return {"year": {"$year": "$date"}}
