"""
schemas/agency.py — Agency Profile Pydantic Models

Defines the request and response schemas for the Agency Profile endpoints:

    GET  /api/agency/profile   → returns AgencyProfileResponse
    PUT  /api/agency/profile   → accepts AgencyProfileRequest, returns AgencyProfileResponse

Design notes:
  - All update fields are Optional (partial update semantics).
  - Validators enforce URL and phone formats.
  - Response model carries all agency-specific metadata.

DB table mapping:
    agency_profiles.user_id             → user_id
    agency_profiles.agency_name         → agency_name
    agency_profiles.company_description → company_description
    agency_profiles.website             → website
    agency_profiles.phone               → phone
    agency_profiles.address             → address
    agency_profiles.city                → city
    agency_profiles.country             → country
    agency_profiles.logo                → logo
    agency_profiles.contact_person      → contact_person
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request Schema (PUT /api/agency/profile body)
# ---------------------------------------------------------------------------

class AgencyProfileRequest(BaseModel):
    """
    Request body for PUT /api/agency/profile.

    All fields are optional — send only those you want to update.

    Validation applied:
        - phone:    E.164 or local format, 7–20 characters
        - website:  Must begin with http:// or https://
        - logo:     Must begin with http:// or https://
    """

    agency_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=150,
        description="Official name of the agency.",
        examples=["Bright Media Group"],
    )

    company_description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Brief description of the agency (max 1 000 characters).",
        examples=["A full-service creator management and brand partnership agency."],
    )

    website: Optional[str] = Field(
        None,
        description="Agency's official website URL.",
        examples=["https://brightmediagroup.com"],
    )

    phone: Optional[str] = Field(
        None,
        description="Agency contact phone number.",
        examples=["+44 20 7946 0123"],
    )

    address: Optional[str] = Field(
        None,
        max_length=255,
        description="Street address of the agency's primary office.",
        examples=["123 Creator Ave, Suite 400"],
    )

    city: Optional[str] = Field(
        None,
        max_length=80,
        description="City where the agency is located.",
        examples=["London"],
    )

    country: Optional[str] = Field(
        None,
        max_length=80,
        description="Country where the agency is registered.",
        examples=["United Kingdom"],
    )

    logo: Optional[str] = Field(
        None,
        description="Absolute URL of the agency's logo image.",
        examples=["https://cdn.brightmediagroup.com/logo.png"],
    )

    contact_person: Optional[str] = Field(
        None,
        max_length=100,
        description="Name of the primary point of contact at the agency.",
        examples=["Alice Johnson"],
    )

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """
        Accept common phone formats:
            +44 20 7946 0123
            +1-800-555-0199
            020 7946 0123
        Pattern: optional leading +, 7–20 chars of digits/spaces/hyphens/parens.
        """
        if value is None:
            return value
        pattern = r"^\+?[\d\s\-()]{7,20}$"
        if not re.match(pattern, value.strip()):
            raise ValueError(
                "Phone number must be 7–20 characters and contain only digits, "
                "spaces, hyphens, or parentheses (e.g. '+44 20 7946 0123')."
            )
        return value.strip()

    @field_validator("website", "logo")
    @classmethod
    def validate_url(cls, value: Optional[str]) -> Optional[str]:
        """Ensure website and logo URLs begin with http:// or https://."""
        if value is None:
            return value
        if not re.match(r"^https?://", value):
            raise ValueError(
                "URL must begin with 'http://' or 'https://'."
            )
        return value


# ---------------------------------------------------------------------------
# Response Schema (GET /api/agency/profile return value)
# ---------------------------------------------------------------------------

class AgencyProfileResponse(BaseModel):
    """
    Response body returned by GET /api/agency/profile.

    Combines data from the agency_profiles table and the users table.

    DB column mapping:
        user_id             → agency_profiles.user_id
        agency_name         → agency_profiles.agency_name
        company_description → agency_profiles.company_description
        website             → agency_profiles.website
        phone               → agency_profiles.phone
        address             → agency_profiles.address
        city                → agency_profiles.city
        country             → agency_profiles.country
        logo                → agency_profiles.logo
        contact_person      → agency_profiles.contact_person
        created_at          → agency_profiles.created_at
    """

    user_id: int = Field(..., description="FK to users.id.")
    agency_name: Optional[str] = Field(None, description="Official agency name.")
    company_description: Optional[str] = Field(None, description="Agency description.")
    website: Optional[str] = Field(None, description="Agency website URL.")
    phone: Optional[str] = Field(None, description="Contact phone number.")
    address: Optional[str] = Field(None, description="Street address.")
    city: Optional[str] = Field(None, description="City.")
    country: Optional[str] = Field(None, description="Country.")
    logo: Optional[str] = Field(None, description="Logo image URL.")
    contact_person: Optional[str] = Field(None, description="Primary contact name.")
    created_at: Optional[datetime] = Field(None, description="ISO-8601 profile creation timestamp.")

    model_config = {"from_attributes": True}
