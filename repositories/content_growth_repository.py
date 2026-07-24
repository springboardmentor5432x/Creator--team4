"""
repositories/content_growth_repository.py — Content Growth Data Access Layer

Handles CRUD operations against the content_growth MongoDB collection.
Tracks daily metric snapshots per individual content item.
"""

from typing import Dict, List, Optional
from datetime import datetime
from mongo.mongodb import get_database
from models.mongo import CONTENT_GROWTH
import pymongo


class ContentGrowthRepository:
    """
    Data access layer for the content_growth collection.

    Document schema:
        {
            content_id: str,
            creator_id: str,
            date: datetime,
            views: int,
            likes: int,
            comments: int,
            shares: int,
            reach: int,
            engagement_rate: float,
        }
    """

    async def get_growth_by_content(
        self,
        content_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Fetch daily growth records for a specific content item.

        Args:
            content_id: The content's ID.
            start: Optional start date filter.
            end: Optional end date filter.

        Returns:
            List of daily metric snapshots, sorted by date ascending.
        """
        db = get_database()
        query: Dict = {"content_id": content_id}
        if start or end:
            date_filter = {}
            if start:
                date_filter["$gte"] = start
            if end:
                date_filter["$lte"] = end
            query["date"] = date_filter

        cursor = db[CONTENT_GROWTH].find(query).sort("date", pymongo.ASCENDING)
        return await cursor.to_list(length=1000)

    async def upsert_daily_growth(
        self,
        content_id: str,
        creator_id: str,
        growth_date: datetime,
        data: Dict,
    ) -> str:
        """
        Insert or update a daily content growth record.

        Returns:
            The document _id as a string.
        """
        db = get_database()
        doc = {
            "content_id": content_id,
            "creator_id": creator_id,
            "date": growth_date,
            **data,
            "updated_at": datetime.utcnow(),
        }
        result = await db[CONTENT_GROWTH].update_one(
            {"content_id": content_id, "date": growth_date},
            {"$set": doc},
            upsert=True,
        )
        if result.upserted_id:
            return str(result.upserted_id)
        existing = await db[CONTENT_GROWTH].find_one(
            {"content_id": content_id, "date": growth_date}, {"_id": 1}
        )
        return str(existing["_id"]) if existing else ""

    async def get_highest_growth_day(
        self, content_id: str, metric: str = "views"
    ) -> Optional[Dict]:
        """
        Find the day with the highest value for a given metric.

        Args:
            content_id: Content ID.
            metric: Metric field name (e.g. 'views', 'likes').

        Returns:
            The document with the highest metric value, or None.
        """
        db = get_database()
        cursor = (
            db[CONTENT_GROWTH]
            .find({"content_id": content_id})
            .sort(metric, pymongo.DESCENDING)
            .limit(1)
        )
        results = await cursor.to_list(length=1)
        return results[0] if results else None

    async def get_lowest_growth_day(
        self, content_id: str, metric: str = "views"
    ) -> Optional[Dict]:
        """
        Find the day with the lowest value for a given metric.

        Args:
            content_id: Content ID.
            metric: Metric field name (e.g. 'views', 'likes').

        Returns:
            The document with the lowest metric value, or None.
        """
        db = get_database()
        cursor = (
            db[CONTENT_GROWTH]
            .find({"content_id": content_id})
            .sort(metric, pymongo.ASCENDING)
            .limit(1)
        )
        results = await cursor.to_list(length=1)
        return results[0] if results else None
