"""
services/platforms/instagram.py — Instagram Graph API Client

Handles OAuth token exchange and analytics fetching via the Meta Graph API.
Requires an Instagram Business or Creator account linked to a Facebook Page.

API Reference: https://developers.facebook.com/docs/instagram-api/
"""

import httpx
from typing import Dict
from datetime import datetime, timedelta
from config import settings

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class InstagramClient:
    """Client for interacting with the Instagram Graph API."""

    def __init__(self, access_token: str):
        self.access_token = access_token

    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict:
        """
        Exchange an OAuth authorization code for an access token.

        Flow:
            1. Exchange code → short-lived token
            2. Exchange short-lived token → long-lived token (~60 days)
        """
        async with httpx.AsyncClient() as client:
            # Step 1: Get short-lived token
            resp = await client.get(f"{GRAPH_API_BASE}/oauth/access_token", params={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "redirect_uri": settings.META_REDIRECT_URI,
                "code": code,
            })
            resp.raise_for_status()
            data = resp.json()
            short_token = data["access_token"]

            # Step 2: Exchange for long-lived token
            resp2 = await client.get(f"{GRAPH_API_BASE}/oauth/access_token", params={
                "grant_type": "fb_exchange_token",
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "fb_exchange_token": short_token,
            })
            resp2.raise_for_status()
            long_data = resp2.json()
            return {
                "access_token": long_data["access_token"],
                "expires_in": long_data.get("expires_in", 5184000),  # ~60 days
            }

    async def get_profile(self) -> Dict:
        """
        Fetch the Instagram Business account profile.

        Traverses: User → Pages → Instagram Business Account → Profile data.
        """
        async with httpx.AsyncClient() as client:
            # Get Facebook Pages the user manages
            resp = await client.get(f"{GRAPH_API_BASE}/me/accounts", params={
                "access_token": self.access_token,
            })
            resp.raise_for_status()
            pages = resp.json().get("data", [])
            if not pages:
                return {}

            page_id = pages[0]["id"]
            page_token = pages[0]["access_token"]

            # Get the linked Instagram Business Account
            resp2 = await client.get(
                f"{GRAPH_API_BASE}/{page_id}",
                params={"fields": "instagram_business_account", "access_token": page_token}
            )
            resp2.raise_for_status()
            ig_id = resp2.json().get("instagram_business_account", {}).get("id")
            if not ig_id:
                return {}

            # Fetch IG profile details
            resp3 = await client.get(
                f"{GRAPH_API_BASE}/{ig_id}",
                params={
                    "fields": "id,username,name,profile_picture_url,followers_count,media_count",
                    "access_token": self.access_token,
                }
            )
            resp3.raise_for_status()
            return resp3.json()

    async def get_insights(self, ig_user_id: str, period: str = "day", days: int = 30) -> Dict:
        """
        Fetch account-level insights (impressions, reach, follower_count).

        Args:
            ig_user_id: The Instagram Business Account ID.
            period: Aggregation period — "day", "week", or "days_28".
            days: Number of days of data to fetch.
        """
        since = datetime.utcnow() - timedelta(days=days)
        until = datetime.utcnow()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API_BASE}/{ig_user_id}/insights",
                params={
                    "metric": "impressions,reach,follower_count",
                    "period": period,
                    "since": int(since.timestamp()),
                    "until": int(until.timestamp()),
                    "access_token": self.access_token,
                }
            )
            resp.raise_for_status()
            return resp.json()

    async def get_media_insights(self, media_id: str) -> Dict:
        """
        Fetch per-post insights for a specific media object.

        Metrics: impressions, reach, engagement, saved, video_views.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API_BASE}/{media_id}/insights",
                params={
                    "metric": "impressions,reach,engagement,saved,video_views",
                    "access_token": self.access_token,
                }
            )
            resp.raise_for_status()
            return resp.json()
