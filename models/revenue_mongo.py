"""
models/revenue_mongo.py — MongoDB Collection definitions & index setup for Revenue Analytics
"""

from pymongo import IndexModel, ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorDatabase

# Collection Names
REVENUE_HISTORY = "revenue_history"
MONTHLY_REVENUE_ANALYTICS = "monthly_revenue_analytics"
REVENUE_TREND_ANALYTICS = "revenue_trend_analytics"
HISTORICAL_REVENUE_REPORTS = "historical_revenue_reports"


async def setup_revenue_mongodb_indexes(db: AsyncIOMotorDatabase):
    """
    Creates necessary indexes for Revenue Analytics MongoDB collections.
    """
    # 1. revenue_history
    await db[REVENUE_HISTORY].create_indexes([
        IndexModel([("creatorId", ASCENDING), ("transactionDate", DESCENDING)]),
        IndexModel([("source", ASCENDING)]),
        IndexModel([("platform", ASCENDING)]),
    ])

    # 2. monthly_revenue_analytics
    await db[MONTHLY_REVENUE_ANALYTICS].create_indexes([
        IndexModel([("creatorId", ASCENDING), ("yearMonth", DESCENDING)], unique=True),
        IndexModel([("yearMonth", DESCENDING)]),
    ])

    # 3. revenue_trend_analytics
    await db[REVENUE_TREND_ANALYTICS].create_indexes([
        IndexModel([("creatorId", ASCENDING), ("calculatedAt", DESCENDING)]),
    ])

    # 4. historical_revenue_reports
    await db[HISTORICAL_REVENUE_REPORTS].create_indexes([
        IndexModel([("creatorId", ASCENDING), ("reportType", ASCENDING), ("generatedAt", DESCENDING)]),
    ])

    print("Revenue Analytics MongoDB indexes created successfully.")
