"""
repositories/revenue_mongo_repository.py — MongoDB Analytics Data Access Layer for Revenue Module

Stores and queries:
- Revenue history snapshots
- Monthly revenue analytics summaries
- Trend analytics records
- Historical revenue reports
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from mongo.mongodb import get_database
from models.revenue_mongo import (
    REVENUE_HISTORY,
    MONTHLY_REVENUE_ANALYTICS,
    REVENUE_TREND_ANALYTICS,
    HISTORICAL_REVENUE_REPORTS,
)


class RevenueMongoRepository:
    """Data Access Layer for Revenue Analytics in MongoDB."""

    async def save_revenue_history_snapshot(self, creator_id: str, snapshot_data: Dict[str, Any]) -> str:
        """Save a snapshot of revenue history to MongoDB."""
        db = get_database()
        document = {
            "creatorId": creator_id,
            "snapshotData": snapshot_data,
            "savedAt": datetime.utcnow(),
        }
        res = await db[REVENUE_HISTORY].insert_one(document)
        return str(res.inserted_id)

    async def upsert_monthly_analytics(self, creator_id: str, year_month: str, analytics_data: Dict[str, Any]):
        """Insert or update monthly revenue analytics document."""
        db = get_database()
        await db[MONTHLY_REVENUE_ANALYTICS].update_one(
            {"creatorId": creator_id, "yearMonth": year_month},
            {"$set": {
                "creatorId": creator_id,
                "yearMonth": year_month,
                "analytics": analytics_data,
                "updatedAt": datetime.utcnow(),
            }},
            upsert=True,
        )

    async def save_trend_analytics(self, creator_id: str, trend_data: Dict[str, Any]) -> str:
        """Save calculated revenue trends into MongoDB."""
        db = get_database()
        doc = {
            "creatorId": creator_id,
            "trends": trend_data,
            "calculatedAt": datetime.utcnow(),
        }
        res = await db[REVENUE_TREND_ANALYTICS].insert_one(doc)
        return str(res.inserted_id)

    async def save_historical_report(self, creator_id: str, report_type: str, report_body: Dict[str, Any]) -> str:
        """Save a generated historical report."""
        db = get_database()
        doc = {
            "creatorId": creator_id,
            "reportType": report_type,
            "report": report_body,
            "generatedAt": datetime.utcnow(),
        }
        res = await db[HISTORICAL_REVENUE_REPORTS].insert_one(doc)
        return str(res.inserted_id)

    async def get_historical_reports(self, creator_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent historical reports for a creator."""
        db = get_database()
        cursor = db[HISTORICAL_REVENUE_REPORTS].find(
            {"creatorId": creator_id}
        ).sort("generatedAt", -1).limit(limit)
        results = await cursor.to_list(length=limit)
        for r in results:
            r["_id"] = str(r["_id"])
        return results
