"""Refund eligibility, approval thresholds and SLA service credits.

Source: ``services/billing/docs/refunds.md``. Approval thresholds are in US
dollars.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Dict, Optional

from .pricing import quantize

ANNUAL_REFUND_WINDOW_DAYS = 30
AGENT_LIMIT = Decimal("500")
TEAM_LEAD_LIMIT = Decimal("5000")
GOODWILL_INTERVAL_DAYS = 365
SLA_CREDIT_REQUEST_DAYS = 30
SLA_CREDIT_CAP_PERCENT = 50
CHARGEBACK_DISPUTE_FEE = Decimal("15.00")

APPROVER_AGENT = "support_agent"
APPROVER_TEAM_LEAD = "support_team_lead"
APPROVER_BILLING_MANAGER = "billing_manager"
_APPROVER_ORDER = (APPROVER_AGENT, APPROVER_TEAM_LEAD, APPROVER_BILLING_MANAGER)

#: Reasons that are always refunded in full because the charge was wrong.
ERROR_REASONS = ("duplicate_charge", "charged_after_cancel")

#: Monthly uptime SLA per plan, in percent. Free has no SLA.
UPTIME_SLA: Dict[str, Decimal] = {
    "starter": Decimal("99.9"), "pro": Decimal("99.9"),
    "business": Decimal("99.95"), "enterprise": Decimal("99.99"),
}


def required_approver(amount: Decimal, goodwill: bool = False) -> str:
    """Return the role that must approve a refund of ``amount`` US dollars.

    Up to 500 – any support agent; 500.01–5,000 – support team lead; over
    5,000 – billing manager. Goodwill refunds need at least a team lead.
    """
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("refund amount must be positive")
    if amount > TEAM_LEAD_LIMIT:
        return APPROVER_BILLING_MANAGER
    if amount > AGENT_LIMIT or goodwill:
        return APPROVER_TEAM_LEAD
    return APPROVER_AGENT


def can_approve(role: str, amount: Decimal, goodwill: bool = False) -> bool:
    """Return True if ``role`` may approve the refund on its own."""
    if role not in _APPROVER_ORDER:
        raise ValueError(f"unknown role: {role}")
    needed = required_approver(amount, goodwill)
    return _APPROVER_ORDER.index(role) >= _APPROVER_ORDER.index(needed)


def is_refundable(cycle: str, purchased_on: date, requested_on: date,
                  reason: str = "cancellation") -> bool:
    """Return True if the charge qualifies for a cash refund under the policy.

    Annual plans are refundable within 30 days of purchase or renewal.
    Monthly plans are not refunded for the current month. Duplicate charges
    and charges made after cancelling are always refunded. Removed seats get
    a prorated credit on the next invoice instead of a refund.
    """
    if reason in ERROR_REASONS:
        return True
    if reason == "seats_removed":
        return False
    if cycle.lower() == "annual":
        return 0 <= (requested_on - purchased_on).days <= ANNUAL_REFUND_WINDOW_DAYS
    return False


def goodwill_allowed(last_goodwill_on: Optional[date], today: date) -> bool:
    """Goodwill refunds are limited to one per account per 12 months."""
    return last_goodwill_on is None or (today - last_goodwill_on).days >= GOODWILL_INTERVAL_DAYS


def sla_credit_percent(plan: str, monthly_uptime: Decimal) -> int:
    """Return the service credit as a percentage of the monthly fee.

    Below the SLA of the plan down to 99.0% – 10%; 95.0% up to 99.0% – 25%;
    below 95.0% – 50%. Uptime at or above the SLA earns no credit.
    """
    plan = plan.lower()
    if plan not in UPTIME_SLA:
        raise ValueError(f"{plan} has no uptime SLA")
    uptime = Decimal(str(monthly_uptime))
    if not Decimal("0") <= uptime <= Decimal("100"):
        raise ValueError("uptime must be between 0 and 100")
    if uptime >= UPTIME_SLA[plan]:
        return 0
    if uptime >= Decimal("99.0"):
        return 10
    if uptime >= Decimal("95.0"):
        return 25
    return SLA_CREDIT_CAP_PERCENT


def sla_credit_amount(plan: str, monthly_uptime: Decimal, monthly_fee: Decimal) -> Decimal:
    """Return the service credit amount, applied to the next invoice."""
    return quantize(Decimal(monthly_fee) * sla_credit_percent(plan, monthly_uptime) / 100)


def sla_credit_request_open(month_end: date, requested_on: date) -> bool:
    """Credits must be requested within 30 days of the end of the month."""
    return 0 <= (requested_on - month_end).days <= SLA_CREDIT_REQUEST_DAYS
