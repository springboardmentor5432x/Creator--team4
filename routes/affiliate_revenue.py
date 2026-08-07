"""
routes/affiliate_revenue.py — Affiliate Marketing Revenue Endpoints

Endpoints:
    POST /api/revenue/affiliate → Record affiliate marketing revenue
    GET  /api/revenue/affiliate → Fetch affiliate income records for a creator
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, require_any_permission
from permissions import Permission
from models import UserModel
from schemas.revenue import (
    RevenueTransactionCreate,
    RevenueTransactionResponse,
)
from services.revenue_service import RevenueService

router = APIRouter(prefix="/api/revenue/affiliate", tags=["Affiliate Revenue"])


def get_service(db: AsyncSession = Depends(get_db)) -> RevenueService:
    return RevenueService(db.sync_session if hasattr(db, "sync_session") else db)


@router.post(
    "",
    response_model=RevenueTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record affiliate income",
    description="Stores affiliate marketing transaction revenue.",
)
async def record_affiliate_income(
    payload: RevenueTransactionCreate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_CREATE, Permission.REVENUE_CREATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    payload_dict = payload.model_dump()
    payload_dict["revenue_source"] = "Affiliate Marketing"
    return await service.create_revenue_transaction(current_user, payload_dict)


@router.get(
    "",
    response_model=List[RevenueTransactionResponse],
    summary="List affiliate income records",
    description="Returns recorded affiliate marketing earnings for a creator.",
)
async def get_affiliate_incomes(
    creator_id: str = Query(..., description="Target creator profile ID"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_revenue_by_source(current_user, creator_id, source_name="Affiliate Marketing")
