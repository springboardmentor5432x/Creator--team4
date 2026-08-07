"""
schemas/revenue.py — Pydantic Schemas for Module 5 (Revenue Analytics Module)

Aligned with exact PostgreSQL Schema DDL provided.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import date as PyDate, datetime as PyDateTime
from decimal import Decimal
from models.revenue import SponsorshipStatus


# ---------------------------------------------------------------------------
# Sponsorship Schemas
# ---------------------------------------------------------------------------

class SponsorshipBase(BaseModel):
    creator_id: str = Field(..., description="Creator Profile ID")
    brand_name: str = Field(..., min_length=1, max_length=100)
    campaign_name: Optional[str] = Field(None, max_length=150)
    platform: Optional[str] = Field(None, max_length=50)
    contract_amount: Decimal = Field(Decimal("0.00"), description="Contract amount")
    amount_received: Decimal = Field(Decimal("0.00"), description="Amount received")
    status: SponsorshipStatus = SponsorshipStatus.PENDING
    start_date: Optional[PyDate] = None
    end_date: Optional[PyDate] = None

    @field_validator("contract_amount", "amount_received")

    def validate_positive_amount(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class SponsorshipCreate(SponsorshipBase):
    pass


class SponsorshipUpdate(BaseModel):
    brand_name: Optional[str] = None
    campaign_name: Optional[str] = None
    platform: Optional[str] = None
    contract_amount: Optional[Decimal] = None
    amount_received: Optional[Decimal] = None
    status: Optional[SponsorshipStatus] = None
    start_date: Optional[PyDate] = None
    end_date: Optional[PyDate] = None

    @field_validator("contract_amount", "amount_received")

    def validate_positive_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class SponsorshipResponse(SponsorshipBase):
    sponsorship_id: int
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Revenue Transaction Schemas
# ---------------------------------------------------------------------------

class RevenueTransactionBase(BaseModel):
    creator_id: str = Field(..., description="Creator Profile ID")
    platform: Optional[str] = Field(None, max_length=50)
    revenue_source: Optional[str] = Field(None, max_length=50)
    amount: Decimal = Field(..., description="Transaction amount")
    currency: str = Field("INR", max_length=10)
    transaction_date: Optional[PyDate] = Field(default_factory=PyDate.today)
    month: Optional[str] = Field(None, max_length=20)

    @field_validator("amount")

    def validate_positive_amount(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Transaction amount cannot be negative")
        return v


class RevenueTransactionCreate(RevenueTransactionBase):
    pass


class RevenueTransactionUpdate(BaseModel):
    platform: Optional[str] = None
    revenue_source: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    transaction_date: Optional[PyDate] = None
    month: Optional[str] = None

    @field_validator("amount")

    def validate_positive_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("Transaction amount cannot be negative")
        return v


class RevenueTransactionResponse(RevenueTransactionBase):
    transaction_id: int
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Subscription Revenue Schemas
# ---------------------------------------------------------------------------

class SubscriptionRevenueBase(BaseModel):
    creator_id: str = Field(..., description="Creator Profile ID")
    platform: Optional[str] = Field(None, max_length=50)
    month: Optional[str] = Field(None, max_length=20)
    subscribers: int = Field(0, ge=0)
    revenue: Decimal = Field(Decimal("0.00"), ge=0)


class SubscriptionRevenueCreate(SubscriptionRevenueBase):
    pass


class SubscriptionRevenueUpdate(BaseModel):
    platform: Optional[str] = None
    month: Optional[str] = None
    subscribers: Optional[int] = Field(None, ge=0)
    revenue: Optional[Decimal] = Field(None, ge=0)


class SubscriptionRevenueResponse(SubscriptionRevenueBase):
    subscription_id: int
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Financial Summary Schemas
# ---------------------------------------------------------------------------

class FinancialSummaryBase(BaseModel):
    creator_id: str
    month: Optional[str] = None
    total_revenue: Decimal = Decimal("0.00")
    ad_revenue: Decimal = Decimal("0.00")
    sponsorship_revenue: Decimal = Decimal("0.00")
    affiliate_revenue: Decimal = Decimal("0.00")
    subscription_revenue: Decimal = Decimal("0.00")
    highest_revenue_source: Optional[str] = None
    highest_platform: Optional[str] = None


class FinancialSummaryCreate(FinancialSummaryBase):
    pass


class FinancialSummaryResponse(FinancialSummaryBase):
    summary_id: int
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Brand Collaboration Details Schemas
# ---------------------------------------------------------------------------

class BrandCollaborationBase(BaseModel):
    creator_id: str
    sponsorship_id: Optional[int] = None
    deliverables: Optional[str] = None
    campaign_status: Optional[str] = None
    completion_percentage: int = Field(0, ge=0, le=100)
    payment_status: Optional[str] = None
    remarks: Optional[str] = None


class BrandCollaborationCreate(BrandCollaborationBase):
    pass


class BrandCollaborationUpdate(BaseModel):
    sponsorship_id: Optional[int] = None
    deliverables: Optional[str] = None
    campaign_status: Optional[str] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    payment_status: Optional[str] = None
    remarks: Optional[str] = None


class BrandCollaborationResponse(BrandCollaborationBase):
    collaboration_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Ad Revenue Schemas
# ---------------------------------------------------------------------------

class AdRevenueCreate(BaseModel):
    creator_id: str
    platform: str = Field(..., description="Platform: YouTube, Instagram, TikTok, Facebook, LinkedIn")
    amount: Decimal
    transaction_date: PyDate = Field(default_factory=PyDate.today)
    month: Optional[str] = None

    @field_validator("amount")

    def validate_amount(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Ad revenue amount cannot be negative")
        return v


class AdRevenueSummaryResponse(BaseModel):
    creator_id: str
    today_earnings: Decimal
    weekly_earnings: Decimal
    monthly_earnings: Decimal
    platform_wise_earnings: Dict[str, Decimal]


# ---------------------------------------------------------------------------
# Trends & Insights Responses
# ---------------------------------------------------------------------------

class DailyRevenueItem(BaseModel):
    date: str
    amount: Decimal


class RevenueTrendsResponse(BaseModel):
    creator_id: str
    daily_revenue: List[DailyRevenueItem]
    weekly_revenue: Decimal
    monthly_revenue: Decimal
    yearly_revenue: Decimal
    moving_average: Decimal
    growth_percentage: float
    comparison_previous_period: Dict[str, Any]


class FinancialInsightsResponse(BaseModel):
    creator_id: str
    highest_earning_month: Optional[str]
    highest_earning_platform: Optional[str]
    highest_earning_creator: Optional[Dict[str, Any]]
    revenue_distribution: Dict[str, Decimal]
    average_monthly_revenue: Decimal
    top_revenue_source: str
    loss_detection: Dict[str, Any]


class TopCreatorRevenueItem(BaseModel):
    creator_id: str
    creator_name: Optional[str]
    username: Optional[str]
    total_revenue: Decimal
