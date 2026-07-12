"""
schemas/creator.py — Creator Profile Pydantic Models

Defines the request and response schemas for the Creator Profile endpoints:

    GET  /api/creator/profile   → returns CreatorProfileResponse
    PUT  /api/creator/profile   → accepts CreatorProfileRequest, returns CreatorProfileResponse

Design notes:
  - All fields on the update request are Optional (partial update / PATCH semantics
    even though the route is PUT, so the caller may omit unchanged fields).
  - Validators enforce URL format, phone format, and username rules.
  - Response model includes user metadata (user_id, created_at) returned from the DB.

DB table mapping:
    creator_profiles.user_id         → user_id
    creator_profiles.full_name       → full_name       (or users.full_name joined)
    creator_profiles.username        → username
    creator_profiles.bio             → bio
    creator_profiles.phone           → phone
    creator_profiles.country         → country
    creator_profiles.city            → city
    creator_profiles.profile_image   → profile_image
    creator_profiles.youtube_channel → youtube_channel
    creator_profiles.instagram_username → instagram_username
    creator_profiles.linkedin_profile   → linkedin_profile
    creator_profiles.website            → website
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, AnyHttpUrl


# ---------------------------------------------------------------------------
# Request Schema (PUT /api/creator/profile body)
# ---------------------------------------------------------------------------

class CreatorProfileRequest(BaseModel):
    """
    Request body for PUT /api/creator/profile.

    All fields are optional so the caller can send only the fields they
    wish to update (partial-update semantics).

    Validation applied:
        - phone:     E.164-style or local format, 7–20 digits/symbols
        - username:  3–50 chars, alphanumeric + underscore only
        - URLs:      AnyHttpUrl validates scheme + host
    """

    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Creator's display name.",
        examples=["Jane Doe"],
    )

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description=(
            "Unique username. Alphanumeric and underscores only. "
            "Returns 409 if already taken."
        ),
        examples=["jane_creates"],
    )

    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="Short creator biography (max 500 characters).",
        examples=["Travel & lifestyle creator based in NYC."],
    )

    phone: Optional[str] = Field(
        None,
        description="Contact phone number, e.g. '+1 555 123 4567' or '07911123456'.",
        examples=["+1 555 123 4567"],
    )

    country: Optional[str] = Field(
        None,
        max_length=80,
        description="Country of residence.",
        examples=["United States"],
    )

    city: Optional[str] = Field(
        None,
        max_length=80,
        description="City of residence.",
        examples=["New York"],
    )

    profile_image: Optional[str] = Field(
        None,
        description="Absolute URL of the creator's profile image.",
        examples=["https://cdn.example.com/avatars/jane.jpg"],
    )

    youtube_channel: Optional[str] = Field(
        None,
        description="Full URL of the creator's YouTube channel.",
        examples=["https://youtube.com/@JaneDoeCreates"],
    )

    instagram_username: Optional[str] = Field(
        None,
        max_length=50,
        description="Instagram handle (without the @ symbol).",
        examples=["janedoecreates"],
    )

    linkedin_profile: Optional[str] = Field(
        None,
        description="Full URL of the creator's LinkedIn profile.",
        examples=["https://linkedin.com/in/janedoe"],
    )

    website: Optional[str] = Field(
        None,
        description="Creator's personal or brand website URL.",
        examples=["https://janedoe.com"],
    )

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """
        Accept common phone formats:
            +1 555 123 4567
            07911 123456
            (555) 867-5309
        Pattern: optional leading +, then 7–20 characters of digits/spaces/hyphens/parens.
        """
        if value is None:
            return value
        pattern = r"^\+?[\d\s\-()]{7,20}$"
        if not re.match(pattern, value.strip()):
            raise ValueError(
                "Phone number must be 7–20 characters and contain only digits, "
                "spaces, hyphens, or parentheses (e.g. '+1 555 123 4567')."
            )
        return value.strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: Optional[str]) -> Optional[str]:
        """
        Username rules:
            - 3 to 50 characters
            - Only letters (a-z, A-Z), digits (0-9), and underscores
            - Must not start or end with an underscore
        """
        if value is None:
            return value
        pattern = r"^[A-Za-z0-9][A-Za-z0-9_]{1,48}[A-Za-z0-9]$|^[A-Za-z0-9]{3}$"
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_]*[A-Za-z0-9]$|^[A-Za-z0-9]{1}$", value):
            raise ValueError(
                "Username must be 3–50 characters, contain only letters, digits, or "
                "underscores, and must not start or end with an underscore."
            )
        return value

    @field_validator("youtube_channel", "linkedin_profile", "website", "profile_image")
    @classmethod
    def validate_url(cls, value: Optional[str]) -> Optional[str]:
        """
        Ensure URLs start with http:// or https://.
        A lightweight check — Pydantic's AnyHttpUrl parsing would be more
        strict but less flexible for partial paths.
        """
        if value is None:
            return value
        if not re.match(r"^https?://", value):
            raise ValueError(
                "URL must begin with 'http://' or 'https://'."
            )
        return value


# ---------------------------------------------------------------------------
# Response Schema (GET /api/creator/profile return value)
# ---------------------------------------------------------------------------

class CreatorProfileResponse(BaseModel):
    """
    Response body returned by GET /api/creator/profile.

    Combines data from the creator_profiles table and the users table (via JOIN).

    DB column mapping:
        user_id            → creator_profiles.user_id
        full_name          → users.full_name  (or creator_profiles.full_name if stored)
        username           → creator_profiles.username
        bio                → creator_profiles.bio
        phone              → creator_profiles.phone
        country            → creator_profiles.country
        city               → creator_profiles.city
        profile_image      → creator_profiles.profile_image
        youtube_channel    → creator_profiles.youtube_channel
        instagram_username → creator_profiles.instagram_username
        linkedin_profile   → creator_profiles.linkedin_profile
        website            → creator_profiles.website
        created_at         → creator_profiles.created_at  (or users.created_at)
    """

    user_id: int = Field(..., description="FK to users.id.")
    full_name: Optional[str] = Field(None, description="Creator's display name.")
    username: Optional[str] = Field(None, description="Unique username.")
    bio: Optional[str] = Field(None, description="Short biography.")
    phone: Optional[str] = Field(None, description="Contact phone number.")
    country: Optional[str] = Field(None, description="Country of residence.")
    city: Optional[str] = Field(None, description="City of residence.")
    profile_image: Optional[str] = Field(None, description="Profile image URL.")
    youtube_channel: Optional[str] = Field(None, description="YouTube channel URL.")
    instagram_username: Optional[str] = Field(None, description="Instagram handle.")
    linkedin_profile: Optional[str] = Field(None, description="LinkedIn profile URL.")
    website: Optional[str] = Field(None, description="Personal/brand website URL.")
    created_at: Optional[datetime] = Field(None, description="ISO-8601 profile creation timestamp.")

    model_config = {"from_attributes": True}
