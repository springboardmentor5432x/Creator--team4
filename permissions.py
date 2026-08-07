"""
permissions.py — Granular Permission Definitions & Role-Permission Mapping

Single source of truth for all fine-grained permissions in the application.

Design:
  - Permission is a str Enum  — same pattern as UserRole in roles.py.
    This gives IDE autocompletion, typo prevention at import time,
    and clean JSON serialisation.
  - ROLE_PERMISSIONS maps each UserRole to the set of Permission values
    that role is allowed to exercise.
  - Permissions ending with `:own` indicate that the role has access
    ONLY to resources it owns. Route handlers / dependencies must
    enforce the ownership check separately.

Permission Matrix:
    | Permission      | Admin | Agency | Creator | Marketing |
    | --------------- | :---: | :----: | :-----: | :-------: |
    | user:view       |   ✅   |   ❌   |   ❌    |    ❌     |
    | user:create     |   ✅   |   ❌   |   ❌    |    ❌     |
    | creator:view    |   ✅   |   ✅   |  Own    |    ✅     |
    | creator:update  |   ✅   |  Own   |  Own    |    ❌     |
    | content:create  |   ✅   |   ✅   |   ✅    |    ❌     |
    | content:update  |   ✅   |   ✅   |  Own    |    ❌     |
    | content:delete  |   ✅   |   ✅   |  Own    |    ❌     |
    | analytics:view  |   ✅   |   ✅   |  Own    |    ✅     |
    | campaign:create |   ✅   |   ✅   |   ❌    |    ✅     |
    | campaign:update |   ✅   |   ✅   |   ❌    |    ✅     |
    | campaign:delete |   ✅   |   ✅   |   ❌    |    ❌     |

Usage:
    from permissions import Permission, ROLE_PERMISSIONS, has_permission

    # Check if a role has a specific permission
    has_permission(UserRole.CREATOR, Permission.CONTENT_CREATE)  # → True
    has_permission(UserRole.MARKETING, Permission.CONTENT_CREATE)  # → False

    # Check if a role has ownership-only access
    has_own_permission(UserRole.CREATOR, Permission.CONTENT_UPDATE)  # → True
"""

from enum import Enum
from typing import Dict, FrozenSet

from roles import UserRole


# ---------------------------------------------------------------------------
# Permission Enum
# ---------------------------------------------------------------------------

class Permission(str, Enum):
    """
    Fine-grained permission strings.

    Naming convention:  <resource>:<action>
    Ownership variants: <resource>:<action>:own

    Inheriting from `str` means:
      - JSON-serialisable as a plain string.
      - Direct string comparisons work.
      - FastAPI/Pydantic serialise it to its string value automatically.
    """

    # --- User management (admin only) ---
    USER_VIEW           = "user:view"
    USER_CREATE         = "user:create"

    # --- Creator profiles ---
    CREATOR_VIEW        = "creator:view"
    CREATOR_VIEW_OWN    = "creator:view:own"
    CREATOR_UPDATE      = "creator:update"
    CREATOR_UPDATE_OWN  = "creator:update:own"

    # --- Content ---
    CONTENT_CREATE      = "content:create"
    CONTENT_UPDATE      = "content:update"
    CONTENT_UPDATE_OWN  = "content:update:own"
    CONTENT_DELETE      = "content:delete"
    CONTENT_DELETE_OWN  = "content:delete:own"

    # --- Analytics ---
    ANALYTICS_VIEW      = "analytics:view"
    ANALYTICS_VIEW_OWN  = "analytics:view:own"

    # --- Growth Analytics ---
    GROWTH_VIEW         = "growth:view"
    GROWTH_VIEW_OWN     = "growth:view:own"

    # --- Campaigns ---
    CAMPAIGN_CREATE     = "campaign:create"
    CAMPAIGN_UPDATE     = "campaign:update"
    CAMPAIGN_DELETE     = "campaign:delete"

    # --- Revenue Analytics ---
    REVENUE_VIEW        = "revenue:view"
    REVENUE_VIEW_OWN    = "revenue:view:own"
    REVENUE_CREATE      = "revenue:create"
    REVENUE_CREATE_OWN  = "revenue:create:own"
    REVENUE_UPDATE      = "revenue:update"
    REVENUE_UPDATE_OWN  = "revenue:update:own"
    REVENUE_DELETE      = "revenue:delete"
    REVENUE_DELETE_OWN  = "revenue:delete:own"


