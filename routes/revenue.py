"""
routes/revenue.py — Primary Revenue Endpoints for Module 5

Endpoints:
    POST   /api/revenue                  → Create revenue transaction
    GET    /api/revenue                  → List revenue transactions for a creator
    GET    /api/revenue/monthly          → Get monthly revenue aggregates
    GET    /api/revenue/yearly           → Get yearly revenue aggregates
    GET    /api/revenue/trends           → Get revenue trends, moving avg, and growth %
    GET    /api/revenue/financial-summary→ Get financial summary
    GET    /api/revenue/source/{source}  → Get revenue by source
    GET    /api/revenue/top-creators     → Get top earning creators
    GET    /api/revenue/{id}             → Get single revenue transaction
    PUT    /api/revenue/{id}             → Update revenue transaction
    DELETE /api/revenue/{id}             → Delete revenue transaction

Permissions matrix:
    revenue:view        — Admin ✅, Agency ✅, Creator Own, Marketing ✅
    revenue:create      — Admin ✅, Agency ✅, Creator Own
    revenue:update      — Admin ✅, Agency ✅, Creator Own
    revenue:delete      — Admin ✅, Agency ✅, Creator Own
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_db, require_any_permission
from permissions import Permission
from models import UserModel
from schemas.revenue import (
    RevenueTransactionCreate,
    RevenueTransactionUpdate,
    RevenueTransactionResponse,
    RevenueTrendsResponse,
    FinancialSummaryResponse,
    TopCreatorRevenueItem,
)
from services.revenue_service import RevenueService

router = APIRouter(prefix="/api/revenue", tags=["Revenue Analytics"])


def get_service(db: AsyncSession = Depends(get_db)) -> RevenueService:
    return RevenueService(db.sync_session if hasattr(db, "sync_session") else db)


# ---------------------------------------------------------------------------
# POST /api/revenue — Create Revenue Transaction
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=RevenueTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create revenue transaction",
    description="Records a new revenue item in the central financial ledger.",
)
async def create_revenue(
    payload: RevenueTransactionCreate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_CREATE, Permission.REVENUE_CREATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return await service.create_revenue_transaction(current_user, payload.model_dump())


# ---------------------------------------------------------------------------
# GET /api/revenue — List Revenue Transactions
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[RevenueTransactionResponse],
    summary="Get revenue by creator",
    description="Returns revenue transactions for a given creator profile ID.",
)
async def get_revenue_by_creator(
    creator_id: str = Query(..., description="Target creator profile ID"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_revenue_by_creator(current_user, creator_id, limit, offset)


# ---------------------------------------------------------------------------
# GET /api/revenue/monthly — Monthly Revenue Breakdown
# ---------------------------------------------------------------------------

@router.get(
    "/monthly",
    response_model=List[Dict[str, Any]],
    summary="Monthly revenue aggregate",
    description="Returns month-by-month total earnings for a creator.",
)
async def get_monthly_revenue(
    creator_id: str = Query(...),
    year: Optional[int] = Query(None),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_monthly_revenue(current_user, creator_id, year)


# ---------------------------------------------------------------------------
# GET /api/revenue/yearly — Yearly Revenue Breakdown
# ---------------------------------------------------------------------------

@router.get(
    "/yearly",
    response_model=List[Dict[str, Any]],
    summary="Yearly revenue aggregate",
    description="Returns year-by-year total earnings for a creator.",
)
async def get_yearly_revenue(
    creator_id: str = Query(...),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_yearly_revenue(current_user, creator_id)


# ---------------------------------------------------------------------------
# GET /api/revenue/trends — Revenue Trends, Moving Average & Growth %
# ---------------------------------------------------------------------------

@router.get(
    "/trends",
    response_model=RevenueTrendsResponse,
    summary="Revenue trends and growth metrics",
    description="Calculates daily, weekly, monthly, yearly totals, moving average, and growth percentage.",
)
async def get_revenue_trends(
    creator_id: str = Query(...),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return await service.get_revenue_trends(current_user, creator_id)


# ---------------------------------------------------------------------------
# GET /api/revenue/financial-summary — Financial Summary
# ---------------------------------------------------------------------------

@router.get(
    "/financial-summary",
    response_model=FinancialSummaryResponse,
    summary="High-level financial summary",
    description="Returns total revenue, MRR, active sponsorships count, and top revenue source.",
)
async def get_financial_summary(
    creator_id: str = Query(...),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_financial_summary(current_user, creator_id)


# ---------------------------------------------------------------------------
# GET /api/revenue/source/{source} — Revenue by Source
# ---------------------------------------------------------------------------

@router.get(
    "/source/{source}",
    response_model=List[Dict[str, Any]],
    summary="Revenue filtered by source",
    description="Returns revenue aggregate for a specific source (e.g., Sponsorship, Ad Revenue).",
)
async def get_revenue_by_source(
    source: str,
    creator_id: str = Query(...),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_revenue_by_source(current_user, creator_id, source)


# ---------------------------------------------------------------------------
# GET /api/revenue/top-creators — Top Earning Creators
# ---------------------------------------------------------------------------

@router.get(
    "/top-creators",
    response_model=List[TopCreatorRevenueItem],
    summary="Top earning creators",
    description="Ranks top creators by overall earnings. Restricted to Admin, Agency, and Marketing roles.",
)
async def get_top_creators(
    limit: int = Query(10, ge=1, le=100),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_top_creators(current_user, limit)


# ---------------------------------------------------------------------------
# GET /api/revenue/{id} — Single Revenue Transaction
# ---------------------------------------------------------------------------

@router.get(
    "/{id}",
    response_model=RevenueTransactionResponse,
    summary="Get single revenue transaction",
    description="Fetches a specific revenue record by ID.",
)
async def get_revenue_by_id(
    id: int,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_revenue_transaction(current_user, id)


# ---------------------------------------------------------------------------
# PUT /api/revenue/{id} — Update Revenue Transaction
# ---------------------------------------------------------------------------

@router.put(
    "/{id}",
    response_model=RevenueTransactionResponse,
    summary="Update revenue transaction",
    description="Updates fields of an existing revenue transaction.",
)
async def update_revenue(
    id: int,
    payload: RevenueTransactionUpdate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_UPDATE, Permission.REVENUE_UPDATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.update_revenue_transaction(current_user, id, payload.model_dump(exclude_unset=True))


# ---------------------------------------------------------------------------
# DELETE /api/revenue/{id} — Delete Revenue Transaction
# ---------------------------------------------------------------------------

@router.delete(
    "/{id}",
    response_model=Dict[str, Any],
    summary="Delete revenue transaction",
    description="Removes a revenue transaction from the database.",
)
async def delete_revenue(
    id: int,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_DELETE, Permission.REVENUE_DELETE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.delete_revenue_transaction(current_user, id)

