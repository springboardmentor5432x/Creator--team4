from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional

from authorization import get_current_user
from models import UserModel
from services.audience_analytics_service import AudienceAnalyticsService

from schemas.audience import (
    AudienceAnalyticsCreate,
    AudienceDemographicsCreate,
    AudienceBehaviorCreate
)


router = APIRouter(
    prefix="/api/audience",
    tags=["Audience Analytics"]
)


def get_audience_service() -> AudienceAnalyticsService:
    return AudienceAnalyticsService()


def get_creator_id(current_user: UserModel) -> str:
    """
    Extract creator id from authenticated user.
    """

    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id

    raise HTTPException(
        status_code=403,
        detail="Not authorized as a creator"
    )


@router.get("/analytics", response_model=Optional[Dict])
async def get_audience_analytics(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service)
):
    """
    Get audience analytics.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_analytics(creator_id)


@router.get("/demographics", response_model=Optional[Dict])
async def get_audience_demographics(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service)
):
    """
    Get audience demographics.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_demographics(creator_id)


@router.get("/behavior", response_model=Optional[Dict])
async def get_audience_behavior(
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service)
):
    """
    Get audience behavior.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_behavior(creator_id)

@router.post("/analytics", response_model=Dict)
async def save_audience_analytics(
    request: AudienceAnalyticsCreate,
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service)
):
    creator_id = get_creator_id(current_user)

    data = request.model_dump()
    data["creatorId"] = creator_id

    inserted_id = await service.save_analytics(data)

    return {
        "message": "Audience analytics saved successfully",
        "id": inserted_id
    }

@router.post("/demographics", response_model=Dict)
async def save_audience_demographics(
    request: AudienceDemographicsCreate,
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service)
):
    creator_id = get_creator_id(current_user)

    data = request.model_dump()
    data["creatorId"] = creator_id

    inserted_id = await service.save_demographics(data)

    return {
        "message": "Audience demographics saved successfully",
        "id": inserted_id
    }

@router.post("/behavior", response_model=Dict)
async def save_audience_behavior(
    request: AudienceBehaviorCreate,
    current_user: UserModel = Depends(get_current_user),
    service: AudienceAnalyticsService = Depends(get_audience_service)
):
    creator_id = get_creator_id(current_user)

    data = request.model_dump()
    data["creatorId"] = creator_id

    inserted_id = await service.save_behavior(data)

    return {
        "message": "Audience behavior saved successfully",
        "id": inserted_id
    }