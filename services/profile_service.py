"""
services/profile_service.py - Profile & Settings Database Service Layer

Placeholder functions for the following tables:
  - creator_profiles
  - agency_profiles
  - account_settings
  - agency_creators
  - social_accounts

TODO (Database Teammate):
  Replace every mock body with actual SQLAlchemy async queries.
  Keep the same function signatures and return types.

  Recommended imports:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.future import select
    from models import (
        CreatorProfileModel, AgencyProfileModel,
        AccountSettingsModel, AgencyCreatorModel, SocialAccountModel
    )
"""

from datetime import datetime, timezone
from typing import Optional

from schemas import (
    AgencyCreatorLink,
    AgencyProfile,
    AccountSettings,
    CreatorProfile,
    SocialAccount,
)


# ---------------------------------------------------------------------------
# In-memory mock stores (development only)
# TODO (Database Teammate): Remove once SQLAlchemy is wired up.
# ---------------------------------------------------------------------------

_CREATOR_PROFILES:  dict[str, CreatorProfile]  = {}  # keyed by user_id
_AGENCY_PROFILES:   dict[str, AgencyProfile]   = {}  # keyed by user_id
_ACCOUNT_SETTINGS:  dict[str, AccountSettings] = {}  # keyed by user_id
_SOCIAL_ACCOUNTS:   dict[str, list[SocialAccount]] = {}  # keyed by creator_profile.id
_AGENCY_CREATORS:   list[AgencyCreatorLink]    = []


# ===========================================================================
# Creator Profile Service  (maps to: creator_profiles table)
# ===========================================================================

async def get_creator_profile(user_id: str) -> Optional[CreatorProfile]:
    """
    Retrieve a creator's profile by their users.id.

    DB equivalent:
        SELECT * FROM creator_profiles WHERE user_id = :user_id;

    TODO (Database Teammate):
        result = await db.execute(
            select(CreatorProfileModel).where(CreatorProfileModel.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        return CreatorProfile.model_validate(row) if row else None
    """
    # --- Mock ---
    return _CREATOR_PROFILES.get(user_id)


async def create_creator_profile(user_id: str, **fields) -> CreatorProfile:
    """
    Insert a row into creator_profiles for a newly registered Creator.

    DB equivalent:
        INSERT INTO creator_profiles (user_id, username, bio, ...)
        VALUES (:user_id, :username, :bio, ...)
        RETURNING *;

    Args:
        user_id: FK to users.id (UNIQUE — one profile per user).
        **fields: Optional profile fields (username, bio, social URLs).

    TODO (Database Teammate):
        new_profile = CreatorProfileModel(user_id=user_id, **fields)
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)
        return CreatorProfile.model_validate(new_profile)
    """
    # --- Mock ---
    profile_id = len(_CREATOR_PROFILES) + 1
    profile = CreatorProfile(id=str(profile_id), user_id=user_id, **fields)
    _CREATOR_PROFILES[user_id] = profile
    return profile


async def update_creator_profile(user_id: str, **fields) -> Optional[CreatorProfile]:
    """
    Update fields in an existing creator_profiles row.

    DB equivalent:
        UPDATE creator_profiles
        SET    username = :username, bio = :bio, ...
        WHERE  user_id = :user_id
        RETURNING *;

    TODO (Database Teammate):
        result = await db.execute(
            select(CreatorProfileModel).where(CreatorProfileModel.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(profile, key, value)
        await db.commit()
        await db.refresh(profile)
        return CreatorProfile.model_validate(profile)
    """
    # --- Mock ---
    profile = _CREATOR_PROFILES.get(user_id)
    if profile is None:
        return None
    updated = profile.model_copy(update={k: v for k, v in fields.items() if v is not None})
    _CREATOR_PROFILES[user_id] = updated
    return updated


# ===========================================================================
# Agency Profile Service  (maps to: agency_profiles table)
# ===========================================================================

async def get_agency_profile(user_id: str) -> Optional[AgencyProfile]:
    """
    Retrieve an agency's profile by their users.id.

    DB equivalent:
        SELECT * FROM agency_profiles WHERE user_id = :user_id;

    TODO (Database Teammate):
        result = await db.execute(
            select(AgencyProfileModel).where(AgencyProfileModel.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        return AgencyProfile.model_validate(row) if row else None
    """
    # --- Mock ---
    return _AGENCY_PROFILES.get(user_id)


