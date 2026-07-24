"""
services/platforms/linkedin.py — LinkedIn Marketing API Client

Handles OAuth token exchange and organization analytics fetching.

API Reference: https://learn.microsoft.com/en-us/linkedin/marketing/
Note: The Marketing Developer Platform product requires approval from LinkedIn.
"""

import httpx
from typing import Dict
from datetime import datetime, timedelta
from config import settings

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
LINKEDIN_OAUTH_URL = "https://www.linkedin.com/oauth/v2"


class LinkedInClient:
    """Client for interacting with the LinkedIn Marketing API."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict:
        """
        Exchange an OAuth authorization code for an access token.

        Returns dict with: access_token, expires_in.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{LINKEDIN_OAUTH_URL}/accessToken", data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            })
            resp.raise_for_status()
            return resp.json()

    async def get_profile(self) -> Dict:
        """
        Fetch the authenticated user's LinkedIn profile.

        Returns: id, localizedFirstName, localizedLastName.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{LINKEDIN_API_BASE}/me",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_organization_id(self) -> str:
        """
        Get the organization (Company Page) administered by the authenticated user.

        Returns the organization ID as a string, or empty string if none found.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{LINKEDIN_API_BASE}/organizationAcls",
                params={
                    "q": "roleAssignee",
                    "role": "ADMINISTRATOR",
                    "projection": "(elements*(organization))",
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            if elements:
                # Organization URN format: "urn:li:organization:12345"
                return elements[0].get("organization", "").split(":")[-1]
            return ""

    async def get_page_statistics(self, org_id: str, days: int = 30) -> Dict:
        """
        Fetch organization page share statistics (impressions, clicks, etc.).

        Args:
            org_id: The LinkedIn organization ID.
            days: Number of days of data to fetch.
        """
        start_ms = int((datetime.utcnow() - timedelta(days=days)).timestamp() * 1000)
        end_ms = int(datetime.utcnow().timestamp() * 1000)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{LINKEDIN_API_BASE}/organizationalEntityShareStatistics",
                params={
                    "q": "organizationalEntity",
                    "organizationalEntity": f"urn:li:organization:{org_id}",
                    "timeIntervals.timeGranularityType": "DAY",
                    "timeIntervals.timeRange.start": start_ms,
                    "timeIntervals.timeRange.end": end_ms,
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_share_statistics(self, share_urn: str) -> Dict:
        """
        Fetch engagement statistics for a specific share/post.

        Args:
            share_urn: The LinkedIn share URN (e.g., "urn:li:share:12345").
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{LINKEDIN_API_BASE}/socialActions/{share_urn}",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()
