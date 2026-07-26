"""
services/platforms/x_twitter.py — X (Twitter) API v2 Client

Handles OAuth 2.0 (PKCE) token exchange and analytics fetching via the X API v2.

X uses OAuth 2.0 with PKCE for user-context authentication.
This client handles token exchange and fetches user profile + tweet metrics.

API Reference: https://developer.x.com/en/docs/x-api
"""

import httpx
import base64
from typing import Dict, List
from datetime import datetime, timedelta
from config import settings

X_API_BASE = "https://api.x.com/2"
X_OAUTH_TOKEN_URL = "https://api.x.com/2/oauth2/token"


class XClient:
    """Client for interacting with the X (Twitter) API v2."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    @staticmethod
    async def exchange_code_for_token(code: str, code_verifier: str = None) -> Dict:
        """
        Exchange an OAuth 2.0 authorization code for an access token.

        X uses OAuth 2.0 with PKCE. The code_verifier is required if
        a code_challenge was used in the authorization request.

        For confidential clients (server-side), Basic Auth with
        client_id:client_secret is used.
        """
        # Basic auth header: base64(client_id:client_secret)
        credentials = base64.b64encode(
            f"{settings.X_CLIENT_ID}:{settings.X_CLIENT_SECRET}".encode()
        ).decode()

        async with httpx.AsyncClient() as client:
            payload = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.X_REDIRECT_URI,
            }
            if code_verifier:
                payload["code_verifier"] = code_verifier

            resp = await client.post(
                X_OAUTH_TOKEN_URL,
                data=payload,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),
                "expires_in": data.get("expires_in", 7200),  # default 2 hours
            }

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Dict:
        """
        Refresh an expired access token using the refresh token.

        X OAuth 2.0 access tokens expire after ~2 hours.
        """
        credentials = base64.b64encode(
            f"{settings.X_CLIENT_ID}:{settings.X_CLIENT_SECRET}".encode()
        ).decode()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                X_OAUTH_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token", refresh_token),
                "expires_in": data.get("expires_in", 7200),
            }

    async def get_me(self) -> Dict:
        """
        Fetch the authenticated user's profile.

        Returns id, name, username, profile_image_url, and public_metrics
        (followers_count, following_count, tweet_count, listed_count).
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{X_API_BASE}/users/me",
                headers=self.headers,
                params={
                    "user.fields": "id,name,username,profile_image_url,public_metrics,description",
                },
            )
            resp.raise_for_status()
            return resp.json().get("data", {})

    async def get_user_tweets(self, user_id: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch recent tweets for a user with engagement metrics.

        Args:
            user_id: The X user ID.
            max_results: Number of tweets to fetch (5-100).
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{X_API_BASE}/users/{user_id}/tweets",
                headers=self.headers,
                params={
                    "max_results": max_results,
                    "tweet.fields": "id,text,created_at,public_metrics,organic_metrics",
                },
            )
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def get_tweet_metrics(self, tweet_ids: List[str]) -> List[Dict]:
        """
        Fetch metrics for specific tweets.

        Args:
            tweet_ids: List of tweet IDs (max 100).
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{X_API_BASE}/tweets",
                headers=self.headers,
                params={
                    "ids": ",".join(tweet_ids[:100]),
                    "tweet.fields": "public_metrics,organic_metrics,created_at",
                },
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
