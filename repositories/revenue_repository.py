"""
repositories/revenue_repository.py — PostgreSQL CRUD Data Access Layer for Revenue Module

Aligned with exact PostgreSQL Schema DDL:
- sponsorships
- revenue_transactions
- subscription_revenue
- financial_summary
- brand_collaborations
"""

from typing import List, Dict, Optional, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, and_

from models.revenue import (
    SponsorshipModel,
    RevenueTransactionModel,
    SubscriptionRevenueModel,
    FinancialSummaryModel,
    BrandCollaborationModel,
    SponsorshipStatus,
)
from models import CreatorProfileModel, UserModel


class RevenueRepository:
    """Data Access Layer for Revenue PostgreSQL tables."""

    def __init__(self, db: Session):
        self.db = db

    # ── Revenue Transactions CRUD ─────────────────────────────────────────

    def create_revenue_transaction(self, data: Dict[str, Any]) -> RevenueTransactionModel:
        """Create a new revenue transaction record."""
        tx_date = data.get("transaction_date") or date.today()
        month_str = data.get("month") or tx_date.strftime("%B %Y")

        transaction = RevenueTransactionModel(
            creator_id=data["creator_id"],
            platform=data.get("platform"),
            revenue_source=data.get("revenue_source"),
            amount=data["amount"],
            currency=data.get("currency", "INR"),
            transaction_date=tx_date,
            month=month_str,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_revenue_by_id(self, transaction_id: int) -> Optional[RevenueTransactionModel]:
        """Fetch transaction by transaction_id."""
        return self.db.query(RevenueTransactionModel).filter(
            RevenueTransactionModel.transaction_id == transaction_id
        ).first()

    def get_revenue_by_creator(
        self,
        creator_id: str,
        limit: int = 50,
        offset: int = 0,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[RevenueTransactionModel]:
        """Get list of revenue transactions for a specific creator."""
        query = self.db.query(RevenueTransactionModel).filter(
            RevenueTransactionModel.creator_id == creator_id
        )
        if start_date:
            query = query.filter(RevenueTransactionModel.transaction_date >= start_date)
        if end_date:
            query = query.filter(RevenueTransactionModel.transaction_date <= end_date)
        
        return query.order_by(desc(RevenueTransactionModel.transaction_date)).offset(offset).limit(limit).all()

    def update_revenue_transaction(
        self, transaction_id: int, update_data: Dict[str, Any]
    ) -> Optional[RevenueTransactionModel]:
        """Update an existing revenue transaction."""
        transaction = self.get_revenue_by_id(transaction_id)
        if not transaction:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(transaction, key):
                setattr(transaction, key, value)
        
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete_revenue_transaction(self, transaction_id: int) -> bool:
        """Delete a revenue transaction."""
        transaction = self.get_revenue_by_id(transaction_id)
        if not transaction:
            return False
        self.db.delete(transaction)
        self.db.commit()
        return True

    # ── Monthly & Yearly Aggregations ──────────────────────────────────────

    def get_monthly_revenue(self, creator_id: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Calculate month-by-month revenue sum for a creator."""
        if not year:
            year = date.today().year

        results = self.db.query(
            extract('month', RevenueTransactionModel.transaction_date).label('month'),
            func.sum(RevenueTransactionModel.amount).label('total_amount')
        ).filter(
            RevenueTransactionModel.creator_id == creator_id,
            extract('year', RevenueTransactionModel.transaction_date) == year
        ).group_by('month').order_by('month').all()

        month_map = {int(row.month): Decimal(str(row.total_amount)) for row in results if row.month is not None}
        return [
            {"month": m, "year": year, "amount": month_map.get(m, Decimal("0.00"))}
            for m in range(1, 13)
        ]

    def get_yearly_revenue(self, creator_id: str) -> List[Dict[str, Any]]:
        """Calculate year-by-year revenue sum for a creator."""
        results = self.db.query(
            extract('year', RevenueTransactionModel.transaction_date).label('year'),
            func.sum(RevenueTransactionModel.amount).label('total_amount')
        ).filter(
            RevenueTransactionModel.creator_id == creator_id
        ).group_by('year').order_by('year').all()

        return [
            {"year": int(row.year), "amount": Decimal(str(row.total_amount))}
            for row in results if row.year is not None
        ]

    def get_revenue_by_source(self, creator_id: str, source_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Aggregate revenue by revenue_source."""
        query = self.db.query(
            RevenueTransactionModel.revenue_source.label('source_name'),
            func.sum(RevenueTransactionModel.amount).label('total_amount')
        ).filter(
            RevenueTransactionModel.creator_id == creator_id
        )

        if source_name:
            query = query.filter(func.lower(RevenueTransactionModel.revenue_source) == source_name.lower())

        results = query.group_by(RevenueTransactionModel.revenue_source).all()
        return [
            {"source_name": row.source_name or "Other", "amount": Decimal(str(row.total_amount))}
            for row in results
        ]

    def get_top_earning_creators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Calculate top earning creators overall across all transactions."""
        results = self.db.query(
            RevenueTransactionModel.creator_id,
            CreatorProfileModel.username,
            UserModel.full_name,
            func.sum(RevenueTransactionModel.amount).label('total_revenue')
        ).join(
            CreatorProfileModel, RevenueTransactionModel.creator_id == CreatorProfileModel.id
        ).join(
            UserModel, CreatorProfileModel.user_id == UserModel.id
        ).group_by(
            RevenueTransactionModel.creator_id,
            CreatorProfileModel.username,
            UserModel.full_name
        ).order_by(
            desc('total_revenue')
        ).limit(limit).all()

        return [
            {
                "creator_id": row.creator_id,
                "username": row.username,
                "creator_name": row.full_name,
                "total_revenue": Decimal(str(row.total_revenue)),
            }
            for row in results
        ]

    # ── Sponsorship CRUD ──────────────────────────────────────────────────

    def check_duplicate_sponsorship(self, creator_id: str, brand_name: str, campaign_name: Optional[str]) -> bool:
        """Returns True if a sponsorship campaign already exists for this creator."""
        if not campaign_name:
            return False
        existing = self.db.query(SponsorshipModel).filter(
            SponsorshipModel.creator_id == creator_id,
            func.lower(SponsorshipModel.brand_name) == brand_name.lower(),
            func.lower(SponsorshipModel.campaign_name) == campaign_name.lower(),
        ).first()
        return existing is not None

    def create_sponsorship(self, data: Dict[str, Any]) -> SponsorshipModel:
        """Create a new sponsorship record."""
        sponsorship = SponsorshipModel(
            creator_id=data["creator_id"],
            brand_name=data["brand_name"],
            campaign_name=data.get("campaign_name"),
            platform=data.get("platform"),
            contract_amount=data.get("contract_amount", Decimal("0.00")),
            amount_received=data.get("amount_received", Decimal("0.00")),
            status=data.get("status", SponsorshipStatus.PENDING),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
        )
        self.db.add(sponsorship)
        self.db.commit()
        self.db.refresh(sponsorship)
        return sponsorship

    def get_sponsorships(self, creator_id: str) -> List[SponsorshipModel]:
        """Fetch all sponsorships for a creator."""
        return self.db.query(SponsorshipModel).filter(
            SponsorshipModel.creator_id == creator_id
        ).order_by(desc(SponsorshipModel.created_at)).all()

    def get_sponsorship_by_id(self, sponsorship_id: int) -> Optional[SponsorshipModel]:
        """Get sponsorship by ID."""
        return self.db.query(SponsorshipModel).filter(SponsorshipModel.sponsorship_id == sponsorship_id).first()

    def update_sponsorship(self, sponsorship_id: int, data: Dict[str, Any]) -> Optional[SponsorshipModel]:
        """Update a sponsorship record."""
        sponsorship = self.get_sponsorship_by_id(sponsorship_id)
        if not sponsorship:
            return None
        for key, val in data.items():
            if val is not None and hasattr(sponsorship, key):
                setattr(sponsorship, key, val)
        self.db.commit()
        self.db.refresh(sponsorship)
        return sponsorship

    def delete_sponsorship(self, sponsorship_id: int) -> bool:
        """Delete a sponsorship record."""
        sponsorship = self.get_sponsorship_by_id(sponsorship_id)
        if not sponsorship:
            return False
        self.db.delete(sponsorship)
        self.db.commit()
        return True

    # ── Ad Revenue Summary ────────────────────────────────────────────────

    def get_ad_revenue_summary(self, creator_id: str) -> Dict[str, Any]:
        """Compute ad revenue breakdown (today, weekly, monthly, platform-wise)."""
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        today_val = self.db.query(func.sum(RevenueTransactionModel.amount)).filter(
            RevenueTransactionModel.creator_id == creator_id,
            func.lower(RevenueTransactionModel.revenue_source) == "ad revenue",
            RevenueTransactionModel.transaction_date == today
        ).scalar() or 0.0

        weekly_val = self.db.query(func.sum(RevenueTransactionModel.amount)).filter(
            RevenueTransactionModel.creator_id == creator_id,
            func.lower(RevenueTransactionModel.revenue_source) == "ad revenue",
            RevenueTransactionModel.transaction_date >= week_ago
        ).scalar() or 0.0

        monthly_val = self.db.query(func.sum(RevenueTransactionModel.amount)).filter(
            RevenueTransactionModel.creator_id == creator_id,
            func.lower(RevenueTransactionModel.revenue_source) == "ad revenue",
            RevenueTransactionModel.transaction_date >= month_ago
        ).scalar() or 0.0

        platform_rows = self.db.query(
            RevenueTransactionModel.platform,
            func.sum(RevenueTransactionModel.amount).label("total")
        ).filter(
            RevenueTransactionModel.creator_id == creator_id,
            func.lower(RevenueTransactionModel.revenue_source) == "ad revenue"
        ).group_by(RevenueTransactionModel.platform).all()

        platform_dict = {
            (row.platform or "Other"): Decimal(str(row.total)) for row in platform_rows
        }

        return {
            "creator_id": creator_id,
            "today_earnings": Decimal(str(today_val)),
            "weekly_earnings": Decimal(str(weekly_val)),
            "monthly_earnings": Decimal(str(monthly_val)),
            "platform_wise_earnings": platform_dict,
        }

    # ── Subscription Revenue CRUD ─────────────────────────────────────────

    def create_subscription_revenue(self, data: Dict[str, Any]) -> SubscriptionRevenueModel:
        month_str = data.get("month") or date.today().strftime("%B %Y")
        item = SubscriptionRevenueModel(
            creator_id=data["creator_id"],
            platform=data.get("platform"),
            month=month_str,
            subscribers=data.get("subscribers", 0),
            revenue=data.get("revenue", Decimal("0.00")),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_subscription_revenues(self, creator_id: str) -> List[SubscriptionRevenueModel]:
        return self.db.query(SubscriptionRevenueModel).filter(
            SubscriptionRevenueModel.creator_id == creator_id
        ).order_by(desc(SubscriptionRevenueModel.created_at)).all()

    # ── Brand Collaboration CRUD ──────────────────────────────────────────

    def create_brand_collaboration(self, data: Dict[str, Any]) -> BrandCollaborationModel:
        item = BrandCollaborationModel(
            creator_id=data["creator_id"],
            sponsorship_id=data.get("sponsorship_id"),
            deliverables=data.get("deliverables"),
            campaign_status=data.get("campaign_status", "Draft"),
            completion_percentage=data.get("completion_percentage", 0),
            payment_status=data.get("payment_status", "Pending"),
            remarks=data.get("remarks"),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_brand_collaborations(self, creator_id: str) -> List[BrandCollaborationModel]:
        return self.db.query(BrandCollaborationModel).filter(
            BrandCollaborationModel.creator_id == creator_id
        ).order_by(desc(BrandCollaborationModel.collaboration_id)).all()

    # ── Financial Summary CRUD ─────────────────────────────────────────────

    def create_financial_summary(self, data: Dict[str, Any]) -> FinancialSummaryModel:
        month_str = data.get("month") or date.today().strftime("%B %Y")
        item = FinancialSummaryModel(
            creator_id=data["creator_id"],
            month=month_str,
            total_revenue=data.get("total_revenue", Decimal("0.00")),
            ad_revenue=data.get("ad_revenue", Decimal("0.00")),
            sponsorship_revenue=data.get("sponsorship_revenue", Decimal("0.00")),
            affiliate_revenue=data.get("affiliate_revenue", Decimal("0.00")),
            subscription_revenue=data.get("subscription_revenue", Decimal("0.00")),
            highest_revenue_source=data.get("highest_revenue_source"),
            highest_platform=data.get("highest_platform"),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
