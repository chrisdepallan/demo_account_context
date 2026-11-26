"""Proration of mid-cycle seat and plan changes, and account credit.

Rules (``services/billing/docs/proration-and-credits.md``):

- Proration is by day. The day of the change counts as a remaining day.
- Adding seats or upgrading is charged immediately.
- Removing seats produces a credit on the next invoice, never a cash refund.
- Downgrades take effect at the end of the period and are not prorated.
- Account credit is applied to an invoice before the payment method is charged.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .pricing import PLANS, quantize, seat_price


class ProrationError(ValueError):
    """Raised when a proration request is not valid."""


@dataclass(frozen=True)
class ProrationResult:
    """Outcome of a mid-cycle change.

    ``amount`` is always positive; ``kind`` says whether it is a ``charge``
    (collected immediately) or a ``credit`` (applied to the next invoice).
    """

    kind: str
    amount: Decimal
    currency: str
    remaining_days: int
    cycle_days: int


def cycle_days(period_start: date, period_end: date) -> int:
    """Return the number of days in the cycle; ``period_end`` is exclusive."""
    days = (period_end - period_start).days
    if days <= 0:
        raise ProrationError("period_end must be after period_start")
    return days


def remaining_days(period_start: date, period_end: date, change_date: date) -> int:
    """Return the days left in the cycle, counting the day of the change."""
    if not period_start <= change_date < period_end:
        raise ProrationError("change_date must fall inside the billing period")
    return (period_end - change_date).days


def prorate(full_cycle_amount: Decimal, period_start: date, period_end: date,
            change_date: date) -> Decimal:
    """Scale ``full_cycle_amount`` by remaining days / cycle days, rounded half up."""
    total = cycle_days(period_start, period_end)
    left = remaining_days(period_start, period_end, change_date)
    return quantize(Decimal(full_cycle_amount) * left / total)


def seat_change(plan: str, cycle: str, currency: str, seat_delta: int,
                period_start: date, period_end: date, change_date: date) -> ProrationResult:
    """Prorate adding (positive ``seat_delta``) or removing (negative) seats.

    Adding 4 Pro monthly seats with 15 of 30 days left is a charge of 30.00 USD.
    """
    if seat_delta == 0:
        raise ProrationError("seat_delta must not be zero")
    full = seat_price(plan, cycle, currency) * abs(seat_delta)
    amount = prorate(full, period_start, period_end, change_date)
    return ProrationResult(
        kind="charge" if seat_delta > 0 else "credit",
        amount=amount,
        currency=currency.upper(),
        remaining_days=remaining_days(period_start, period_end, change_date),
        cycle_days=cycle_days(period_start, period_end),
    )


def plan_upgrade(old_plan: str, new_plan: str, cycle: str, currency: str, seats: int,
                 period_start: date, period_end: date, change_date: date) -> ProrationResult:
    """Prorate an upgrade: the price difference for the rest of the period.

    Downgrades are not prorated (they apply at the end of the period), so a
    ``new_plan`` that is not higher than ``old_plan`` raises ``ProrationError``.
    """
    old_plan, new_plan = old_plan.lower(), new_plan.lower()
    if old_plan not in PLANS or new_plan not in PLANS:
        raise ProrationError("unknown plan")
    if PLANS.index(new_plan) <= PLANS.index(old_plan):
        raise ProrationError("downgrades take effect at the end of the period and are not prorated")
    if seats < 1:
        raise ProrationError("seats must be at least 1")
    difference = seat_price(new_plan, cycle, currency) - seat_price(old_plan, cycle, currency)
    amount = prorate(difference * seats, period_start, period_end, change_date)
    return ProrationResult("charge", amount, currency.upper(),
                           remaining_days(period_start, period_end, change_date),
                           cycle_days(period_start, period_end))


@dataclass(frozen=True)
class CreditApplication:
    """Result of applying account credit to an invoice total."""

    credit_applied: Decimal
    amount_due: Decimal
    credit_remaining: Decimal


def apply_credit(invoice_total: Decimal, credit_balance: Decimal) -> CreditApplication:
    """Apply account credit to an invoice before charging the payment method.

    Credit never makes an invoice negative; any unused credit stays on the
    account for the following invoice.
    """
    invoice_total, credit_balance = Decimal(invoice_total), Decimal(credit_balance)
    if invoice_total < 0 or credit_balance < 0:
        raise ProrationError("invoice total and credit balance must not be negative")
    applied = min(invoice_total, credit_balance)
    return CreditApplication(quantize(applied), quantize(invoice_total - applied),
                             quantize(credit_balance - applied))


def next_monthly_charge_date(anchor_day: int, after: date) -> date:
    """Return the next monthly charge date strictly after ``after``.

    Charges fall on the same day each month as the first payment. If that day
    does not exist in a month (for example the 31st), the charge happens on
    the last day of that month.
    """
    if not 1 <= anchor_day <= 31:
        raise ProrationError("anchor_day must be between 1 and 31")
    year, month = after.year, after.month
    while True:
        day = min(anchor_day, calendar.monthrange(year, month)[1])
        candidate = date(year, month, day)
        if candidate > after:
            return candidate
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
