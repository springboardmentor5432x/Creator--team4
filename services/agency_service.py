"""
services/agency_service.py — Agency Profile Service Layer (Placeholder)

This module is the single integration point between the Agency Profile
API routes and the PostgreSQL database.

IMPORTANT (Database Teammate):
    Replace each placeholder body with real SQLAlchemy async queries.
    Every function signature and return type MUST remain unchanged so
    that the route layer above needs zero modifications.

    Recommended imports when wiring up:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.future import select
        from models import AgencyProfileModel   # your ORM model

    Inject the async session via FastAPI's Depends():
        async def get_agency_profile(user_id: int, db: AsyncSession = Depends(get_db)):
            ...

Public API surface:
    get_agency_profile(user_id)          → AgencyProfileResponse | None
    update_agency_profile(user_id, data) → AgencyProfileResponse | None
"""

from datetime import datetime, timezone
from typing import Optional

from schemas.agency import AgencyProfileRequest, AgencyProfileResponse


# ---------------------------------------------------------------------------
# In-Memory Mock Store  (development / testing only)
# TODO (Database Teammate): Delete this block once SQLAlchemy is connected.
# ---------------------------------------------------------------------------

# Keyed by user_id (int). Each value mirrors what the DB would return.
_MOCK_AGENCY_PROFILES: dict[int, dict] = {}


# ===========================================================================
# Agency Profile — Service Methods
# ===========================================================================

async def get_agency_profile(user_id: int) -> Optional[AgencyProfileResponse]:
    """
    Retrieve the agency profile for the given user.

    Args:
        user_id: The authenticated agency user's users.id (integer PK).

    Returns:
        An AgencyProfileResponse populated from agency_profiles row,
        or None if no profile row exists yet for this user.

    Raises:
        Does NOT raise HTTP exceptions — the route layer handles 404.

    ─── DB Equivalent ────────────────────────────────────────────────────
        SELECT
            ap.user_id,
            ap.agency_name,
            ap.company_description,
            ap.website,
            ap.phone,
            ap.address,
            ap.city,
            ap.country,
            ap.logo,
            ap.contact_person,
            ap.created_at
        FROM agency_profiles ap
        WHERE ap.user_id = :user_id;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        result = await db.execute(
            select(AgencyProfileModel)
            .where(AgencyProfileModel.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return AgencyProfileResponse(
            user_id=row.user_id,
            agency_name=row.agency_name,
            company_description=row.company_description,
            website=row.website,
            phone=row.phone,
            address=row.address,
            city=row.city,
            country=row.country,
            logo=row.logo,
            contact_person=row.contact_person,
            created_at=row.created_at,
        )
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock implementation ────────────────────────────────────────────
    row = _MOCK_AGENCY_PROFILES.get(user_id)
    if row is None:
        return None
    return AgencyProfileResponse(**row)


async def update_agency_profile(
    user_id: int,
    data: AgencyProfileRequest,
) -> Optional[AgencyProfileResponse]:
    """
    Update the agency profile for the given user.

    Only fields explicitly provided in `data` (i.e. not None) are written.
    If the profile row does not yet exist, this method creates it (upsert).

    Args:
        user_id: The authenticated agency user's users.id.
        data:    Validated AgencyProfileRequest from the route layer.

    Returns:
        The updated (or newly created) AgencyProfileResponse,
        or None if the user record does not exist.

    Raises:
        Does NOT raise HTTP exceptions — the route layer handles errors.

    ─── DB Equivalent ────────────────────────────────────────────────────
        INSERT INTO agency_profiles
            (user_id, agency_name, company_description, website, phone,
             address, city, country, logo, contact_person)
        VALUES
            (:user_id, :agency_name, :company_description, :website, :phone,
             :address, :city, :country, :logo, :contact_person)
        ON CONFLICT (user_id) DO UPDATE
        SET
            agency_name         = COALESCE(EXCLUDED.agency_name,         agency_profiles.agency_name),
            company_description = COALESCE(EXCLUDED.company_description, agency_profiles.company_description),
            website             = COALESCE(EXCLUDED.website,             agency_profiles.website),
            phone               = COALESCE(EXCLUDED.phone,               agency_profiles.phone),
            address             = COALESCE(EXCLUDED.address,             agency_profiles.address),
            city                = COALESCE(EXCLUDED.city,                agency_profiles.city),
            country             = COALESCE(EXCLUDED.country,             agency_profiles.country),
            logo                = COALESCE(EXCLUDED.logo,                agency_profiles.logo),
            contact_person      = COALESCE(EXCLUDED.contact_person,      agency_profiles.contact_person)
        RETURNING *;

    ─── TODO (Database Teammate) ─────────────────────────────────────────
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await db.execute(
            select(AgencyProfileModel).where(AgencyProfileModel.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            profile = AgencyProfileModel(user_id=user_id, **payload)
            db.add(profile)
        else:
            for field, val in payload.items():
                setattr(profile, field, val)
        await db.commit()
        await db.refresh(profile)
        return AgencyProfileResponse.model_validate(profile)
    ──────────────────────────────────────────────────────────────────────
    """
    # ── Mock: upsert ──────────────────────────────────────────────────
    existing = _MOCK_AGENCY_PROFILES.get(user_id, {"user_id": user_id})
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    merged = {**existing, **updates}

    # Stamp creation time if this is a new profile
    if "created_at" not in merged:
        merged["created_at"] = datetime.now(timezone.utc)

    _MOCK_AGENCY_PROFILES[user_id] = merged
    return AgencyProfileResponse(**merged)
