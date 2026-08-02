from typing import Optional, Dict
from datetime import datetime
from mongo.mongodb import get_database
from models.mongo import (
    AUDIENCE_ANALYTICS,
    AUDIENCE_DEMOGRAPHICS,
    AUDIENCE_BEHAVIOR
)


class AudienceRepository:
    def __init__(self):
        # Database gets retrieved per request
        pass

    async def get_audience_analytics(self, creator_id: str) -> Optional[Dict]:
        db = get_database()
        return await db[AUDIENCE_ANALYTICS].find_one(
            {"creatorId": creator_id}
        )

    async def get_audience_demographics(self, creator_id: str) -> Optional[Dict]:
        db = get_database()
        return await db[AUDIENCE_DEMOGRAPHICS].find_one(
            {"creatorId": creator_id}
        )

    async def get_audience_behavior(self, creator_id: str) -> Optional[Dict]:
        db = get_database()
        return await db[AUDIENCE_BEHAVIOR].find_one(
            {"creatorId": creator_id}
        )

    async def save_audience_analytics(self, data: Dict) -> str:
        db = get_database()

        data["recordedAt"] = datetime.utcnow()

        result = await db[AUDIENCE_ANALYTICS].insert_one(data)

        return str(result.inserted_id)

    async def save_audience_demographics(self, data: Dict) -> str:
        db = get_database()

        data["recordedAt"] = datetime.utcnow()

        result = await db[AUDIENCE_DEMOGRAPHICS].insert_one(data)

        return str(result.inserted_id)

    async def save_audience_behavior(self, data: Dict) -> str:
        db = get_database()

        data["recordedAt"] = datetime.utcnow()

        result = await db[AUDIENCE_BEHAVIOR].insert_one(data)

        return str(result.inserted_id)