from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from repositories.content_repository import ContentRepository
from utils.analytics import calculate_engagement_rate, calculate_performance_score, calculate_growth_percentage
from schemas.metrics import MetricSyncRequest
from fastapi import HTTPException

class ContentAnalyticsService:
    def __init__(self):
        self.repository = ContentRepository()

    async def get_all_content(
        self,
        creator_id: str,
        search: Optional[str] = None,
        platform: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "publishedAt",
        sort_order: str = "desc",
    ) -> List[Dict]:
        import pymongo
        order = pymongo.DESCENDING if sort_order == "desc" else pymongo.ASCENDING
        return await self.repository.get_posts_by_creator(
            creator_id,
            search=search,
            platform=platform,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=order,
        )

    async def get_content(self, creator_id: str, post_id: str) -> Dict:
        post = await self.repository.get_post_by_id(post_id)
        if not post or post.get("creatorId") != creator_id:
            raise HTTPException(status_code=404, detail="Content not found or unauthorized")
        return post

    async def get_content_metrics(self, creator_id: str, post_id: str) -> Dict:
        # Verify access
        await self.get_content(creator_id, post_id)
        metrics = await self.repository.get_metrics_by_post(post_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Metrics not found")
        return metrics

    async def get_content_history(self, creator_id: str, post_id: str) -> List[Dict]:
        # Verify access
        await self.get_content(creator_id, post_id)
        return await self.repository.get_metrics_history(post_id)

    # Metrics that can be used to rank top-performing content.
    # Each key maps to the field name inside the content_metrics document.
    _METRIC_SORT_FIELDS = {
        "views": "views",
        "likes": "likes",
        "comments": "comments",
        "shares": "shares",
        "watchTime": "watchTime",
        "engagementRate": "engagementRate",
        "performanceScore": None,  # composite — handled separately
    }

    async def get_top_performing_content(
        self,
        creator_id: str,
        limit: int = 10,
        platform: Optional[str] = None,
        sort_by: str = "performanceScore",
    ) -> List[Dict]:
        posts = await self.repository.get_posts_by_creator(
            creator_id, limit=0, platform=platform
        )

        if not posts:
            return []

        post_ids = [str(p["_id"]) for p in posts]

        # Fetch latest metrics for all posts in a single DB round-trip
        metrics_list = await self.repository.get_metrics_for_posts(post_ids)
        metrics_map = {m["postId"]: m for m in metrics_list}

        if sort_by == "performanceScore":
            # Use stored performanceScore from content_insights
            insights = await self.repository.get_all_insights(post_ids)
            insight_map = {i["postId"]: i for i in insights}
            results = [
                {
                    "post": p,
                    "metrics": metrics_map.get(str(p["_id"]), {}),
                    "performanceScore": insight_map.get(str(p["_id"]), {}).get("performanceScore", 0),
                }
                for p in posts
            ]
            results.sort(key=lambda x: x["performanceScore"], reverse=True)
        else:
            # Sort by a specific raw metric field
            metric_field = self._METRIC_SORT_FIELDS.get(sort_by, "views")
            results = [
                {
                    "post": p,
                    "metrics": metrics_map.get(str(p["_id"]), {}),
                    "performanceScore": metrics_map.get(str(p["_id"]), {}).get(metric_field, 0),
                }
                for p in posts
            ]
            results.sort(key=lambda x: x["performanceScore"], reverse=True)

        return results[:limit]

    async def compare_posts(self, creator_id: str, post_ids: List[str]) -> Dict:
        """Compare 2 or more posts side by side."""
        if len(post_ids) < 2:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="At least 2 post IDs are required for comparison")

        posts = []
        for pid in post_ids:
            post = await self.get_content(creator_id, pid)
            posts.append(post)

        metrics_list = await self.repository.get_metrics_for_posts(post_ids)
        metrics_map = {m["postId"]: m for m in metrics_list}

        comparison = []
        for post in posts:
            pid = str(post["_id"])
            comparison.append({
                "post": post,
                "metrics": metrics_map.get(pid, {}),
            })

        return {"comparison": comparison, "count": len(comparison)}

    async def reach_analysis(self, creator_id: str) -> Dict:
        summary = await self.repository.get_analytics_summary(creator_id)
        if not summary:
            return {"reach": 0, "views": 0, "uniqueReach": 0, "growth": 0.0}
            
        return {
            "reach": summary.get("totalReach", 0),
            "views": summary.get("totalViews", 0),
            "uniqueReach": summary.get("totalReach", 0), # Simplified for now
            "growth": 0.0 # Requires historical trend calculation for accurate growth
        }

    async def get_performance_trends(self, creator_id: str, period: str = "monthly") -> List[Dict]:
        end_date = datetime.utcnow()
        if period == "daily":
            start_date = end_date - timedelta(days=7)
        elif period == "weekly":
            start_date = end_date - timedelta(weeks=4)
        else: # monthly
            start_date = end_date - timedelta(days=365)
            
        return await self.repository.get_performance_trends(creator_id, start_date, end_date)

    async def get_dashboard_summary(self, creator_id: str) -> Dict:
        summary = await self.repository.get_analytics_summary(creator_id)
        if not summary:
            return {
                "totalViews": 0,
                "totalLikes": 0,
                "totalComments": 0,
                "totalShares": 0,
                "totalSaves": 0,
                "totalReach": 0,
                "averageEngagement": 0.0,
                "bestContent": None,
                "worstContent": None,
            }

        return {
            "totalViews": summary.get("totalViews", 0),
            "totalLikes": summary.get("totalLikes", 0),
            "totalComments": summary.get("totalComments", 0),
            "totalShares": summary.get("totalShares", 0),
            "totalSaves": summary.get("totalSaves", 0),
            "totalReach": summary.get("totalReach", 0),
            "averageEngagement": summary.get("averageEngagementRate", 0.0),
            "bestContent": None,
            "worstContent": None,
        }

    async def sync_metrics(self, creator_id: str, request: MetricSyncRequest) -> str:
        """
        Sync a metric snapshot for a single post, then rebuild analytics_summary
        and upsert today's performance_trends entry so all read endpoints stay current.

        Flow:
          1. Verify the post belongs to this creator.
          2. Compute engagementRate and save a new content_metrics snapshot.
          3. Compute performanceScore and upsert content_insights.
          4. Fetch the latest metrics for ALL creator posts and aggregate totals.
          5. Upsert analytics_summary with those totals.
          6. Upsert today's performance_trends entry (one record per calendar day).
        """
        # 1. Verify access
        await self.get_content(creator_id, request.postId)

        # 2. Compute engagement rate and persist the snapshot
        engagement_rate = calculate_engagement_rate(request.metrics, request.platform)
        request.metrics["engagementRate"] = engagement_rate
        snapshot_id = await self.repository.save_metric_snapshot(request.postId, request.metrics)

        # 3. Upsert content_insights with the composite performance score
        perf_score = calculate_performance_score(request.metrics)
        await self.repository.upsert_content_insight(request.postId, {
            "postId": request.postId,
            "performanceScore": perf_score,
        })

        # 4. Re-aggregate totals across ALL posts for this creator
        all_posts = await self.repository.get_posts_by_creator(creator_id, limit=0)
        all_post_ids = [str(p["_id"]) for p in all_posts]

        total_views = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        total_saves = 0
        total_reach = 0
        total_watch_time = 0
        engagement_rates: List[float] = []

        if all_post_ids:
            latest_metrics = await self.repository.get_metrics_for_posts(all_post_ids)
            for m in latest_metrics:
                total_views    += m.get("views", 0)
                total_likes    += m.get("likes", 0)
                total_comments += m.get("comments", 0)
                total_shares   += m.get("shares", 0)
                total_saves    += m.get("saves", 0)
                total_reach    += m.get("reach", 0)
                total_watch_time += m.get("watchTime", 0)
                er = m.get("engagementRate", 0.0)
                if er:
                    engagement_rates.append(er)

        avg_engagement = (
            round(sum(engagement_rates) / len(engagement_rates), 4)
            if engagement_rates else 0.0
        )

        # 5. Upsert analytics_summary (one document per creator)
        summary_data = {
            "totalViews":            total_views,
            "totalLikes":            total_likes,
            "totalComments":         total_comments,
            "totalShares":           total_shares,
            "totalSaves":            total_saves,
            "totalReach":            total_reach,
            "totalWatchTime":        total_watch_time,
            "averageEngagementRate": avg_engagement,
        }
        await self.repository.update_analytics_summary(creator_id, summary_data)

        # 6. Upsert today's entry in performance_trends (daily bucket)
        trend_data = {
            "totalViews":        total_views,
            "totalLikes":        total_likes,
            "totalComments":     total_comments,
            "totalShares":       total_shares,
            "totalSaves":        total_saves,
            "totalReach":        total_reach,
            "averageWatchTime":  round(total_watch_time / len(all_post_ids), 2) if all_post_ids else 0.0,
            "engagementRate":    avg_engagement,
        }
        await self.repository.upsert_performance_trend(
            creator_id, datetime.utcnow(), trend_data
        )

        return snapshot_id