async def create_agency_profile(user_id: str, **fields) -> AgencyProfile:
    """
    Insert a row into agency_profiles for a newly registered Agency.

    DB equivalent:
        INSERT INTO agency_profiles (user_id, agency_name, website, contact_number)
        VALUES (:user_id, :agency_name, :website, :contact_number)
        RETURNING *;

    TODO (Database Teammate):
        new_profile = AgencyProfileModel(user_id=user_id, **fields)
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)
        return AgencyProfile.model_validate(new_profile)
    """
    # --- Mock ---
    profile_id = len(_AGENCY_PROFILES) + 1
    profile = AgencyProfile(id=str(profile_id), user_id=user_id, **fields)
    _AGENCY_PROFILES[user_id] = profile
    return profile


async def update_agency_profile(user_id: str, **fields) -> Optional[AgencyProfile]:
    """
    Update fields in an existing agency_profiles row.

    DB equivalent:
        UPDATE agency_profiles
        SET    agency_name = :agency_name, ...
        WHERE  user_id = :user_id
        RETURNING *;

    TODO (Database Teammate): Similar pattern to update_creator_profile above.
    """
    # --- Mock ---
    profile = _AGENCY_PROFILES.get(user_id)
    if profile is None:
        return None
    updated = profile.model_copy(update={k: v for k, v in fields.items() if v is not None})
    _AGENCY_PROFILES[user_id] = updated
    return updated


# ===========================================================================
# Account Settings Service  (maps to: account_settings table)
# ===========================================================================

async def get_account_settings(user_id: str) -> Optional[AccountSettings]:
    """
    Retrieve account settings for a user.

    DB equivalent:
        SELECT * FROM account_settings WHERE user_id = :user_id;

    TODO (Database Teammate):
        result = await db.execute(
            select(AccountSettingsModel).where(AccountSettingsModel.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        return AccountSettings.model_validate(row) if row else None
    """
    # --- Mock ---
    return _ACCOUNT_SETTINGS.get(user_id)


async def create_account_settings(user_id: str) -> AccountSettings:
    """
    Insert a default account_settings row for a new user.
    Called automatically after registration.

    DB equivalent:
        INSERT INTO account_settings (user_id)
        VALUES (:user_id)
        RETURNING *;

    Default values come from the DB column defaults:
        theme         = 'Light'
        notifications = TRUE
        language      = 'English'

    TODO (Database Teammate):
        settings = AccountSettingsModel(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        return AccountSettings.model_validate(settings)
    """
    # --- Mock ---
    settings_id = len(_ACCOUNT_SETTINGS) + 1
    settings = AccountSettings(id=str(settings_id), user_id=user_id)
    _ACCOUNT_SETTINGS[user_id] = settings
    return settings


async def update_account_settings(user_id: str, **fields) -> Optional[AccountSettings]:
    """
    Update account settings for a user.

    DB equivalent:
        UPDATE account_settings
        SET    theme = :theme, notifications = :notifications, language = :language
        WHERE  user_id = :user_id
        RETURNING *;

    TODO (Database Teammate): Similar update pattern — fetch, setattr, commit.
    """
    # --- Mock ---
    settings = _ACCOUNT_SETTINGS.get(user_id)
    if settings is None:
        return None
    updated = settings.model_copy(update={k: v for k, v in fields.items() if v is not None})
    _ACCOUNT_SETTINGS[user_id] = updated
    return updated


# ===========================================================================
# Agency–Creator Link Service  (maps to: agency_creators table)
# ===========================================================================

