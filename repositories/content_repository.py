from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from mongo.mongodb import get_database
from models.mongo import (
    CONTENT_POSTS, CONTENT_METRICS, ANALYTICS_SUMMARY, PERFORMANCE_TRENDS, CONTENT_INSIGHTS
)
import pymongo

class ContentRepository:
    def __init__(self):
        # Database gets retrieved per request to ensure motor client is ready
        pass

    async def get_posts_by_creator(
        self,
        creator_id: str,
        limit: int = 100,
        search: Optional[str] = None,
        platform: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "publishedAt",
        sort_order: int = pymongo.DESCENDING,
    ) -> List[Dict]:
        db = get_database()
        query: Dict[str, Any] = {"creatorId": creator_id}

        if search:
            query["title"] = {"$regex": search, "$options": "i"}

        if platform:
            query["platform"] = platform

        if date_from or date_to:
            date_filter: Dict[str, Any] = {}
            if date_from:
                date_filter["$gte"] = date_from
            if date_to:
                date_filter["$lte"] = date_to
            query["publishedAt"] = date_filter

        allowed_sort_fields = {
            "publishedAt", "title", "platform",
        }
        if sort_by not in allowed_sort_fields:
            sort_by = "publishedAt"

        cursor = (
            db[CONTENT_POSTS]
            .find(query)
            .sort(sort_by, sort_order)
            .limit(limit if limit > 0 else 0)
        )
        return await cursor.to_list(length=limit if limit > 0 else None)

    async def get_post_by_id(self, post_id: str) -> Optional[Dict]:
        db = get_database()
        try:
            return await db[CONTENT_POSTS].find_one({"_id": ObjectId(post_id)})
        except Exception:
            # Handle invalid ObjectId
            return await db[CONTENT_POSTS].find_one({"platformPostId": post_id})

    async def get_metrics_by_post(self, post_id: str) -> Optional[Dict]:
        db = get_database()
        return await db[CONTENT_METRICS].find_one({"postId": post_id}, sort=[("snapshotDate", pymongo.DESCENDING)])

    async def get_metrics_history(self, post_id: str) -> List[Dict]:
        db = get_database()
        cursor = db[CONTENT_METRICS].find({"postId": post_id}).sort("snapshotDate", pymongo.DESCENDING)
        return await cursor.to_list(length=100)
    
    async def get_all_insights(self, post_ids: List[str]) -> List[Dict]:
        db = get_database()
        cursor = db[CONTENT_INSIGHTS].find({"postId": {"$in": post_ids}})
        return await cursor.to_list(length=len(post_ids))

    async def get_metrics_for_posts(self, post_ids: List[str]) -> List[Dict]:
        """Return the latest metric snapshot for each post in post_ids."""
        db = get_database()
        # Aggregate: sort by snapshotDate desc, group by postId to get latest per post
        pipeline = [
            {"$match": {"postId": {"$in": post_ids}}},
            {"$sort": {"snapshotDate": pymongo.DESCENDING}},
            {"$group": {
                "_id": "$postId",
                "doc": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$doc"}}
        ]
        cursor = db[CONTENT_METRICS].aggregate(pipeline)
        return await cursor.to_list(length=len(post_ids))

    async def save_metric_snapshot(self, post_id: str, metric_data: Dict) -> str:
        db = get_database()
        metric_data["postId"] = post_id
        metric_data["snapshotDate"] = datetime.utcnow()
        result = await db[CONTENT_METRICS].insert_one(metric_data)
        return str(result.inserted_id)

    async def get_performance_trends(self, creator_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        db = get_database()
        cursor = db[PERFORMANCE_TRENDS].find({
            "creatorId": creator_id,
            "trendDate": {"$gte": start_date, "$lte": end_date}
        }).sort("trendDate", pymongo.ASCENDING)
        return await cursor.to_list(length=100)

    async def get_analytics_summary(self, creator_id: str) -> Optional[Dict]:
        db = get_database()
        return await db[ANALYTICS_SUMMARY].find_one({"creatorId": creator_id})

    async def update_analytics_summary(self, creator_id: str, summary_data: Dict):
        db = get_database()
        summary_data["lastUpdated"] = datetime.utcnow()
        await db[ANALYTICS_SUMMARY].update_one(
            {"creatorId": creator_id},
            {"$set": summary_data},
            upsert=True
        )

    async def upsert_content_insight(self, post_id: str, insight_data: Dict):
        db = get_database()
        await db[CONTENT_INSIGHTS].update_one(
            {"postId": post_id},
            {"$set": insight_data},
            upsert=True
        )

    async def upsert_performance_trend(self, creator_id: str, trend_date: datetime, trend_data: Dict):
        """
        Insert or update a daily performance trend snapshot for the creator.
        Uses (creatorId, trendDate) as the unique key so one record per day is kept.
        The date is normalised to midnight so all syncs on the same day update the same record.
        """
        db = get_database()
        # Normalise to midnight (date-only bucket)
        bucket = trend_date.replace(hour=0, minute=0, second=0, microsecond=0)
        trend_data["creatorId"] = creator_id
        trend_data["trendDate"] = bucket
        trend_data["lastUpdated"] = datetime.utcnow()
        await db[PERFORMANCE_TRENDS].update_one(
            {"creatorId": creator_id, "trendDate": bucket},
            {"$set": trend_data},
            upsert=True
        )
