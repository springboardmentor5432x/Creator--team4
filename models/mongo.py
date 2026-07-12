from pymongo import IndexModel, ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorDatabase

# Collection Names
SOCIAL_ACCOUNTS = "social_accounts"
CONTENT_POSTS = "content_posts"
CONTENT_METRICS = "content_metrics"
ANALYTICS_SUMMARY = "analytics_summary"
PERFORMANCE_TRENDS = "performance_trends"
CONTENT_INSIGHTS = "content_insights"

async def setup_mongodb_indexes(db: AsyncIOMotorDatabase):
    """
    Creates necessary indexes for MongoDB collections.
    """
    
    # 1. social_accounts
    await db[SOCIAL_ACCOUNTS].create_indexes([
        IndexModel([("creatorId", ASCENDING)]),
        IndexModel([("creatorId", ASCENDING), ("platform", ASCENDING), ("accountId", ASCENDING)], unique=True)
    ])

    # 2. content_posts
    await db[CONTENT_POSTS].create_indexes([
        IndexModel([("creatorId", ASCENDING)]),
        IndexModel([("socialAccountId", ASCENDING), ("platformPostId", ASCENDING)], unique=True),
        IndexModel([("creatorId", ASCENDING), ("publishedAt", DESCENDING)])
    ])

    # 3. content_metrics
    await db[CONTENT_METRICS].create_indexes([
        IndexModel([("postId", ASCENDING)], unique=True),
        IndexModel([("snapshotDate", DESCENDING)])
    ])

    # 4. analytics_summary
    await db[ANALYTICS_SUMMARY].create_indexes([
        IndexModel([("creatorId", ASCENDING)], unique=True)
    ])

    # 5. performance_trends
    await db[PERFORMANCE_TRENDS].create_indexes([
        IndexModel([("creatorId", ASCENDING), ("trendDate", DESCENDING)])
    ])

    # 6. content_insights
    await db[CONTENT_INSIGHTS].create_indexes([
        IndexModel([("postId", ASCENDING)], unique=True)
    ])
    
    print("MongoDB indexes created successfully.")
