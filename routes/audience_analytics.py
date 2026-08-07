"""
routes/audience_analytics.py — Audience Analytics Endpoints

Features covered:
  1. Audience Overview        GET /api/audience/overview
  2. Audience Demographics    GET /api/audience/demographics
  3. Follower Growth Analysis GET /api/audience/follower-growth
  4. Audience Activity        GET /api/audience/activity
  5. Device Usage             GET /api/audience/devices
  6. Geographic Analysis      GET /api/audience/geographic
  7. Reach & Impressions      GET /api/audience/reach
  8. Engagement Insights      GET /api/audience/engagement

  Write endpoints (POST) allow syncing fresh data from social platforms.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional

from authorization import get_current_user
from models import UserModel
from services.audience_analytics_service import AudienceAnalyticsService

from schemas.audience import (
    AudienceAnalyticsCreate,
    AudienceDemographicsCreate,
    AudienceBehaviorCreate,
)


router = APIRouter(
    prefix="/api/audience",
    tags=["Audience Analytics"]
)


def get_audience_service() -> AudienceAnalyticsService:
    return AudienceAnalyticsService()


def get_creator_id(current_user: UserModel) -> str:
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    raise HTTPException(status_code=403, detail="Not authorized as a creator")


# ---------------------------------------------------------------------------
# Feature 1 — Audience Overview
# ---------------------------------------------------------------------------

@router.get("/overview", response_model=Optional[Dict])
async def get_audience_overview(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """
    Return the latest audience snapshot:
    total followers, new followers, monthly growth, reach,
    impressions, and average engagement rate.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_analytics(creator_id)


# ---------------------------------------------------------------------------
# Feature 2 — Audience Demographics
# ---------------------------------------------------------------------------

@router.get("/demographics", response_model=Optional[Dict])
async def get_audience_demographics(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """Return age distribution, gender distribution, and geographic breakdown."""
    creator_id = get_creator_id(current_user)
    return await service.get_demographics(creator_id)


# ---------------------------------------------------------------------------
# Feature 3 — Follower Growth Analysis
# ---------------------------------------------------------------------------

@router.get("/follower-growth", response_model=Dict)
async def get_follower_growth(
    period: str = Query(
        "monthly",
        pattern="^(daily|weekly|monthly)$",
        description="Growth period: daily (7 days) | weekly (4 weeks) | monthly (12 months)",
    ),
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """
    Return follower growth breakdown for the requested period.
    Includes daily/weekly/monthly growth, growth percentage, and a
    time-series array for charting.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_follower_growth(creator_id, period)


# ---------------------------------------------------------------------------
# Feature 4 — Audience Activity Analysis
# ---------------------------------------------------------------------------

@router.get("/activity", response_model=Optional[Dict])
async def get_audience_activity(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """
    Return audience activity patterns:
    most active hours, most active days, and peak engagement time.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_behavior(creator_id)


@router.get("/activity/trends", response_model=Dict)
async def get_activity_trends(
    days: int = Query(30, ge=7, le=90, description="Number of days of trend history"),
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """Return time-series engagement data to track audience activity trends."""
    creator_id = get_creator_id(current_user)
    return await service.get_activity_trends(creator_id, days)


# ---------------------------------------------------------------------------
# Feature 5 — Device Usage Analysis
# ---------------------------------------------------------------------------

@router.get("/devices", response_model=Dict)
async def get_device_usage(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """
    Return device breakdown:
    percentage of mobile, desktop, tablet, and smart TV users.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_device_usage(creator_id)


# ---------------------------------------------------------------------------
# Feature 6 — Geographic Audience Analysis
# ---------------------------------------------------------------------------

@router.get("/geographic", response_model=Dict)
async def get_geographic_analysis(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """
    Return geographic audience breakdown:
    countries, regions, cities, top countries, and top cities.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_geographic_analysis(creator_id)


# ---------------------------------------------------------------------------
# Feature 7 — Reach and Impressions Analysis
# ---------------------------------------------------------------------------

@router.get("/reach", response_model=Dict)
async def get_reach_impressions(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """
    Return reach and impressions analysis:
    total reach, total impressions, unique viewers, reach trend,
    and impression trend (last 30 days).
    """
    creator_id = get_creator_id(current_user)
    return await service.get_reach_impressions(creator_id)


# ---------------------------------------------------------------------------
# Feature 8 — Audience Engagement Insights
# ---------------------------------------------------------------------------

@router.get("/engagement", response_model=Dict)
async def get_engagement_insights(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """
    Return audience engagement insights:
    likes, comments, shares, saves, engagement rate, and
    30-day interaction trend series.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_engagement_insights(creator_id)


# ---------------------------------------------------------------------------
# Write Endpoints — Sync fresh data from social platforms
# ---------------------------------------------------------------------------

@router.post("/analytics", response_model=Dict)
async def save_audience_analytics(
    request: AudienceAnalyticsCreate,
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """Sync a new audience analytics snapshot (followers, reach, impressions)."""
    creator_id = get_creator_id(current_user)
    data = request.model_dump()
    data["creatorId"] = creator_id
    inserted_id = await service.save_analytics(data)
    return {"message": "Audience analytics saved successfully", "id": inserted_id}


@router.post("/demographics", response_model=Dict)
async def save_audience_demographics(
    request: AudienceDemographicsCreate,
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """Sync a new audience demographics snapshot (age, gender, location)."""
    creator_id = get_creator_id(current_user)
    data = request.model_dump()
    data["creatorId"] = creator_id
    inserted_id = await service.save_demographics(data)
    return {"message": "Audience demographics saved successfully", "id": inserted_id}


@router.post("/behavior", response_model=Dict)
async def save_audience_behavior(
    request: AudienceBehaviorCreate,
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    """Sync a new audience behavior snapshot (activity, devices, engagement)."""
    creator_id = get_creator_id(current_user)
    data = request.model_dump()
    data["creatorId"] = creator_id
    inserted_id = await service.save_behavior(data)
    return {"message": "Audience behavior saved successfully", "id": inserted_id}


# Legacy alias — keep /analytics working alongside the new /overview
@router.get("/analytics", response_model=Optional[Dict], include_in_schema=False)
async def get_audience_analytics_legacy(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service),
):
    creator_id = get_creator_id(current_user)
    return await service.get_analytics(creator_id)