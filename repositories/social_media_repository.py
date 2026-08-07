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

    async def update_sync_status(
        self,
        creator_id: str,
        platform: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Update the sync status fields on a social_accounts document.

        Called by SyncService after every sync attempt (success or failure).

        Args:
            creator_id: The creator's ID.
            platform:   The platform name.
            status:     One of "idle", "syncing", "error".
            error_message: Last error message (set on failure, cleared on success).
        """
        db = get_database()
        update_doc: Dict = {
            "syncStatus": status,
        }
        if status == "syncing":
            update_doc["syncStartedAt"] = datetime.utcnow()
        elif status in ("idle", "error"):
            update_doc["lastSyncedAt"] = datetime.utcnow()
            update_doc["syncErrorMessage"] = error_message  # None on success

        await db[SOCIAL_ACCOUNTS].update_one(
            {"creatorId": creator_id, "platform": platform},
            {"$set": update_doc},
        )

    async def get_all_active_accounts(self) -> List[Dict]:
        """
        Return all active social accounts across ALL creators.

        Used by the background scheduler to iterate every connected
        account for bulk analytics synchronisation.

        Returns only the fields needed by the sync service — token fields
        are included because this is a server-side call.
        """
        db = get_database()
        cursor = db[SOCIAL_ACCOUNTS].find(
            {"isActive": True},
            projection={
                "creatorId": 1,
                "platform": 1,
                "accountId": 1,
                "accountName": 1,
                "accessToken": 1,
                "refreshToken": 1,
                "pageAccessToken": 1,
                "tokenExpiry": 1,
            },
        )
        return await cursor.to_list(length=1000)
