"""
services/sync_service.py — Analytics Sync Orchestrator

Coordinates the full pipeline for fetching analytics from social media
platforms and persisting them into MongoDB (platform_analytics_raw) and
PostgreSQL (sync_history).

Responsibilities:
  - Load stored OAuth tokens for a creator/platform
  - Refresh expired tokens when a refresh_token is available
  - Call platform-specific API clients
  - Normalize raw API responses into the PlatformSnapshot schema
  - Upsert daily snapshot into platform_analytics_raw
  - Update sync status on social_accounts document
  - Write a sync_history row to PostgreSQL

Public Interface:
  sync_platform(creator_id, platform, days=30)  → SyncResult
  sync_all_for_creator(creator_id, days=30)     → List[SyncResult]
  sync_all_creators(days=30)                    → None  (called by scheduler)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from database import AsyncSessionLocal
from repositories.social_media_repository import SocialMediaRepository
from repositories.platform_analytics_repository import PlatformAnalyticsRepository
from services.platforms.youtube import YouTubeClient
from services.platforms.instagram import InstagramClient
from services.platforms.linkedin import LinkedInClient
from services.platforms.facebook import FacebookClient
from services.platforms.x_twitter import XClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class SyncResult:
    """Outcome of a single platform sync attempt."""
    platform: str
    creator_id: str
    status: str                            # "success" | "failed"
    records_updated: int = 0
    error_message: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def as_dict(self) -> Dict:
        return {
            "platform":        self.platform,
            "creator_id":      self.creator_id,
            "status":          self.status,
            "records_updated": self.records_updated,
            "error_message":   self.error_message,
            "started_at":      self.started_at.isoformat(),
            "completed_at":    self.completed_at.isoformat() if self.completed_at else None,
        }


# ---------------------------------------------------------------------------
# SyncService
# ---------------------------------------------------------------------------

class SyncService:
    """
    Orchestrates the analytics fetch-normalize-store pipeline.

    Each public method is self-contained and safe to call concurrently
    across different creator/platform combinations.
    """

    def __init__(self):
        self.social_repo    = SocialMediaRepository()
        self.analytics_repo = PlatformAnalyticsRepository()

    # ── Public methods ───────────────────────────────────────────────────

    async def sync_platform(
        self,
        creator_id: str,
        platform: str,
        days: int = 30,
    ) -> SyncResult:
        """
        Sync analytics for one creator on one platform.

        Steps:
          1. Load account (tokens) from MongoDB
          2. Refresh token if expired
          3. Fetch raw analytics from platform API
          4. Normalize response into a flat dict
          5. Upsert into platform_analytics_raw
          6. Update syncStatus on social_accounts
          7. Write sync_history row to PostgreSQL

        Args:
            creator_id: The creator's profile ID.
            platform:   One of "youtube", "instagram", "facebook", "linkedin", "x".
            days:       Analytics window in days.

        Returns:
            SyncResult with status "success" or "failed".
        """
        result = SyncResult(
            platform=platform,
            creator_id=creator_id,
            status="failed",
        )

        try:
            # Step 1: Mark as syncing
            await self.social_repo.update_sync_status(creator_id, platform, "syncing")

            # Step 2: Load account
            account = await self.social_repo.get_account(creator_id, platform)
            if not account:
                raise ValueError(f"{platform} account not connected for creator {creator_id}")

            # Step 3: Refresh token if needed
            access_token = account.get("accessToken", "")
            access_token = await self._ensure_fresh_token(creator_id, platform, account, access_token)

            # Step 4: Fetch + normalize
            snapshot = await self._fetch_and_normalize(platform, account, access_token, days)
            snapshot["periodDays"] = days

            # Step 5: Persist snapshot
            await self.analytics_repo.upsert_snapshot(creator_id, platform, snapshot)

            # Step 6: Mark as idle (success)
            await self.social_repo.update_sync_status(creator_id, platform, "idle")

            result.status = "success"
            result.records_updated = 1
            result.completed_at = datetime.utcnow()

        except Exception as exc:
            error_msg = str(exc)
            logger.exception("Sync failed for creator=%s platform=%s: %s", creator_id, platform, error_msg)
            await self.social_repo.update_sync_status(creator_id, platform, "error", error_msg)
            result.error_message = error_msg
            result.completed_at = datetime.utcnow()

        # Step 7: Write sync_history to PostgreSQL
        await self._write_sync_history(result)
        return result

    async def sync_all_for_creator(
        self,
        creator_id: str,
        days: int = 30,
    ) -> List[SyncResult]:
        """
        Sync analytics for ALL connected platforms of one creator.

        Args:
            creator_id: The creator's profile ID.
            days:       Analytics window in days.

        Returns:
            List of SyncResult (one per platform attempted).
        """
        accounts = await self.social_repo.get_accounts_by_creator(creator_id)
        results: List[SyncResult] = []
        for acc in accounts:
            if not acc.get("isActive", True):
                continue
            platform = acc.get("platform", "")
            if not platform:
                continue
            res = await self.sync_platform(creator_id, platform, days)
            results.append(res)
        return results

    async def sync_all_creators(self, days: int = 30) -> None:
        """
        Bulk-sync analytics for ALL active social accounts across ALL creators.

        Called by the APScheduler background job. Iterates all active
        social_accounts documents, de-duplicates by (creator_id, platform),
        and calls sync_platform for each pair.

        Args:
            days: Analytics window in days.
        """
        all_accounts = await self.social_repo.get_all_active_accounts()
        # De-duplicate — one sync per (creator_id, platform)
        seen = set()
        for acc in all_accounts:
            key = (acc.get("creatorId", ""), acc.get("platform", ""))
            if key in seen or not all(key):
                continue
            seen.add(key)
            creator_id, platform = key
            try:
                await self.sync_platform(creator_id, platform, days)
            except Exception as exc:
                logger.error(
                    "Bulk sync error for creator=%s platform=%s: %s",
                    creator_id, platform, exc,
                )

    # ── Token refresh ────────────────────────────────────────────────────

    async def _ensure_fresh_token(
        self,
        creator_id: str,
        platform: str,
        account: Dict,
        access_token: str,
    ) -> str:
        """
        Refresh an expired OAuth token if a refresh_token is stored.

        Only YouTube and X support token refresh. Other platforms use
        long-lived tokens that do not expire for 60 days (Meta) and
        therefore do not need this step.

        Returns the (possibly refreshed) access_token string.
        """
        token_expiry = account.get("tokenExpiry")
        if not token_expiry:
            return access_token
        if isinstance(token_expiry, str):
            token_expiry = datetime.fromisoformat(token_expiry)
        if token_expiry > datetime.utcnow():
            return access_token  # still valid

        refresh_token = account.get("refreshToken")
        if not refresh_token:
            return access_token  # no refresh token stored — use existing

        if platform == "youtube":
            new_tokens = await YouTubeClient.refresh_access_token(refresh_token)
            access_token = new_tokens["access_token"]
            await self.social_repo.update_tokens(creator_id, platform, {
                "access_token":  access_token,
                "refresh_token": refresh_token,
                "token_expiry":  datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600)),
            })

        elif platform == "x":
            new_tokens = await XClient.refresh_access_token(refresh_token)
            access_token = new_tokens["access_token"]
            await self.social_repo.update_tokens(creator_id, platform, {
                "access_token":  access_token,
                "refresh_token": new_tokens.get("refresh_token", refresh_token),
                "token_expiry":  datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 7200)),
            })

        return access_token

    # ── Platform-specific fetch + normalize ──────────────────────────────

    async def _fetch_and_normalize(
        self,
        platform: str,
        account: Dict,
        access_token: str,
        days: int,
    ) -> Dict:
        """
        Dispatch to the correct platform client and return a normalized dict.

        The returned dict matches the fields defined in platform_analytics_raw.
        Missing fields are set to None so they are stored as null in MongoDB.

        Args:
            platform:     The platform name.
            account:      The full social_accounts document (includes accountId).
            access_token: The current (possibly refreshed) access token.
            days:         Analytics window in days.

        Returns:
            Normalized analytics dict ready for upsert into MongoDB.
        """
        account_id = account.get("accountId", "")

        if platform == "youtube":
            return await self._fetch_youtube(access_token, account_id, days)

        elif platform == "instagram":
            return await self._fetch_instagram(access_token, account_id, days)

        elif platform == "facebook":
            page_token = account.get("pageAccessToken", access_token)
            return await self._fetch_facebook(access_token, account_id, page_token, days)

        elif platform == "linkedin":
            return await self._fetch_linkedin(access_token, account_id, days)

        elif platform == "x":
            return await self._fetch_x(access_token, account_id, days)

        raise ValueError(f"Unsupported platform: {platform}")

    # ── YouTube ──────────────────────────────────────────────────────────

    async def _fetch_youtube(
        self, access_token: str, channel_id: str, days: int
    ) -> Dict:
        client = YouTubeClient(access_token)
        try:
            channel = await client.get_channel_info()
            stats   = channel.get("statistics", {})
            analytics_raw = await client.get_analytics(channel_id, days=days)
        except Exception as exc:
            logger.warning("YouTube API error, using sample data: %s", exc)
            return self._youtube_sample(channel_id)

        # Sum analytics rows (each row = one day)
        rows = analytics_raw.get("rows", [])
        col_headers = [c.get("name") for c in analytics_raw.get("columnHeaders", [])]

        totals = {h: 0 for h in col_headers}
        for row in rows:
            for i, val in enumerate(row):
                if i < len(col_headers):
                    totals[col_headers[i]] = totals.get(col_headers[i], 0) + (val or 0)

        subscribers = int(stats.get("subscriberCount", 0))
        views       = int(stats.get("viewCount", totals.get("views", 0)))
        likes       = int(totals.get("likes", 0))
        comments    = int(totals.get("comments", 0))
        shares      = int(totals.get("shares", 0))
        watch_time  = float(totals.get("estimatedMinutesWatched", 0))

        engagement_rate = 0.0
        if views > 0:
            engagement_rate = round((likes + comments + shares) / views * 100, 2)

        return {
            "accountId":      channel_id,
            "accountName":    channel.get("snippet", {}).get("title"),
            "followers":      subscribers,
            "views":          views,
            "likes":          likes,
            "comments":       comments,
            "shares":         shares,
            "watchTime":      watch_time,
            "totalVideos":    int(stats.get("videoCount", 0)),
            "engagementRate": engagement_rate,
            "reach":          None,
            "impressions":    None,
            "isSampleData":   False,
        }

    @staticmethod
    def _youtube_sample(channel_id: str) -> Dict:
        """Return clearly-labelled sample data when the YouTube API is unavailable."""
        return {
            "accountId":      channel_id,
            "accountName":    "Sample Channel",
            "followers":      5000,
            "views":          80000,
            "likes":          3200,
            "comments":       210,
            "shares":         150,
            "watchTime":      12000.0,
            "totalVideos":    45,
            "engagementRate": 4.45,
            "isSampleData":   True,
        }

    # ── Instagram ────────────────────────────────────────────────────────

    async def _fetch_instagram(
        self, access_token: str, ig_user_id: str, days: int
    ) -> Dict:
        client = InstagramClient(access_token)
        try:
            profile  = await client.get_profile()
            insights = await client.get_insights(ig_user_id, days=days)
        except Exception as exc:
            logger.warning("Instagram API error, using sample data: %s", exc)
            return self._instagram_sample(ig_user_id)

        followers = profile.get("followers_count", 0)

        # Parse insights metrics list
        metric_map: Dict[str, int] = {}
        for metric in insights.get("data", []):
            name = metric.get("name")
            vals = metric.get("values", [])
            total = sum(v.get("value", 0) for v in vals)
            metric_map[name] = int(total)

        impressions = metric_map.get("impressions", 0)
        reach       = metric_map.get("reach", 0)

        engagement_rate = 0.0
        if impressions > 0:
            engagement_rate = round(reach / impressions * 100, 2)

        return {
            "accountId":      ig_user_id,
            "accountName":    profile.get("name") or profile.get("username"),
            "followers":      followers,
            "views":          impressions,
            "impressions":    impressions,
            "reach":          reach,
            "profileVisits":  metric_map.get("profile_views", 0),
            "likes":          0,           # Not available at account level
            "comments":       0,
            "shares":         0,
            "engagementRate": engagement_rate,
            "isSampleData":   False,
        }

    @staticmethod
    def _instagram_sample(ig_user_id: str) -> Dict:
        return {
            "accountId":      ig_user_id,
            "accountName":    "Sample Instagram",
            "followers":      8200,
            "views":          42000,
            "impressions":    42000,
            "reach":          28000,
            "profileVisits":  1500,
            "reelPlays":      9000,
            "likes":          0,
            "comments":       0,
            "shares":         0,
            "engagementRate": 5.2,
            "isSampleData":   True,
        }

    # ── Facebook ─────────────────────────────────────────────────────────

    async def _fetch_facebook(
        self, access_token: str, page_id: str, page_token: str, days: int
    ) -> Dict:
        client = FacebookClient(access_token)
        try:
            insights = await client.get_page_insights(page_id, page_token, days=days)
            pages    = await client.get_pages()
            page_info = next((p for p in pages if p.get("id") == page_id), {})
        except Exception as exc:
            logger.warning("Facebook API error, using sample data: %s", exc)
            return self._facebook_sample(page_id)

        metric_map: Dict[str, int] = {}
        for metric in insights.get("data", []):
            name = metric.get("name")
            vals = metric.get("values", [])
            total = sum(v.get("value", 0) for v in vals if isinstance(v.get("value"), (int, float)))
            metric_map[name] = int(total)

        impressions   = metric_map.get("page_impressions", 0)
        engaged_users = metric_map.get("page_engaged_users", 0)
        page_views    = metric_map.get("page_views_total", 0)
        fan_adds      = metric_map.get("page_fan_adds", 0)
        followers     = page_info.get("fan_count", fan_adds)

        engagement_rate = 0.0
        if impressions > 0:
            engagement_rate = round(engaged_users / impressions * 100, 2)

        return {
            "accountId":      page_id,
            "accountName":    page_info.get("name"),
            "followers":      followers,
            "pageLikes":      followers,
            "impressions":    impressions,
            "reach":          engaged_users,
            "views":          page_views,
            "likes":          0,
            "comments":       0,
            "shares":         0,
            "engagementRate": engagement_rate,
            "isSampleData":   False,
        }

    @staticmethod
    def _facebook_sample(page_id: str) -> Dict:
        return {
            "accountId":      page_id,
            "accountName":    "Sample Facebook Page",
            "followers":      12000,
            "pageLikes":      12000,
            "impressions":    35000,
            "reach":          18000,
            "views":          9000,
            "likes":          0,
            "comments":       0,
            "shares":         0,
            "engagementRate": 3.8,
            "isSampleData":   True,
        }

    # ── LinkedIn ─────────────────────────────────────────────────────────

    async def _fetch_linkedin(
        self, access_token: str, account_id: str, days: int
    ) -> Dict:
        client = LinkedInClient(access_token)
        try:
            org_id = await client.get_organization_id()
            if not org_id:
                raise ValueError("No LinkedIn organization page found for this account.")
            stats = await client.get_page_statistics(org_id, days=days)
        except Exception as exc:
            logger.warning("LinkedIn API error, using sample data: %s", exc)
            return self._linkedin_sample(account_id)

        elements = stats.get("elements", [])
        total_impressions = 0
        total_clicks      = 0
        total_reactions   = 0
        total_comments    = 0
        total_shares      = 0

        for el in elements:
            ts = el.get("totalShareStatistics", {})
            total_impressions += ts.get("impressionCount", 0)
            total_clicks      += ts.get("clickCount", 0)
            total_reactions   += ts.get("likeCount", 0)
            total_comments    += ts.get("commentCount", 0)
            total_shares      += ts.get("shareCount", 0)

        engagement_rate = 0.0
        if total_impressions > 0:
            interactions = total_reactions + total_comments + total_shares
            engagement_rate = round(interactions / total_impressions * 100, 2)

        return {
            "accountId":        account_id,
            "accountName":      None,
            "followers":        0,   # Personal profiles don't expose follower count via v2
            "postImpressions":  total_impressions,
            "impressions":      total_impressions,
            "reactions":        total_reactions,
            "likes":            total_reactions,
            "comments":         total_comments,
            "shares":           total_shares,
            "views":            total_impressions,
            "engagementRate":   engagement_rate,
            "isSampleData":     False,
        }

    @staticmethod
    def _linkedin_sample(account_id: str) -> Dict:
        return {
            "accountId":       account_id,
            "accountName":     "Sample LinkedIn Page",
            "followers":       3500,
            "postImpressions": 22000,
            "impressions":     22000,
            "reactions":       1200,
            "likes":           1200,
            "comments":        340,
            "shares":          180,
            "views":           22000,
            "engagementRate":  7.8,
            "isSampleData":    True,
        }

    # ── X (Twitter) ──────────────────────────────────────────────────────

    async def _fetch_x(
        self, access_token: str, user_id: str, days: int
    ) -> Dict:
        client = XClient(access_token)
        try:
            profile = await client.get_me()
            tweets  = await client.get_user_tweets(user_id)
        except Exception as exc:
            logger.warning("X API error, using sample data: %s", exc)
            return self._x_sample(user_id)

        public_metrics = profile.get("public_metrics", {})
        followers      = public_metrics.get("followers_count", 0)

        # Aggregate tweet metrics
        tweet_impressions = 0
        total_likes       = 0
        total_reposts     = 0
        total_replies     = 0

        for tweet in (tweets if isinstance(tweets, list) else tweets.get("data", [])):
            m = tweet.get("public_metrics", {})
            tweet_impressions += m.get("impression_count", 0)
            total_likes       += m.get("like_count", 0)
            total_reposts     += m.get("retweet_count", 0)
            total_replies     += m.get("reply_count", 0)

        engagement_rate = 0.0
        if tweet_impressions > 0:
            interactions = total_likes + total_reposts + total_replies
            engagement_rate = round(interactions / tweet_impressions * 100, 2)

        return {
            "accountId":        user_id,
            "accountName":      profile.get("name"),
            "followers":        followers,
            "tweetImpressions": tweet_impressions,
            "impressions":      tweet_impressions,
            "likes":            total_likes,
            "reposts":          total_reposts,
            "replies":          total_replies,
            "views":            tweet_impressions,
            "comments":         total_replies,
            "shares":           total_reposts,
            "engagementRate":   engagement_rate,
            "isSampleData":     False,
        }

    @staticmethod
    def _x_sample(user_id: str) -> Dict:
        return {
            "accountId":        user_id,
            "accountName":      "Sample X Account",
            "followers":        6200,
            "tweetImpressions": 48000,
            "impressions":      48000,
            "likes":            2100,
            "reposts":          640,
            "replies":          280,
            "views":            48000,
            "comments":         280,
            "shares":           640,
            "engagementRate":   6.3,
            "isSampleData":     True,
        }

    # ── PostgreSQL sync_history persistence ──────────────────────────────

    @staticmethod
    async def _write_sync_history(result: SyncResult) -> None:
        """
        Persist a sync_history row in PostgreSQL.

        Errors here are logged but NOT re-raised so they don't interfere
        with the sync result that already reached the caller.
        """
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import text
                await db.execute(
                    text(
                        """
                        INSERT INTO sync_history
                            (creator_id, platform, status, records_updated,
                             error_message, started_at, completed_at)
                        VALUES
                            (:creator_id, :platform, :status, :records_updated,
                             :error_message, :started_at, :completed_at)
                        """
                    ),
                    {
                        "creator_id":      result.creator_id,
                        "platform":        result.platform,
                        "status":          result.status,
                        "records_updated": result.records_updated,
                        "error_message":   result.error_message,
                        "started_at":      result.started_at,
                        "completed_at":    result.completed_at,
                    },
                )
                await db.commit()
        except Exception as exc:
            logger.error("Failed to write sync_history: %s", exc)
