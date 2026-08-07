"""
schemas/notifications.py — Pydantic schemas for Notification Center and Performance Alerts.

Models for:
  - Notification items
  - Paginated notification list response
  - Unread count response
  - Notification creation request
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class NotificationTypeEnum(str, Enum):
    PERFORMANCE_MILESTONE = "performance_milestone"
    REVENUE_UPDATE = "revenue_update"
    REPORT_GENERATED = "report_generated"
    SYSTEM_ALERT = "system_alert"


class NotificationCreateRequest(BaseModel):
    """Internal/Admin request to create a notification."""
    userId: str
    creatorId: Optional[str] = None
    title: str = Field(..., max_length=255)
    message: str
    type: NotificationTypeEnum
    linkUrl: Optional[str] = None


class NotificationItem(BaseModel):
    """Public representation of an in-app notification."""
    id: int
    userId: str
    creatorId: Optional[str] = None
    title: str
    message: str
    type: str
    isRead: bool
    linkUrl: Optional[str] = None
    createdAt: datetime


class NotificationListResponse(BaseModel):
    """Paginated response for the Notification Center UI."""
    notifications: List[NotificationItem]
    total: int
    unreadCount: int


class UnreadCountResponse(BaseModel):
    """Quick badge count endpoint response."""
    unreadCount: int
