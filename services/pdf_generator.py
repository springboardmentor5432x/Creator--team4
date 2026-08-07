"""
services/pdf_generator.py — ReportLab PDF Generator for Analytics Reports

Generates professional, styled PDF performance reports containing:
  - Header with Creator info & Report Period
  - KPI Summary Metrics Table (Total Views, Followers, Engagement Rate, Revenue)
  - Best Performing Content Section
  - Top Performing Platform Breakdown
  - Revenue & Audience Summaries
"""

import os
import logging
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

logger = logging.getLogger(__name__)

EXPORT_DIR = os.path.join(os.getcwd(), "static", "exports", "pdf")


class PDFReportGenerator:
    """PDF Generator utilizing ReportLab Flowables."""

    def __init__(self):
        os.makedirs(EXPORT_DIR, exist_ok=True)

    def generate_pdf(self, report_id: int, data: Dict[str, Any]) -> str:
        """
        Builds a PDF file from report data dictionary.

        Returns:
            Relative or absolute file path to the generated PDF.
        """
        filename = f"report_{report_id}_{data.get('reportType', 'analytics')}.pdf"
        file_path = os.path.join(EXPORT_DIR, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom Palette Styles
        primary_color = colors.HexColor("#4F46E5")   # Indigo
        dark_color = colors.HexColor("#1F2937")      # Charcoal
        light_bg = colors.HexColor("#F3F4F6")        # Light Gray
        accent_color = colors.HexColor("#10B981")    # Emerald Green

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=primary_color,
            fontName="Helvetica-Bold",
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#6B7280"),
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=dark_color,
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=dark_color,
        )

        elements = []

        # ── 1. Document Header ──────────────────────────────────────────────
        creator_name = data.get("creatorName", "Creator Analytics")
        period_label = data.get("periodLabel", "Weekly Summary")
        report_type = data.get("reportType", "Performance Report").capitalize()

        elements.append(Paragraph(f"{creator_name} — {report_type}", title_style))
        elements.append(Paragraph(f"Period: <b>{period_label}</b> | Generated: {data.get('endDate', '')}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=15))

        # ── 2. Summary KPI Table ───────────────────────────────────────────
        elements.append(Paragraph("Key Performance Indicators", section_heading))
        summary = data.get("summaryMetrics", {})

        kpi_data = [
            [
                Paragraph("<b>Total Views</b>", body_style),
                Paragraph(f"{summary.get('totalViews', 0):,}", body_style),
                Paragraph("<b>New Followers</b>", body_style),
                Paragraph(f"+{summary.get('newFollowers', 0):,}", body_style),
            ],
            [
                Paragraph("<b>Engagement Rate</b>", body_style),
                Paragraph(f"{summary.get('engagementRate', 0.0):.2f}%", body_style),
                Paragraph("<b>Total Revenue</b>", body_style),
                Paragraph(f"${summary.get('totalRevenue', 0.0):,.2f}", body_style),
            ],
        ]

        kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
        kpi_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), light_bg),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elements.append(kpi_table)
        elements.append(Spacer(1, 15))

        # ── 3. Best Performing Content & Top Platform ─────────────────────
        best_content = data.get("bestContent") or {}
        top_platform = data.get("topPlatform") or {}

        elements.append(Paragraph("Performance Highlights", section_heading))

        highlight_data = [
            [
                Paragraph("<b>Top Performing Content</b>", body_style),
                Paragraph(
                    f"Title: <b>{best_content.get('title', 'N/A')}</b><br/>"
                    f"Platform: {best_content.get('platform', 'N/A').capitalize()}<br/>"
                    f"Views: {best_content.get('views', 0):,} | Likes: {best_content.get('likes', 0):,}",
                    body_style,
                ),
            ],
            [
                Paragraph("<b>Top Performing Platform</b>", body_style),
                Paragraph(
                    f"Platform: <b>{top_platform.get('platform', 'N/A').capitalize()}</b><br/>"
                    f"Views: {top_platform.get('views', 0):,} | Followers: {top_platform.get('followers', 0):,}<br/>"
                    f"Engagement: {top_platform.get('engagementRate', 0.0):.2f}%",
                    body_style,
                ),
            ],
        ]

        highlight_table = Table(highlight_data, colWidths=[160, 360])
        highlight_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D2FE")),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        elements.append(highlight_table)
        elements.append(Spacer(1, 15))

        # ── 4. Platform Breakdown Table ──────────────────────────────────
        breakdown = data.get("platformBreakdown", [])
        if breakdown:
            elements.append(Paragraph("Platform Breakdown", section_heading))
            headers = ["Platform", "Followers", "Views", "Likes", "Engagement"]
            table_rows = [[Paragraph(f"<b>{h}</b>", body_style) for h in headers]]

            for p in breakdown:
                table_rows.append([
                    Paragraph(str(p.get("platform", "")).capitalize(), body_style),
                    Paragraph(f"{p.get('followers', 0):,}", body_style),
                    Paragraph(f"{p.get('views', 0):,}", body_style),
                    Paragraph(f"{p.get('likes', 0):,}", body_style),
                    Paragraph(f"{p.get('engagementRate', 0.0):.2f}%", body_style),
                ])

            breakdown_table = Table(table_rows, colWidths=[100, 100, 105, 105, 110])
            breakdown_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ])
            )
            elements.append(breakdown_table)
            elements.append(Spacer(1, 15))

        # ── 5. Revenue Summary ───────────────────────────────────────────
        rev_summary = data.get("revenueSummary", {})
        if rev_summary:
            elements.append(Paragraph("Revenue Overview", section_heading))
            rev_data = [
                [
                    Paragraph("<b>Ad Revenue</b>", body_style),
                    Paragraph(f"${rev_summary.get('adRevenue', 0.0):,.2f}", body_style),
                    Paragraph("<b>Sponsorships</b>", body_style),
                    Paragraph(f"${rev_summary.get('sponsorshipRevenue', 0.0):,.2f}", body_style),
                ],
                [
                    Paragraph("<b>Affiliate Earnings</b>", body_style),
                    Paragraph(f"${rev_summary.get('affiliateRevenue', 0.0):,.2f}", body_style),
                    Paragraph("<b>Subscriptions</b>", body_style),
                    Paragraph(f"${rev_summary.get('subscriptionRevenue', 0.0):,.2f}", body_style),
                ],
            ]
            rev_table = Table(rev_data, colWidths=[130, 130, 130, 130])
            rev_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A7F3D0")),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ])
            )
            elements.append(rev_table)

        # ── Footer ────────────────────────────────────────────────────────
        elements.append(Spacer(1, 25))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB"), spaceAfter=8))
        elements.append(Paragraph("Generated automatically by Creator Analytics Engine.", subtitle_style))

        doc.build(elements)
        logger.info("PDF Report generated successfully: %s", file_path)
        return file_path
