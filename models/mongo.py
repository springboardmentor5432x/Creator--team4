from pymongo import IndexModel, ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorDatabase

# ---------------------------------------------------------------------------
# Collection Names — Existing
# ---------------------------------------------------------------------------
SOCIAL_ACCOUNTS = "social_accounts"
CONTENT_POSTS = "content_posts"
CONTENT_METRICS = "content_metrics"
ANALYTICS_SUMMARY = "analytics_summary"
PERFORMANCE_TRENDS = "performance_trends"
CONTENT_INSIGHTS = "content_insights"

# ---------------------------------------------------------------------------
# Collection Names — Growth Analytics Module
# ---------------------------------------------------------------------------
GROWTH_METRICS = "growth_metrics"
CONTENT_GROWTH = "content_growth"
HASHTAGS = "hashtags"
TREND_SCORES = "trend_scores"
PREDICTIONS = "predictions"


async def setup_mongodb_indexes(db: AsyncIOMotorDatabase):
    """
    Creates necessary indexes for MongoDB collections.
    Called once during app startup from main.py.
    """

    # -----------------------------------------------------------------------
    # Existing Collections
    # -----------------------------------------------------------------------
    
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

    # -----------------------------------------------------------------------
    # Growth Analytics Collections
    # -----------------------------------------------------------------------

    # 7. growth_metrics — one record per creator per day per platform
    await db[GROWTH_METRICS].create_indexes([
        IndexModel([("creator_id", ASCENDING), ("date", ASCENDING)], unique=True),
        IndexModel([("creator_id", ASCENDING), ("platform", ASCENDING), ("date", ASCENDING)]),
    ])

    # 8. content_growth — daily per-content metric snapshots
    await db[CONTENT_GROWTH].create_indexes([
        IndexModel([("content_id", ASCENDING), ("date", ASCENDING)], unique=True),
        IndexModel([("creator_id", ASCENDING), ("date", ASCENDING)]),
    ])

    # 9. hashtags — aggregated hashtag statistics
    await db[HASHTAGS].create_indexes([
        IndexModel([("name", ASCENDING)], unique=True),
        IndexModel([("growth_percentage", DESCENDING)]),
    ])

    # 10. trend_scores — computed trend rankings
    await db[TREND_SCORES].create_indexes([
        IndexModel([("content_id", ASCENDING)]),
        IndexModel([("trend_score", DESCENDING)]),
        IndexModel([("generated_at", ASCENDING)], expireAfterSeconds=604800),  # 7-day TTL
    ])

    # 11. predictions — reach/audience predictions
    await db[PREDICTIONS].create_indexes([
        IndexModel([("creator_id", ASCENDING), ("prediction_type", ASCENDING)]),
        IndexModel([("generated_at", ASCENDING)], expireAfterSeconds=2592000),  # 30-day TTL
    ])
    
    print("MongoDB indexes created successfully.")
