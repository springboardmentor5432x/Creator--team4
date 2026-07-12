"""
schemas/account.py — Account Settings & Management Pydantic Models

Defines request and response schemas for the Account endpoints:

    GET   /api/account/settings         → returns AccountSettingsResponse
    PATCH /api/account/settings         → accepts AccountSettingsUpdateRequest
    PATCH /api/account/change-password  → accepts ChangePasswordRequest
    PATCH /api/account/deactivate       → returns AccountStatusResponse
    PATCH /api/account/reactivate       → returns AccountStatusResponse
    PATCH /api/account/delete           → returns AccountStatusResponse

Design notes:
  - Email validated via Pydantic EmailStr.
  - Phone validated via regex (same pattern as creator/agency).
  - Password: minimum 8 characters, must contain ≥1 letter and ≥1 digit.
  - Username: alphanumeric + underscore, 3–50 chars.

DB table mapping:
    users.email           → email
    users.username        → username
    users.phone           → phone
    users.profile_picture → profile_picture
    users.is_active       → is_active  (PATCH deactivate / reactivate)
    users.is_deleted      → is_deleted (PATCH delete — soft delete)
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Account Settings — Response Schema (GET /api/account/settings)
# ---------------------------------------------------------------------------

class AccountSettingsResponse(BaseModel):
    """
    Response body for GET /api/account/settings.

    Returns the authenticated user's mutable account fields.

    DB column mapping:
        id              → users.id
        email           → users.email
        username        → users.username (or creator_profiles/agency_profiles.username)
        phone           → users.phone
        profile_picture → users.profile_picture
        is_active       → users.is_active
        is_deleted      → users.is_deleted
        updated_at      → users.updated_at
    """

    id: Optional[int] = Field(None, description="users.id primary key.")
    email: Optional[str] = Field(None, description="Registered email address.")
    username: Optional[str] = Field(None, description="Display username.")
    phone: Optional[str] = Field(None, description="Contact phone number.")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL.")
    is_active: bool = Field(True, description="Whether the account is active.")
    is_deleted: bool = Field(False, description="Whether the account has been soft-deleted.")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp (ISO-8601).")

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Account Settings — Request Schema (PATCH /api/account/settings)
# ---------------------------------------------------------------------------

class AccountSettingsUpdateRequest(BaseModel):
    """
    Request body for PATCH /api/account/settings.

    All fields are optional — the caller sends only what they want to change.
    The service layer checks username uniqueness and email uniqueness before saving.

    Validation applied:
        - email:           Pydantic EmailStr (RFC 5322 compliant)
        - username:        Alphanumeric + underscore, 3–50 chars
        - phone:           7–20 chars, digits/spaces/hyphens/parens
        - profile_picture: Must begin with http:// or https://
    """

    email: Optional[EmailStr] = Field(
        None,
        description=(
            "New email address. Must be unique across all users (users.email UNIQUE). "
            "Returns 409 if already taken."
        ),
        examples=["newemail@example.com"],
    )

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description=(
            "New display username. Must be unique. "
            "Returns 409 if already taken."
        ),
        examples=["jane_creates"],
    )

    phone: Optional[str] = Field(
        None,
        description="New contact phone number.",
        examples=["+1 555 123 4567"],
    )

    profile_picture: Optional[str] = Field(
        None,
        description="Absolute URL of the new profile picture.",
        examples=["https://cdn.example.com/avatars/jane_new.jpg"],
    )

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: Optional[str]) -> Optional[str]:
        """
        Username rules:
            - 3 to 50 characters
            - Only letters (a-z, A-Z), digits (0-9), and underscores
            - Must start and end with a letter or digit (not underscore)
        """
        if value is None:
            return value
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_]*[A-Za-z0-9]$|^[A-Za-z0-9]{1}$", value):
            raise ValueError(
                "Username must be 3–50 characters, use only letters/digits/underscores, "
                "and must not start or end with an underscore."
            )
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """E.164-style or local format — 7–20 characters."""
        if value is None:
            return value
        if not re.match(r"^\+?[\d\s\-()]{7,20}$", value.strip()):
            raise ValueError(
                "Phone number must be 7–20 characters: digits, spaces, hyphens, or parentheses."
            )
        return value.strip()

    @field_validator("profile_picture")
    @classmethod
    def validate_profile_picture_url(cls, value: Optional[str]) -> Optional[str]:
        """Profile picture must be a valid absolute URL."""
        if value is None:
            return value
        if not re.match(r"^https?://", value):
            raise ValueError("profile_picture must begin with 'http://' or 'https://'.")
        return value


# ---------------------------------------------------------------------------
# Change Password — Request Schema (PATCH /api/account/change-password)
# ---------------------------------------------------------------------------

class ChangePasswordRequest(BaseModel):
    """
    Request body for PATCH /api/account/change-password.

    The service layer must:
        1. Verify `current_password` matches users.password_hash (bcrypt check).
        2. Hash `new_password` and update users.password_hash.

    Password strength rules:
        - Minimum 8 characters
        - At least one letter
        - At least one digit
    """

    current_password: str = Field(
        ...,
        min_length=1,
        description="The user's current password (used for verification before change).",
        examples=["OldPass@123"],
    )

    new_password: str = Field(
        ...,
        min_length=8,
        description=(
            "New password. Minimum 8 characters, "
            "must contain at least one letter and one digit."
        ),
        examples=["NewSecure@456"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """
        Enforce:
            - At least 8 characters (already enforced by min_length)
            - At least one alphabetic character
            - At least one numeric digit
        """
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("New password must contain at least one letter.")
        if not re.search(r"\d", value):
            raise ValueError("New password must contain at least one digit.")
        return value


# ---------------------------------------------------------------------------
# Account Status — Response Schema (PATCH deactivate / reactivate / delete)
# ---------------------------------------------------------------------------

class AccountStatusResponse(BaseModel):
    """
    Generic response for account lifecycle endpoints:
        PATCH /api/account/deactivate
        PATCH /api/account/reactivate
        PATCH /api/account/delete

    Tells the caller the operation that was performed and the resulting flags.
    """

    message: str = Field(..., description="Human-readable confirmation message.")
    user_id: int = Field(..., description="ID of the affected user.")
    is_active: bool = Field(..., description="Current is_active flag value after the operation.")
    is_deleted: bool = Field(..., description="Current is_deleted flag value after the operation.")
