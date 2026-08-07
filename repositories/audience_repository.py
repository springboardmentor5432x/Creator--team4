from typing import Optional, Dict, List
from datetime import datetime, timedelta
from mongo.mongodb import get_database
from models.mongo import (
    AUDIENCE_ANALYTICS,
    AUDIENCE_DEMOGRAPHICS,
    AUDIENCE_BEHAVIOR,
)
import pymongo


class AudienceRepository:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # audience_analytics
    # ------------------------------------------------------------------

    async def get_audience_analytics(self, creator_id: str) -> Optional[Dict]:
        """Return the most recent analytics snapshot for the creator."""
        db = get_database()
        return await db[AUDIENCE_ANALYTICS].find_one(
            {"creatorId": creator_id},
            sort=[("recordedAt", pymongo.DESCENDING)]
        )

    async def get_audience_analytics_history(
        self, creator_id: str, start_date: datetime, limit: int = 90
    ) -> List[Dict]:
        """Return time-ordered analytics snapshots for growth trend analysis."""
        db = get_database()
        cursor = (
            db[AUDIENCE_ANALYTICS]
            .find({"creatorId": creator_id, "recordedAt": {"$gte": start_date}})
            .sort("recordedAt", pymongo.ASCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def save_audience_analytics(self, data: Dict) -> str:
        db = get_database()
        data["recordedAt"] = datetime.utcnow()
        result = await db[AUDIENCE_ANALYTICS].insert_one(data)
        return str(result.inserted_id)

    # ------------------------------------------------------------------
    # audience_demographics
    # ------------------------------------------------------------------

    async def get_audience_demographics(self, creator_id: str) -> Optional[Dict]:
        """Return the most recent demographics snapshot."""
        db = get_database()
        return await db[AUDIENCE_DEMOGRAPHICS].find_one(
            {"creatorId": creator_id},
            sort=[("recordedAt", pymongo.DESCENDING)]
        )

    async def save_audience_demographics(self, data: Dict) -> str:
        db = get_database()
        data["recordedAt"] = datetime.utcnow()
        result = await db[AUDIENCE_DEMOGRAPHICS].insert_one(data)
        return str(result.inserted_id)

    # ------------------------------------------------------------------
    # audience_behavior
    # ------------------------------------------------------------------

    async def get_audience_behavior(self, creator_id: str) -> Optional[Dict]:
        """Return the most recent behavior snapshot."""
        db = get_database()
        return await db[AUDIENCE_BEHAVIOR].find_one(
            {"creatorId": creator_id},
            sort=[("recordedAt", pymongo.DESCENDING)]
        )

    async def get_audience_behavior_history(
        self, creator_id: str, start_date: datetime, limit: int = 30
    ) -> List[Dict]:
        """Return time-ordered behavior snapshots for trend analysis."""
        db = get_database()
        cursor = (
            db[AUDIENCE_BEHAVIOR]
            .find({"creatorId": creator_id, "recordedAt": {"$gte": start_date}})
            .sort("recordedAt", pymongo.ASCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def save_audience_behavior(self, data: Dict) -> str:
        db = get_database()
        data["recordedAt"] = datetime.utcnow()
        result = await db[AUDIENCE_BEHAVIOR].insert_one(data)
        return str(result.inserted_id)