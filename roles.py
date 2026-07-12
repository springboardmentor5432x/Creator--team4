"""
roles.py - RBAC Role Definitions

Single source of truth for all user roles in the application.

Importing from this module (rather than schemas.py) keeps role logic
decoupled from Pydantic models and makes it easy to add new roles
without touching request/response schemas.

Usage:
    from roles import UserRole

    # Enum member access
    UserRole.CREATOR          # → <UserRole.CREATOR: 'creator'>
    UserRole.CREATOR.value    # → 'creator'

    # String comparison works because UserRole inherits from str
    UserRole.CREATOR == "creator"   # → True

    # Iterate all roles
    list(UserRole)  # → [CREATOR, AGENCY, MARKETING, ADMINISTRATOR]

JWT role claim convention:
    The JWT payload stores the role as its string value:
        { "role": "creator" }
    This matches UserRole.CREATOR.value, so decoding is trivial:
        UserRole(payload["role"])   # → UserRole.CREATOR
"""

from enum import Enum


class UserRole(str, Enum):
    """
    Supported RBAC roles.

    Inheriting from `str` means:
      - The enum is JSON-serialisable as a plain string.
      - Direct string comparisons work (no .value needed in most contexts).
      - FastAPI/Pydantic serialise it to its string value automatically.

    Role hierarchy (informational, not enforced here):
        Administrator > Agency ≈ Marketing Team > Creator
    """

    CREATOR       = "creator"
    AGENCY        = "agency"
    MARKETING     = "marketing_team"
    ADMINISTRATOR = "administrator"

    @classmethod
    def values(cls) -> list[str]:
        """Return a list of all valid role string values."""
        return [r.value for r in cls]

    @classmethod
    def from_str(cls, value: str) -> "UserRole":
        """
        Convert a raw string (e.g. from a JWT claim) back to a UserRole member.

        Raises:
            ValueError: If `value` does not match any known role.

        Example:
            UserRole.from_str("creator")  # → UserRole.CREATOR
        """
        try:
            return cls(value)
        except ValueError:
            raise ValueError(
                f"'{value}' is not a valid role. "
                f"Allowed values: {cls.values()}"
            )
