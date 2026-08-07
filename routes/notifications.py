"""
routes/notifications.py — Notification Center Endpoints

Provides endpoints for:
  - Fetching user in-app notifications
  - Unread count badge query
  - Marking notifications as read (single or all)
  - Deleting notifications
  - Manual milestone check trigger
"""

import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from authorization import get_current_active_user
from models import UserModel
from services.notification_service import NotificationService
from schemas.notifications import (
    NotificationListResponse,
    UnreadCountResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notification Center"])


def _get_notif_service() -> NotificationService:
    return NotificationService()


def _get_user_id(current_user: UserModel) -> str:
    return str(getattr(current_user, "id", ""))


def _get_creator_id(current_user: UserModel) -> Optional[str]:
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    return None


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False, description="Filter to only unread notifications"),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserModel = Depends(get_current_active_user),
    service: NotificationService = Depends(_get_notif_service),
):
    """Fetch notifications for the authenticated user."""
    user_id = _get_user_id(current_user)
    return await service.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        notification_type=type,
        limit=limit,
        offset=offset,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: UserModel = Depends(get_current_active_user),
    service: NotificationService = Depends(_get_notif_service),
):
    """Get quick unread count for navbar badge indicator."""
    user_id = _get_user_id(current_user)
    count = await service.notification_repo.get_unread_count(user_id)
    return UnreadCountResponse(unreadCount=count)


@router.patch("/{id}/read", response_model=Dict[str, Any])
async def mark_notification_read(
    id: int,
    current_user: UserModel = Depends(get_current_active_user),
    service: NotificationService = Depends(_get_notif_service),
):
    """Mark a single notification as read."""
    user_id = _get_user_id(current_user)
    success = await service.mark_as_read(id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read", "id": id}


@router.patch("/read-all", response_model=Dict[str, Any])
async def mark_all_notifications_read(
    current_user: UserModel = Depends(get_current_active_user),
    service: NotificationService = Depends(_get_notif_service),
):
    """Mark all notifications as read for the authenticated user."""
    user_id = _get_user_id(current_user)
    count = await service.mark_all_as_read(user_id)
    return {"message": "All notifications marked as read", "updatedCount": count}


@router.delete("/{id}", response_model=Dict[str, Any])
async def delete_notification(
    id: int,
    current_user: UserModel = Depends(get_current_active_user),
    service: NotificationService = Depends(_get_notif_service),
):
    """Delete a notification."""
    user_id = _get_user_id(current_user)
    success = await service.delete_notification(id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted", "id": id}


@router.post("/trigger-milestones", response_model=Dict[str, Any])
async def trigger_milestone_check(
    current_user: UserModel = Depends(get_current_active_user),
    service: NotificationService = Depends(_get_notif_service),
):
    """Manually trigger milestone threshold check for the current creator."""
    user_id = _get_user_id(current_user)
    creator_id = _get_creator_id(current_user) or user_id
    notif_ids = await service.check_performance_milestones(user_id=user_id, creator_id=creator_id)
    return {"message": "Milestone check complete", "newNotifications": len(notif_ids), "notificationIds": notif_ids}
