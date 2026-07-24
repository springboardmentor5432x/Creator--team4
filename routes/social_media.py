"""
routes/social_media.py — Social Media Integration Endpoints

Provides endpoints for:
    - OAuth connection flow (get URL, handle callback)
    - Listing/disconnecting connected accounts
    - Fetching analytics from connected platforms

Permission matrix:
    social:connect      — Admin ✅, Agency ✅, Creator ✅
    social:disconnect   — Admin ✅, Agency ✅, Creator ✅
    social:analytics    — Admin ✅, Agency ✅, Creator Own, Marketing ✅

Endpoints:
    GET    /api/social/connect/{platform}       → Get OAuth URL
    GET    /api/social/callback/{platform}      → Handle OAuth callback
    GET    /api/social/accounts                 → List connected accounts
    GET    /api/social/analytics/{platform}     → Fetch platform analytics
    DELETE /api/social/disconnect/{platform}    → Disconnect an account
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List

from authorization import require_any_permission, require_permission
from permissions import Permission
from models import UserModel
from services.social_media_service import SocialMediaService
from schemas.social_media import PlatformEnum

router = APIRouter(prefix="/api/social", tags=["Social Media Integration"])


def get_social_service() -> SocialMediaService:
    """Dependency injector for SocialMediaService."""
    return SocialMediaService()


def get_creator_id(current_user: UserModel) -> str:
    """
    Extract the creator profile ID from the authenticated user.

    Raises HTTPException 403 if the user has no creator profile.
    """
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    raise HTTPException(status_code=403, detail="Not authorized as a creator")


# ── OAuth Flow ───────────────────────────────────────────────────────────


@router.get("/connect/{platform}", response_model=Dict)
async def connect_platform(
    platform: PlatformEnum,
    current_user: UserModel = Depends(
        require_any_permission(Permission.CONTENT_CREATE)
    ),
    service: SocialMediaService = Depends(get_social_service),
):
    """
    Returns the OAuth authorization URL for the given platform.

    The frontend should redirect the user to this URL to begin the
    OAuth consent flow.
    """
    oauth_url = service.get_oauth_url(platform.value)
    return {"platform": platform.value, "oauth_url": oauth_url}


@router.get("/callback/{platform}", response_model=Dict)
async def oauth_callback(
    platform: PlatformEnum,
    code: str = Query(..., description="OAuth authorization code"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.CONTENT_CREATE)
    ),
    service: SocialMediaService = Depends(get_social_service),
):
    """
    Handle the OAuth callback from a social media platform.

    Exchanges the authorization code for tokens, fetches the user's
    profile, and saves the connected account.
    """
    creator_id = get_creator_id(current_user)
    return await service.handle_oauth_callback(platform.value, code, creator_id)


# ── Account Management ──────────────────────────────────────────────────


@router.get("/accounts", response_model=List[Dict])
async def list_connected_accounts(
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: SocialMediaService = Depends(get_social_service),
):
    """
    List all connected social media accounts for the authenticated creator.

    Sensitive fields (tokens) are stripped from the response.
    """
    creator_id = get_creator_id(current_user)
    return await service.get_connected_accounts(creator_id)


@router.delete("/disconnect/{platform}", response_model=Dict)
async def disconnect_platform(
    platform: PlatformEnum,
    current_user: UserModel = Depends(
        require_any_permission(Permission.CONTENT_CREATE)
    ),
    service: SocialMediaService = Depends(get_social_service),
):
    """
    Disconnect a social media account.

    Removes the account and its stored tokens from MongoDB.
    """
    creator_id = get_creator_id(current_user)
    return await service.disconnect_account(creator_id, platform.value)


# ── Analytics Fetching ───────────────────────────────────────────────────


@router.get("/analytics/{platform}", response_model=Dict)
async def get_platform_analytics(
    platform: PlatformEnum,
    days: int = Query(30, ge=1, le=90, description="Number of days of analytics to fetch"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: SocialMediaService = Depends(get_social_service),
):
    """
    Fetch analytics from a connected social media platform.

    Returns platform-specific metrics for the specified time period.
    For YouTube, automatically refreshes expired tokens.
    """
    creator_id = get_creator_id(current_user)
    return await service.fetch_platform_analytics(creator_id, platform.value, days)
