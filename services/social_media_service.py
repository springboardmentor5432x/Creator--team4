"""
services/social_media_service.py — Social Media Integration Orchestrator

Coordinates OAuth flows, account management, and analytics fetching
across all supported platforms (Instagram, YouTube, LinkedIn, Facebook, X/Twitter).

Dispatches to platform-specific clients and persists results via
SocialMediaRepository.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import HTTPException

from repositories.social_media_repository import SocialMediaRepository
from repositories.content_repository import ContentRepository
from services.platforms.instagram import InstagramClient
from services.platforms.youtube import YouTubeClient
from services.platforms.linkedin import LinkedInClient
from services.platforms.facebook import FacebookClient
from services.platforms.x_twitter import XClient
from utils.analytics import calculate_engagement_rate, calculate_performance_score
from config import settings


class SocialMediaService:
    """
    Business logic layer for social media integrations.

    Responsibilities:
        - Generate OAuth URLs for each platform
        - Handle OAuth callbacks (token exchange + profile fetch)
        - List/disconnect connected accounts
        - Fetch analytics from platform APIs
    """

    def __init__(self):
        self.social_repo = SocialMediaRepository()
        self.content_repo = ContentRepository()

    # ── OAuth URL Generation ─────────────────────────────────────────────

    def get_oauth_url(self, platform: str) -> str:
        """
        Generate the OAuth authorization URL for a given platform.

        Args:
            platform: One of "instagram", "youtube", "linkedin", "facebook".

        Returns:
            The full OAuth authorization URL to redirect the user to.

        Raises:
            HTTPException: If the platform is not supported.
        """
        if platform == "instagram":
            return (
                f"https://www.facebook.com/v21.0/dialog/oauth?"
                f"client_id={settings.META_APP_ID}"
                f"&redirect_uri={settings.META_REDIRECT_URI}"
                f"&scope=instagram_basic,instagram_manage_insights,pages_show_list"
                f"&response_type=code"
            )
        elif platform == "youtube":
            return (
                f"https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={settings.GOOGLE_CLIENT_ID}"
                f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
                f"&scope=https://www.googleapis.com/auth/youtube.readonly "
                f"https://www.googleapis.com/auth/yt-analytics.readonly"
                f"&response_type=code&access_type=offline&prompt=consent"
            )
        elif platform == "linkedin":
            return (
                f"https://www.linkedin.com/oauth/v2/authorization?"
                f"client_id={settings.LINKEDIN_CLIENT_ID}"
                f"&redirect_uri={settings.LINKEDIN_REDIRECT_URI}"
                f"&scope=r_liteprofile r_organization_social"
                f"&response_type=code"
            )
        elif platform == "facebook":
            return (
                f"https://www.facebook.com/v21.0/dialog/oauth?"
                f"client_id={settings.META_APP_ID}"
                f"&redirect_uri={settings.META_FACEBOOK_REDIRECT_URI}"
                f"&scope=pages_show_list,pages_read_engagement,read_insights"
                f"&response_type=code"
            )
        elif platform == "x":
            return (
                f"https://x.com/i/oauth2/authorize?"
                f"response_type=code"
                f"&client_id={settings.X_CLIENT_ID}"
                f"&redirect_uri={settings.X_REDIRECT_URI}"
                f"&scope=tweet.read users.read offline.access"
                f"&state=x_oauth"
                f"&code_challenge=challenge&code_challenge_method=plain"
            )
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    # ── OAuth Callback Handling ──────────────────────────────────────────

    async def handle_oauth_callback(self, platform: str, code: str, creator_id: str) -> Dict:
        """
        Exchange the OAuth authorization code for tokens, fetch the user's
        profile from the platform, and save the connected account to MongoDB.

        Args:
            platform: The platform name.
            code: The OAuth authorization code from the callback.
            creator_id: The creator's ID (from PostgreSQL).

        Returns:
            Dict with platform, status, and account name.
        """
        if platform == "instagram":
            token_data = await InstagramClient.exchange_code_for_token(code)
            client = InstagramClient(token_data["access_token"])
            profile = await client.get_profile()
            account_data = {
                "accountId": profile.get("id", ""),
                "accountName": profile.get("name", ""),
                "username": profile.get("username", ""),
                "followers": profile.get("followers_count", 0),
                "profileUrl": f"https://instagram.com/{profile.get('username', '')}",
                "profilePicture": profile.get("profile_picture_url"),
                "accessToken": token_data["access_token"],
                "tokenExpiry": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000)),
                "isActive": True,
            }

        elif platform == "youtube":
            token_data = await YouTubeClient.exchange_code_for_token(code)
            client = YouTubeClient(token_data["access_token"])
            channel = await client.get_channel_info()
            snippet = channel.get("snippet", {})
            stats = channel.get("statistics", {})
            account_data = {
                "accountId": channel.get("id", ""),
                "accountName": snippet.get("title", ""),
                "username": snippet.get("customUrl", ""),
                "followers": int(stats.get("subscriberCount", 0)),
                "profileUrl": f"https://youtube.com/channel/{channel.get('id', '')}",
                "profilePicture": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                "accessToken": token_data["access_token"],
                "refreshToken": token_data.get("refresh_token"),
                "tokenExpiry": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                "isActive": True,
            }

        elif platform == "linkedin":
            token_data = await LinkedInClient.exchange_code_for_token(code)
            client = LinkedInClient(token_data["access_token"])
            profile = await client.get_profile()
            account_data = {
                "accountId": profile.get("id", ""),
                "accountName": f"{profile.get('localizedFirstName', '')} {profile.get('localizedLastName', '')}",
                "username": profile.get("id", ""),
                "followers": 0,  # LinkedIn doesn't return follower count from /me
                "accessToken": token_data["access_token"],
                "tokenExpiry": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000)),
                "isActive": True,
            }

        elif platform == "facebook":
            # Facebook has its own redirect URI, so use FacebookClient for token exchange
            token_data = await FacebookClient.exchange_code_for_token(code)
            client = FacebookClient(token_data["access_token"])
            pages = await client.get_pages()
            page = pages[0] if pages else {}
            account_data = {
                "accountId": page.get("id", ""),
                "accountName": page.get("name", ""),
                "username": page.get("name", ""),
                "followers": page.get("fan_count", 0),
                "accessToken": token_data["access_token"],
                "pageAccessToken": page.get("access_token", ""),
                "tokenExpiry": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000)),
                "isActive": True,
            }

        elif platform == "x":
            token_data = await XClient.exchange_code_for_token(code, code_verifier="challenge")
            client = XClient(token_data["access_token"])
            profile = await client.get_me()
            metrics = profile.get("public_metrics", {})
            account_data = {
                "accountId": profile.get("id", ""),
                "accountName": profile.get("name", ""),
                "username": profile.get("username", ""),
                "followers": metrics.get("followers_count", 0),
                "profileUrl": f"https://x.com/{profile.get('username', '')}",
                "profilePicture": profile.get("profile_image_url"),
                "accessToken": token_data["access_token"],
                "refreshToken": token_data.get("refresh_token"),
                "tokenExpiry": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 7200)),
                "isActive": True,
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

        await self.social_repo.upsert_account(creator_id, platform, account_data)
        return {
            "platform": platform,
            "status": "connected",
            "account": account_data.get("accountName"),
        }

    # ── Account Management ───────────────────────────────────────────────

    async def get_connected_accounts(self, creator_id: str) -> List[Dict]:
        """
        Return all connected social accounts for a creator.

        Sensitive fields (tokens) are stripped before returning.
        """
        accounts = await self.social_repo.get_accounts_by_creator(creator_id)
        for acc in accounts:
            # Never expose tokens to the frontend
            acc.pop("accessToken", None)
            acc.pop("refreshToken", None)
            acc.pop("pageAccessToken", None)
            # Serialize ObjectId for JSON
            acc["_id"] = str(acc["_id"])
        return accounts

    async def disconnect_account(self, creator_id: str, platform: str) -> Dict:
        """
        Remove a connected social media account.

        Raises:
            HTTPException: If no account was found for the platform.
        """
        deleted = await self.social_repo.delete_account(creator_id, platform)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"{platform} account not found")
        return {"platform": platform, "status": "disconnected"}

    # ── Analytics Fetching ───────────────────────────────────────────────

    async def fetch_platform_analytics(self, creator_id: str, platform: str, days: int = 30) -> Dict:
        """
        Fetch analytics from a specific connected platform.

        The raw API response is returned, enriched with metadata.

        Args:
            creator_id: The creator's ID.
            platform: The platform to fetch from.
            days: Number of days of analytics to retrieve.

        Raises:
            HTTPException: If the platform account is not connected.
        """
        account = await self.social_repo.get_account(creator_id, platform)
        if not account:
            raise HTTPException(status_code=404, detail=f"{platform} account not connected")

        access_token = account["accessToken"]

        if platform == "instagram":
            client = InstagramClient(access_token)
            insights = await client.get_insights(account["accountId"], days=days)
            return {
                "platform": platform,
                "accountId": account["accountId"],
                "insights": insights,
                "fetchedAt": datetime.utcnow().isoformat(),
            }

        elif platform == "youtube":
            # Check if token needs refresh
            if account.get("tokenExpiry") and account["tokenExpiry"] < datetime.utcnow():
                refresh_token = account.get("refreshToken")
                if refresh_token:
                    new_tokens = await YouTubeClient.refresh_access_token(refresh_token)
                    access_token = new_tokens["access_token"]
                    await self.social_repo.update_tokens(creator_id, platform, {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_expiry": datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600)),
                    })

            client = YouTubeClient(access_token)
            analytics = await client.get_analytics(account["accountId"], days=days)
            return {
                "platform": platform,
                "accountId": account["accountId"],
                "analytics": analytics,
                "fetchedAt": datetime.utcnow().isoformat(),
            }

        elif platform == "linkedin":
            client = LinkedInClient(access_token)
            org_id = await client.get_organization_id()
            if not org_id:
                return {
                    "platform": platform,
                    "accountId": account["accountId"],
                    "statistics": {},
                    "message": "No organization page found for this account",
                    "fetchedAt": datetime.utcnow().isoformat(),
                }
            stats = await client.get_page_statistics(org_id, days=days)
            return {
                "platform": platform,
                "accountId": account["accountId"],
                "organizationId": org_id,
                "statistics": stats,
                "fetchedAt": datetime.utcnow().isoformat(),
            }

        elif platform == "facebook":
            client = FacebookClient(access_token)
            page_token = account.get("pageAccessToken", access_token)
            insights = await client.get_page_insights(account["accountId"], page_token, days=days)
            return {
                "platform": platform,
                "accountId": account["accountId"],
                "insights": insights,
                "fetchedAt": datetime.utcnow().isoformat(),
            }

        elif platform == "x":
            # Check if token needs refresh
            if account.get("tokenExpiry") and account["tokenExpiry"] < datetime.utcnow():
                refresh_token = account.get("refreshToken")
                if refresh_token:
                    new_tokens = await XClient.refresh_access_token(refresh_token)
                    access_token = new_tokens["access_token"]
                    await self.social_repo.update_tokens(creator_id, platform, {
                        "access_token": access_token,
                        "refresh_token": new_tokens.get("refresh_token", refresh_token),
                        "token_expiry": datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 7200)),
                    })

            client = XClient(access_token)
            profile = await client.get_me()
            tweets = await client.get_user_tweets(account["accountId"])
            return {
                "platform": platform,
                "accountId": account["accountId"],
                "profile_metrics": profile.get("public_metrics", {}),
                "recent_tweets": tweets,
                "fetchedAt": datetime.utcnow().isoformat(),
            }

        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
