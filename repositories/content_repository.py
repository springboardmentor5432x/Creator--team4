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

    async def get_posts_by_creator(self, creator_id: str, limit: int = 100) -> List[Dict]:
        db = get_database()
        cursor = db[CONTENT_POSTS].find({"creatorId": creator_id}).sort("publishedAt", pymongo.DESCENDING).limit(limit)
        return await cursor.to_list(length=limit)

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
