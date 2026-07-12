"""
schemas/__init__.py — Schema Package Re-Exports

This package-level __init__.py does two jobs:

  1. Re-exports every symbol from the ORIGINAL schemas.py (the flat module
     that existed before this package was created) so that all existing
     application imports — e.g.
         from schemas import UserInDB
         from schemas import CreatorProfile
     — continue to work without any changes.

  2. Re-exports the NEW feature-specific schema models added for the
     Creator / Agency / Account profile endpoints.

How the old schemas.py is accessed:
    Because the `schemas/` directory now takes priority over `schemas.py`,
    we import the original flat module by temporarily adjusting sys.path
    so it is loaded as `_schemas_legacy`.

IMPORTANT (Teammates):
    Do NOT import from `schemas.py` directly in new code — always import
    from the sub-modules (schemas.creator, schemas.agency, schemas.account)
    or from this package root.
"""

import importlib.util
import os
import sys

# ---------------------------------------------------------------------------
# Step 1: Load the original flat schemas.py as a side-module
# so we can re-export its symbols here.
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)  # backend/
_SCHEMAS_PY = os.path.join(_PARENT, "schemas.py")

_spec = importlib.util.spec_from_file_location("_schemas_legacy", _SCHEMAS_PY)
_legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_legacy)
sys.modules["_schemas_legacy"] = _legacy

# Re-export every public symbol from the original schemas.py
from _schemas_legacy import (  # noqa: F401, E402
    UserRole,
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserPublicResponse,
    RegisterSuccessResponse,
    UserInDB,
    CreatorProfile,
    CreatorProfileUpdate,
    AgencyProfile,
    AgencyProfileUpdate,
    AccountSettings,
    AccountSettingsUpdate,
    SocialAccount,
    SocialAccountCreate,
    AgencyCreatorLink,
    AgencyCreatorAssign,
)

# ---------------------------------------------------------------------------
# Step 2: Re-export the NEW feature-specific schema models
# ---------------------------------------------------------------------------

from schemas.creator import (       # noqa: F401
    CreatorProfileRequest,
    CreatorProfileResponse,
)

from schemas.agency import (        # noqa: F401
    AgencyProfileRequest,
    AgencyProfileResponse,
)

from schemas.account import (       # noqa: F401
    AccountSettingsResponse,
    AccountSettingsUpdateRequest,
    ChangePasswordRequest,
    AccountStatusResponse,
)
