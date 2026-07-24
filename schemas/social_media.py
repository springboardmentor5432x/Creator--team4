"""
schemas/social_media.py — Pydantic schemas for social media integration.

Defines request/response models for OAuth flows, connected accounts,
and platform analytics.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class PlatformEnum(str, Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


class OAuthInitRequest(BaseModel):
    """Request to initiate OAuth flow for a platform."""
    platform: PlatformEnum


class OAuthCallbackRequest(BaseModel):
    """OAuth callback payload containing the authorization code."""
    code: str
    state: Optional[str] = None


class SocialAccountResponse(BaseModel):
    """Public-facing social account info (tokens stripped)."""
    platform: str
    accountName: str
    username: str
    followers: int
    profileUrl: Optional[str] = None
    isActive: bool = True
    connectedAt: datetime


class PlatformAnalyticsResponse(BaseModel):
    """Analytics data fetched from a platform API."""
    platform: str
    accountId: str
    period: str  # "7d", "30d", "90d"
    metrics: Dict  # Platform-specific metrics
    fetchedAt: datetime


class SyncAllResponse(BaseModel):
    """Response after syncing analytics from all connected platforms."""
    synced: List[str]
    failed: List[Dict]  # [{"platform": "...", "error": "..."}]
    syncedAt: datetime
