from typing import Dict, List, Optional
from datetime import datetime, timedelta
from repositories.audience_repository import AudienceRepository


class AudienceAnalyticsService:
    def __init__(self):
        self.repository = AudienceRepository()

    # ------------------------------------------------------------------
    # Feature 1 — Audience Overview
    # ------------------------------------------------------------------

    async def get_analytics(self, creator_id: str) -> Optional[Dict]:
        """
        Return the latest audience snapshot including total followers,
        new followers, monthly growth, reach, impressions, and
        average engagement rate.
        """
        return await self.repository.get_audience_analytics(creator_id)

    # ------------------------------------------------------------------
    # Feature 2 — Audience Demographics
    # ------------------------------------------------------------------

    async def get_demographics(self, creator_id: str) -> Optional[Dict]:
        """Return age, gender, geographic, and city breakdown."""
        return await self.repository.get_audience_demographics(creator_id)

    # ------------------------------------------------------------------
    # Feature 3 — Follower Growth Analysis
    # ------------------------------------------------------------------

    async def get_follower_growth(
        self, creator_id: str, period: str = "monthly"
    ) -> Dict:
        """
        Return follower growth data for the requested period.

        period:
          - "daily"   → last 7 days of daily snapshots
          - "weekly"  → last 4 weeks (28 days)
          - "monthly" → last 12 months (365 days)
        """
        now = datetime.utcnow()
        if period == "daily":
            start_date = now - timedelta(days=7)
            limit = 7
        elif period == "weekly":
            start_date = now - timedelta(weeks=4)
            limit = 28
        else:  # monthly
            start_date = now - timedelta(days=365)
            limit = 365

        history = await self.repository.get_audience_analytics_history(
            creator_id, start_date, limit=limit
        )

        # Latest snapshot for summary fields
        latest = history[-1] if history else {}

        # Build time-series list
        growth_series = [
            {
                "date": doc.get("recordedAt"),
                "totalFollowers": doc.get("totalFollowers", 0),
                "newFollowers": doc.get("newFollowers", 0),
                "dailyGrowth": doc.get("dailyGrowth", 0),
                "weeklyGrowth": doc.get("weeklyGrowth", 0),
                "monthlyGrowth": doc.get("monthlyGrowth", 0),
                "growthRate": doc.get("growthRate", 0.0),
            }
            for doc in history
        ]

        return {
            "period": period,
            "totalFollowers": latest.get("totalFollowers", 0),
            "newFollowers": latest.get("newFollowers", 0),
            "growthPercentage": latest.get("growthRate", 0.0),
            "dailyGrowth": latest.get("dailyGrowth", 0),
            "weeklyGrowth": latest.get("weeklyGrowth", 0),
            "monthlyGrowth": latest.get("monthlyGrowth", 0),
            "growthSeries": growth_series,
        }

    # ------------------------------------------------------------------
    # Feature 4 — Audience Activity Analysis
    # ------------------------------------------------------------------

    async def get_behavior(self, creator_id: str) -> Optional[Dict]:
        """
        Return audience activity patterns: active hours, active days,
        peak engagement time, and device usage breakdown.
        """
        return await self.repository.get_audience_behavior(creator_id)

    async def get_activity_trends(self, creator_id: str, days: int = 30) -> Dict:
        """Return time-series behavior snapshots for activity trend analysis."""
        start_date = datetime.utcnow() - timedelta(days=days)
        history = await self.repository.get_audience_behavior_history(
            creator_id, start_date, limit=days
        )
        trend_series = [
            {
                "date": doc.get("recordedAt"),
                "engagementRate": doc.get("engagementRate", 0.0),
                "likes": doc.get("likes", 0),
                "comments": doc.get("comments", 0),
                "shares": doc.get("shares", 0),
                "saves": doc.get("saves", 0),
            }
            for doc in history
        ]
        return {"days": days, "activityTrends": trend_series}

    # ------------------------------------------------------------------
    # Feature 5 — Device Usage Analysis
    # ------------------------------------------------------------------

    async def get_device_usage(self, creator_id: str) -> Dict:
        """
        Return device breakdown: mobile, desktop, tablet, smart TV.
        Pulls from the latest audience_behavior snapshot.
        """
        doc = await self.repository.get_audience_behavior(creator_id)
        if not doc:
            return {
                "mobileUsers": 0.0,
                "desktopUsers": 0.0,
                "tabletUsers": 0.0,
                "smartTVUsers": 0.0,
                "deviceUsage": {},
            }
        return {
            "mobileUsers": doc.get("mobileUsers", 0.0),
            "desktopUsers": doc.get("desktopUsers", 0.0),
            "tabletUsers": doc.get("tabletUsers", 0.0),
            "smartTVUsers": doc.get("smartTVUsers", 0.0),
            "deviceUsage": doc.get("deviceUsage", {}),
        }

    # ------------------------------------------------------------------
    # Feature 6 — Geographic Audience Analysis
    # ------------------------------------------------------------------

    async def get_geographic_analysis(self, creator_id: str) -> Dict:
        """
        Return geographic breakdown: countries, regions, cities,
        and pre-ranked top countries / cities.
        """
        doc = await self.repository.get_audience_demographics(creator_id)
        if not doc:
            return {
                "countries": {},
                "regions": {},
                "cities": {},
                "topCountries": [],
                "topCities": [],
            }

        countries: Dict[str, float] = doc.get("countries", {})
        regions: Dict[str, float] = doc.get("regions", {})
        cities: Dict[str, float] = doc.get("cities", {})

        # Derive top lists if not pre-computed
        top_countries = doc.get("topCountries") or sorted(
            countries, key=countries.get, reverse=True
        )[:5]
        top_cities = doc.get("topCities") or sorted(
            cities, key=cities.get, reverse=True
        )[:5]

        return {
            "countries": countries,
            "regions": regions,
            "cities": cities,
            "topCountries": top_countries,
            "topCities": top_cities,
        }

    # ------------------------------------------------------------------
    # Feature 7 — Reach and Impressions Analysis
    # ------------------------------------------------------------------

    async def get_reach_impressions(self, creator_id: str) -> Dict:
        """
        Return reach, impressions, unique viewers, and time-series
        trends for the last 30 days.
        """
        latest = await self.repository.get_audience_analytics(creator_id)
        if not latest:
            return {
                "totalReach": 0,
                "totalImpressions": 0,
                "uniqueViewers": 0,
                "reachTrend": [],
                "impressionTrend": [],
            }

        # Last 30 days of history for trend data
        start_date = datetime.utcnow() - timedelta(days=30)
        history = await self.repository.get_audience_analytics_history(
            creator_id, start_date, limit=30
        )
        reach_trend = [
            {"date": d.get("recordedAt"), "reach": d.get("reach", 0)}
            for d in history
        ]
        impression_trend = [
            {"date": d.get("recordedAt"), "impressions": d.get("impressions", 0)}
            for d in history
        ]

        return {
            "totalReach": latest.get("reach", 0),
            "totalImpressions": latest.get("impressions", 0),
            "uniqueViewers": latest.get("uniqueViewers", 0),
            "reachTrend": reach_trend,
            "impressionTrend": impression_trend,
        }

    # ------------------------------------------------------------------
    # Feature 8 — Audience Engagement Insights
    # ------------------------------------------------------------------

    async def get_engagement_insights(self, creator_id: str) -> Dict:
        """
        Return engagement metrics (likes, comments, shares, saves,
        engagement rate) and 30-day interaction trends.
        """
        latest = await self.repository.get_audience_behavior(creator_id)
        if not latest:
            return {
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "saves": 0,
                "engagementRate": 0.0,
                "interactionTrends": [],
            }

        start_date = datetime.utcnow() - timedelta(days=30)
        history = await self.repository.get_audience_behavior_history(
            creator_id, start_date, limit=30
        )
        interaction_trends = [
            {
                "date": d.get("recordedAt"),
                "likes": d.get("likes", 0),
                "comments": d.get("comments", 0),
                "shares": d.get("shares", 0),
                "saves": d.get("saves", 0),
                "engagementRate": d.get("engagementRate", 0.0),
            }
            for d in history
        ]

        return {
            "likes": latest.get("likes", 0),
            "comments": latest.get("comments", 0),
            "shares": latest.get("shares", 0),
            "saves": latest.get("saves", 0),
            "engagementRate": latest.get("engagementRate", 0.0),
            "interactionTrends": interaction_trends,
        }

    # ------------------------------------------------------------------
    # Write methods (POST endpoints)
    # ------------------------------------------------------------------

    async def save_analytics(self, data: Dict) -> str:
        return await self.repository.save_audience_analytics(data)

    async def save_demographics(self, data: Dict) -> str:
        return await self.repository.save_audience_demographics(data)

    async def save_behavior(self, data: Dict) -> str:
        return await self.repository.save_audience_behavior(data)