"""
services/scheduler.py — Background Analytics Sync Scheduler

Uses APScheduler's AsyncIOScheduler to run periodic analytics syncs
without blocking the main FastAPI event loop.

Schedule:
  - analytics_sync job: every 6 hours, syncs all active creator accounts

Lifecycle:
  - start_scheduler()  → called from main.py on_startup
  - stop_scheduler()   → called from main.py on_shutdown
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Module-level scheduler instance — shared across the app
_scheduler: AsyncIOScheduler = AsyncIOScheduler()


# ---------------------------------------------------------------------------
# Job functions
# ---------------------------------------------------------------------------

async def _sync_all_creators_job() -> None:
    """
    APScheduler job: runs every 6 hours to sync analytics for all creators.

    Errors are caught and logged so a single platform failure does NOT
    stop the scheduler from running on the next tick.
    """
    logger.info("[Scheduler] Starting scheduled analytics sync for all creators...")
    try:
        from services.sync_service import SyncService
        service = SyncService()
        await service.sync_all_creators(days=30)
        logger.info("[Scheduler] Scheduled sync completed.")
    except Exception as exc:
        logger.error("[Scheduler] Sync job failed: %s", exc)


async def _weekly_reports_job() -> None:
    """APScheduler job: auto-generates weekly performance reports for creators."""
    logger.info("[Scheduler] Starting scheduled weekly performance report generation...")
    try:
        from repositories.social_media_repository import SocialMediaRepository
        from services.report_service import ReportService

        social_repo = SocialMediaRepository()
        report_service = ReportService()
        accounts = await social_repo.get_all_active_accounts()

        creators = set(acc.get("creatorId") for acc in accounts if acc.get("creatorId"))
        for creator_id in creators:
            try:
                await report_service.generate_report(
                    creator_id=creator_id,
                    report_type="weekly",
                    send_email=True,
                )
            except Exception as e:
                logger.error("[Scheduler] Failed weekly report for creator=%s: %s", creator_id, e)
        logger.info("[Scheduler] Scheduled weekly reports completed.")
    except Exception as exc:
        logger.error("[Scheduler] Weekly report job error: %s", exc)


async def _milestone_check_job() -> None:
    """APScheduler job: periodic milestone check for follower/view/engagement alerts."""
    logger.info("[Scheduler] Starting periodic milestone check...")
    try:
        from repositories.social_media_repository import SocialMediaRepository
        from services.notification_service import NotificationService

        social_repo = SocialMediaRepository()
        notif_service = NotificationService()
        accounts = await social_repo.get_all_active_accounts()

        creators = set(acc.get("creatorId") for acc in accounts if acc.get("creatorId"))
        for creator_id in creators:
            try:
                await notif_service.check_performance_milestones(user_id=creator_id, creator_id=creator_id)
            except Exception as e:
                logger.error("[Scheduler] Failed milestone check for creator=%s: %s", creator_id, e)
        logger.info("[Scheduler] Periodic milestone check completed.")
    except Exception as exc:
        logger.error("[Scheduler] Milestone check job error: %s", exc)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

async def start_scheduler() -> None:
    """
    Start the background scheduler.

    Called once from main.py on_startup. Safe to call multiple times
    (APScheduler ignores duplicate start calls when already running).
    """
    if _scheduler.running:
        logger.info("[Scheduler] Already running, skipping start.")
        return

    _scheduler.add_job(
        _sync_all_creators_job,
        trigger=IntervalTrigger(hours=6),
        id="analytics_sync",
        name="Sync all creator analytics",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    _scheduler.add_job(
        _weekly_reports_job,
        trigger=IntervalTrigger(days=7),
        id="weekly_reports",
        name="Generate weekly reports",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    _scheduler.add_job(
        _milestone_check_job,
        trigger=IntervalTrigger(hours=12),
        id="milestone_checker",
        name="Check performance milestones",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    _scheduler.start()
    logger.info(
        "[Scheduler] Started. Sync, report generation, and milestone checker jobs active."
    )


def stop_scheduler() -> None:
    """
    Gracefully stop the background scheduler.

    Called from main.py on_shutdown. Waits for currently running jobs
    to finish before stopping (wait=True is the default).
    """
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped.")


def get_scheduler_status() -> dict:
    """
    Return a summary of the scheduler's current state.

    Used by the /api/sync/scheduler-status admin endpoint.
    """
    if not _scheduler.running:
        return {"running": False, "jobs": []}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id":       job.id,
            "name":     job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        })
    return {"running": True, "jobs": jobs}
