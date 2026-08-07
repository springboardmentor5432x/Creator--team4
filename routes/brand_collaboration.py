"""
routes/brand_collaboration.py — Brand Collaboration Endpoints

Endpoints:
    POST /api/revenue/brand-collaboration → Record brand collaboration contract
    GET  /api/revenue/brand-collaboration → List brand collaborations for a creator
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, require_any_permission
from permissions import Permission
from models import UserModel
from schemas.revenue import (
    BrandCollaborationCreate,
    BrandCollaborationResponse,
)
from services.revenue_service import RevenueService

router = APIRouter(prefix="/api/revenue/brand-collaboration", tags=["Brand Collaboration"])


def get_service(db: AsyncSession = Depends(get_db)) -> RevenueService:
    return RevenueService(db.sync_session if hasattr(db, "sync_session") else db)


@router.post(
    "",
    response_model=BrandCollaborationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record brand collaboration",
    description="Stores brand name, campaign title, payment amount, duration in days, and campaign status.",
)
async def record_brand_collaboration(
    payload: BrandCollaborationCreate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_CREATE, Permission.REVENUE_CREATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.record_brand_collaboration(current_user, payload.model_dump())


@router.get(
    "",
    response_model=List[BrandCollaborationResponse],
    summary="List brand collaborations",
    description="Returns brand collaboration contracts for a creator.",
)
async def get_brand_collaborations(
    creator_id: str = Query(..., description="Target creator profile ID"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_brand_collaborations(current_user, creator_id)
