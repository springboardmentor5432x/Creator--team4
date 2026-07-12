"""
dependencies.py - Backward-Compatible Re-Export Shim

All authorization logic has been moved to authorization.py.
This file re-exports everything so that existing imports from
`dependencies.py` continue to work without any changes.

New code should import directly from authorization.py:
    from authorization import get_current_user, require_roles, require_admin

Existing imports like these still work unchanged:
    from dependencies import get_current_user
    from dependencies import require_creator
    from dependencies import require_roles
"""

# Re-export everything from authorization.py.
# The "noqa: F401" suppresses "imported but unused" linter warnings
# since these are intentional re-exports.
from authorization import (           # noqa: F401
    oauth2_scheme,
    get_current_user,
    get_current_active_user,
    require_roles,
    require_creator,
    require_agency,
    require_marketing_team,
    require_admin,
)

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
