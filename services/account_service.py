"""
services/account_service.py — Account Settings & Lifecycle Service Layer (Placeholder)

This module handles all account-level operations for any authenticated user
(Creator, Agency, Marketing Team, or Administrator):

    - get_account_settings()    — Read email, username, phone, profile_picture
    - update_account_settings() — Update those fields (with uniqueness checks)
    - change_password()         — Verify old password, hash and save new one
    - deactivate_account()      — Set users.is_active = False
    - reactivate_account()      — Set users.is_active = True
    - delete_account()          — Soft delete: set users.is_deleted = True

IMPORTANT (Database Teammate):
    Replace each placeholder body with real SQLAlchemy async queries.
    Every function signature and return type MUST remain unchanged so
    that the route layer above needs zero modifications.

    Recommended imports when wiring up:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.future import select
        from sqlalchemy import update as sql_update
        from models import UserModel             # your ORM model
        from security import verify_password, get_password_hash

    Inject the async session via FastAPI's Depends():
        async def change_password(user_id, ..., db: AsyncSession = Depends(get_db)):
            ...

Public API surface:
    get_account_settings(user_id)                               → AccountSettingsResponse | None
    update_account_settings(user_id, data)                      → AccountSettingsResponse | None
    change_password(user_id, current_password, new_password)    → bool
    deactivate_account(user_id)                                 → dict  {is_active, is_deleted}
    reactivate_account(user_id)                                 → dict  {is_active, is_deleted}
    delete_account(user_id)                                     → dict  {is_active, is_deleted}
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from schemas.account import AccountSettingsResponse, AccountSettingsUpdateRequest


# ---------------------------------------------------------------------------
# In-Memory Mock Store  (development / testing only)
# TODO (Database Teammate): Delete this block once SQLAlchemy is connected.
# ---------------------------------------------------------------------------

# Keyed by user_id. Each value is a dict mirroring a users table row.
# In production this data comes from the `users` table directly.
_MOCK_USER_ACCOUNTS: dict[int, dict] = {}

# Simulated password store for mock bcrypt verification.
# TODO (Database Teammate): Remove — use users.password_hash with bcrypt.
_MOCK_PASSWORDS: dict[int, str] = {}


def _ensure_mock_user(user_id: int) -> dict:
    """
    Lazily create a mock user row so the mock endpoints work even when
    the DB team has not yet seeded data.

    TODO (Database Teammate): Remove this function entirely.
    """
    if user_id not in _MOCK_USER_ACCOUNTS:
        _MOCK_USER_ACCOUNTS[user_id] = {
            "id": user_id,
            "email": f"user{user_id}@example.com",
            "username": f"user_{user_id}",
            "phone": None,
            "profile_picture": None,
            "is_active": True,
            "is_deleted": False,
            "updated_at": datetime.now(timezone.utc),
        }
        _MOCK_PASSWORDS[user_id] = "password1"   # default mock password
    return _MOCK_USER_ACCOUNTS[user_id]


# ===========================================================================
# Account Settings — Read
# ===========================================================================

async def get_account_settings(user_id: int) -> Optional[AccountSettingsResponse]:
    """
    Retrieve the mutable account settings for the authenticated user.

    Args:
        user_id: The authenticated user's users.id.

    Returns:
        AccountSettingsResponse populated from the users row,
        or None if the user_id does not exist in the database.

    ─── DB Equivalent ────────────────────────────────────────────────────
        SELECT
            id,
            email,
            username,
            phone,
            profile_picture,
            is_active,
            is_deleted,
            updated_at
        FROM users
        WHERE id = :user_id;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        result = await db.execute(
            select(
                UserModel.id,
                UserModel.email,
                UserModel.username,
                UserModel.phone,
                UserModel.profile_picture,
                UserModel.is_active,
                UserModel.is_deleted,
                UserModel.updated_at,
            ).where(UserModel.id == user_id)
        )
        row = result.mappings().first()
        if row is None:
            return None
        return AccountSettingsResponse(**row)
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock implementation ────────────────────────────────────────────
    row = _ensure_mock_user(user_id)
    return AccountSettingsResponse(**row)


