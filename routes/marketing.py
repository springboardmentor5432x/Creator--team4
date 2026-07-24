"""
routes/marketing.py - Marketing Team Endpoints

Endpoints:
  GET /api/marketing/dashboard — requires campaign:create permission

Permission matrix applied:
    campaign:create — Admin ✅, Agency ✅, Marketing ✅
    campaign:update — Admin ✅, Agency ✅, Marketing ✅
    analytics:view  — Admin ✅, Agency ✅, Marketing ✅
"""

from fastapi import APIRouter, Depends

from authorization import require_permission
from permissions import Permission
from schemas import UserInDB

router = APIRouter(prefix="/api/marketing", tags=["Marketing Team"])


@router.get(
    "/dashboard",
    summary="Marketing Team dashboard",
    description=(
        "Returns Marketing Team dashboard data. "
        "Requires the 'campaign:create' permission."
    ),
)
async def marketing_dashboard(
    current_user: UserInDB = Depends(require_permission(Permission.CAMPAIGN_CREATE)),
):
    """
    Marketing Team dashboard — accessible by roles with campaign:create
    permission (Admin, Agency, Marketing).

    Authorization flow (handled by require_permission()):
      1. Bearer token extracted from Authorization header.
      2. JWT verified — raises 401 if missing, expired, or invalid.
      3. Permission checked — raises 403 if role lacks 'campaign:create'.
    """
    return {
        "message": f"Welcome to the Marketing Dashboard, {current_user.full_name}!",
        "role":    current_user.role.value,
        "user_id": current_user.id,
        "email":   current_user.email,
        # TODO (Database Teammate): Replace with real marketing data from DB.
        "data": {
            "active_campaigns":  0,
            "scheduled_posts":   0,
            "analytics_summary": {},
        },
    }

