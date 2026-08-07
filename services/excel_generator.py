"""
services/excel_generator.py — OpenPyXL Excel Generator for Analytics Reports

Generates styled multi-tab Excel workbooks (.xlsx) containing:
  - Tab 1: Executive Summary
  - Tab 2: Platform Breakdown
  - Tab 3: Revenue Analytics
  - Tab 4: Content Performance
"""

import os
import logging
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)

EXPORT_DIR = os.path.join(os.getcwd(), "static", "exports", "excel")


class ExcelReportGenerator:
    """Excel Report Exporter utilizing OpenPyXL."""

    def __init__(self):
        os.makedirs(EXPORT_DIR, exist_ok=True)

    def generate_excel(self, report_id: int, data: Dict[str, Any]) -> str:
        """
        Builds a multi-tab .xlsx workbook from report data dictionary.

        Returns:
            Relative or absolute file path to the generated Excel file.
        """
        filename = f"report_{report_id}_{data.get('reportType', 'analytics')}.xlsx"
        file_path = os.path.join(EXPORT_DIR, filename)

        wb = openpyxl.Workbook()

        # Styles definition
        header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

        sub_header_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
        sub_header_font = Font(name="Calibri", size=11, bold=True, color="1F2937")

        title_font = Font(name="Calibri", size=16, bold=True, color="4F46E5")
        subtitle_font = Font(name="Calibri", size=11, italic=True, color="6B7280")
        bold_font = Font(name="Calibri", size=11, bold=True)

        thin_border = Border(
            left=Side(style="thin", color="E5E7EB"),
            right=Side(style="thin", color="E5E7EB"),
            top=Side(style="thin", color="E5E7EB"),
            bottom=Side(style="thin", color="E5E7EB"),
        )

        # ── Tab 1: Executive Summary ──────────────────────────────────────
        ws_summary = wb.active
        ws_summary.title = "Executive Summary"
        ws_summary.viewsheet_views[0].showGridLines = True

        ws_summary["A1"] = f"{data.get('creatorName', 'Creator')} — {data.get('reportType', 'Analytics').capitalize()} Report"
        ws_summary["A1"].font = title_font
        ws_summary["A2"] = f"Period: {data.get('periodLabel', '')} ({data.get('startDate', '')} to {data.get('endDate', '')})"
        ws_summary["A2"].font = subtitle_font

        ws_summary.append([])

        summary_headers = ["Metric", "Value"]
        ws_summary.append(summary_headers)
        for col in range(1, 3):
            cell = ws_summary.cell(row=4, column=col)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        summary = data.get("summaryMetrics", {})
        summary_rows = [
            ["Total Views", summary.get("totalViews", 0)],
            ["New Followers", summary.get("newFollowers", 0)],
            ["Engagement Rate (%)", f"{summary.get('engagementRate', 0.0):.2f}%"],
            ["Total Revenue ($)", f"${summary.get('totalRevenue', 0.0):,.2f}"],
            ["Total Posts Published", summary.get("totalPosts", 0)],
        ]

        for row_idx, r in enumerate(summary_rows, start=5):
            ws_summary.append(r)
            ws_summary.cell(row=row_idx, column=1).font = bold_font
            for c in range(1, 3):
                ws_summary.cell(row=row_idx, column=c).border = thin_border

        # ── Tab 2: Platform Breakdown ────────────────────────────────────
        ws_platform = wb.create_sheet(title="Platform Performance")
        ws_platform.viewsheet_views[0].showGridLines = True

        plat_headers = ["Platform", "Followers", "Views", "Likes", "Comments", "Shares", "Engagement Rate (%)"]
        ws_platform.append(plat_headers)
        for col_idx in range(1, len(plat_headers) + 1):
            cell = ws_platform.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        breakdown = data.get("platformBreakdown", [])
        for r_idx, p in enumerate(breakdown, start=2):
            ws_platform.append([
                str(p.get("platform", "")).capitalize(),
                p.get("followers", 0),
                p.get("views", 0),
                p.get("likes", 0),
                p.get("comments", 0),
                p.get("shares", 0),
                f"{p.get('engagementRate', 0.0):.2f}%",
            ])
            for col_idx in range(1, len(plat_headers) + 1):
                ws_platform.cell(row=r_idx, column=col_idx).border = thin_border

        # ── Tab 3: Revenue Analytics ──────────────────────────────────────
        ws_rev = wb.create_sheet(title="Revenue Summary")
        ws_rev.viewsheet_views[0].showGridLines = True

        rev_headers = ["Revenue Stream", "Amount ($)"]
        ws_rev.append(rev_headers)
        for col_idx in range(1, 3):
            cell = ws_rev.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font

        rev = data.get("revenueSummary", {})
        rev_rows = [
            ["Ad Revenue", rev.get("adRevenue", 0.0)],
            ["Sponsorship Revenue", rev.get("sponsorshipRevenue", 0.0)],
            ["Affiliate Commissions", rev.get("affiliateRevenue", 0.0)],
            ["Subscriptions", rev.get("subscriptionRevenue", 0.0)],
            ["Total Revenue", summary.get("totalRevenue", 0.0)],
        ]

        for r_idx, r in enumerate(rev_rows, start=2):
            ws_rev.append([r[0], f"${r[1]:,.2f}"])
            if r[0] == "Total Revenue":
                ws_rev.cell(row=r_idx, column=1).font = bold_font
                ws_rev.cell(row=r_idx, column=2).font = bold_font
                ws_rev.cell(row=r_idx, column=1).fill = sub_header_fill
                ws_rev.cell(row=r_idx, column=2).fill = sub_header_fill
            for c in range(1, 3):
                ws_rev.cell(row=r_idx, column=c).border = thin_border

        # Auto-adjust column widths across all sheets
        for sheet in wb.worksheets:
            for col in sheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                sheet.column_dimensions[col_letter].width = max(max_len + 3, 14)

        wb.save(file_path)
        logger.info("Excel Report generated successfully: %s", file_path)
        return file_path
