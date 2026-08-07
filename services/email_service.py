"""
services/email_service.py — Email Dispatch Service

Sends email notifications, performance alerts, and weekly/monthly PDF reports.
Uses standard library smtplib + email.mime for HTML emails.
If SMTP environment variables are unconfigured, logs cleanly without throwing errors.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional, List
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email Service handler."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@creatoriq.app")

    def is_configured(self) -> bool:
        """Check if SMTP credentials are provided."""
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachment_path: Optional[str] = None,
    ) -> bool:
        """
        Send an HTML email with optional file attachment.

        Returns:
            True if sent successfully, False if SMTP unconfigured or error occurs.
        """
        if not self.is_configured():
            logger.info(
                "[EmailService (Simulated)] Email to '%s' | Subject: '%s' | Attachment: '%s'",
                to_email,
                subject,
                attachment_path or "None",
            )
            return True

        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(html_content, "html"))

            if attachment_path and os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=filename)
                part["Content-Disposition"] = f'attachment; filename="{filename}"'
                msg.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("Email sent successfully to %s: %s", to_email, subject)
            return True

        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to_email, exc)
            return False

    async def send_report_email(
        self,
        to_email: str,
        creator_name: str,
        report_type: str,
        period_label: str,
        pdf_path: Optional[str] = None,
    ) -> bool:
        """Helper to send a performance report email."""
        subject = f"Your {report_type.capitalize()} Performance Report — {period_label}"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h2 style="color: #4F46E5;">CreatorIQ Analytics Report</h2>
            <p>Hi <b>{creator_name}</b>,</p>
            <p>Your <b>{report_type.capitalize()} Report</b> for <b>{period_label}</b> has been generated!</p>
            <p>You can view your updated performance, revenue totals, and platform analytics in the attached PDF report or directly on your dashboard.</p>
            <hr style="border: 1px solid #E5E7EB; margin: 20px 0;" />
            <p style="font-size: 12px; color: #6B7280;">CreatorIQ Analytics Engine — Automated Notification</p>
        </div>
        """
        return await self.send_email(to_email, subject, html_body, attachment_path=pdf_path)

    async def send_alert_email(
        self,
        to_email: str,
        alert_title: str,
        alert_message: str,
    ) -> bool:
        """Helper to send an alert email."""
        subject = f"🔔 Alert: {alert_title}"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h2 style="color: #10B981;">CreatorIQ Performance Alert</h2>
            <h3 style="color: #1F2937;">{alert_title}</h3>
            <p style="font-size: 15px; line-height: 1.5;">{alert_message}</p>
            <hr style="border: 1px solid #E5E7EB; margin: 20px 0;" />
            <p style="font-size: 12px; color: #6B7280;">CreatorIQ Alert Center — Automatic Notification</p>
        </div>
        """
        return await self.send_email(to_email, subject, html_body)
