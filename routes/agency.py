"""
routes/agency.py — Agency-Only Endpoints

All routes require the authenticated user to hold the `agency` role,
EXCEPT where the Administrator override is also allowed (GET /profile).

Endpoints:
    GET  /api/agency/dashboard   — Agency dashboard summary (existing)
    GET  /api/agency/profile     — Read agency profile     (Agency | Admin)
    PUT  /api/agency/profile     — Update agency profile   (Agency only)

Authorization dependency chain (handled automatically):
    require_agency()             → JWT verified → role == "agency"
    require_agency_or_admin()    → JWT verified → role in ["agency", "administrator"]
"""

from fastapi import APIRouter, Depends, HTTPException, status

from authorization import require_agency, require_roles
from roles import UserRole
from schemas import UserInDB
from schemas.agency import AgencyProfileRequest, AgencyProfileResponse
from services.agency_service import get_agency_profile, update_agency_profile

router = APIRouter(prefix="/api/agency", tags=["Agency"])


# ---------------------------------------------------------------------------
# Dependency: Agency OR Administrator
# (used for GET /profile so admins can inspect any agency's profile)
# ---------------------------------------------------------------------------

def require_agency_or_admin():
    """
    Returns a dependency that passes for Agency or Administrator roles.

    Administrators can READ any profile for oversight/support purposes,
    but cannot WRITE to an agency's profile (PUT uses require_agency() only).
    """
    return require_roles([UserRole.AGENCY, UserRole.ADMINISTRATOR])


# ---------------------------------------------------------------------------
# GET /api/agency/dashboard
# Roles: Agency only
# (Preserved from original implementation — no changes)
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    summary="Agency dashboard",
    description="Returns Agency-specific dashboard data. Accessible by the Agency role only.",
)
async def agency_dashboard(current_user: UserInDB = Depends(require_agency())):
    """
    Agency-only protected route.

    Authorization flow (handled entirely by require_agency()):
      1. Bearer token extracted from Authorization header.
      2. JWT verified — raises 401 if missing, expired, or invalid.
      3. User loaded from database — raises 401 if not found.
      4. Role checked — raises 403 if role != "agency".
      5. Handler executes with the authenticated UserInDB.
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
# Roles: Agency (own profile) | Administrator (any agency's profile)
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=AgencyProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get agency profile",
    description=(
        "Returns the full agency profile for the authenticated agency user. "
        "Administrator users can also call this endpoint to inspect any agency's profile."
    ),
    responses={
        200: {"description": "Agency profile returned successfully."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient role — Agency or Administrator required."},
        404: {"description": "Agency profile not found (profile not yet completed)."},
    },
)
async def get_agency_profile_endpoint(
    current_user: UserInDB = Depends(require_agency_or_admin()),
) -> AgencyProfileResponse:
    """
    Retrieve the authenticated agency user's profile.

    The user_id is taken from the verified JWT — no query param needed.
    The Administrator sees the same response shape as an Agency user.

    Service call:
        get_agency_profile(user_id) → AgencyProfileResponse | None

    Error responses:
        401 — Token missing / expired / invalid
        403 — Role is not agency or administrator
        404 — No agency_profiles row found for this user_id
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
# Roles: Agency only (no admin write access)
# ---------------------------------------------------------------------------

@router.put(
    "/profile",
    response_model=AgencyProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update agency profile",
    description=(
        "Update the authenticated agency user's profile. "
        "All fields are optional — send only the fields you wish to change. "
        "Only users with the Agency role can call this endpoint."
    ),
    responses={
        200: {"description": "Profile updated successfully."},
        400: {"description": "Validation error — check field formats."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Insufficient role — Agency required."},
    },
)
async def update_agency_profile_endpoint(
    data: AgencyProfileRequest,
    current_user: UserInDB = Depends(require_agency()),
) -> AgencyProfileResponse:
    """
    Update the agency's own profile.

    The user_id is taken from the verified JWT — agency users can only update
    their own profile; they cannot supply a different user_id.

    Validation:
        - phone:   Regex — 7-20 chars, digits/spaces/hyphens/parens
        - website: Must begin with http:// or https://
        - logo:    Must begin with http:// or https://

    Service call:
        update_agency_profile(user_id, data) → AgencyProfileResponse | None

    On success:
        Returns the full updated profile as AgencyProfileResponse (HTTP 200).

    Error responses:
        400 — Pydantic validation failure (invalid phone, URL, etc.)
        401 — Token missing / expired / invalid
        403 — Role is not agency
    """
    updated_profile = await update_agency_profile(current_user.id, data)

    if updated_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agency account not found. Cannot update profile.",
        )

    return updated_profile
