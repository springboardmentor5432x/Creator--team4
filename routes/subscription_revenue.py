"""
routes/subscription_revenue.py — Subscription Revenue Endpoints

Endpoints:
    POST /api/revenue/subscription → Record subscription revenue
    GET  /api/revenue/subscription → List subscription revenue records for a creator
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, require_any_permission
from permissions import Permission
from models import UserModel
from schemas.revenue import (
    SubscriptionRevenueCreate,
    SubscriptionRevenueResponse,
)
from services.revenue_service import RevenueService

router = APIRouter(prefix="/api/revenue/subscription", tags=["Subscription Revenue"])


def get_service(db: AsyncSession = Depends(get_db)) -> RevenueService:
    return RevenueService(db.sync_session if hasattr(db, "sync_session") else db)


@router.post(
    "",
    response_model=SubscriptionRevenueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record subscription revenue",
    description="Tracks platform, month, subscribers count, and total subscription revenue.",
)
async def record_subscription_revenue(
    payload: SubscriptionRevenueCreate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_CREATE, Permission.REVENUE_CREATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.record_subscription_revenue(current_user, payload.model_dump())


@router.get(
    "",
    response_model=List[SubscriptionRevenueResponse],
    summary="List subscription revenue records",
    description="Returns recurring subscription earnings breakdown for a creator.",
)
async def get_subscription_revenues(
    creator_id: str = Query(..., description="Target creator profile ID"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_subscription_revenues(current_user, creator_id)
