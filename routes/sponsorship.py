"""
routes/sponsorship.py — Sponsorship Management Endpoints

Endpoints:
    POST   /api/sponsorship       → Create sponsorship campaign
    GET    /api/sponsorship       → List creator sponsorships
    PUT    /api/sponsorship/{id}  → Update sponsorship campaign
    DELETE /api/sponsorship/{id}  → Delete sponsorship campaign
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, require_any_permission
from permissions import Permission
from models import UserModel
from schemas.revenue import (
    SponsorshipCreate,
    SponsorshipUpdate,
    SponsorshipResponse,
)
from services.revenue_service import RevenueService

router = APIRouter(prefix="/api/sponsorship", tags=["Sponsorship Tracking"])


def get_service(db: AsyncSession = Depends(get_db)) -> RevenueService:
    return RevenueService(db.sync_session if hasattr(db, "sync_session") else db)


@router.post(
    "",
    response_model=SponsorshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create sponsorship deal",
    description="Registers a brand sponsorship deal with company, campaign name, amount, start/end dates, and status.",
)
async def create_sponsorship(
    payload: SponsorshipCreate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_CREATE, Permission.REVENUE_CREATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.create_sponsorship(current_user, payload.model_dump())


@router.get(
    "",
    response_model=List[SponsorshipResponse],
    summary="List creator sponsorships",
    description="Fetches all sponsorship contracts recorded for a creator.",
)
async def get_sponsorships(
    creator_id: str = Query(..., description="Target creator profile ID"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_VIEW, Permission.REVENUE_VIEW_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.get_sponsorships(current_user, creator_id)


@router.put(
    "/{id}",
    response_model=SponsorshipResponse,
    summary="Update sponsorship deal",
    description="Updates sponsorship details or status.",
)
async def update_sponsorship(
    id: int,
    payload: SponsorshipUpdate,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_UPDATE, Permission.REVENUE_UPDATE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.update_sponsorship(current_user, id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{id}",
    response_model=Dict[str, Any],
    summary="Delete sponsorship deal",
    description="Removes a sponsorship record.",
)
async def delete_sponsorship(
    id: int,
    current_user: UserModel = Depends(
        require_any_permission(Permission.REVENUE_DELETE, Permission.REVENUE_DELETE_OWN)
    ),
    service: RevenueService = Depends(get_service),
):
    return service.delete_sponsorship(current_user, id)

