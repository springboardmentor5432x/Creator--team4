"""
services/revenue_service.py — Revenue Analytics Service Business Logic Layer

Aligned with exact PostgreSQL Schema DDL:
- sponsorships
- revenue_transactions
- subscription_revenue
- financial_summary
- brand_collaborations
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from repositories.revenue_repository import RevenueRepository
from repositories.revenue_mongo_repository import RevenueMongoRepository
from models import UserModel, CreatorProfileModel, AgencyCreatorModel
from models.revenue import (
    SponsorshipModel,
    RevenueTransactionModel,
    SubscriptionRevenueModel,
    FinancialSummaryModel,
    BrandCollaborationModel,
    SponsorshipStatus,
)
from roles import UserRole
from utils.exceptions import (
    InvalidRevenueDataException,
    DuplicateSponsorshipException,
    InvalidDateRangeException,
    RevenueNotFoundException,
    UnauthorizedRevenueAccessException,
)

logger = logging.getLogger("revenue_analytics")
logger.setLevel(logging.INFO)


class RevenueService:
    """Business logic orchestrator for Module 5 (Revenue Analytics)."""

    def __init__(self, db: Session):
        self.db = db
        self.pg_repo = RevenueRepository(db)
        self.mongo_repo = RevenueMongoRepository()

    # ── RBAC & Ownership Validation ───────────────────────────────────────

    def authorize_creator_access(self, current_user: UserModel, target_creator_id: str, is_write_op: bool = False):
        role_name = getattr(current_user.role, "role_name", "")

        if role_name == UserRole.ADMINISTRATOR.value:
            return

        if role_name == UserRole.MARKETING.value:
            if is_write_op:
                raise UnauthorizedRevenueAccessException("Marketing team has read-only access to revenue records.")
            return

        if role_name == UserRole.CREATOR.value:
            creator_profile = getattr(current_user, "creator_profile", None)
            if not creator_profile or creator_profile.id != target_creator_id:
                raise UnauthorizedRevenueAccessException("Creators can view/manage only their own revenue records.")
            return

        if role_name == UserRole.AGENCY.value:
            agency_profile = getattr(current_user, "agency_profile", None)
            if not agency_profile:
                raise UnauthorizedRevenueAccessException("Agency profile not found.")
            
            assigned = self.db.query(AgencyCreatorModel).filter(
                AgencyCreatorModel.agency_id == agency_profile.id,
                AgencyCreatorModel.creator_id == target_creator_id
            ).first()

            if not assigned:
                raise UnauthorizedRevenueAccessException(
                    f"Agency '{agency_profile.agency_name}' is not authorized to access revenue for creator '{target_creator_id}'."
                )
            return

        raise UnauthorizedRevenueAccessException("Unauthorized access to revenue records.")

    def _verify_creator_exists(self, creator_id: str):
        creator = self.db.query(CreatorProfileModel).filter(CreatorProfileModel.id == creator_id).first()
        if not creator:
            raise HTTPException(status_code=404, detail=f"Creator profile '{creator_id}' not found.")

    # ── Revenue Transactions API Logic ────────────────────────────────────

    async def create_revenue_transaction(self, current_user: UserModel, data: Dict[str, Any]) -> Dict[str, Any]:
        creator_id = data["creator_id"]
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=True)

        if data["amount"] < 0:
            raise InvalidRevenueDataException("Revenue amount cannot be negative.")

        tx = self.pg_repo.create_revenue_transaction(data)
        logger.info(f"Revenue Created: ID={tx.transaction_id}, Creator={creator_id}, Amount={tx.amount}, Source={tx.revenue_source}")

        # Save snapshot in MongoDB
        await self.mongo_repo.save_revenue_history_snapshot(creator_id, {
            "transactionId": tx.transaction_id,
            "amount": float(tx.amount),
            "platform": tx.platform,
            "date": str(tx.transaction_date),
            "source": tx.revenue_source,
        })

        return self._format_tx(tx)

    def get_revenue_transaction(self, current_user: UserModel, transaction_id: int) -> Dict[str, Any]:
        tx = self.pg_repo.get_revenue_by_id(transaction_id)
        if not tx:
            raise RevenueNotFoundException("Revenue transaction", str(transaction_id))
        self.authorize_creator_access(current_user, tx.creator_id, is_write_op=False)
        return self._format_tx(tx)

    def get_revenue_by_creator(
        self, current_user: UserModel, creator_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        txs = self.pg_repo.get_revenue_by_creator(creator_id, limit=limit, offset=offset)
        return [self._format_tx(t) for t in txs]

    def update_revenue_transaction(
        self, current_user: UserModel, transaction_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        tx = self.pg_repo.get_revenue_by_id(transaction_id)
        if not tx:
            raise RevenueNotFoundException("Revenue transaction", str(transaction_id))
        self.authorize_creator_access(current_user, tx.creator_id, is_write_op=True)

        if "amount" in update_data and update_data["amount"] is not None and update_data["amount"] < 0:
            raise InvalidRevenueDataException("Revenue amount cannot be negative.")

        updated = self.pg_repo.update_revenue_transaction(transaction_id, update_data)
        logger.info(f"Revenue Updated: ID={transaction_id}, UpdatedBy={current_user.email}")
        return self._format_tx(updated)

    def delete_revenue_transaction(self, current_user: UserModel, transaction_id: int) -> Dict[str, Any]:
        tx = self.pg_repo.get_revenue_by_id(transaction_id)
        if not tx:
            raise RevenueNotFoundException("Revenue transaction", str(transaction_id))
        self.authorize_creator_access(current_user, tx.creator_id, is_write_op=True)

        creator_id = tx.creator_id
        self.pg_repo.delete_revenue_transaction(transaction_id)
        logger.info(f"Revenue Deleted: ID={transaction_id}, Creator={creator_id}, DeletedBy={current_user.email}")
        return {"status": "success", "id": transaction_id, "message": "Revenue transaction deleted successfully"}

    def get_monthly_revenue(self, current_user: UserModel, creator_id: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        return self.pg_repo.get_monthly_revenue(creator_id, year)

    def get_yearly_revenue(self, current_user: UserModel, creator_id: str) -> List[Dict[str, Any]]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        return self.pg_repo.get_yearly_revenue(creator_id)

    def get_revenue_by_source(self, current_user: UserModel, creator_id: str, source_name: Optional[str] = None) -> List[Dict[str, Any]]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        return self.pg_repo.get_revenue_by_source(creator_id, source_name)

    def get_top_creators(self, current_user: UserModel, limit: int = 10) -> List[Dict[str, Any]]:
        role_name = getattr(current_user.role, "role_name", "")
        if role_name == UserRole.CREATOR.value:
            raise UnauthorizedRevenueAccessException("Creators are not permitted to view global top creator revenue rankings.")
        return self.pg_repo.get_top_earning_creators(limit)

    # ── Sponsorship Management ────────────────────────────────────────────

    def create_sponsorship(self, current_user: UserModel, data: Dict[str, Any]) -> Dict[str, Any]:
        creator_id = data["creator_id"]
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=True)

        if data.get("contract_amount", 0) < 0 or data.get("amount_received", 0) < 0:
            raise InvalidRevenueDataException("Sponsorship amounts cannot be negative.")
        if data.get("start_date") and data.get("end_date") and data["end_date"] < data["start_date"]:
            raise InvalidDateRangeException("Sponsorship end_date cannot be earlier than start_date.")

        if self.pg_repo.check_duplicate_sponsorship(creator_id, data["brand_name"], data.get("campaign_name")):
            raise DuplicateSponsorshipException(
                f"Sponsorship campaign '{data.get('campaign_name')}' for '{data['brand_name']}' already exists for this creator."
            )

        sp = self.pg_repo.create_sponsorship(data)

        # Log as a revenue transaction
        if data.get("contract_amount", 0) > 0:
            self.pg_repo.create_revenue_transaction({
                "creator_id": creator_id,
                "platform": data.get("platform", "Sponsorship"),
                "revenue_source": "Sponsorship",
                "amount": data["contract_amount"],
                "currency": "INR",
                "transaction_date": data.get("start_date") or date.today(),
            })

        logger.info(f"Sponsorship Created: ID={sp.sponsorship_id}, Brand={sp.brand_name}, ContractAmount={sp.contract_amount}")
        return self._format_sp(sp)

    def get_sponsorships(self, current_user: UserModel, creator_id: str) -> List[Dict[str, Any]]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        sps = self.pg_repo.get_sponsorships(creator_id)
        return [self._format_sp(s) for s in sps]

    def update_sponsorship(self, current_user: UserModel, sponsorship_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        sp = self.pg_repo.get_sponsorship_by_id(sponsorship_id)
        if not sp:
            raise RevenueNotFoundException("Sponsorship", str(sponsorship_id))
        self.authorize_creator_access(current_user, sp.creator_id, is_write_op=True)

        updated = self.pg_repo.update_sponsorship(sponsorship_id, data)
        return self._format_sp(updated)

    def delete_sponsorship(self, current_user: UserModel, sponsorship_id: int) -> Dict[str, Any]:
        sp = self.pg_repo.get_sponsorship_by_id(sponsorship_id)
        if not sp:
            raise RevenueNotFoundException("Sponsorship", str(sponsorship_id))
        self.authorize_creator_access(current_user, sp.creator_id, is_write_op=True)

        self.pg_repo.delete_sponsorship(sponsorship_id)
        return {"status": "success", "id": sponsorship_id, "message": "Sponsorship deleted successfully"}

    # ── Ad Revenue ────────────────────────────────────────────────────────

    def record_ad_revenue(self, current_user: UserModel, data: Dict[str, Any]) -> Dict[str, Any]:
        creator_id = data["creator_id"]
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=True)

        if data["amount"] < 0:
            raise InvalidRevenueDataException("Ad revenue amount cannot be negative.")

        tx = self.pg_repo.create_revenue_transaction({
            "creator_id": creator_id,
            "platform": data["platform"],
            "revenue_source": "Ad Revenue",
            "amount": data["amount"],
            "currency": "INR",
            "transaction_date": data.get("transaction_date") or date.today(),
            "month": data.get("month"),
        })
        return self._format_tx(tx)

    def get_ad_revenue_summary(self, current_user: UserModel, creator_id: str) -> Dict[str, Any]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        return self.pg_repo.get_ad_revenue_summary(creator_id)

    # ── Subscription Revenue ──────────────────────────────────────────────

    def record_subscription_revenue(self, current_user: UserModel, data: Dict[str, Any]) -> Dict[str, Any]:
        creator_id = data["creator_id"]
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=True)

        if data.get("revenue", 0) < 0:
            raise InvalidRevenueDataException("Subscription revenue cannot be negative.")

        sub = self.pg_repo.create_subscription_revenue(data)

        if data.get("revenue", 0) > 0:
            self.pg_repo.create_revenue_transaction({
                "creator_id": creator_id,
                "platform": data.get("platform", "Subscription"),
                "revenue_source": "Subscription Revenue",
                "amount": data["revenue"],
                "currency": "INR",
                "transaction_date": date.today(),
                "month": data.get("month"),
            })

        return self._format_sub(sub)

    def get_subscription_revenues(self, current_user: UserModel, creator_id: str) -> List[Dict[str, Any]]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        items = self.pg_repo.get_subscription_revenues(creator_id)
        return [self._format_sub(i) for i in items]

    # ── Brand Collaborations ──────────────────────────────────────────────

    def record_brand_collaboration(self, current_user: UserModel, data: Dict[str, Any]) -> Dict[str, Any]:
        creator_id = data["creator_id"]
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=True)

        collab = self.pg_repo.create_brand_collaboration(data)
        return self._format_bc(collab)

    def get_brand_collaborations(self, current_user: UserModel, creator_id: str) -> List[Dict[str, Any]]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)
        items = self.pg_repo.get_brand_collaborations(creator_id)
        return [self._format_bc(i) for i in items]

    # ── Trends & Analytics ────────────────────────────────────────────────

    async def get_revenue_trends(self, current_user: UserModel, creator_id: str) -> Dict[str, Any]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)

        today = date.today()
        txs = self.pg_repo.get_revenue_by_creator(creator_id, limit=300, offset=0)
        
        daily_map: Dict[str, Decimal] = {}
        for d in range(30):
            day_str = (today - timedelta(days=d)).isoformat()
            daily_map[day_str] = Decimal("0.00")

        weekly_total = Decimal("0.00")
        monthly_total = Decimal("0.00")
        yearly_total = Decimal("0.00")

        week_cutoff = today - timedelta(days=7)
        month_cutoff = today - timedelta(days=30)
        year_cutoff = today - timedelta(days=365)
        prev_month_start = today - timedelta(days=60)
        prev_month_end = today - timedelta(days=31)
        prev_month_total = Decimal("0.00")

        for t in txs:
            t_date = t.transaction_date or today
            amount = Decimal(str(t.amount))

            t_str = t_date.isoformat()
            if t_str in daily_map:
                daily_map[t_str] += amount

            if t_date >= week_cutoff:
                weekly_total += amount
            if t_date >= month_cutoff:
                monthly_total += amount
            if t_date >= year_cutoff:
                yearly_total += amount
            if prev_month_start <= t_date <= prev_month_end:
                prev_month_total += amount

        daily_list = [
            {"date": d_str, "amount": amt}
            for d_str, amt in sorted(daily_map.items())
        ]

        moving_avg = weekly_total / Decimal("7.0") if weekly_total > 0 else Decimal("0.00")

        if prev_month_total > 0:
            growth_pct = float(((monthly_total - prev_month_total) / prev_month_total) * 100)
        else:
            growth_pct = 100.0 if monthly_total > 0 else 0.0

        trend_res = {
            "creator_id": creator_id,
            "daily_revenue": daily_list,
            "weekly_revenue": weekly_total,
            "monthly_revenue": monthly_total,
            "yearly_revenue": yearly_total,
            "moving_average": round(moving_avg, 2),
            "growth_percentage": round(growth_pct, 2),
            "comparison_previous_period": {
                "current_30_days": monthly_total,
                "previous_30_days": prev_month_total,
                "diff": monthly_total - prev_month_total,
            },
        }

        await self.mongo_repo.save_trend_analytics(creator_id, {
            "weekly_revenue": float(weekly_total),
            "monthly_revenue": float(monthly_total),
            "yearly_revenue": float(yearly_total),
            "growth_percentage": growth_pct,
        })
        logger.info(f"Report Generated: Revenue trends for creator {creator_id}")
        return trend_res

    def get_financial_summary(self, current_user: UserModel, creator_id: str) -> Dict[str, Any]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)

        txs = self.pg_repo.get_revenue_by_creator(creator_id, limit=500)
        total_rev = sum((Decimal(str(t.amount)) for t in txs), Decimal("0.00"))

        subs = self.pg_repo.get_subscription_revenues(creator_id)
        sub_rev = sum((Decimal(str(s.revenue or 0)) for s in subs), Decimal("0.00"))

        sps = self.pg_repo.get_sponsorships(creator_id)
        sp_rev = sum((Decimal(str(s.amount_received or 0)) for s in sps), Decimal("0.00"))

        source_breakdown = self.pg_repo.get_revenue_by_source(creator_id)
        top_source = max(source_breakdown, key=lambda x: x["amount"])["source_name"] if source_breakdown else "N/A"

        ad_summary = self.pg_repo.get_ad_revenue_summary(creator_id)
        platforms = ad_summary.get("platform_wise_earnings", {})
        top_platform = max(platforms, key=platforms.get) if platforms else "N/A"

        curr_month = date.today().strftime("%B %Y")

        return {
            "creator_id": creator_id,
            "month": curr_month,
            "total_revenue": total_rev,
            "ad_revenue": ad_summary.get("monthly_earnings", Decimal("0.00")),
            "sponsorship_revenue": sp_rev,
            "affiliate_revenue": Decimal("0.00"),
            "subscription_revenue": sub_rev,
            "highest_revenue_source": top_source,
            "highest_platform": top_platform,
        }

    def get_financial_insights(self, current_user: UserModel, creator_id: str) -> Dict[str, Any]:
        self._verify_creator_exists(creator_id)
        self.authorize_creator_access(current_user, creator_id, is_write_op=False)

        monthly_data = self.pg_repo.get_monthly_revenue(creator_id)
        highest_month_item = max(monthly_data, key=lambda x: x["amount"]) if monthly_data else None
        highest_month_str = f"Month {highest_month_item['month']}" if highest_month_item and highest_month_item["amount"] > 0 else "N/A"

        ad_summary = self.pg_repo.get_ad_revenue_summary(creator_id)
        platforms = ad_summary.get("platform_wise_earnings", {})
        highest_platform = max(platforms, key=platforms.get) if platforms else "N/A"

        top_creators = self.pg_repo.get_top_earning_creators(limit=1)
        top_creator_info = top_creators[0] if top_creators else None

        source_data = self.pg_repo.get_revenue_by_source(creator_id)
        total_source_rev = sum((s["amount"] for s in source_data), Decimal("0.00"))
        dist_dict: Dict[str, Decimal] = {}
        for s in source_data:
            pct = (s["amount"] / total_source_rev * 100) if total_source_rev > 0 else Decimal("0.0")
            dist_dict[s["source_name"]] = round(pct, 2)

        top_source = max(source_data, key=lambda x: x["amount"])["source_name"] if source_data else "N/A"
        avg_monthly = total_source_rev / Decimal("12.0")

        current_m = date.today().month
        curr_month_rev = next((m["amount"] for m in monthly_data if m["month"] == current_m), Decimal("0.00"))
        prev_m = (current_m - 1) if current_m > 1 else 12
        prev_month_rev = next((m["amount"] for m in monthly_data if m["month"] == prev_m), Decimal("0.00"))

        has_loss = False
        loss_reason = "No significant loss detected."
        drop_pct = 0.0

        if prev_month_rev > 0 and curr_month_rev < prev_month_rev:
            drop_pct = float(((prev_month_rev - curr_month_rev) / prev_month_rev) * 100)
            if drop_pct >= 20.0:
                has_loss = True
                loss_reason = f"Revenue dropped by {round(drop_pct, 1)}% from Month {prev_m} to Month {current_m}."

        return {
            "creator_id": creator_id,
            "highest_earning_month": highest_month_str,
            "highest_earning_platform": highest_platform,
            "highest_earning_creator": top_creator_info,
            "revenue_distribution": dist_dict,
            "average_monthly_revenue": round(avg_monthly, 2),
            "top_revenue_source": top_source,
            "loss_detection": {
                "has_loss": has_loss,
                "drop_percentage": round(drop_pct, 2),
                "reason": loss_reason,
            },
        }

    # ── Formatting Helpers ────────────────────────────────────────────────

    def _format_tx(self, t: RevenueTransactionModel) -> Dict[str, Any]:
        return {
            "transaction_id": t.transaction_id,
            "creator_id": t.creator_id,
            "platform": t.platform,
            "revenue_source": t.revenue_source,
            "amount": Decimal(str(t.amount)),
            "currency": t.currency,
            "transaction_date": t.transaction_date,
            "month": t.month,
            "created_at": t.created_at,
        }

    def _format_sp(self, s: SponsorshipModel) -> Dict[str, Any]:
        return {
            "sponsorship_id": s.sponsorship_id,
            "creator_id": s.creator_id,
            "brand_name": s.brand_name,
            "campaign_name": s.campaign_name,
            "platform": s.platform,
            "contract_amount": Decimal(str(s.contract_amount or 0)),
            "amount_received": Decimal(str(s.amount_received or 0)),
            "status": s.status,
            "start_date": s.start_date,
            "end_date": s.end_date,
            "created_at": s.created_at,
        }

    def _format_sub(self, sub: SubscriptionRevenueModel) -> Dict[str, Any]:
        return {
            "subscription_id": sub.subscription_id,
            "creator_id": sub.creator_id,
            "platform": sub.platform,
            "month": sub.month,
            "subscribers": sub.subscribers,
            "revenue": Decimal(str(sub.revenue or 0)),
            "created_at": sub.created_at,
        }

    def _format_bc(self, b: BrandCollaborationModel) -> Dict[str, Any]:
        return {
            "collaboration_id": b.collaboration_id,
            "creator_id": b.creator_id,
            "sponsorship_id": b.sponsorship_id,
            "deliverables": b.deliverables,
            "campaign_status": b.campaign_status,
            "completion_percentage": b.completion_percentage,
            "payment_status": b.payment_status,
            "remarks": b.remarks,
        }