# ---------------------------------------------------------------------------
# Role → Permissions Mapping
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: Dict[UserRole, FrozenSet[Permission]] = {

    # Administrator — full access to everything
    UserRole.ADMINISTRATOR: frozenset({
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.CREATOR_VIEW,
        Permission.CREATOR_UPDATE,
        Permission.CONTENT_CREATE,
        Permission.CONTENT_UPDATE,
        Permission.CONTENT_DELETE,
        Permission.ANALYTICS_VIEW,
        Permission.GROWTH_VIEW,
        Permission.CAMPAIGN_CREATE,
        Permission.CAMPAIGN_UPDATE,
        Permission.CAMPAIGN_DELETE,
        Permission.REVENUE_VIEW,
        Permission.REVENUE_CREATE,
        Permission.REVENUE_UPDATE,
        Permission.REVENUE_DELETE,
    }),

    # Agency — broad content/campaign access, owns creator updates
    UserRole.AGENCY: frozenset({
        Permission.CREATOR_VIEW,
        Permission.CREATOR_UPDATE_OWN,   # can update only managed creators
        Permission.CONTENT_CREATE,
        Permission.CONTENT_UPDATE,
        Permission.CONTENT_DELETE,
        Permission.ANALYTICS_VIEW,
        Permission.GROWTH_VIEW,
        Permission.CAMPAIGN_CREATE,
        Permission.CAMPAIGN_UPDATE,
        Permission.CAMPAIGN_DELETE,
        Permission.REVENUE_VIEW,
        Permission.REVENUE_CREATE,
        Permission.REVENUE_UPDATE,
        Permission.REVENUE_DELETE,
    }),

    # Creator — own resources only, plus content creation
    UserRole.CREATOR: frozenset({
        Permission.CREATOR_VIEW_OWN,
        Permission.CREATOR_UPDATE_OWN,
        Permission.CONTENT_CREATE,
        Permission.CONTENT_UPDATE_OWN,
        Permission.CONTENT_DELETE_OWN,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.GROWTH_VIEW_OWN,
        Permission.REVENUE_VIEW_OWN,
        Permission.REVENUE_CREATE_OWN,
        Permission.REVENUE_UPDATE_OWN,
        Permission.REVENUE_DELETE_OWN,
    }),

    # Marketing Team — read analytics, manage campaigns, view creators
    UserRole.MARKETING: frozenset({
        Permission.CREATOR_VIEW,
        Permission.ANALYTICS_VIEW,
        Permission.GROWTH_VIEW,
        Permission.CAMPAIGN_CREATE,
        Permission.CAMPAIGN_UPDATE,
        Permission.REVENUE_VIEW,
    }),
}


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def has_permission(role: UserRole, permission: Permission) -> bool:
    """
    Check if a role has the exact permission granted.

    Args:
        role: The user's role.
        permission: The permission to check.

    Returns:
        True if the role has this permission, False otherwise.
    """
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def has_full_or_own_permission(role: UserRole, full_perm: Permission, own_perm: Permission) -> str:
    """
    Determine the access level a role has for a given resource action.

    Args:
        role: The user's role.
        full_perm: The full-access permission (e.g., Permission.CONTENT_UPDATE).
        own_perm: The own-only permission (e.g., Permission.CONTENT_UPDATE_OWN).

    Returns:
        "full"  — role has unrestricted access
        "own"   — role can access only its own resources
        "none"  — role has no access
    """
    role_perms = ROLE_PERMISSIONS.get(role, frozenset())
    if full_perm in role_perms:
        return "full"
    if own_perm in role_perms:
        return "own"
    return "none"
