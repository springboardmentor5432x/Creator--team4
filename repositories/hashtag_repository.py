"""
repositories/hashtag_repository.py — Hashtag Data Access Layer

Handles CRUD operations against the hashtags MongoDB collection
and runs aggregation pipelines across content_posts + content_metrics
to compute real-time hashtag statistics.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from mongo.mongodb import get_database
from models.mongo import HASHTAGS, CONTENT_POSTS, CONTENT_METRICS
import pymongo


class HashtagRepository:
    """
    Data access layer for the hashtags collection.

    Document schema:
        {
            name: str,
            frequency: int,
            average_reach: float,
            average_engagement: float,
            growth_percentage: float,
            updated_at: datetime,
        }
    """

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Dict], int]:
        """
        Fetch a paginated list of all hashtags.

        Returns:
            Tuple of (items, total_count).
        """
        db = get_database()
        skip = (page - 1) * page_size

        # Default sort by frequency
        sort_field = sort_by if sort_by in (
            "frequency", "average_reach", "average_engagement", "growth_percentage"
        ) else "frequency"
        sort_dir = pymongo.ASCENDING if sort_order == "asc" else pymongo.DESCENDING

        total = await db[HASHTAGS].count_documents({})
        cursor = (
            db[HASHTAGS]
            .find()
            .sort(sort_field, sort_dir)
            .skip(skip)
            .limit(page_size)
        )
        items = await cursor.to_list(length=page_size)
        return items, total

    async def get_by_name(self, name: str) -> Optional[Dict]:
        """Find a single hashtag by its name (case-insensitive)."""
        db = get_database()
        return await db[HASHTAGS].find_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}}
        )

    async def get_top(self, limit: int = 10, sort_field: str = "frequency") -> List[Dict]:
        """Return the top N hashtags sorted by the given field descending."""
        db = get_database()
        valid_fields = ("frequency", "average_reach", "average_engagement", "growth_percentage")
        if sort_field not in valid_fields:
            sort_field = "frequency"

        cursor = (
            db[HASHTAGS]
            .find()
            .sort(sort_field, pymongo.DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_trending(self, limit: int = 10) -> List[Dict]:
        """Return hashtags sorted by growth_percentage descending."""
        db = get_database()
        cursor = (
            db[HASHTAGS]
            .find()
            .sort("growth_percentage", pymongo.DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def upsert_hashtag(self, name: str, stats: Dict) -> str:
        """Insert or update a hashtag's statistics."""
        db = get_database()
        stats["name"] = name.lower()
        stats["updated_at"] = datetime.utcnow()

        result = await db[HASHTAGS].update_one(
            {"name": name.lower()},
            {"$set": stats},
            upsert=True,
        )
        if result.upserted_id:
            return str(result.upserted_id)
        return name

    async def aggregate_from_content(self, hashtag_name: str) -> Dict:
        """
        Compute real-time statistics for a hashtag by aggregating
        across content_posts and content_metrics.

        Finds all posts containing the hashtag, joins with their metrics,
        and calculates average reach and engagement.

        Args:
            hashtag_name: The hashtag to analyze (without #).

        Returns:
            Dict with frequency, average_reach, average_engagement,
            content_ids, and related_hashtags.
        """
        db = get_database()
        pipeline = [
            # Find all posts with this hashtag
            {"$match": {"hashtags": {"$regex": f"^#?{hashtag_name}$", "$options": "i"}}},
            # Lookup their metrics
            {
                "$lookup": {
                    "from": CONTENT_METRICS,
                    "let": {"post_id": {"$toString": "$_id"}},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$postId", "$$post_id"]}}},
                        {"$sort": {"snapshotDate": -1}},
                        {"$limit": 1},
                    ],
                    "as": "latest_metrics",
                }
            },
            {"$unwind": {"path": "$latest_metrics", "preserveNullAndEmptyArrays": True}},
            # Group to get aggregates
            {
                "$group": {
                    "_id": None,
                    "frequency": {"$sum": 1},
                    "average_reach": {"$avg": {"$ifNull": ["$latest_metrics.reach", 0]}},
                    "average_engagement": {
                        "$avg": {"$ifNull": ["$latest_metrics.engagementRate", 0]}
                    },
                    "content_ids": {"$push": {"$toString": "$_id"}},
                    "all_hashtags": {"$push": "$hashtags"},
                }
            },
        ]

        cursor = db[CONTENT_POSTS].aggregate(pipeline)
        results = await cursor.to_list(length=1)

        if not results:
            return {
                "frequency": 0,
                "average_reach": 0.0,
                "average_engagement": 0.0,
                "content_ids": [],
                "related_hashtags": [],
            }

        result = results[0]
        # Flatten and deduplicate related hashtags
        all_tags = set()
        for tag_list in result.get("all_hashtags", []):
            if isinstance(tag_list, list):
                for t in tag_list:
                    clean = t.lstrip("#").lower()
                    if clean != hashtag_name.lower():
                        all_tags.add(clean)

        result["related_hashtags"] = list(all_tags)[:20]
        result.pop("all_hashtags", None)
        result.pop("_id", None)

        return result
