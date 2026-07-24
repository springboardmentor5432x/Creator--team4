"""
services/platforms/facebook.py — Facebook Graph API Client

Handles Page-level analytics fetching via the Meta Graph API.
OAuth token exchange is shared with Instagram (same Meta App).

API Reference: https://developers.facebook.com/docs/graph-api/
"""

import httpx
from typing import Dict, List
from datetime import datetime, timedelta
from config import settings

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class FacebookClient:
    """Client for interacting with the Facebook Graph API (Page analytics)."""

    def __init__(self, access_token: str):
        self.access_token = access_token

    async def get_pages(self) -> List[Dict]:
        """
        Fetch Facebook Pages managed by the authenticated user.

        Returns a list of page objects with id, name, fan_count, picture,
        and the page-specific access_token.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API_BASE}/me/accounts",
                params={
                    "fields": "id,name,fan_count,picture,access_token",
                    "access_token": self.access_token,
                }
            )
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def get_page_insights(self, page_id: str, page_token: str, days: int = 30) -> Dict:
        """
        Fetch Page-level insights (impressions, engaged users, fan adds, views).

        Args:
            page_id: The Facebook Page ID.
            page_token: The Page-specific access token.
            days: Number of days of data to fetch.
        """
        since = datetime.utcnow() - timedelta(days=days)
        until = datetime.utcnow()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API_BASE}/{page_id}/insights",
                params={
                    "metric": "page_impressions,page_engaged_users,page_fan_adds,page_views_total",
                    "period": "day",
                    "since": int(since.timestamp()),
                    "until": int(until.timestamp()),
                    "access_token": page_token,
                }
            )
            resp.raise_for_status()
            return resp.json()

    async def get_post_insights(self, post_id: str, page_token: str) -> Dict:
        """
        Fetch per-post insights (impressions, engaged users, reactions).

        Args:
            post_id: The Facebook post ID.
            page_token: The Page-specific access token.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API_BASE}/{post_id}/insights",
                params={
                    "metric": "post_impressions,post_engaged_users,post_reactions_by_type_total",
                    "access_token": page_token,
                }
            )
            resp.raise_for_status()
            return resp.json()

    async def get_page_posts(self, page_id: str, page_token: str, limit: int = 25) -> List[Dict]:
        """
        Fetch recent posts from a Facebook Page.

        Args:
            page_id: The Facebook Page ID.
            page_token: The Page-specific access token.
            limit: Maximum number of posts to return.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API_BASE}/{page_id}/posts",
                params={
                    "fields": "id,message,created_time,type,shares,likes.summary(true),comments.summary(true)",
                    "limit": limit,
                    "access_token": page_token,
                }
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
