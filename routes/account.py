"""
routes/account.py — Account Settings & Lifecycle Endpoints

Available to ALL authenticated users regardless of role
(Creator, Agency, Marketing Team, Administrator).

The authenticated user can only manage their OWN account — user_id is
always sourced from the verified JWT, never from a request parameter.

Endpoints:
    GET   /api/account/settings         — Read mutable account fields
    PATCH /api/account/settings         — Update email / username / phone / picture
    PATCH /api/account/change-password  — Verify old password, set new password
    PATCH /api/account/deactivate       — Set is_active = False
    PATCH /api/account/reactivate       — Set is_active = True
    PATCH /api/account/delete           — Soft delete: is_deleted = True

Authorization:
    All endpoints use get_current_active_user() from authorization.py.
    This dependency:
        1. Extracts and verifies the JWT Bearer token (raises 401 on failure).
        2. Loads the user from the database (raises 401 if not found).
        3. Confirms is_active = True (raises 403 if deactivated).

HTTP Status Codes:
    200 — Success
    400 — Bad request (e.g. wrong current password)
    401 — Token missing / expired / invalid
    403 — Account inactive
    404 — User not found
    409 — Duplicate email or username
"""

from fastapi import APIRouter, Depends, HTTPException, status

from authorization import get_current_active_user
from schemas import UserInDB
from schemas.account import (
    AccountSettingsResponse,
    AccountSettingsUpdateRequest,
    AccountStatusResponse,
    ChangePasswordRequest,
)
from services.account_service import (
    change_password,
    deactivate_account,
    delete_account,
    get_account_settings,
    reactivate_account,
    update_account_settings,
)

router = APIRouter(prefix="/api/account", tags=["Account"])


# ---------------------------------------------------------------------------
# GET /api/account/settings
# Roles: All authenticated users
# ---------------------------------------------------------------------------

@router.get(
    "/settings",
    response_model=AccountSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get account settings",
    description=(
        "Returns the mutable account fields for the currently authenticated user: "
        "email, username, phone, profile picture, and account status flags."
    ),
    responses={
        200: {"description": "Account settings returned successfully."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Account is inactive."},
        404: {"description": "User account not found."},
    },
)
async def get_settings(
    current_user: UserInDB = Depends(get_current_active_user),
) -> AccountSettingsResponse:
    """
    Return the authenticated user's account settings.

    No role restriction — any authenticated user may call this.
    The user_id is sourced from the verified JWT.

    Service call:
        get_account_settings(user_id) → AccountSettingsResponse | None

    Error responses:
        401 — Token missing / expired / invalid
        403 — Account inactive
        404 — User record not found in the database
    """
    settings = await get_account_settings(current_user.id)

    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account settings not found for this user.",
        )

    return settings


# ---------------------------------------------------------------------------
# PATCH /api/account/settings
# Roles: All authenticated users
# ---------------------------------------------------------------------------

@router.patch(
    "/settings",
    response_model=AccountSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update account settings",
    description=(
        "Update one or more of the following account fields: "
        "email, username, phone, profile_picture. "
        "All fields are optional — send only what you want to change. "
        "Returns 409 if the new email or username is already taken."
    ),
    responses={
        200: {"description": "Account settings updated successfully."},
        400: {"description": "Validation error — check field formats."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Account is inactive."},
        404: {"description": "User account not found."},
        409: {"description": "Email or username is already registered to another account."},
    },
)
async def patch_settings(
    data: AccountSettingsUpdateRequest,
    current_user: UserInDB = Depends(get_current_active_user),
) -> AccountSettingsResponse:
    """
    Update the authenticated user's mutable account fields.

    Partial update semantics — only non-null fields in the request body
    are written to the database. Fields omitted from the body are unchanged.

    Validation (enforced by Pydantic before reaching this handler):
        - email:           RFC 5322 compliant (EmailStr)
        - username:        3–50 chars, alphanumeric + underscore, no leading/trailing underscore
        - phone:           7–20 chars, digits/spaces/hyphens/parens
        - profile_picture: Must begin with http:// or https://

    Service call:
        update_account_settings(user_id, data) → AccountSettingsResponse | None

    Error responses:
        400  — Pydantic validation failure
        401  — Token missing / expired / invalid
        403  — Account inactive
        404  — User not found
        409  — Email or username already taken
    """
    updated = await update_account_settings(current_user.id, data)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found. Cannot update settings.",
        )

    return updated


# ---------------------------------------------------------------------------
# PATCH /api/account/change-password
# Roles: All authenticated users
# ---------------------------------------------------------------------------

