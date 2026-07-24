"""
repositories/social_media_repository.py — MongoDB CRUD for social_accounts

Handles storage and retrieval of connected social media accounts,
including OAuth tokens. Uses the existing `social_accounts` collection
already indexed in models/mongo.py.
"""

from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from mongo.mongodb import get_database
from models.mongo import SOCIAL_ACCOUNTS


class SocialMediaRepository:
    """Data access layer for the social_accounts MongoDB collection."""

    async def get_accounts_by_creator(self, creator_id: str) -> List[Dict]:
        """Fetch all connected social accounts for a creator."""
        db = get_database()
        cursor = db[SOCIAL_ACCOUNTS].find({"creatorId": creator_id})
        return await cursor.to_list(length=50)

    async def get_account(self, creator_id: str, platform: str) -> Optional[Dict]:
        """Fetch a specific platform account for a creator."""
        db = get_database()
        return await db[SOCIAL_ACCOUNTS].find_one({
            "creatorId": creator_id,
            "platform": platform,
        })

    async def upsert_account(self, creator_id: str, platform: str, account_data: Dict) -> str:
        """
        Insert or update a connected social account.

        Uses the compound unique index (creatorId, platform, accountId)
        defined in models/mongo.py.
        """
        db = get_database()
        account_data["creatorId"] = creator_id
        account_data["platform"] = platform
        account_data["lastSynced"] = datetime.utcnow()
        result = await db[SOCIAL_ACCOUNTS].update_one(
            {
                "creatorId": creator_id,
                "platform": platform,
                "accountId": account_data.get("accountId", ""),
            },
            {
                "$set": account_data,
                "$setOnInsert": {"connectedAt": datetime.utcnow()},
            },
            upsert=True,
        )
        return str(result.upserted_id) if result.upserted_id else "updated"

    async def delete_account(self, creator_id: str, platform: str) -> bool:
        """
        Remove a connected social account.

        Returns True if an account was deleted, False otherwise.
        """
        db = get_database()
        result = await db[SOCIAL_ACCOUNTS].delete_one({
            "creatorId": creator_id,
            "platform": platform,
        })
        return result.deleted_count > 0

    async def update_tokens(self, creator_id: str, platform: str, token_data: Dict):
        """
        Update OAuth tokens for an existing connected account.

        Called after token refresh flows (e.g., YouTube refresh_token).
        """
        db = get_database()
        await db[SOCIAL_ACCOUNTS].update_one(
            {"creatorId": creator_id, "platform": platform},
            {"$set": {
                "accessToken": token_data["access_token"],
                "refreshToken": token_data.get("refresh_token"),
                "tokenExpiry": token_data.get("token_expiry"),
                "lastSynced": datetime.utcnow(),
            }}
        )
