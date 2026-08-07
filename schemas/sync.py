"""
schemas/sync.py — Pydantic schemas for analytics synchronization.

Defines response models for manual sync triggers, sync status queries,
and sync history records stored in the PostgreSQL sync_history table.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SyncStatusItem(BaseModel):
    """Current sync status for one connected platform."""
    platform: str
    accountName: Optional[str] = None
    syncStatus: str                        # "idle" | "syncing" | "error"
    lastSyncedAt: Optional[datetime] = None
    syncErrorMessage: Optional[str] = None
    isActive: bool = True


class SyncStatusResponse(BaseModel):
    """Aggregated sync status for all connected platforms of a creator."""
    creatorId: str
    platforms: List[SyncStatusItem]
    queriedAt: datetime


class SyncTriggerResponse(BaseModel):
    """Response returned after triggering a manual sync for one platform."""
    platform: str
    status: str                            # "success" | "failed"
    recordsUpdated: int = 0
    message: Optional[str] = None
    startedAt: datetime
    completedAt: Optional[datetime] = None
    errorMessage: Optional[str] = None


class SyncAllResponse(BaseModel):
    """Response after triggering sync for all connected platforms."""
    synced: List[str]                      # platforms that succeeded
    failed: List[dict]                     # [{"platform": "...", "error": "..."}]
    syncedAt: datetime
    totalRecordsUpdated: int = 0


class SyncHistoryRecord(BaseModel):
    """One row from the PostgreSQL sync_history table."""
    id: int
    platform: str
    status: str
    recordsUpdated: int = 0
    startedAt: datetime
    completedAt: Optional[datetime] = None
    errorMessage: Optional[str] = None


class SyncHistoryResponse(BaseModel):
    """Paginated list of sync history records."""
    creatorId: str
    records: List[SyncHistoryRecord]
    total: int