# ===========================================================================
# Account Settings — Update
# ===========================================================================

async def update_account_settings(
    user_id: int,
    data: AccountSettingsUpdateRequest,
) -> Optional[AccountSettingsResponse]:
    """
    Update mutable account fields for the authenticated user.

    Only non-None fields in `data` are applied (partial update semantics).

    Args:
        user_id: The authenticated user's users.id.
        data:    Validated AccountSettingsUpdateRequest from the route layer.

    Returns:
        The updated AccountSettingsResponse,
        or None if user_id is not found.

    Raises:
        HTTPException 409: If `email` or `username` is already used by another user.

    ─── DB Equivalent ────────────────────────────────────────────────────
        -- Uniqueness check for email (if provided)
        SELECT id FROM users WHERE email = :email AND id != :user_id;

        -- Uniqueness check for username (if provided)
        SELECT id FROM users WHERE username = :username AND id != :user_id;

        -- Apply the update
        UPDATE users
        SET
            email           = COALESCE(:email,           email),
            username        = COALESCE(:username,        username),
            phone           = COALESCE(:phone,           phone),
            profile_picture = COALESCE(:profile_picture, profile_picture),
            updated_at      = NOW()
        WHERE id = :user_id
        RETURNING *;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        # 1. Email uniqueness
        if data.email:
            conflict = await db.execute(
                select(UserModel.id).where(
                    UserModel.email == data.email,
                    UserModel.id != user_id,
                )
            )
            if conflict.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Email is already registered.")

        # 2. Username uniqueness
        if data.username:
            conflict = await db.execute(
                select(UserModel.id).where(
                    UserModel.username == data.username,
                    UserModel.id != user_id,
                )
            )
            if conflict.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Username is already taken.")

        # 3. Apply update
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        payload["updated_at"] = datetime.now(timezone.utc)
        await db.execute(
            sql_update(UserModel).where(UserModel.id == user_id).values(**payload)
        )
        await db.commit()
        return await get_account_settings(user_id)
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock: uniqueness checks ────────────────────────────────────────
    if data.email:
        for uid, row in _MOCK_USER_ACCOUNTS.items():
            if row.get("email") == str(data.email) and uid != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email address is already registered to another account.",
                )

    if data.username:
        for uid, row in _MOCK_USER_ACCOUNTS.items():
            if row.get("username") == data.username and uid != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username is already taken by another account.",
                )

    # ── Mock: apply update ────────────────────────────────────────────
    row = _ensure_mock_user(user_id)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    row.update(updates)
    row["updated_at"] = datetime.now(timezone.utc)
    return AccountSettingsResponse(**row)


# ===========================================================================
# Change Password
# ===========================================================================

async def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
) -> bool:
    """
    Verify `current_password` against the stored hash, then update the hash.

    Args:
        user_id:          The authenticated user's users.id.
        current_password: Plaintext password submitted by the user.
        new_password:     Validated new plaintext password (min 8 chars, 1 letter, 1 digit).

    Returns:
        True on success.

    Raises:
        HTTPException 400: If `current_password` does not match the stored hash.
        HTTPException 404: If user_id is not found.

    ─── DB Equivalent ────────────────────────────────────────────────────
        -- 1. Fetch the stored hash
        SELECT id, password_hash FROM users WHERE id = :user_id;

        -- 2. Verify with bcrypt
        if not bcrypt.checkpw(current_password, stored_hash):
            raise 400

        -- 3. Hash the new password and save
        UPDATE users
        SET password_hash = :new_hash, updated_at = NOW()
        WHERE id = :user_id;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        # 1. Fetch user
        result = await db.execute(
            select(UserModel.id, UserModel.password_hash).where(UserModel.id == user_id)
        )
        row = result.first()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found.")

        # 2. Verify current password (uses bcrypt via security.py)
        if not verify_password(current_password, row.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        # 3. Hash and store new password
        new_hash = get_password_hash(new_password)
        await db.execute(
            sql_update(UserModel)
            .where(UserModel.id == user_id)
            .values(password_hash=new_hash, updated_at=datetime.now(timezone.utc))
        )
        await db.commit()
        return True
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock: verify current password ─────────────────────────────────
    stored = _MOCK_PASSWORDS.get(user_id)
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found.",
        )

    if stored != current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    # ── Mock: save new password ───────────────────────────────────────
    _MOCK_PASSWORDS[user_id] = new_password
    _ensure_mock_user(user_id)["updated_at"] = datetime.now(timezone.utc)
    return True


