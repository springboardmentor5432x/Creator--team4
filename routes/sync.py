"""
routes/sync.py — Manual Sync Trigger & Sync History Endpoints

Provides endpoints for:
  - Manually triggering analytics sync (one platform or all)
  - Checking current sync status per platform
  - Viewing sync history from PostgreSQL
  - Checking scheduler status (admin only)

Permission matrix:
  social:analytics — Admin ✅, Agency ✅, Creator Own, Marketing ✅

Endpoints:
  POST  /api/sync/{platform}         → Manually sync one platform
  POST  /api/sync/all                → Manually sync all connected platforms
  GET   /api/sync/status             → Current sync status for all accounts
  GET   /api/sync/history            → Sync history from PostgreSQL (last N records)
  GET   /api/sync/scheduler          → Scheduler status (admin only)
"""

import logging
from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text

from authorization import require_any_permission, require_admin
from permissions import Permission
from models import UserModel
from database import AsyncSessionLocal
from services.sync_service import SyncService
from services.scheduler import get_scheduler_status
from repositories.social_media_repository import SocialMediaRepository
from schemas.sync import (
    SyncTriggerResponse,
    SyncAllResponse,
    SyncStatusResponse,
    SyncStatusItem,
    SyncHistoryRecord,
    SyncHistoryResponse,
)
from schemas.social_media import PlatformEnum

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sync", tags=["Analytics Sync"])


def _get_creator_id(current_user: UserModel) -> str:
    if hasattr(current_user, "creator_profile") and current_user.creator_profile:
        return current_user.creator_profile.id
    raise HTTPException(status_code=403, detail="Not authorized as a creator")


def _get_sync_service() -> SyncService:
    return SyncService()


def _get_social_repo() -> SocialMediaRepository:
    return SocialMediaRepository()


# ── Manual Sync ──────────────────────────────────────────────────────────


@router.post("/{platform}", response_model=SyncTriggerResponse)
async def sync_single_platform(
    platform: PlatformEnum,
    days: int = Query(30, ge=1, le=90, description="Analytics window in days"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: SyncService = Depends(_get_sync_service),
):
    """
    Manually trigger an analytics sync for one connected platform.

    Fetches the latest analytics from the platform API, normalizes
    them, and stores the result in MongoDB. Also writes a sync_history
    row to PostgreSQL.

    This is useful for immediately refreshing data without waiting for
    the scheduled 6-hour sync cycle.
    """
    creator_id = _get_creator_id(current_user)
    result = await service.sync_platform(creator_id, platform.value, days=days)
    return SyncTriggerResponse(
        platform=result.platform,
        status=result.status,
        recordsUpdated=result.records_updated,
        message=result.error_message or f"Sync {result.status}.",
        startedAt=result.started_at,
        completedAt=result.completed_at,
        errorMessage=result.error_message,
    )


@router.post("/all", response_model=SyncAllResponse)
async def sync_all_platforms(
    days: int = Query(30, ge=1, le=90, description="Analytics window in days"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    service: SyncService = Depends(_get_sync_service),
):
    """
    Manually trigger analytics sync for ALL connected platforms.

    Iterates every active social account linked to the authenticated creator
    and syncs each one. Returns a summary of successes and failures.
    """
    creator_id = _get_creator_id(current_user)
    results = await service.sync_all_for_creator(creator_id, days=days)

    synced  = [r.platform for r in results if r.status == "success"]
    failed  = [
        {"platform": r.platform, "error": r.error_message}
        for r in results if r.status == "failed"
    ]
    total_records = sum(r.records_updated for r in results)

    return SyncAllResponse(
        synced=synced,
        failed=failed,
        syncedAt=datetime.utcnow(),
        totalRecordsUpdated=total_records,
    )


# ── Sync Status ───────────────────────────────────────────────────────────


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
    repo: SocialMediaRepository = Depends(_get_social_repo),
):
    """
    Return the current sync status for all connected social accounts.

    Shows per-platform: sync state, last synced time, and last error (if any).
    This data comes from the syncStatus / lastSyncedAt fields on each
    social_accounts document in MongoDB.
    """
    creator_id = _get_creator_id(current_user)
    accounts = await repo.get_accounts_by_creator(creator_id)

    items: List[SyncStatusItem] = []
    for acc in accounts:
        # Strip tokens before exposing
        items.append(SyncStatusItem(
            platform=acc.get("platform", ""),
            accountName=acc.get("accountName"),
            syncStatus=acc.get("syncStatus", "idle"),
            lastSyncedAt=acc.get("lastSyncedAt"),
            syncErrorMessage=acc.get("syncErrorMessage"),
            isActive=acc.get("isActive", True),
        ))

    return SyncStatusResponse(
        creatorId=creator_id,
        platforms=items,
        queriedAt=datetime.utcnow(),
    )


# ── Sync History ──────────────────────────────────────────────────────────


@router.get("/history", response_model=SyncHistoryResponse)
async def get_sync_history(
    platform: str = Query(None, description="Filter by platform (optional)"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    current_user: UserModel = Depends(
        require_any_permission(Permission.ANALYTICS_VIEW, Permission.ANALYTICS_VIEW_OWN)
    ),
):
    """
    Return the most recent analytics sync history records from PostgreSQL.

    Records are ordered newest-first. Each record shows the platform,
    outcome (success/failed), number of records updated, and timestamps.

    Optionally filter by platform name.
    """
    creator_id = _get_creator_id(current_user)

    base_query = """
        SELECT id, platform, status, records_updated,
               error_message, started_at, completed_at
        FROM sync_history
        WHERE creator_id = :creator_id
    """
    params: Dict = {"creator_id": creator_id, "limit": limit}

    if platform:
        base_query += " AND platform = :platform"
        params["platform"] = platform

    base_query += " ORDER BY started_at DESC LIMIT :limit"

    count_query = "SELECT COUNT(*) FROM sync_history WHERE creator_id = :creator_id"
    count_params: Dict = {"creator_id": creator_id}
    if platform:
        count_query += " AND platform = :platform"
        count_params["platform"] = platform

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(text(base_query), params)).fetchall()
        total_count = (await db.execute(text(count_query), count_params)).scalar()

    records = [
        SyncHistoryRecord(
            id=row.id,
            platform=row.platform,
            status=row.status,
            recordsUpdated=row.records_updated or 0,
            startedAt=row.started_at,
            completedAt=row.completed_at,
            errorMessage=row.error_message,
        )
        for row in rows
    ]

    return SyncHistoryResponse(
        creatorId=creator_id,
        records=records,
        total=total_count or 0,
    )


# ── Scheduler Status (admin) ──────────────────────────────────────────────


@router.get("/scheduler", response_model=Dict)
async def get_scheduler_info(
    current_user: UserModel = Depends(require_admin()),
):
    """
    Return current APScheduler status and next job run times.

    Admin-only endpoint for monitoring the background sync scheduler.
    """
    return get_scheduler_status()
