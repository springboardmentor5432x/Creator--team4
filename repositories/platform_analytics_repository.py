"""
repositories/platform_analytics_repository.py — MongoDB CRUD for platform_analytics_raw

Handles normalized per-platform analytics snapshots that power the
multi-platform dashboard and history endpoints.

Collection: platform_analytics_raw
Indexes:    (creatorId, platform, snapshotDate) unique
            (creatorId, snapshotDate DESC)
            (platform, snapshotDate DESC)
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from bson import ObjectId
from mongo.mongodb import get_database
from models.mongo import PLATFORM_ANALYTICS_RAW, CONTENT_SYNC_STATE


class PlatformAnalyticsRepository:
    """Data access layer for platform_analytics_raw and content_sync_state collections."""

    # ── Analytics Snapshots ───────────────────────────────────────────────

    async def upsert_snapshot(
        self,
        creator_id: str,
        platform: str,
        data: Dict,
    ) -> str:
        """
        Insert or update today's analytics snapshot for a given platform.

        The unique key is (creatorId, platform, snapshotDate). Only one
        snapshot per creator per platform per day is stored; subsequent
        upserts on the same day overwrite the previous data.

        Args:
            creator_id: The creator's profile ID.
            platform:   The platform name (e.g. "youtube").
            data:       Normalized analytics dict matching the schema.

        Returns:
            The MongoDB document ID (str) or "updated".
        """
        db = get_database()
        snapshot_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        doc = {
            **data,
            "creatorId":    creator_id,
            "platform":     platform,
            "snapshotDate": snapshot_date,
            "recordedAt":   datetime.utcnow(),
        }
        result = await db[PLATFORM_ANALYTICS_RAW].update_one(
            {
                "creatorId":    creator_id,
                "platform":     platform,
                "snapshotDate": snapshot_date,
            },
            {"$set": doc},
            upsert=True,
        )
        return str(result.upserted_id) if result.upserted_id else "updated"

    async def get_latest_by_platform(
        self,
        creator_id: str,
        platform: str,
    ) -> Optional[Dict]:
        """
        Fetch the most recent analytics snapshot for a specific platform.

        Args:
            creator_id: The creator's profile ID.
            platform:   The platform name.

        Returns:
            The snapshot document, or None if not found.
        """
        db = get_database()
        return await db[PLATFORM_ANALYTICS_RAW].find_one(
            {"creatorId": creator_id, "platform": platform},
            sort=[("snapshotDate", -1)],
        )

    async def get_latest_all_platforms(self, creator_id: str) -> List[Dict]:
        """
        Fetch the most recent snapshot for EACH connected platform.

        Used by GET /api/analytics/overview to build the multi-platform
        dashboard card row without requiring N separate queries.

        Args:
            creator_id: The creator's profile ID.

        Returns:
            List of the latest snapshot document per platform.
        """
        db = get_database()
        # MongoDB aggregation: group by platform, pick latest snapshotDate per group
        pipeline = [
            {"$match": {"creatorId": creator_id}},
            {"$sort": {"snapshotDate": -1}},
            {
                "$group": {
                    "_id": "$platform",
                    "doc": {"$first": "$$ROOT"},
                }
            },
            {"$replaceRoot": {"newRoot": "$doc"}},
        ]
        cursor = db[PLATFORM_ANALYTICS_RAW].aggregate(pipeline)
        results = await cursor.to_list(length=20)
        for doc in results:
            doc["_id"] = str(doc["_id"])
        return results

    async def get_history(
        self,
        creator_id: str,
        platform: str,
        days: int = 30,
    ) -> List[Dict]:
        """
        Return time-series analytics snapshots for one platform.

        Args:
            creator_id: The creator's profile ID.
            platform:   The platform name.
            days:       Number of past days to include.

        Returns:
            List of snapshot documents sorted ascending by date.
        """
        db = get_database()
        since = datetime.utcnow() - timedelta(days=days)
        cursor = db[PLATFORM_ANALYTICS_RAW].find(
            {
                "creatorId":    creator_id,
                "platform":     platform,
                "snapshotDate": {"$gte": since},
            },
            sort=[("snapshotDate", 1)],
        )
        results = await cursor.to_list(length=days + 5)
        for doc in results:
            doc["_id"] = str(doc["_id"])
        return results

    async def get_multi_platform_totals(self, creator_id: str) -> Dict:
        """
        Aggregate cross-platform totals from the latest snapshot of each platform.

        Used by the dashboard header to show combined numbers like
        "Total Followers across all platforms".

        Returns:
            Dict with totalFollowers, totalViews, totalLikes, etc.
        """
        snapshots = await self.get_latest_all_platforms(creator_id)
        totals: Dict = {
            "totalFollowers":         0,
            "totalViews":             0,
            "totalLikes":             0,
            "totalComments":          0,
            "totalShares":            0,
            "totalReach":             0,
            "totalImpressions":       0,
            "connectedPlatforms":     len(snapshots),
            "averageEngagementRate":  0.0,
        }
        if not snapshots:
            return totals

        engagement_rates = []
        for snap in snapshots:
            totals["totalFollowers"]   += snap.get("followers", 0) or 0
            totals["totalViews"]       += snap.get("views", 0) or 0
            totals["totalLikes"]       += snap.get("likes", 0) or 0
            totals["totalComments"]    += snap.get("comments", 0) or 0
            totals["totalShares"]      += snap.get("shares", 0) or 0
            totals["totalReach"]       += snap.get("reach", 0) or 0
            totals["totalImpressions"] += snap.get("impressions", 0) or 0
            if snap.get("engagementRate"):
                engagement_rates.append(snap["engagementRate"])

        if engagement_rates:
            totals["averageEngagementRate"] = round(
                sum(engagement_rates) / len(engagement_rates), 2
            )
        return totals

    # ── Content Sync State ───────────────────────────────────────────────

    async def get_content_sync_state(
        self,
        creator_id: str,
        platform: str,
    ) -> Optional[Dict]:
        """
        Fetch the last content-fetch state for a creator/platform pair.

        Returns None if content has never been fetched for this combination.
        """
        db = get_database()
        return await db[CONTENT_SYNC_STATE].find_one(
            {"creatorId": creator_id, "platform": platform}
        )

    async def upsert_content_sync_state(
        self,
        creator_id: str,
        platform: str,
        state: Dict,
    ) -> None:
        """
        Insert or update the content-fetch cursor state.

        Args:
            creator_id: The creator's profile ID.
            platform:   The platform name.
            state:      Dict with lastFetchedAt, totalPostsFetched, etc.
        """
        db = get_database()
        state["updatedAt"] = datetime.utcnow()
        await db[CONTENT_SYNC_STATE].update_one(
            {"creatorId": creator_id, "platform": platform},
            {
                "$set": state,
                "$setOnInsert": {
                    "creatorId": creator_id,
                    "platform":  platform,
                },
            },
            upsert=True,
        )
