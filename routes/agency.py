"""
routes/agency.py — Agency Endpoints

Endpoints:
    GET  /api/agency/dashboard   — Agency dashboard summary
    GET  /api/agency/profile     — Read agency profile
    PUT  /api/agency/profile     — Update agency profile

Permission matrix applied:
    creator:view   — Agency ✅ (full)
    creator:update — Agency Own (managed creators only)
    analytics:view — Agency ✅ (full)
    campaign:*     — Agency ✅ (full)
"""

from fastapi import APIRouter, Depends, HTTPException, status

from authorization import (
    require_any_permission,
    require_permission,
    get_access_level,
    verify_ownership,
)
from permissions import Permission
from schemas import UserInDB
from schemas.agency import AgencyProfileRequest, AgencyProfileResponse
from services.agency_service import get_agency_profile, update_agency_profile

router = APIRouter(prefix="/api/agency", tags=["Agency"])


# ---------------------------------------------------------------------------
# GET /api/agency/dashboard
# Permissions: analytics:view
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    summary="Agency dashboard",
    description=(
        "Returns Agency-specific dashboard data. "
        "Requires 'analytics:view' permission."
    ),
)
async def agency_dashboard(
    current_user: UserInDB = Depends(require_permission(Permission.ANALYTICS_VIEW)),
):
    """
    Agency dashboard — accessible by roles with analytics:view permission
    (Admin, Agency, Marketing).

    Authorization flow (handled by require_permission()):
      1. Bearer token extracted from Authorization header.
      2. JWT verified — raises 401 if missing, expired, or invalid.
      3. Permission checked — raises 403 if role lacks 'analytics:view'.
    """
    return {
        "message": f"Welcome to the Agency Dashboard, {current_user.full_name}!",
        "role":    current_user.role.value,
        "user_id": current_user.id,
        "email":   current_user.email,
        # TODO (Database Teammate): Replace with real agency analytics from DB.
        "data": {
            "managed_campaigns": 0,
            "active_clients":    0,
            "pending_approvals": 0,
        },
    }


# ---------------------------------------------------------------------------
# GET /api/agency/profile
# Permissions: creator:view (full) or creator:view:own
# Agency has full creator:view, so they can view any profile.
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=AgencyProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get agency profile",
    description=(
        "Returns the full agency profile. "
        "Admin and Agency have full access. "
    ),
    responses={
        200: {"description": "Agency profile returned successfully."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient permission."},
        404: {"description": "Agency profile not found (profile not yet completed)."},
    },
)
async def get_agency_profile_endpoint(
    current_user: UserInDB = Depends(
        require_any_permission(Permission.CREATOR_VIEW, Permission.CREATOR_VIEW_OWN)
    ),
) -> AgencyProfileResponse:
    """
    Retrieve the agency user's profile.

    Access levels:
      - "full"  (Admin, Agency, Marketing): Can view any profile.
      - "own"   (Creator): Can only view their own.
    """
    profile = await get_agency_profile(current_user.id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Agency profile not found. "
                "The profile may not have been set up yet."
            ),
        )

    return profile


# ---------------------------------------------------------------------------
# PUT /api/agency/profile
# Permissions: creator:update (full) or creator:update:own
# ---------------------------------------------------------------------------

@router.put(
    "/profile",
    response_model=AgencyProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update agency profile",
    description=(
        "Update the agency user's profile. "
        "Admin has full access. Agency can update only their own profile."
    ),
    responses={
        200: {"description": "Profile updated successfully."},
        400: {"description": "Validation error — check field formats."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient permission — creator:update required."},
    },
)
async def update_agency_profile_endpoint(
    data: AgencyProfileRequest,
    current_user: UserInDB = Depends(
        require_any_permission(Permission.CREATOR_UPDATE, Permission.CREATOR_UPDATE_OWN)
    ),
) -> AgencyProfileResponse:
    """
    Update the agency's own profile.

    Access levels:
      - "full"  (Admin): Can update any agency's profile.
      - "own"   (Agency): Can only update their own profile.
    """
    # Determine access level and enforce ownership if needed
    level = get_access_level(
        current_user, Permission.CREATOR_UPDATE, Permission.CREATOR_UPDATE_OWN
    )
    if level == "own":
        verify_ownership(current_user.id, current_user.id, "agency profile")

    updated_profile = await update_agency_profile(current_user.id, data)

    if updated_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agency account not found. Cannot update profile.",
        )

    return updated_profile

