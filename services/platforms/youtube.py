"""
services/platforms/youtube.py — YouTube Data API v3 + Analytics API Client

Handles OAuth token exchange and analytics fetching via Google APIs.

APIs used:
    - YouTube Data API v3: Channel info, video statistics
    - YouTube Analytics API: Channel-level reports (views, watch time, etc.)

API Reference: https://developers.google.com/youtube/v3
"""

import httpx
from typing import Dict
from datetime import datetime, timedelta
from config import settings

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
YOUTUBE_ANALYTICS_BASE = "https://youtubeanalytics.googleapis.com/v2"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"


class YouTubeClient:
    """Client for interacting with YouTube Data and Analytics APIs."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict:
        """
        Exchange an OAuth authorization code for access and refresh tokens.

        Returns dict with: access_token, refresh_token, expires_in, token_type.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(OAUTH_TOKEN_URL, data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            })
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Dict:
        """
        Refresh an expired access token using the stored refresh token.

        Returns dict with: access_token, expires_in, token_type.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(OAUTH_TOKEN_URL, data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            })
            resp.raise_for_status()
            return resp.json()

    async def get_channel_info(self) -> Dict:
        """
        Fetch the authenticated user's YouTube channel info.

        Returns snippet (title, description, thumbnails) and statistics
        (subscriber count, video count, view count).
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/channels",
                params={"part": "snippet,statistics", "mine": "true"},
                headers=self.headers,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            return items[0] if items else {}

    async def get_analytics(self, channel_id: str, days: int = 30) -> Dict:
        """
        Fetch channel-level analytics report.

        Metrics: views, likes, comments, shares, estimatedMinutesWatched,
                 subscribersGained.

        Args:
            channel_id: The YouTube channel ID.
            days: Number of days of data to fetch.
        """
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{YOUTUBE_ANALYTICS_BASE}/reports",
                params={
                    "ids": f"channel=={channel_id}",
                    "startDate": start_date,
                    "endDate": end_date,
                    "metrics": "views,likes,comments,shares,estimatedMinutesWatched,subscribersGained",
                    "dimensions": "day",
                    "sort": "day",
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_video_analytics(self, video_id: str) -> Dict:
        """
        Fetch statistics and snippet for a specific video.

        Args:
            video_id: The YouTube video ID.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/videos",
                params={"part": "statistics,snippet", "id": video_id},
                headers=self.headers,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            return items[0] if items else {}