# ===========================================================================
# Account Lifecycle — Deactivate / Reactivate / Soft Delete
# ===========================================================================

async def deactivate_account(user_id: int) -> dict:
    """
    Set users.is_active = False for the given user.

    An inactive account cannot log in (blocked by get_current_active_user()
    in authorization.py). The account data is preserved and the account
    can be reactivated later.

    Returns:
        dict with keys: is_active (False), is_deleted (unchanged).

    ─── DB Equivalent ────────────────────────────────────────────────────
        UPDATE users
        SET is_active = FALSE, updated_at = NOW()
        WHERE id = :user_id
        RETURNING is_active, is_deleted;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        result = await db.execute(
            sql_update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=False, updated_at=datetime.now(timezone.utc))
            .returning(UserModel.is_active, UserModel.is_deleted)
        )
        row = result.first()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found.")
        await db.commit()
        return {"is_active": row.is_active, "is_deleted": row.is_deleted}
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock ───────────────────────────────────────────────────────────
    row = _ensure_mock_user(user_id)
    row["is_active"] = False
    row["updated_at"] = datetime.now(timezone.utc)
    return {"is_active": row["is_active"], "is_deleted": row["is_deleted"]}


async def reactivate_account(user_id: int) -> dict:
    """
    Set users.is_active = True for the given user.

    Restores login access for a previously deactivated account.

    Returns:
        dict with keys: is_active (True), is_deleted (unchanged).

    ─── DB Equivalent ────────────────────────────────────────────────────
        UPDATE users
        SET is_active = TRUE, updated_at = NOW()
        WHERE id = :user_id AND is_deleted = FALSE
        RETURNING is_active, is_deleted;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        result = await db.execute(
            sql_update(UserModel)
            .where(UserModel.id == user_id, UserModel.is_deleted == False)
            .values(is_active=True, updated_at=datetime.now(timezone.utc))
            .returning(UserModel.is_active, UserModel.is_deleted)
        )
        row = result.first()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or account is permanently deleted.",
            )
        await db.commit()
        return {"is_active": row.is_active, "is_deleted": row.is_deleted}
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock ───────────────────────────────────────────────────────────
    row = _ensure_mock_user(user_id)
    if row.get("is_deleted"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reactivate a deleted account.",
        )
    row["is_active"] = True
    row["updated_at"] = datetime.now(timezone.utc)
    return {"is_active": row["is_active"], "is_deleted": row["is_deleted"]}


async def delete_account(user_id: int) -> dict:
    """
    Soft-delete the account by setting users.is_deleted = True.

    The account record is PRESERVED in the database (no hard DELETE).
    A soft-deleted account:
        - Cannot log in.
        - Does not appear in public listings.
        - Can be hard-deleted later by an Administrator if required.

    Returns:
        dict with keys: is_active (False), is_deleted (True).

    ─── DB Equivalent ────────────────────────────────────────────────────
        UPDATE users
        SET
            is_active  = FALSE,
            is_deleted = TRUE,
            updated_at = NOW()
        WHERE id = :user_id
        RETURNING is_active, is_deleted;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        result = await db.execute(
            sql_update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                is_active=False,
                is_deleted=True,
                updated_at=datetime.now(timezone.utc),
            )
            .returning(UserModel.is_active, UserModel.is_deleted)
        )
        row = result.first()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found.")
        await db.commit()
        return {"is_active": row.is_active, "is_deleted": row.is_deleted}
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock ───────────────────────────────────────────────────────────
    row = _ensure_mock_user(user_id)
    row["is_active"] = False
    row["is_deleted"] = True
    row["updated_at"] = datetime.now(timezone.utc)
    return {"is_active": row["is_active"], "is_deleted": row["is_deleted"]}
