"""
authorization.py - Role-Based Access Control (RBAC)

This module is the single authority for all authorization logic.

Responsibilities:
  ┌─────────────────────────────────────────────────────────────┐
  │  get_current_user()         Authentication layer            │
  │    └─ verify_token()          Validates JWT, raises 401     │
  │    └─ get_user_by_email()     Loads user from DB/mock       │
  ├─────────────────────────────────────────────────────────────┤
  │  get_current_active_user()  Active-account guard            │
  ├─────────────────────────────────────────────────────────────┤
  │  require_roles([...])       Generic role gate, raises 403   │
  │    └─ require_creator()       Shorthand for Creator role    │
  │    └─ require_agency()        Shorthand for Agency role     │
  │    └─ require_marketing_team()                              │
  │    └─ require_admin()         Shorthand for Admin role      │
  └─────────────────────────────────────────────────────────────┘

Why a dedicated authorization.py (separate from dependencies.py)?
  - dependencies.py becomes a thin backward-compat re-export shim.
  - authorization.py contains all the business logic — one place to audit.
  - Easy to unit-test without importing the whole app.
"""

from typing import Callable, List, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from roles import UserRole
from schemas import UserInDB
from security import verify_token
from services.user_service import get_user_by_email
from permissions import Permission, ROLE_PERMISSIONS, has_permission, has_full_or_own_permission

# ---------------------------------------------------------------------------
# OAuth2 Bearer Token Scheme
# ---------------------------------------------------------------------------

# FastAPI uses this to:
#   1. Extract the token from the "Authorization: Bearer <token>" header.
#   2. Display a lock icon and "Authorize" button in /docs (Swagger UI).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ---------------------------------------------------------------------------
# Authentication — get_current_user
# ---------------------------------------------------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Core authentication dependency.

    Decodes the JWT Bearer token and returns the authenticated user.

    JWT claims extracted:
        "sub"     → email   — used to look up the user in the database
        "user_id" → int     — integer primary key (informational)
        "role"    → str     — RBAC role string (e.g. "creator")

    Error responses (automatic, via verify_token):
        401 — Token missing          (no Authorization header)
        401 — Token expired          (exp claim in the past)
        401 — Token invalid          (bad signature / malformed)
        401 — Missing sub claim      (token doesn't carry an email)
        401 — User not found         (email in token no longer in DB)
        403 — Account inactive       (is_active = False)

    Usage in a route:
        @router.get("/protected")
        async def protected(user: UserInDB = Depends(get_current_user)):
            return {"email": user.email}
    """
    # Step 1: Decode & verify the JWT.
    # verify_token() raises HTTP 401 automatically for expired/invalid tokens,
    # so there is no need for a manual None check here.
    payload = verify_token(token)

    # Step 2: Extract JWT claims.
    email:   str = payload.get("sub")       # Standard JWT "subject" claim
    user_id: int = payload.get("user_id")   # App-specific claim
    role:    str = payload.get("role")      # App-specific claim (e.g. "creator")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing the subject (email) claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 3: Confirm the user still exists in the database.
    # The JWT may be valid but the account could have been deleted.
    # TODO (Database Teammate): get_user_by_email will run a SQLAlchemy query here.
    user = await get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token was not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 4: Reject requests from deactivated accounts.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """
    Convenience wrapper that re-asserts the account is active.

    Use this instead of `get_current_user` in routes where you want an
    explicit, self-documenting active-account guard.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )
    return current_user


# ---------------------------------------------------------------------------
# Authorization — require_roles (generic factory)
# ---------------------------------------------------------------------------

def require_roles(allowed_roles: List[UserRole]) -> Callable:
    """
    Role authorization factory.

    Returns a FastAPI dependency that:
      1. Authenticates the request via get_current_active_user().
      2. Checks whether the user's role is in `allowed_roles`.
      3. Returns UserInDB on success.
      4. Raises HTTP 403 on failure (role not permitted).

    Args:
        allowed_roles: List of UserRole members that may access the endpoint.

    Returns:
        An async callable suitable for use with FastAPI's Depends().

    Examples:
        # Single role
        Depends(require_roles([UserRole.ADMINISTRATOR]))

        # Multiple roles
        Depends(require_roles([UserRole.AGENCY, UserRole.ADMINISTRATOR]))

        # Via shorthand helpers (preferred)
        Depends(require_admin())
        Depends(require_creator())
    """
    async def _role_checker(
        current_user: UserInDB = Depends(get_current_active_user),
    ) -> UserInDB:
        """
        Inner dependency — runs on every request to a protected endpoint.

        Raises:
            HTTPException 403: If current_user.role is not in allowed_roles.
        """
        if current_user.role not in allowed_roles:
            allowed_values = [r.value for r in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error":    "Permission denied.",
                    "required": allowed_values,
                    "yours":    current_user.role.value,
                    "hint":     f"This endpoint requires one of: {allowed_values}",
                },
            )
        return current_user

    # Preserve a human-readable name for FastAPI's dependency graph
    role_names = [r.value for r in allowed_roles]
    _role_checker.__name__ = f"require_roles({role_names})"

    return _role_checker


# ---------------------------------------------------------------------------
# Authorization — Role-Specific Shorthand Dependencies
# ---------------------------------------------------------------------------
# Each function below returns a dependency that permits exactly one role.
# They all delegate to require_roles() — zero duplicated logic.
# ---------------------------------------------------------------------------

