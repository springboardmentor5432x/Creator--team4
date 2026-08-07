"""
services/notification_service.py — Notification Center & Milestone Alert Handler

Manages:
  - Creating and retrieving in-app notifications
  - Performance milestone alerts (views, engagement, followers)
  - Revenue notification alerts (sponsorships, commissions, revenue milestones)
  - Automated trigger evaluations against creator analytics
"""

import logging
from typing import List, Dict, Any, Optional
from repositories.notification_repository import NotificationRepository
from repositories.platform_analytics_repository import PlatformAnalyticsRepository
from services.email_service import EmailService

logger = logging.getLogger(__name__)


class NotificationService:
    """Business logic for notifications and automated milestone alerts."""

    def __init__(self):
        self.notification_repo = NotificationRepository()
        self.analytics_repo = PlatformAnalyticsRepository()
        self.email_service = EmailService()

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        creator_id: Optional[str] = None,
        link_url: Optional[str] = None,
        send_email: bool = False,
        user_email: Optional[str] = None,
    ) -> int:
        """Create an in-app notification and optionally dispatch an email."""
        notif_id = await self.notification_repo.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            creator_id=creator_id,
            link_url=link_url,
        )

        if send_email and user_email:
            await self.email_service.send_alert_email(
                to_email=user_email,
                alert_title=title,
                alert_message=message,
            )

        return notif_id

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        notification_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Fetch user notifications with unread badge count."""
        items = await self.notification_repo.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            notification_type=notification_type,
            limit=limit,
            offset=offset,
        )
        total = await self.notification_repo.get_total_count(user_id)
        unread = await self.notification_repo.get_unread_count(user_id)

        return {
            "notifications": items,
            "total": total,
            "unreadCount": unread,
        }

    async def mark_as_read(self, notification_id: int, user_id: str) -> bool:
        """Mark single notification as read."""
        return await self.notification_repo.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read."""
        return await self.notification_repo.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: int, user_id: str) -> bool:
        """Delete notification."""
        return await self.notification_repo.delete_notification(notification_id, user_id)

    # ── Automated Milestone Checkers ──────────────────────────────────────

    async def check_performance_milestones(self, user_id: str, creator_id: str) -> List[int]:
        """
        Evaluates current analytics against milestone thresholds and generates alerts.

        Triggers:
          - Follower Milestone (e.g. 1K, 5K, 10K, 50K, 100K)
          - Total Views Milestone (e.g. 10K, 50K, 100K, 500K, 1M)
          - High Engagement Rate Alert (> 5%)
        """
        created_notif_ids = []
        totals = await self.analytics_repo.get_multi_platform_totals(creator_id)

        total_followers = totals.get("totalFollowers", 0)
        total_views = totals.get("totalViews", 0)
        avg_engagement = totals.get("averageEngagementRate", 0.0)

        # 1. Follower Milestones Check
        follower_thresholds = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        for t in follower_thresholds:
            if total_followers >= t:
                # Check if we should notify (simple threshold match logic)
                title = "🎉 Follower Milestone Achieved!"
                msg = f"Congratulations! Your total connected followers have crossed {t:,}!"
                notif_id = await self.create_notification(
                    user_id=user_id,
                    creator_id=creator_id,
                    title=title,
                    message=msg,
                    notification_type="performance_milestone",
                    link_url="/analytics/overview",
                )
                created_notif_ids.append(notif_id)
                break  # Alert for highest achieved

        # 2. View Milestones Check
        view_thresholds = [10000, 50000, 100000, 500000, 1000000]
        for v in view_thresholds:
            if total_views >= v:
                title = "🚀 Views Milestone Reached!"
                msg = f"Awesome progress! Your total content views reached {v:,} views across platforms."
                notif_id = await self.create_notification(
                    user_id=user_id,
                    creator_id=creator_id,
                    title=title,
                    message=msg,
                    notification_type="performance_milestone",
                    link_url="/analytics/overview",
                )
                created_notif_ids.append(notif_id)
                break

        # 3. High Engagement Spike
        if avg_engagement > 5.0:
            title = "🔥 High Engagement Spike!"
            msg = f"Your average engagement rate reached {avg_engagement:.2f}%, significantly outperforming average benchmarks!"
            notif_id = await self.create_notification(
                user_id=user_id,
                creator_id=creator_id,
                title=title,
                message=msg,
                notification_type="performance_milestone",
                link_url="/analytics/overview",
            )
            created_notif_ids.append(notif_id)

        return created_notif_ids

    async def notify_revenue_event(
        self,
        user_id: str,
        creator_id: str,
        event_type: str,
        amount: float,
        description: str,
        user_email: Optional[str] = None,
    ) -> int:
        """
        Creates notifications for financial events:
          - Sponsorship Payment Received
          - Affiliate Commission Updated
          - Monthly Revenue Report Generated
          - Revenue Milestone Achieved
        """
        title = f"💰 Revenue Update: {event_type.replace('_', ' ').capitalize()}"
        msg = f"{description} Amount: ${amount:,.2f}"

        return await self.create_notification(
            user_id=user_id,
            creator_id=creator_id,
            title=title,
            message=msg,
            notification_type="revenue_update",
            link_url="/revenue",
            send_email=True,
            user_email=user_email,
        )
