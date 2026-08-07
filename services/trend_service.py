"""
services/trend_service.py — Trend Detection Business Logic

Identifies trending content using a weighted score formula,
normalizes scores to 0–100, and returns the top N trending items.
"""

from typing import List, Optional
from datetime import datetime, timedelta

from repositories.trend_repository import TrendRepository
from repositories.content_repository import ContentRepository
from schemas.trend import (
    TrendScoreResponse,
    TrendingContentResponse,
    CategoryTrendResponse,
    CategoryTrendListResponse,
)
from utils.analytics import calculate_trend_score, normalize_scores


class TrendService:
    """
    Handles trend detection and scoring.

    Trend Score Formula:
        trend_score = 0.30*views + 0.20*likes + 0.20*shares
                    + 0.15*comments + 0.15*engagement_rate

    Scores are normalized to 0–100 using min-max scaling.
    """

    def __init__(self):
        self.trend_repo = TrendRepository()
        self.content_repo = ContentRepository()

    async def get_category_trends(
        self, creator_id: str
    ) -> CategoryTrendListResponse:
        """
        Feature 2 — Trend Detection by Category.
        Aggregates content performance grouped by Category.
        """
        categories_data = await self.trend_repo.aggregate_by_category(creator_id)

        items = [
            CategoryTrendResponse(**c) for c in categories_data
        ]
        best_cat = items[0].category if items else None

        return CategoryTrendListResponse(
            best_performing_category=best_cat,
            categories=items,
        )


    async def get_top_trending(
        self,
        creator_id: str,
        limit: int = 10,
        platform: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        content_type: Optional[str] = None,
    ) -> TrendingContentResponse:
        """
        Return the top N trending content items.

        Steps:
            1. Fetch creator's content posts.
            2. For each, get latest metrics and compute trend score.
            3. Normalize scores to 0–100.
            4. Cache results in trend_scores collection.
            5. Return sorted top N.

        Args:
            creator_id: Creator ID.
            limit: Max items to return.
            platform: Optional platform filter.
            date_from: Optional start date for content.
            date_to: Optional end date for content.
            content_type: Optional content type filter.

        Returns:
            TrendingContentResponse with ranked items.
        """
        # Step 1: Get all creator content
        posts = await self.content_repo.get_posts_by_creator(creator_id, limit=0)

        # Apply filters
        if platform:
            posts = [p for p in posts if p.get("platform") == platform]
        if content_type:
            posts = [p for p in posts if p.get("contentType") == content_type]
        if date_from:
            posts = [p for p in posts if p.get("publishedAt") and p["publishedAt"] >= date_from]
        if date_to:
            posts = [p for p in posts if p.get("publishedAt") and p["publishedAt"] <= date_to]

        if not posts:
            return TrendingContentResponse(
                trending=[],
                total_count=0,
                generated_at=datetime.utcnow(),
            )

        # Step 2: Get metrics for each post and compute scores
        scored_items = []
        for post in posts:
            post_id = str(post["_id"])
            metrics = await self.content_repo.get_metrics_by_post(post_id)
            if not metrics:
                continue

            raw_score = calculate_trend_score(metrics)
            scored_items.append({
                "content_id": post_id,
                "title": post.get("title", ""),
                "platform": post.get("platform", ""),
                "content_type": post.get("contentType", ""),
                "raw_score": raw_score,
                "views": metrics.get("views", 0),
                "likes": metrics.get("likes", 0),
                "shares": metrics.get("shares", 0),
                "comments": metrics.get("comments", 0),
                "engagement_rate": metrics.get("engagementRate", 0.0),
            })

        if not scored_items:
            return TrendingContentResponse(
                trending=[],
                total_count=0,
                generated_at=datetime.utcnow(),
            )

        # Step 3: Normalize scores to 0–100
        raw_scores = [item["raw_score"] for item in scored_items]
        normalized = normalize_scores(raw_scores)

        for item, norm_score in zip(scored_items, normalized):
            item["trend_score"] = norm_score

        # Step 4: Sort and limit
        scored_items.sort(key=lambda x: x["trend_score"], reverse=True)
        top_items = scored_items[:limit]

        # Step 5: Cache in trend_scores collection
        cache_data = [
            {
                "content_id": item["content_id"],
                "trend_score": item["trend_score"],
                "platform": item["platform"],
                "content_type": item.get("content_type", ""),
                "views": item["views"],
                "likes": item["likes"],
                "shares": item["shares"],
                "comments": item["comments"],
                "engagement_rate": item["engagement_rate"],
            }
            for item in top_items
        ]
        await self.trend_repo.bulk_upsert_trend_scores(cache_data)

        # Step 6: Build response
        now = datetime.utcnow()
        trending = [
            TrendScoreResponse(
                rank=i + 1,
                content_id=item["content_id"],
                title=item.get("title"),
                platform=item.get("platform"),
                trend_score=round(item["trend_score"], 2),
                views=item["views"],
                likes=item["likes"],
                shares=item["shares"],
                comments=item["comments"],
                engagement_rate=item["engagement_rate"],
                generated_at=now,
            )
            for i, item in enumerate(top_items)
        ]

        return TrendingContentResponse(
            trending=trending,
            total_count=len(trending),
            generated_at=now,
        )

    async def recalculate_all_scores(self, creator_id: str) -> int:
        """
        Batch recalculation of trend scores for all creator content.
        Intended for cron/background jobs.

        Returns:
            Number of scores updated.
        """
        result = await self.get_top_trending(creator_id, limit=1000)
        return result.total_count
