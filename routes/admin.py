"""
routes/admin.py - Administrator-Only Endpoints

All routes require the authenticated user to hold the `administrator` role.
Authorization is enforced via the require_admin() dependency from authorization.py.

Protected Endpoints:
  GET /api/admin/dashboard
"""

from fastapi import APIRouter, Depends

from authorization import require_admin
from schemas import UserInDB

router = APIRouter(prefix="/api/admin", tags=["Administrator"])


@router.get(
    "/dashboard",
    summary="Administrator dashboard",
    description="Returns Admin dashboard data. Accessible by the Administrator role only.",
)
async def admin_dashboard(current_user: UserInDB = Depends(require_admin())):
    """
    Administrator-only protected route.

    Authorization flow (handled entirely by require_admin()):
      1. Bearer token extracted from Authorization header.
      2. JWT verified — raises 401 if missing, expired, or invalid.
      3. User loaded from database — raises 401 if not found.
      4. Role checked — raises 403 if role != "administrator".
      5. Handler executes with the authenticated UserInDB.
    """
    return {
        "message": f"Welcome to the Admin Dashboard, {current_user.full_name}!",
        "role":    current_user.role.value,
        "user_id": current_user.id,
        "email":   current_user.email,
        # TODO (Database Teammate): Replace with real admin data from DB.
        "data": {
            "total_users":      0,
            "active_users":     0,
            "system_health":    "ok",
            "recent_audit_logs": [],
        },
    }
