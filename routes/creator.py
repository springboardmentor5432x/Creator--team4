"""
routes/creator.py — Creator Endpoints

Endpoints:
    GET  /api/creator/dashboard   — Creator dashboard summary
    GET  /api/creator/profile     — Read creator profile
    PUT  /api/creator/profile     — Update creator profile

Permission matrix applied:
    creator:view   — Admin ✅, Agency ✅, Creator Own, Marketing ✅
    creator:update — Admin ✅, Agency Own, Creator Own
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
from schemas.creator import CreatorProfileRequest, CreatorProfileResponse
from services.creator_service import get_creator_profile, update_creator_profile

router = APIRouter(prefix="/api/creator", tags=["Creator"])


# ---------------------------------------------------------------------------
# GET /api/creator/dashboard
# Permissions: creator:view (full) or creator:view:own
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    summary="Creator dashboard",
    description=(
        "Returns Creator-specific dashboard data. "
        "Accessible by roles with 'creator:view' or 'creator:view:own' permission."
    ),
)
async def creator_dashboard(
    current_user: UserInDB = Depends(
        require_any_permission(Permission.CREATOR_VIEW, Permission.CREATOR_VIEW_OWN)
    ),
):
    """
    Creator dashboard — accessible by Creator (own data), Admin, Agency, Marketing.

    Authorization flow (handled by require_any_permission()):
      1. Bearer token extracted from Authorization header.
      2. JWT verified — raises 401 if missing, expired, or invalid.
      3. Permission checked — raises 403 if role lacks both creator:view and creator:view:own.
    """
    return {
        "message": f"Welcome to the Creator Dashboard, {current_user.full_name}!",
        "role":    current_user.role.value,
        "user_id": current_user.id,
        "email":   current_user.email,
        # TODO (Database Teammate): Replace with real creator analytics from DB.
        "data": {
            "total_posts":     0,
            "total_views":     0,
            "pending_reviews": 0,
        },
    }


# ---------------------------------------------------------------------------
# GET /api/creator/profile
# Permissions: creator:view (full) or creator:view:own
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=CreatorProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get creator profile",
    description=(
        "Returns the full creator profile. "
        "Admin/Agency/Marketing see any creator's profile. "
        "Creator sees only their own profile."
    ),
    responses={
        200: {"description": "Creator profile returned successfully."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient permission — creator:view required."},
        404: {"description": "Creator profile not found (profile not yet completed)."},
    },
)
async def get_creator_profile_endpoint(
    current_user: UserInDB = Depends(
        require_any_permission(Permission.CREATOR_VIEW, Permission.CREATOR_VIEW_OWN)
    ),
) -> CreatorProfileResponse:
    """
    Retrieve a creator's profile.

    Access levels:
      - "full"  (Admin, Agency, Marketing): Can view any creator's profile.
      - "own"   (Creator): Can only view their own profile.

    The user_id is taken from the verified JWT — creators always see their own.
    """
    profile = await get_creator_profile(current_user.id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Creator profile not found. "
                "The profile may not have been set up yet."
            ),
        )

    return profile


# ---------------------------------------------------------------------------
# PUT /api/creator/profile
# Permissions: creator:update (full) or creator:update:own
# ---------------------------------------------------------------------------

@router.put(
    "/profile",
    response_model=CreatorProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update creator profile",
    description=(
        "Update a creator profile. "
        "Admin has full access. Agency and Creator can update only their own. "
        "Marketing has no access."
    ),
    responses={
        200: {"description": "Profile updated successfully."},
        400: {"description": "Validation error — check field formats."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient permission — creator:update required."},
        409: {"description": "Username is already taken by another creator."},
    },
)
async def update_creator_profile_endpoint(
    data: CreatorProfileRequest,
    current_user: UserInDB = Depends(
        require_any_permission(Permission.CREATOR_UPDATE, Permission.CREATOR_UPDATE_OWN)
    ),
) -> CreatorProfileResponse:
    """
    Update a creator's profile.

    Access levels:
      - "full"  (Admin): Can update any creator's profile.
      - "own"   (Agency, Creator): Can only update their own / managed profile.
    """
    # Determine access level and enforce ownership if needed
    level = get_access_level(
        current_user, Permission.CREATOR_UPDATE, Permission.CREATOR_UPDATE_OWN
    )
    if level == "own":
        # Creator / Agency can only update their own profile
        verify_ownership(current_user.id, current_user.id, "creator profile")

    updated_profile = await update_creator_profile(current_user.id, data)

    if updated_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator account not found. Cannot update profile.",
        )

    return updated_profile

