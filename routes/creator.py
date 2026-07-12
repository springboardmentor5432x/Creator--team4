"""
routes/creator.py — Creator-Only Endpoints

All routes require the authenticated user to hold the `creator` role,
EXCEPT where the Administrator override is also allowed (GET /profile).

Endpoints:
    GET  /api/creator/dashboard   — Creator dashboard summary (existing)
    GET  /api/creator/profile     — Read creator profile     (Creator | Admin)
    PUT  /api/creator/profile     — Update creator profile   (Creator only)

Authorization dependency chain (handled automatically):
    require_creator()       → JWT verified → role == "creator"
    require_creator_or_admin() → JWT verified → role in ["creator", "administrator"]
"""

from fastapi import APIRouter, Depends, HTTPException, status

from authorization import require_creator, require_roles
from roles import UserRole
from schemas import UserInDB
from schemas.creator import CreatorProfileRequest, CreatorProfileResponse
from services.creator_service import get_creator_profile, update_creator_profile

router = APIRouter(prefix="/api/creator", tags=["Creator"])


# ---------------------------------------------------------------------------
# Dependency: Creator OR Administrator
# (used for GET /profile so admins can inspect any creator's profile)
# ---------------------------------------------------------------------------

def require_creator_or_admin():
    """
    Returns a dependency that passes for Creator or Administrator roles.

    Administrators can READ any profile for oversight/support purposes,
    but cannot WRITE to a creator's profile (PUT uses require_creator() only).
    """
    return require_roles([UserRole.CREATOR, UserRole.ADMINISTRATOR])


# ---------------------------------------------------------------------------
# GET /api/creator/dashboard
# Roles: Creator only
# (Preserved from original implementation — no changes)
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    summary="Creator dashboard",
    description="Returns Creator-specific dashboard data. Accessible by the Creator role only.",
)
async def creator_dashboard(current_user: UserInDB = Depends(require_creator())):
    """
    Creator-only protected route.

    Authorization flow (handled entirely by require_creator()):
      1. Bearer token extracted from Authorization header.
      2. JWT verified — raises 401 if missing, expired, or invalid.
      3. User loaded from database — raises 401 if not found.
      4. Role checked — raises 403 if role != "creator".
      5. Handler executes with the authenticated UserInDB.
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
# Roles: Creator (own profile) | Administrator (any creator's profile)
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=CreatorProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get creator profile",
    description=(
        "Returns the full creator profile for the authenticated creator. "
        "Administrator users can also call this endpoint to inspect any creator's profile."
    ),
    responses={
        200: {"description": "Creator profile returned successfully."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient role — Creator or Administrator required."},
        404: {"description": "Creator profile not found (profile not yet completed)."},
    },
)
async def get_creator_profile_endpoint(
    current_user: UserInDB = Depends(require_creator_or_admin()),
) -> CreatorProfileResponse:
    """
    Retrieve the authenticated creator's profile.

    The user_id is taken from the verified JWT — no query param needed.
    The Administrator sees the same response shape as a Creator.

    Service call:
        get_creator_profile(user_id) → CreatorProfileResponse | None

    Error responses:
        401 — Token missing / expired / invalid
        403 — Role is not creator or administrator
        404 — No creator_profiles row found for this user_id
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
# Roles: Creator only (no admin write access)
# ---------------------------------------------------------------------------

@router.put(
    "/profile",
    response_model=CreatorProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update creator profile",
    description=(
        "Update the authenticated creator's profile. "
        "All fields are optional — send only the fields you wish to change. "
        "Only users with the Creator role can call this endpoint."
    ),
    responses={
        200: {"description": "Profile updated successfully."},
        400: {"description": "Validation error — check field formats."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient role — Creator required."},
        409: {"description": "Username is already taken by another creator."},
    },
)
async def update_creator_profile_endpoint(
    data: CreatorProfileRequest,
    current_user: UserInDB = Depends(require_creator()),
) -> CreatorProfileResponse:
    """
    Update the creator's own profile.

    The user_id is taken from the verified JWT — creators can only update
    their own profile; they cannot supply a different user_id.

    Validation:
        - phone:     Regex — 7-20 chars, digits/spaces/hyphens/parens
        - username:  Alphanumeric + underscores, 3–50 chars
        - URLs:      Must begin with http:// or https://

    Service call:
        update_creator_profile(user_id, data) → CreatorProfileResponse | None

    On success:
        Returns the full updated profile as CreatorProfileResponse (HTTP 200).

    Error responses:
        400 — Pydantic validation failure (invalid phone, URL, etc.)
        401 — Token missing / expired / invalid
        403 — Role is not creator
        409 — Username already taken
    """
    updated_profile = await update_creator_profile(current_user.id, data)

    if updated_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator account not found. Cannot update profile.",
        )

    return updated_profile
