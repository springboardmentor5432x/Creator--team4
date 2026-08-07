"""
schemas.py - Pydantic Models (Request & Response Schemas)

Aligned with the PostgreSQL database schema:

    users             → UserInDB, UserPublicResponse, UserRegisterRequest
    roles             → (handled via UserRole enum in roles.py)
    creator_profiles  → CreatorProfile, CreatorProfileUpdate
    agency_profiles   → AgencyProfile, AgencyProfileUpdate
    account_settings  → AccountSettings, AccountSettingsUpdate
    agency_creators   → AgencyCreatorLink
    social_accounts   → SocialAccount, SocialAccountCreate

Note: UserRole is defined in roles.py — single source of truth.
"""

import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional

from roles import UserRole  # noqa: F401 — re-exported for backward compat


# ===========================================================================
# AUTH / USER SCHEMAS  (maps to: users + roles tables)
# ===========================================================================

# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class UserRegisterRequest(BaseModel):
    """
    Request body for POST /api/auth/register.

    DB mapping:
        full_name  → users.full_name
        email      → users.email
        password   → hashed → users.password_hash
        role       → looked up → users.role_id  (FK to roles.id)
    """

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full name as stored in users.full_name.",
        examples=["Jane Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address. Must be unique (users.email UNIQUE).",
        examples=["jane@example.com"],
    )
    phone_number: str = Field(
        ...,
        max_length=20,
        description="User's phone number with country code (e.g. +1234567890).",
        examples=["+1234567890"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (min 8 chars, must contain a letter and a digit).",
        examples=["Secure@123"],
    )
    role: UserRole = Field(
        ...,
        description=(
            "RBAC role. Valid values: creator, agency, marketing_team, administrator. "
            "Maps to roles.role_name → users.role_id."
        ),
        examples=["creator"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Enforce: ≥8 chars, at least one letter, at least one digit."""
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Password must contain at least one letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        """Enforce: starts with +, followed by digits. Strips spaces and dashes."""
        # Clean the input first (remove spaces and dashes)
        clean_value = value.replace(" ", "").replace("-", "")
        
        if not re.match(r"^\+\d{7,15}$", clean_value):
            raise ValueError("Phone number must start with a '+' country code followed by 7 to 15 digits (e.g. +91 1234567890).")
        return clean_value

        debug.print(UserRegisterRequest.full_name,UserRegisterRequest.email,UserRegisterRequest.password,UserRegisterRequest.role,UserRegisterRequest.phone_number    )
    
class UserLoginRequest(BaseModel):
    """Request body for POST /api/auth/login."""

    email: EmailStr = Field(..., examples=["jane@example.com"])
    password: str = Field(..., examples=["Secure@123"])


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    """Returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
    role: UserRole



class UserPublicResponse(BaseModel):
    """
    Safe public representation of a user row.

    UID format (generated on registration, unique per user):
        Creator   → crt{u}{n}   RID = 1
        Agency    → agc{u}{n}   RID = 2
        Marketing → mrt{u}{n}   RID = 3
        Admin     → adm{u}{n}   RID = 4

        u = nth user of the application (users.id)
        n = nth user within their role group

    DB mapping:
        id         → users.id
        uid        → users.uid         (generated composite key, stored in DB)
        full_name  → users.full_name
        email      → users.email
        rid        → users.role_id     (FK → roles.id; aliased as rid)
        role       → roles.role_name   (joined)
        created_at → users.created_at
    """

    id: Optional[str] = None
    full_name: str
    email: str
    phone_number: str
    rid: Optional[int] = None           # users.role_id — FK to roles.id
    role: UserRole
    created_at: Optional[datetime] = None


class RegisterSuccessResponse(BaseModel):
    """Returned after successful registration (HTTP 201)."""

    message: str = "User registered successfully."
    user: UserPublicResponse


# ---------------------------------------------------------------------------
# Internal / Service-Layer User Schema
# ---------------------------------------------------------------------------

class UserInDB(BaseModel):
    """
    Internal representation of a full user row (users JOIN roles).

    This is what user_service functions must return so that auth/authz logic
    can access the role without an extra query.

    DB column mapping:
        id             → users.id          (SERIAL PRIMARY KEY)
        full_name      → users.full_name   (VARCHAR 100)
        email          → users.email       (VARCHAR 100 UNIQUE)
        hashed_password→ users.password_hash (TEXT)
        role_id        → users.role_id     (INTEGER FK → roles.id)
        role           → roles.role_name   (joined; stored as UserRole enum)
        created_at     → users.created_at  (TIMESTAMP)
        is_active      → application-level flag (add column when DB team is ready)

    TODO (Database Teammate):
        Replace mock data with SQLAlchemy query results:
            SELECT u.*, r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.email = :email
        Then map to UserInDB.model_validate(row._mapping)
    """

    id: Optional[str] = None
    full_name: str
    email: str
    phone_number: str
    hashed_password: str               # maps to users.password_hash
    role_id: Optional[int] = None      # maps to users.role_id (FK → roles.id)
    role: UserRole                     # derived from roles.role_name (joined)
    created_at: Optional[datetime] = None
    is_active: bool = True             # TODO: add users.is_active column in DB

    @property
    def rid(self) -> Optional[int]:
        """Alias for role_id — matches the RID column name in the design."""
        return self.role_id


# ===========================================================================
# CREATOR PROFILE SCHEMAS  (maps to: creator_profiles table)
# ===========================================================================

class CreatorProfile(BaseModel):
    """
    Read model for creator_profiles table.

    DB mapping:
        id            → creator_profiles.id
        user_id       → creator_profiles.user_id  (FK → users.id)
        username      → creator_profiles.username
        bio           → creator_profiles.bio
        youtube_url   → creator_profiles.youtube_url
        instagram_url → creator_profiles.instagram_url
        tiktok_url    → creator_profiles.tiktok_url
        linkedin_url  → creator_profiles.linkedin_url
    """
    id: Optional[str] = None
    user_id: str
    username: Optional[str] = None
    bio: Optional[str] = None
    youtube_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class CreatorProfileUpdate(BaseModel):
    """Request body for updating a creator's profile (PATCH)."""

    username: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    youtube_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    linkedin_url: Optional[str] = None


# ===========================================================================
# AGENCY PROFILE SCHEMAS  (maps to: agency_profiles table)
# ===========================================================================

class AgencyProfile(BaseModel):
    """
    Read model for agency_profiles table.

    DB mapping:
        id             → agency_profiles.id
        user_id        → agency_profiles.user_id  (FK → users.id)
        agency_name    → agency_profiles.agency_name
        website        → agency_profiles.website
        contact_number → agency_profiles.contact_number
    """
    id: Optional[str] = None
    user_id: str
    agency_name: Optional[str] = None
    website: Optional[str] = None
    contact_number: Optional[str] = None


class AgencyProfileUpdate(BaseModel):
    """Request body for updating an agency's profile (PATCH)."""

    agency_name: Optional[str] = Field(None, max_length=150)
    website: Optional[str] = None
    contact_number: Optional[str] = Field(None, max_length=20)


# ===========================================================================
# ACCOUNT SETTINGS SCHEMAS  (maps to: account_settings table)
# ===========================================================================

class AccountSettings(BaseModel):
    """
    Read model for account_settings table.

    DB mapping:
        id            → account_settings.id
        user_id       → account_settings.user_id (FK → users.id, UNIQUE)
        theme         → account_settings.theme          DEFAULT 'Light'
        notifications → account_settings.notifications  DEFAULT TRUE
        language      → account_settings.language       DEFAULT 'English'
    """
    id: Optional[str] = None
    user_id: str
    theme: str = "Light"
    notifications: bool = True
    language: str = "English"


class AccountSettingsUpdate(BaseModel):
    """Request body for updating account settings (PATCH)."""

    theme: Optional[str] = Field(None, max_length=20)
    notifications: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=30)


# ===========================================================================
# SOCIAL ACCOUNT SCHEMAS  (maps to: social_accounts table)
# ===========================================================================

class SocialAccount(BaseModel):
    """
    Read model for social_accounts table.

    DB mapping:
        id           → social_accounts.id
        creator_id   → social_accounts.creator_id (FK → creator_profiles.id)
        platform     → social_accounts.platform
        account_name → social_accounts.account_name
        account_id   → social_accounts.account_id
        connected_at → social_accounts.connected_at
    """
    id: Optional[str] = None
    creator_id: str
    platform: Optional[str] = None
    account_name: Optional[str] = None
    account_id: Optional[str] = None
    connected_at: Optional[datetime] = None


class SocialAccountCreate(BaseModel):
    """Request body for POST /api/creator/social-accounts."""

    platform: str = Field(..., max_length=50, examples=["YouTube"])
    account_name: str = Field(..., max_length=100, examples=["@JaneDoeCreates"])
    account_id: str = Field(..., max_length=100, examples=["UCxxxxxxxxxxxxxxxx"])


# ===========================================================================
# AGENCY–CREATOR LINK SCHEMAS  (maps to: agency_creators table)
# ===========================================================================

class AgencyCreatorLink(BaseModel):
    """
    Read model for agency_creators table.

    DB mapping:
        id          → agency_creators.id
        agency_id   → agency_creators.agency_id   (FK → agency_profiles.id)
        creator_id  → agency_creators.creator_id  (FK → creator_profiles.id)
        assigned_on → agency_creators.assigned_on
    """
    id: Optional[str] = None
    agency_id: str
    creator_id: str
    assigned_on: Optional[datetime] = None


class AgencyCreatorAssign(BaseModel):
    """Request body for assigning a creator to an agency."""

    creator_id: str = Field(..., description="creator_profiles.id of the creator to assign.")