async def assign_creator_to_agency(
    agency_profile_id: str,
    creator_profile_id: str,
) -> AgencyCreatorLink:
    """
    Create a new row in agency_creators linking an agency to a creator.

    DB equivalent:
        INSERT INTO agency_creators (agency_id, creator_id)
        VALUES (:agency_profile_id, :creator_profile_id)
        RETURNING *;

    Args:
        agency_profile_id:  agency_profiles.id  (NOT users.id)
        creator_profile_id: creator_profiles.id (NOT users.id)

    TODO (Database Teammate):
        link = AgencyCreatorModel(
            agency_id=agency_profile_id,
            creator_id=creator_profile_id,
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return AgencyCreatorLink.model_validate(link)
    """
    # --- Mock ---
    link = AgencyCreatorLink(
        id=str(len(_AGENCY_CREATORS) + 1),
        agency_id=agency_profile_id,
        creator_id=creator_profile_id,
        assigned_on=datetime.now(timezone.utc),
    )
    _AGENCY_CREATORS.append(link)
    return link


async def get_creators_for_agency(agency_profile_id: str) -> list[AgencyCreatorLink]:
    """
    List all creators assigned to an agency.

    DB equivalent:
        SELECT * FROM agency_creators WHERE agency_id = :agency_profile_id;

    TODO (Database Teammate):
        result = await db.execute(
            select(AgencyCreatorModel)
            .where(AgencyCreatorModel.agency_id == agency_profile_id)
        )
        return [AgencyCreatorLink.model_validate(r) for r in result.scalars().all()]
    """
    # --- Mock ---
    return [link for link in _AGENCY_CREATORS if link.agency_id == agency_profile_id]


# ===========================================================================
# Social Accounts Service  (maps to: social_accounts table)
# ===========================================================================

async def get_social_accounts(creator_profile_id: str) -> list[SocialAccount]:
    """
    List all connected social accounts for a creator.

    DB equivalent:
        SELECT * FROM social_accounts WHERE creator_id = :creator_profile_id;

    TODO (Database Teammate):
        result = await db.execute(
            select(SocialAccountModel)
            .where(SocialAccountModel.creator_id == creator_profile_id)
        )
        return [SocialAccount.model_validate(r) for r in result.scalars().all()]
    """
    # --- Mock ---
    return _SOCIAL_ACCOUNTS.get(creator_profile_id, [])


async def add_social_account(
    creator_profile_id: str,
    platform: str,
    account_name: str,
    account_id: str,
) -> SocialAccount:
    """
    Insert a row into social_accounts for a creator.

    DB equivalent:
        INSERT INTO social_accounts (creator_id, platform, account_name, account_id)
        VALUES (:creator_profile_id, :platform, :account_name, :account_id)
        RETURNING *;

    TODO (Database Teammate):
        social = SocialAccountModel(
            creator_id=creator_profile_id,
            platform=platform,
            account_name=account_name,
            account_id=account_id,
        )
        db.add(social)
        await db.commit()
        await db.refresh(social)
        return SocialAccount.model_validate(social)
    """
    # --- Mock ---
    existing = _SOCIAL_ACCOUNTS.setdefault(creator_profile_id, [])
    new_id = sum(len(v) for v in _SOCIAL_ACCOUNTS.values()) + 1
    social = SocialAccount(
        id=str(new_id),
        creator_id=creator_profile_id,
        platform=platform,
        account_name=account_name,
        account_id=account_id,
        connected_at=datetime.now(timezone.utc),
    )
    existing.append(social)
    return social


async def delete_social_account(social_account_id: str, creator_profile_id: str) -> bool:
    """
    Delete a social_accounts row by id (guarded by creator_id to prevent tampering).

    DB equivalent:
        DELETE FROM social_accounts
        WHERE id = :social_account_id AND creator_id = :creator_profile_id;

    Returns:
        True if a row was deleted, False if not found.

    TODO (Database Teammate):
        result = await db.execute(
            delete(SocialAccountModel)
            .where(
                SocialAccountModel.id == social_account_id,
                SocialAccountModel.creator_id == creator_profile_id,
            )
        )
        await db.commit()
        return result.rowcount > 0
    """
    # --- Mock ---
    accounts = _SOCIAL_ACCOUNTS.get(creator_profile_id, [])
    before = len(accounts)
    _SOCIAL_ACCOUNTS[creator_profile_id] = [a for a in accounts if a.id != social_account_id]
    return len(_SOCIAL_ACCOUNTS[creator_profile_id]) < before
