from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from repositories.content_repository import ContentRepository
from utils.analytics import calculate_engagement_rate, calculate_performance_score, calculate_growth_percentage
from schemas.metrics import MetricSyncRequest
from fastapi import HTTPException

class ContentAnalyticsService:
    def __init__(self):
        self.repository = ContentRepository()

    async def get_all_content(self, creator_id: str) -> List[Dict]:
        return await self.repository.get_posts_by_creator(creator_id)

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

    async def get_top_performing_content(self, creator_id: str, limit: int = 10, platform: str = None) -> List[Dict]:
        posts = await self.repository.get_posts_by_creator(creator_id, limit=0)
        if platform:
            posts = [p for p in posts if p.get("platform") == platform]
        
        post_ids = [str(p["_id"]) for p in posts]
        insights = await self.repository.get_all_insights(post_ids)
        
        # Merge posts and insights, sort by performanceScore
        insight_map = {insight["postId"]: insight for insight in insights}
        
        results = []
        for p in posts:
            p_id = str(p["_id"])
            p_insight = insight_map.get(p_id, {})
            score = p_insight.get("performanceScore", 0)
            results.append({
                "post": p,
                "performanceScore": score
            })
            
        results.sort(key=lambda x: x["performanceScore"], reverse=True)
        return results[:limit]

    async def compare_posts(self, creator_id: str, post1_id: str, post2_id: str) -> Dict:
        p1 = await self.get_content(creator_id, post1_id)
        p2 = await self.get_content(creator_id, post2_id)
        
        m1 = await self.repository.get_metrics_by_post(post1_id) or {}
        m2 = await self.repository.get_metrics_by_post(post2_id) or {}
        
        return {
            "post1": {"post": p1, "metrics": m1},
            "post2": {"post": p2, "metrics": m2}
        }

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
                "averageEngagement": 0.0,
                "bestContent": None,
                "worstContent": None
            }
        
        # Simple extraction based on schema
        return {
            "totalViews": summary.get("totalViews", 0),
            "totalLikes": summary.get("totalLikes", 0),
            "averageEngagement": summary.get("averageEngagementRate", 0.0),
            "bestContent": None, # Could fetch from topContent list
            "worstContent": None
        }

    async def sync_metrics(self, creator_id: str, request: MetricSyncRequest) -> str:
        # Verify access
        await self.get_content(creator_id, request.postId)
        
        # Calculate derived metrics
        engagement_rate = calculate_engagement_rate(request.metrics, request.platform)
        request.metrics['engagementRate'] = engagement_rate
        
        # Save snapshot
        snapshot_id = await self.repository.save_metric_snapshot(request.postId, request.metrics)
        
        # Update insights
        perf_score = calculate_performance_score(request.metrics)
        insight_data = {
            "postId": request.postId,
            "performanceScore": perf_score
        }
        await self.repository.upsert_content_insight(request.postId, insight_data)
        
        return snapshot_id
