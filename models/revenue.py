"""
models/revenue.py — SQLAlchemy Models for Module 5 (Revenue Analytics Module)

Aligned with exact PostgreSQL Schema DDL:
- sponsorships
- revenue_transactions
- subscription_revenue
- financial_summary
- brand_collaborations
"""

import enum
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Float, Boolean, Date, DateTime, Enum, ForeignKey, Index, CheckConstraint, TIMESTAMP, func
)
from sqlalchemy.orm import relationship
from database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SponsorshipStatus(str, enum.Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# ---------------------------------------------------------------------------
# SQLAlchemy Models
# ---------------------------------------------------------------------------

class SponsorshipModel(Base):
    """Brand sponsorship agreements."""
    __tablename__ = "sponsorships"

    sponsorship_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    creator_id = Column(String(20), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_name = Column(String(100), nullable=False, index=True)
    campaign_name = Column(String(150), nullable=True)
    platform = Column(String(50), nullable=True, index=True)
    contract_amount = Column(Numeric(12, 2), nullable=True)
    amount_received = Column(Numeric(12, 2), default=0.00, nullable=True)
    status = Column(Enum(SponsorshipStatus, values_callable=lambda obj: [e.value for e in obj]), default=SponsorshipStatus.PENDING, nullable=True, index=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('Pending','Active','Completed','Cancelled')", name="chk_sponsorship_status"),
    )

    creator = relationship("CreatorProfileModel", backref="sponsorships")
    collaborations = relationship("BrandCollaborationModel", back_populates="sponsorship", cascade="all, delete-orphan")


class RevenueTransactionModel(Base):
    """Central monetary ledger recording all revenue transactions."""
    __tablename__ = "revenue_transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    creator_id = Column(String(20), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=True, index=True)
    revenue_source = Column(String(50), nullable=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=True)
    transaction_date = Column(Date, nullable=True, index=True)
    month = Column(String(20), nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    creator = relationship("CreatorProfileModel", backref="revenue_transactions")


class SubscriptionRevenueModel(Base):
    """Recurring subscription revenue metrics."""
    __tablename__ = "subscription_revenue"

    subscription_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    creator_id = Column(String(20), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=True, index=True)
    month = Column(String(20), nullable=True, index=True)
    subscribers = Column(Integer, default=0, nullable=True)
    revenue = Column(Numeric(12, 2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    creator = relationship("CreatorProfileModel", backref="subscription_revenues")


class FinancialSummaryModel(Base):
    """Monthly financial summary aggregated metrics."""
    __tablename__ = "financial_summary"

    summary_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    creator_id = Column(String(20), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(String(20), nullable=True, index=True)
    total_revenue = Column(Numeric(12, 2), nullable=True)
    ad_revenue = Column(Numeric(12, 2), nullable=True)
    sponsorship_revenue = Column(Numeric(12, 2), nullable=True)
    affiliate_revenue = Column(Numeric(12, 2), nullable=True)
    subscription_revenue = Column(Numeric(12, 2), nullable=True)
    highest_revenue_source = Column(String(50), nullable=True)
    highest_platform = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    creator = relationship("CreatorProfileModel", backref="financial_summaries")


class BrandCollaborationModel(Base):
    """Brand Collaboration details linked to sponsorships."""
    __tablename__ = "brand_collaborations"

    collaboration_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    creator_id = Column(String(20), ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    sponsorship_id = Column(Integer, ForeignKey("sponsorships.sponsorship_id", ondelete="CASCADE"), nullable=True, index=True)
    deliverables = Column(Text, nullable=True)
    campaign_status = Column(String(30), nullable=True)
    completion_percentage = Column(Integer, default=0, nullable=True)
    payment_status = Column(String(20), nullable=True)
    remarks = Column(Text, nullable=True)

    creator = relationship("CreatorProfileModel", backref="brand_collaborations")
    sponsorship = relationship("SponsorshipModel", back_populates="collaborations")
