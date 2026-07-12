"""
routes/profile.py - Shared Profile Endpoint

Accessible by ALL authenticated roles:
  GET /api/profile

Demonstrates require_roles() used with every role simultaneously —
effectively any authenticated, active user is permitted.
"""

from fastapi import APIRouter, Depends

from authorization import require_roles
from roles import UserRole
from schemas import UserInDB, UserPublicResponse

router = APIRouter(prefix="/api", tags=["Profile"])

# Every supported role is included — any authenticated user may access this.
_ALL_ROLES = list(UserRole)


@router.get(
    "/profile",
    response_model=UserPublicResponse,
    summary="Get user profile",
    description=(
        "Returns the authenticated user's public profile. "
        "Accessible by all roles: creator, agency, marketing_team, administrator."
    ),
)
async def get_profile(
    current_user: UserInDB = Depends(require_roles(_ALL_ROLES)),
):
    """
    Shared profile endpoint — open to every role.

    Uses require_roles([...all roles...]) to permit any authenticated user.
    To restrict to a subset of roles in your own endpoints, pass a smaller list:

        Depends(require_roles([UserRole.CREATOR, UserRole.AGENCY]))
    """
    return UserPublicResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
    )
