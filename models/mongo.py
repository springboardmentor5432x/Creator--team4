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

# ---------------------------------------------------------------------------
# Collection Names — Audience Analytics Module
# ---------------------------------------------------------------------------
AUDIENCE_ANALYTICS   = "audience_analytics"
AUDIENCE_DEMOGRAPHICS = "audience_demographics"
AUDIENCE_BEHAVIOR    = "audience_behavior"


# ---------------------------------------------------------------------------
# Collection Names — Social Media Analytics Module
# ---------------------------------------------------------------------------
PLATFORM_ANALYTICS_RAW = "platform_analytics_raw"
CONTENT_SYNC_STATE     = "content_sync_state"

# ---------------------------------------------------------------------------
# Collection Names — Reports & Notifications Module
# ---------------------------------------------------------------------------
REPORT_SNAPSHOTS       = "report_snapshots"


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
        IndexModel([("postId", ASCENDING)]),                                       # non-unique: multiple snapshots per post
        IndexModel([("postId", ASCENDING), ("snapshotDate", DESCENDING)], unique=True),  # one snapshot per post per timestamp
        IndexModel([("snapshotDate", DESCENDING)])
    ])

    # 4. analytics_summary
    await db[ANALYTICS_SUMMARY].create_indexes([
        IndexModel([("creatorId", ASCENDING)], unique=True)
    ])

    # 5. performance_trends
    await db[PERFORMANCE_TRENDS].create_indexes([
        IndexModel([("creatorId", ASCENDING), ("trendDate", DESCENDING)]),
        IndexModel([("creatorId", ASCENDING), ("trendDate", ASCENDING)], unique=True),  # one row per creator per day
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

    # -----------------------------------------------------------------------
    # Audience Analytics Collections
    # -----------------------------------------------------------------------

    # 12. audience_analytics — latest follower/reach/impression snapshot per creator
    await db[AUDIENCE_ANALYTICS].create_indexes([
        IndexModel([("creatorId", ASCENDING)]),
        IndexModel([("creatorId", ASCENDING), ("recordedAt", DESCENDING)]),
    ])

    # 13. audience_demographics — age / gender / geo breakdown
    await db[AUDIENCE_DEMOGRAPHICS].create_indexes([
        IndexModel([("creatorId", ASCENDING)]),
        IndexModel([("creatorId", ASCENDING), ("recordedAt", DESCENDING)]),
    ])

    # 14. audience_behavior — active hours / device / engagement breakdown
    await db[AUDIENCE_BEHAVIOR].create_indexes([
        IndexModel([("creatorId", ASCENDING)]),
        IndexModel([("creatorId", ASCENDING), ("recordedAt", DESCENDING)]),
    ])

    # -----------------------------------------------------------------------
    # Social Media Analytics Module Collections
    # -----------------------------------------------------------------------

    # 15. platform_analytics_raw — normalized per-platform daily analytics snapshots
    await db[PLATFORM_ANALYTICS_RAW].create_indexes([
        IndexModel(
            [("creatorId", ASCENDING), ("platform", ASCENDING), ("snapshotDate", ASCENDING)],
            unique=True,
        ),
        IndexModel([("creatorId", ASCENDING), ("snapshotDate", DESCENDING)]),
        IndexModel([("platform", ASCENDING), ("snapshotDate", DESCENDING)]),
    ])

    # 16. content_sync_state — last-fetch cursor per creator per platform
    await db[CONTENT_SYNC_STATE].create_indexes([
        IndexModel([("creatorId", ASCENDING), ("platform", ASCENDING)], unique=True),
    ])

    # 17. report_snapshots — JSON snapshots of generated reports
    await db[REPORT_SNAPSHOTS].create_indexes([
        IndexModel([("reportId", ASCENDING)], unique=True),
        IndexModel([("creatorId", ASCENDING), ("createdAt", DESCENDING)]),
    ])

    from models.revenue_mongo import setup_revenue_mongodb_indexes
    await setup_revenue_mongodb_indexes(db)

    print("MongoDB indexes created successfully.")
