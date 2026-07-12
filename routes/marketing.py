"""
routes/marketing.py - Marketing Team-Only Endpoints

All routes require the authenticated user to hold the `marketing_team` role.
Authorization is enforced via the require_marketing_team() dependency from authorization.py.

Protected Endpoints:
  GET /api/marketing/dashboard
"""

from fastapi import APIRouter, Depends

from authorization import require_marketing_team
from schemas import UserInDB

router = APIRouter(prefix="/api/marketing", tags=["Marketing Team"])


@router.get(
    "/dashboard",
    summary="Marketing Team dashboard",
    description="Returns Marketing Team dashboard data. Accessible by the Marketing Team role only.",
)
async def marketing_dashboard(current_user: UserInDB = Depends(require_marketing_team())):
    """
    Marketing Team-only protected route.

    Authorization flow (handled entirely by require_marketing_team()):
      1. Bearer token extracted from Authorization header.
      2. JWT verified — raises 401 if missing, expired, or invalid.
      3. User loaded from database — raises 401 if not found.
      4. Role checked — raises 403 if role != "marketing_team".
      5. Handler executes with the authenticated UserInDB.
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