def require_creator() -> Callable:
    """
    Dependency: permits only the Creator role.

    Raises HTTP 403 for Agency, Marketing Team, and Administrator users.

    Usage:
        @router.get("/creator/dashboard")
        async def dashboard(user: UserInDB = Depends(require_creator())):
            ...
    """
    return require_roles([UserRole.CREATOR])


def require_agency() -> Callable:
    """
    Dependency: permits only the Agency role.

    Raises HTTP 403 for all other roles.

    Usage:
        @router.get("/agency/dashboard")
        async def dashboard(user: UserInDB = Depends(require_agency())):
            ...
    """
    return require_roles([UserRole.AGENCY])


def require_marketing_team() -> Callable:
    """
    Dependency: permits only the Marketing Team role.

    Raises HTTP 403 for all other roles.

    Usage:
        @router.get("/marketing/dashboard")
        async def dashboard(user: UserInDB = Depends(require_marketing_team())):
            ...
    """
    return require_roles([UserRole.MARKETING])


def require_admin() -> Callable:
    """
    Dependency: permits only the Administrator role.

    Raises HTTP 403 for Creator, Agency, and Marketing Team users.

    Usage:
        @router.get("/admin/dashboard")
        async def dashboard(user: UserInDB = Depends(require_admin())):
            ...
    """
    return require_roles([UserRole.ADMINISTRATOR])


# ---------------------------------------------------------------------------
# Authorization — Granular Permission Dependencies
# ---------------------------------------------------------------------------
# These replace the role-only checks with fine-grained permission checks.
# The old require_<role>() functions above are kept for backward compat.
# ---------------------------------------------------------------------------

def require_permission(required_permission: Permission) -> Callable:
    """
    Permission-based authorization factory.

    Returns a FastAPI dependency that:
      1. Authenticates the request via get_current_active_user().
      2. Checks whether the user's role has `required_permission` in
         the ROLE_PERMISSIONS mapping from permissions.py.
      3. Returns UserInDB on success.
      4. Raises HTTP 403 on failure.

    For ":own" permissions, this dependency only confirms the role has
    the permission — the route handler must still verify resource ownership.

    Args:
        required_permission: The Permission enum member to check.

    Returns:
        An async callable suitable for use with FastAPI's Depends().

    Examples:
        # Admin-only endpoint
        Depends(require_permission(Permission.USER_VIEW))

        # Creator can create content
        Depends(require_permission(Permission.CONTENT_CREATE))
    """
    async def _permission_checker(
        current_user: UserInDB = Depends(get_current_active_user),
    ) -> UserInDB:
        if not has_permission(current_user.role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error":      "Permission denied.",
                    "required":   required_permission.value,
                    "your_role":  current_user.role.value,
                    "hint":       f"Your role '{current_user.role.value}' does not have the '{required_permission.value}' permission.",
                },
            )
        return current_user

    _permission_checker.__name__ = f"require_permission({required_permission.value})"
    return _permission_checker


def require_any_permission(*permissions: Permission) -> Callable:
    """
    Permit the request if the user's role has ANY of the listed permissions.

    Useful when a single endpoint accepts both full-access and own-only roles.
    For example, an endpoint that Admin can use on any resource and Creator
    can use on their own resource:

        Depends(require_any_permission(
            Permission.CONTENT_UPDATE,       # full access
            Permission.CONTENT_UPDATE_OWN,   # own-only access
        ))

    The route handler should then call `get_access_level()` to determine
    whether the caller has full or own-only access.
    """
    async def _any_permission_checker(
        current_user: UserInDB = Depends(get_current_active_user),
    ) -> UserInDB:
        role_perms = ROLE_PERMISSIONS.get(current_user.role, frozenset())
        if not any(p in role_perms for p in permissions):
            perm_values = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error":      "Permission denied.",
                    "required":   perm_values,
                    "your_role":  current_user.role.value,
                    "hint":       f"Your role '{current_user.role.value}' does not have any of: {perm_values}",
                },
            )
        return current_user

    perm_names = [p.value for p in permissions]
    _any_permission_checker.__name__ = f"require_any_permission({perm_names})"
    return _any_permission_checker


def get_access_level(
    user: UserInDB,
    full_perm: Permission,
    own_perm: Permission,
) -> str:
    """
    Determine whether the user has 'full', 'own', or 'none' access.

    Call this inside a route handler AFTER require_any_permission() has
    already confirmed the user has at least one of the two permissions.

    Args:
        user: The authenticated user (from Depends).
        full_perm: Permission granting unrestricted access.
        own_perm: Permission granting own-resource-only access.

    Returns:
        "full"  — user can act on any resource
        "own"   — user can act only on their own resources
        "none"  — user has no access (should not happen after require_any_permission)

    Example:
        level = get_access_level(current_user, Permission.CONTENT_UPDATE, Permission.CONTENT_UPDATE_OWN)
        if level == "own" and resource.owner_id != current_user.id:
            raise HTTPException(403, "You can only update your own content.")
    """
    return has_full_or_own_permission(user.role, full_perm, own_perm)


def verify_ownership(
    resource_owner_id: Union[int, str],
    current_user_id: Union[int, str],
    resource_name: str = "resource",
) -> None:
    """
    Assert that a resource belongs to the current user.

    Raises HTTP 403 if the IDs don't match.

    Args:
        resource_owner_id: The owner ID stored on the resource.
        current_user_id: The authenticated user's ID.
        resource_name: Human-readable name for the error message.

    Usage:
        verify_ownership(content.creator_id, current_user.id, "content")
    """
    if str(resource_owner_id) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Ownership required.",
                "hint":  f"You can only modify your own {resource_name}.",
            },
        )
