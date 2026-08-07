"""
repositories/report_repository.py — Data access layer for Reports History and Snapshots

Dual database handler:
  - PostgreSQL `generated_reports`: Stores report metadata, date ranges, status, and file paths (PDF/Excel).
  - MongoDB `report_snapshots`: Stores full JSON report data payloads for instant UI preview.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy import text
from database import AsyncSessionLocal
from mongo.mongodb import get_database
from models.mongo import REPORT_SNAPSHOTS


class ReportRepository:
    """Repository handling generated_reports (PostgreSQL) and report_snapshots (MongoDB)."""

    # ── PostgreSQL: generated_reports ─────────────────────────────────────

    async def create_report_record(
        self,
        creator_id: str,
        report_name: str,
        report_type: str,
        period_label: str,
        start_date: date,
        end_date: date,
        pdf_path: Optional[str] = None,
        excel_path: Optional[str] = None,
        status: str = "generated",
    ) -> int:
        """Insert a metadata record into PostgreSQL generated_reports table."""
        query = """
            INSERT INTO generated_reports
                (creator_id, report_name, report_type, period_label, start_date, end_date, pdf_path, excel_path, status, created_at)
            VALUES
                (:creator_id, :report_name, :report_type, :period_label, :start_date, :end_date, :pdf_path, :excel_path, :status, :created_at)
            RETURNING id
        """
        now = datetime.utcnow()
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text(query),
                {
                    "creator_id": creator_id,
                    "report_name": report_name,
                    "report_type": report_type,
                    "period_label": period_label,
                    "start_date": start_date,
                    "end_date": end_date,
                    "pdf_path": pdf_path,
                    "excel_path": excel_path,
                    "status": status,
                    "created_at": now,
                },
            )
            await db.commit()
            report_id = result.scalar()
            return report_id

    async def update_report_files(
        self,
        report_id: int,
        pdf_path: Optional[str] = None,
        excel_path: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """Update file paths or status for a generated report record."""
        query = "UPDATE generated_reports SET "
        updates = []
        params: Dict[str, Any] = {"id": report_id}

        if pdf_path is not None:
            updates.append("pdf_path = :pdf_path")
            params["pdf_path"] = pdf_path
        if excel_path is not None:
            updates.append("excel_path = :excel_path")
            params["excel_path"] = excel_path
        if status is not None:
            updates.append("status = :status")
            params["status"] = status

        if not updates:
            return

        query += ", ".join(updates) + " WHERE id = :id"

        async with AsyncSessionLocal() as db:
            await db.execute(text(query), params)
            await db.commit()

    async def get_reports_by_creator(
        self,
        creator_id: str,
        report_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Fetch report history for a creator."""
        query = """
            SELECT id, creator_id, report_name, report_type, period_label,
                   start_date, end_date, pdf_path, excel_path, status, created_at
            FROM generated_reports
            WHERE creator_id = :creator_id
        """
        params: Dict[str, Any] = {"creator_id": creator_id, "limit": limit, "offset": offset}

        if report_type:
            query += " AND report_type = :report_type"
            params["report_type"] = report_type

        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

        async with AsyncSessionLocal() as db:
            rows = (await db.execute(text(query), params)).fetchall()
            return [
                {
                    "id": row.id,
                    "creatorId": row.creator_id,
                    "reportName": row.report_name,
                    "reportType": row.report_type,
                    "periodLabel": row.period_label,
                    "startDate": row.start_date,
                    "endDate": row.end_date,
                    "pdfPath": row.pdf_path,
                    "excelPath": row.excel_path,
                    "status": row.status,
                    "createdAt": row.created_at,
                }
                for row in rows
            ]

    async def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single report metadata by ID."""
        query = """
            SELECT id, creator_id, report_name, report_type, period_label,
                   start_date, end_date, pdf_path, excel_path, status, created_at
            FROM generated_reports
            WHERE id = :id
        """
        async with AsyncSessionLocal() as db:
            row = (await db.execute(text(query), {"id": report_id})).fetchone()
            if not row:
                return None
            return {
                "id": row.id,
                "creatorId": row.creator_id,
                "reportName": row.report_name,
                "reportType": row.report_type,
                "periodLabel": row.period_label,
                "startDate": row.start_date,
                "endDate": row.end_date,
                "pdfPath": row.pdf_path,
                "excelPath": row.excel_path,
                "status": row.status,
                "createdAt": row.created_at,
            }

    async def get_total_count(self, creator_id: str, report_type: Optional[str] = None) -> int:
        """Count total generated reports for a creator."""
        query = "SELECT COUNT(*) FROM generated_reports WHERE creator_id = :creator_id"
        params: Dict[str, Any] = {"creator_id": creator_id}
        if report_type:
            query += " AND report_type = :report_type"
            params["report_type"] = report_type

        async with AsyncSessionLocal() as db:
            count = (await db.execute(text(query), params)).scalar()
            return count or 0

    # ── MongoDB: report_snapshots ─────────────────────────────────────────

    async def save_report_snapshot(self, report_id: int, creator_id: str, data: Dict[str, Any]) -> None:
        """Upsert a report JSON payload snapshot in MongoDB."""
        db = get_database()
        doc = {
            "reportId": report_id,
            "creatorId": creator_id,
            "data": data,
            "createdAt": datetime.utcnow(),
        }
        await db[REPORT_SNAPSHOTS].update_one(
            {"reportId": report_id},
            {"$set": doc},
            upsert=True,
        )

    async def get_report_snapshot(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve full report JSON snapshot from MongoDB by reportId."""
        db = get_database()
        doc = await db[REPORT_SNAPSHOTS].find_one({"reportId": report_id})
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc.get("data")
        return None
