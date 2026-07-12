"""
services/creator_service.py — Creator Profile Service Layer (Placeholder)

This module is the single integration point between the Creator Profile
API routes and the PostgreSQL database.

IMPORTANT (Database Teammate):
    Replace each placeholder body with real SQLAlchemy async queries.
    Every function signature and return type MUST remain unchanged so
    that the route layer above needs zero modifications.

    Recommended imports when wiring up:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.future import select
        from models import CreatorProfileModel   # your ORM model

    Inject the async session via FastAPI's Depends():
        async def get_creator_profile(user_id: int, db: AsyncSession = Depends(get_db)):
            ...

Public API surface:
    get_creator_profile(user_id)          → CreatorProfileResponse | None
    update_creator_profile(user_id, data) → CreatorProfileResponse | None
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from schemas.creator import CreatorProfileRequest, CreatorProfileResponse


# ---------------------------------------------------------------------------
# In-Memory Mock Store  (development / testing only)
# TODO (Database Teammate): Delete this block once SQLAlchemy is connected.
# ---------------------------------------------------------------------------

# Keyed by user_id (int). Each value mirrors what the DB would return.
_MOCK_CREATOR_PROFILES: dict[int, dict] = {}


# ===========================================================================
# Creator Profile — Service Methods
# ===========================================================================

async def get_creator_profile(user_id: int) -> Optional[CreatorProfileResponse]:
    """
    Retrieve the creator profile for the given user.

    Args:
        user_id: The authenticated creator's users.id (integer PK).

    Returns:
        A CreatorProfileResponse populated from creator_profiles row,
        or None if no profile row exists yet for this user.

    Raises:
        Does NOT raise HTTP exceptions — the route layer handles 404.

    ─── DB Equivalent ────────────────────────────────────────────────────
        SELECT
            cp.user_id,
            u.full_name,
            cp.username,
            cp.bio,
            cp.phone,
            cp.country,
            cp.city,
            cp.profile_image,
            cp.youtube_channel,
            cp.instagram_username,
            cp.linkedin_profile,
            cp.website,
            cp.created_at
        FROM creator_profiles cp
        JOIN users u ON cp.user_id = u.id
        WHERE cp.user_id = :user_id;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        result = await db.execute(
            select(CreatorProfileModel, UserModel.full_name)
            .join(UserModel, CreatorProfileModel.user_id == UserModel.id)
            .where(CreatorProfileModel.user_id == user_id)
        )
        row = result.first()
        if row is None:
            return None
        profile, full_name = row
        return CreatorProfileResponse(
            user_id=profile.user_id,
            full_name=full_name,
            username=profile.username,
            bio=profile.bio,
            phone=profile.phone,
            country=profile.country,
            city=profile.city,
            profile_image=profile.profile_image,
            youtube_channel=profile.youtube_channel,
            instagram_username=profile.instagram_username,
            linkedin_profile=profile.linkedin_profile,
            website=profile.website,
            created_at=profile.created_at,
        )
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock implementation ────────────────────────────────────────────
    row = _MOCK_CREATOR_PROFILES.get(user_id)
    if row is None:
        return None
    return CreatorProfileResponse(**row)


async def update_creator_profile(
    user_id: int,
    data: CreatorProfileRequest,
) -> Optional[CreatorProfileResponse]:
    """
    Update the creator profile for the given user.

    Only fields explicitly provided in `data` (i.e. not None) are written.
    If the profile row does not yet exist, this method creates it (upsert).

    Args:
        user_id: The authenticated creator's users.id.
        data:    Validated CreatorProfileRequest from the route layer.

    Returns:
        The updated (or newly created) CreatorProfileResponse,
        or None if the user does not exist (route layer maps this to 404).

    Raises:
        HTTPException 409: If `data.username` is already taken by another user.
        Does NOT raise 404 — the route layer handles that.

    ─── DB Equivalent ────────────────────────────────────────────────────
        -- Check username uniqueness (if provided)
        SELECT user_id FROM creator_profiles
        WHERE username = :username AND user_id != :user_id;

        -- Upsert
        INSERT INTO creator_profiles (user_id, username, bio, ...)
        VALUES (:user_id, :username, :bio, ...)
        ON CONFLICT (user_id) DO UPDATE
        SET
            username          = COALESCE(EXCLUDED.username,          creator_profiles.username),
            bio               = COALESCE(EXCLUDED.bio,               creator_profiles.bio),
            phone             = COALESCE(EXCLUDED.phone,             creator_profiles.phone),
            country           = COALESCE(EXCLUDED.country,           creator_profiles.country),
            city              = COALESCE(EXCLUDED.city,              creator_profiles.city),
            profile_image     = COALESCE(EXCLUDED.profile_image,     creator_profiles.profile_image),
            youtube_channel   = COALESCE(EXCLUDED.youtube_channel,   creator_profiles.youtube_channel),
            instagram_username= COALESCE(EXCLUDED.instagram_username,creator_profiles.instagram_username),
            linkedin_profile  = COALESCE(EXCLUDED.linkedin_profile,  creator_profiles.linkedin_profile),
            website           = COALESCE(EXCLUDED.website,           creator_profiles.website),
            full_name         = COALESCE(EXCLUDED.full_name,         creator_profiles.full_name)
        RETURNING *;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        # 1. Check username uniqueness
        if data.username:
            conflict = await db.execute(
                select(CreatorProfileModel.user_id)
                .where(
                    CreatorProfileModel.username == data.username,
                    CreatorProfileModel.user_id != user_id,
                )
            )
            if conflict.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username is already taken.",
                )

        # 2. Upsert
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await db.execute(
            select(CreatorProfileModel).where(CreatorProfileModel.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            profile = CreatorProfileModel(user_id=user_id, **payload)
            db.add(profile)
        else:
            for field, val in payload.items():
                setattr(profile, field, val)
        await db.commit()
        await db.refresh(profile)
        return CreatorProfileResponse.model_validate(profile)
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock: check username uniqueness ───────────────────────────────
    if data.username:
        for uid, row in _MOCK_CREATOR_PROFILES.items():
            if row.get("username") == data.username and uid != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username is already taken by another creator.",
                )

    # ── Mock: upsert ──────────────────────────────────────────────────
    existing = _MOCK_CREATOR_PROFILES.get(user_id, {"user_id": user_id})
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    merged = {**existing, **updates}

    # Stamp creation time if this is a new profile
    if "created_at" not in merged:
        merged["created_at"] = datetime.now(timezone.utc)

    _MOCK_CREATOR_PROFILES[user_id] = merged
    return CreatorProfileResponse(**merged)
