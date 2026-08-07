"""
tests/test_revenue.py — Unit Test Suite for Module 5 (Revenue Analytics)

Supports both pytest and standard unittest runner. Aligned with PostgreSQL DDL.
"""

import unittest
from datetime import date, timedelta
from decimal import Decimal
from pydantic import ValidationError

from schemas.revenue import (
    RevenueTransactionCreate,
    SponsorshipCreate,
    AdRevenueCreate,
    SubscriptionRevenueCreate,
    BrandCollaborationCreate,
)
from utils.exceptions import (
    InvalidRevenueDataException,
    DuplicateSponsorshipException,
    InvalidDateRangeException,
    UnauthorizedRevenueAccessException,
)


class TestRevenueModule(unittest.TestCase):

    def test_revenue_transaction_negative_amount_validation(self):
        """Verify negative revenue amount is rejected by schema validation."""
        with self.assertRaises(ValidationError):
            RevenueTransactionCreate(
                creator_id="crt_123",
                revenue_source="Ad Revenue",
                amount=Decimal("-150.00"),
            )

    def test_sponsorship_create_schema_valid(self):
        """Verify valid sponsorship schema instantiation."""
        sp = SponsorshipCreate(
            creator_id="crt_123",
            brand_name="Nike",
            campaign_name="Summer Showcase",
            platform="YouTube",
            contract_amount=Decimal("5000.00"),
            amount_received=Decimal("2500.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        self.assertEqual(sp.brand_name, "Nike")
        self.assertEqual(sp.contract_amount, Decimal("5000.00"))

    def test_ad_revenue_create_valid(self):
        """Verify valid ad revenue payload."""
        ad = AdRevenueCreate(
            creator_id="crt_123",
            platform="YouTube",
            amount=Decimal("1250.50"),
        )
        self.assertEqual(ad.platform, "YouTube")
        self.assertEqual(ad.amount, Decimal("1250.50"))

    def test_subscription_revenue_valid(self):
        """Verify subscription revenue creation."""
        sub = SubscriptionRevenueCreate(
            creator_id="crt_123",
            platform="Patreon",
            subscribers=120,
            revenue=Decimal("600.00"),
            month="July 2026",
        )
        self.assertEqual(sub.platform, "Patreon")
        self.assertEqual(sub.revenue, Decimal("600.00"))

    def test_brand_collaboration_valid(self):
        """Verify brand collaboration payload."""
        bc = BrandCollaborationCreate(
            creator_id="crt_123",
            sponsorship_id=1,
            deliverables="2 YouTube Shorts + 1 Instagram Reel",
            campaign_status="In Progress",
            completion_percentage=50,
            payment_status="Partial",
            remarks="First milestone delivered",
        )
        self.assertEqual(bc.sponsorship_id, 1)
        self.assertEqual(bc.completion_percentage, 50)

    def test_custom_exceptions(self):
        """Verify custom exception status codes and messages."""
        exc1 = InvalidRevenueDataException("Negative amount")
        self.assertEqual(exc1.status_code, 400)
        self.assertIn("Negative amount", exc1.detail)

        exc2 = DuplicateSponsorshipException()
        self.assertEqual(exc2.status_code, 409)

        exc3 = InvalidDateRangeException()
        self.assertEqual(exc3.status_code, 400)

        exc4 = UnauthorizedRevenueAccessException()
        self.assertEqual(exc4.status_code, 403)


if __name__ == "__main__":
    unittest.main()
