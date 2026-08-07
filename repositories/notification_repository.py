"""
repositories/notification_repository.py — PostgreSQL CRUD for notifications table

Handles storing and retrieving in-app notifications, marking items as read,
deleting notifications, and fetching unread counts.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
from database import AsyncSessionLocal


class NotificationRepository:
    """Data access layer for the notifications table in PostgreSQL."""

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        creator_id: Optional[str] = None,
        link_url: Optional[str] = None,
    ) -> int:
        """Create a new notification record."""
        query = """
            INSERT INTO notifications (user_id, creator_id, title, message, type, is_read, link_url, created_at)
            VALUES (:user_id, :creator_id, :title, :message, :type, FALSE, :link_url, :created_at)
            RETURNING id
        """
        now = datetime.utcnow()
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text(query),
                {
                    "user_id": user_id,
                    "creator_id": creator_id,
                    "title": title,
                    "message": message,
                    "type": notification_type,
                    "link_url": link_url,
                    "created_at": now,
                },
            )
            await db.commit()
            notification_id = result.scalar()
            return notification_id

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        notification_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Fetch notifications for a specific user with filtering."""
        query = """
            SELECT id, user_id, creator_id, title, message, type, is_read, link_url, created_at
            FROM notifications
            WHERE user_id = :user_id
        """
        params: Dict[str, Any] = {"user_id": user_id, "limit": limit, "offset": offset}

        if unread_only:
            query += " AND is_read = FALSE"
        if notification_type:
            query += " AND type = :type"
            params["type"] = notification_type

        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

        async with AsyncSessionLocal() as db:
            rows = (await db.execute(text(query), params)).fetchall()
            return [
                {
                    "id": row.id,
                    "userId": row.user_id,
                    "creatorId": row.creator_id,
                    "title": row.title,
                    "message": row.message,
                    "type": row.type,
                    "isRead": row.is_read,
                    "linkUrl": row.link_url,
                    "createdAt": row.created_at,
                }
                for row in rows
            ]

    async def get_unread_count(self, user_id: str) -> int:
        """Get total unread notification count for a user."""
        query = "SELECT COUNT(*) FROM notifications WHERE user_id = :user_id AND is_read = FALSE"
        async with AsyncSessionLocal() as db:
            count = (await db.execute(text(query), {"user_id": user_id})).scalar()
            return count or 0

    async def get_total_count(self, user_id: str) -> int:
        """Get total notification count for a user."""
        query = "SELECT COUNT(*) FROM notifications WHERE user_id = :user_id"
        async with AsyncSessionLocal() as db:
            count = (await db.execute(text(query), {"user_id": user_id})).scalar()
            return count or 0

    async def mark_as_read(self, notification_id: int, user_id: str) -> bool:
        """Mark a single notification as read."""
        query = """
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = :id AND user_id = :user_id
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(query), {"id": notification_id, "user_id": user_id})
            await db.commit()
            return result.rowcount > 0

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        query = """
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = :user_id AND is_read = FALSE
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(query), {"user_id": user_id})
            await db.commit()
            return result.rowcount

    async def delete_notification(self, notification_id: int, user_id: str) -> bool:
        """Delete a notification."""
        query = "DELETE FROM notifications WHERE id = :id AND user_id = :user_id"
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(query), {"id": notification_id, "user_id": user_id})
            await db.commit()
            return result.rowcount > 0