@router.patch(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description=(
        "Change the authenticated user's password. "
        "Requires the correct current password for verification before saving the new one. "
        "New password must be at least 8 characters and contain one letter and one digit."
    ),
    responses={
        200: {"description": "Password changed successfully."},
        400: {"description": "Current password is incorrect, or new password fails strength rules."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Account is inactive."},
    },
)
async def change_password_endpoint(
    data: ChangePasswordRequest,
    current_user: UserInDB = Depends(get_current_active_user),
) -> dict:
    """
    Change the authenticated user's password.

    Flow:
        1. Pydantic validates the request body (new_password strength).
        2. The service verifies `current_password` against the stored bcrypt hash.
        3. On success, the new password is hashed and stored.

    Service call:
        change_password(user_id, current_password, new_password) → bool

    Request body example:
        {
            "current_password": "OldPass@123",
            "new_password":     "NewSecure@456"
        }

    Error responses:
        400 — current_password is wrong
        400 — new_password fails strength validation (handled by Pydantic at the schema level)
        401 — Token missing / expired / invalid
        403 — Account inactive
    """
    await change_password(
        user_id=current_user.id,
        current_password=data.current_password,
        new_password=data.new_password,
    )

    return {"message": "Password changed successfully."}


# ---------------------------------------------------------------------------
# PATCH /api/account/deactivate
# Roles: All authenticated users (own account only)
# ---------------------------------------------------------------------------

@router.patch(
    "/deactivate",
    response_model=AccountStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate account",
    description=(
        "Deactivate the authenticated user's account. "
        "Sets users.is_active = False. "
        "The account data is preserved and can be reactivated later. "
        "After deactivation the current JWT becomes invalid on the next request."
    ),
    responses={
        200: {"description": "Account deactivated successfully."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Account is already inactive."},
        404: {"description": "User account not found."},
    },
)
async def deactivate_account_endpoint(
    current_user: UserInDB = Depends(get_current_active_user),
) -> AccountStatusResponse:
    """
    Deactivate the authenticated user's own account.

    Sets users.is_active = False.
    The account is NOT deleted — all data is preserved.
    A deactivated account can be reactivated via PATCH /api/account/reactivate.

    After this call succeeds, the Authorization middleware will block all
    further requests from this user (is_active = False → HTTP 403).

    Service call:
        deactivate_account(user_id) → {is_active, is_deleted}

    Error responses:
        401 — Token missing / expired / invalid
        403 — Account already inactive (caught by get_current_active_user)
        404 — User not found
    """
    result = await deactivate_account(current_user.id)

    return AccountStatusResponse(
        message="Account has been deactivated successfully.",
        user_id=current_user.id,
        is_active=result["is_active"],
        is_deleted=result["is_deleted"],
    )


# ---------------------------------------------------------------------------
# PATCH /api/account/reactivate
# Roles: All authenticated users
# Note: A deactivated user cannot call this with their own token because
#       get_current_active_user() will raise 403. This endpoint is useful
#       when called via an Administrator flow or a separate reactivation token.
# ---------------------------------------------------------------------------

@router.patch(
    "/reactivate",
    response_model=AccountStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Reactivate account",
    description=(
        "Reactivate a previously deactivated account. "
        "Sets users.is_active = True. "
        "Note: A deactivated user cannot authenticate with a regular JWT — "
        "reactivation is typically performed by an Administrator."
    ),
    responses={
        200: {"description": "Account reactivated successfully."},
        400: {"description": "Cannot reactivate a deleted account."},
        401: {"description": "Missing or invalid JWT token."},
        404: {"description": "User account not found."},
    },
)
async def reactivate_account_endpoint(
    current_user: UserInDB = Depends(get_current_active_user),
) -> AccountStatusResponse:
    """
    Reactivate the authenticated user's account.

    Sets users.is_active = True.
    Restores the ability to log in.

    Cannot reactivate a soft-deleted account (is_deleted = True).

    Service call:
        reactivate_account(user_id) → {is_active, is_deleted}

    Error responses:
        400 — Account is soft-deleted and cannot be reactivated
        401 — Token missing / expired / invalid
        404 — User not found
    """
    result = await reactivate_account(current_user.id)

    return AccountStatusResponse(
        message="Account has been reactivated successfully.",
        user_id=current_user.id,
        is_active=result["is_active"],
        is_deleted=result["is_deleted"],
    )


# ---------------------------------------------------------------------------
# PATCH /api/account/delete
# Roles: All authenticated users (own account only)
# ---------------------------------------------------------------------------

@router.patch(
    "/delete",
    response_model=AccountStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete account",
    description=(
        "Soft-delete the authenticated user's account. "
        "Sets users.is_deleted = True AND users.is_active = False. "
        "The account record is PRESERVED in the database (no hard DELETE). "
        "A soft-deleted account cannot log in and does not appear in public listings. "
        "Permanent deletion can be performed by an Administrator."
    ),
    responses={
        200: {"description": "Account soft-deleted successfully."},
        401: {"description": "Missing or invalid JWT token."},
        403: {"description": "Account is inactive."},
        404: {"description": "User account not found."},
    },
)
async def delete_account_endpoint(
    current_user: UserInDB = Depends(get_current_active_user),
) -> AccountStatusResponse:
    """
    Soft-delete the authenticated user's own account.

    Sets:
        users.is_deleted = True
        users.is_active  = False

    The database row is NOT removed. This allows:
        - Audit trail preservation.
        - Administrator-level recovery if needed.
        - Grace period before a scheduled hard delete.

    Service call:
        delete_account(user_id) → {is_active, is_deleted}

    Error responses:
        401 — Token missing / expired / invalid
        403 — Account inactive (already deactivated first)
        404 — User not found
    """
    result = await delete_account(current_user.id)

    return AccountStatusResponse(
        message=(
            "Account has been scheduled for deletion. "
            "Your data will be permanently removed after the retention period."
        ),
        user_id=current_user.id,
        is_active=result["is_active"],
        is_deleted=result["is_deleted"],
    )
