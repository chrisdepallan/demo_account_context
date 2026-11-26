"""First-response targets and business-hours arithmetic.

Source: ``services/support/docs/sla-and-escalation.md``.

Business hours are Monday–Friday, 08:00–18:00 US Central Time, so one
business day is 10 business hours. Every ``datetime`` passed to this module
must be naive and already expressed in US Central local time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Dict, Optional

PLANS = ("free", "starter", "pro", "business", "enterprise")
PRIORITIES = ("P1", "P2", "P3", "P4")

BUSINESS_OPEN = time(8, 0)
BUSINESS_CLOSE = time(18, 0)
BUSINESS_DAY_MINUTES = 600
_HOUR = 60
_DAY = BUSINESS_DAY_MINUTES


@dataclass(frozen=True)
class Target:
    """A first-response target: ``minutes`` on a business or 24/7 clock."""

    minutes: int
    around_the_clock: bool = False


def _bh(hours: int) -> Target:
    return Target(hours * _HOUR)


#: First-response targets. ``None`` means best effort (no target).
FIRST_RESPONSE: Dict[str, Dict[str, Optional[Target]]] = {
    "free": {p: None for p in PRIORITIES},
    "starter": {"P1": _bh(24), "P2": _bh(48), "P3": Target(3 * _DAY), "P4": Target(5 * _DAY)},
    "pro": {"P1": _bh(8), "P2": _bh(12), "P3": Target(1 * _DAY), "P4": Target(2 * _DAY)},
    "business": {"P1": _bh(2), "P2": _bh(4), "P3": _bh(8), "P4": Target(1 * _DAY)},
    "enterprise": {
        "P1": Target(30, around_the_clock=True),
        "P2": Target(2 * _HOUR, around_the_clock=True),
        "P3": _bh(4),
        "P4": Target(1 * _DAY),
    },
}


def target_for(plan: str, priority: str) -> Optional[Target]:
    """Return the first-response target, or ``None`` for best effort."""
    plan, priority = plan.lower(), priority.upper()
    if plan not in FIRST_RESPONSE:
        raise ValueError(f"unknown plan: {plan}")
    if priority not in PRIORITIES:
        raise ValueError(f"unknown priority: {priority}")
    return FIRST_RESPONSE[plan][priority]


def is_business_time(moment: datetime) -> bool:
    """Return True if ``moment`` falls inside business hours."""
    return moment.weekday() < 5 and BUSINESS_OPEN <= moment.time() < BUSINESS_CLOSE


def next_business_open(moment: datetime) -> datetime:
    """Return ``moment`` if inside business hours, else the next opening time."""
    if is_business_time(moment):
        return moment
    day = moment
    if moment.weekday() < 5 and moment.time() >= BUSINESS_CLOSE:
        day = moment + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return datetime.combine(day.date(), BUSINESS_OPEN)


def add_business_minutes(start: datetime, minutes: int) -> datetime:
    """Add ``minutes`` of business time to ``start``.

    A ticket created on Friday at 17:00 with an 8 business hour target is
    due on Monday at 15:00.
    """
    if minutes < 0:
        raise ValueError("minutes must not be negative")
    current = next_business_open(start)
    remaining = minutes
    while True:
        close = datetime.combine(current.date(), BUSINESS_CLOSE)
        available = int((close - current).total_seconds() // 60)
        if remaining <= available:
            return current + timedelta(minutes=remaining)
        remaining -= available
        current = next_business_open(close)


def business_minutes_between(start: datetime, end: datetime) -> int:
    """Return the business minutes elapsed between ``start`` and ``end``."""
    if end <= start:
        return 0
    total = 0
    current = next_business_open(start)
    while current < end:
        close = datetime.combine(current.date(), BUSINESS_CLOSE)
        total += int((min(close, end) - current).total_seconds() // 60)
        current = next_business_open(close)
    return total


def first_response_due(plan: str, priority: str, created_at: datetime) -> Optional[datetime]:
    """Return when the first human reply is due, or ``None`` for best effort."""
    target = target_for(plan, priority)
    if target is None:
        return None
    if target.around_the_clock:
        return created_at + timedelta(minutes=target.minutes)
    return add_business_minutes(created_at, target.minutes)


def is_breached(plan: str, priority: str, created_at: datetime,
                first_reply_at: Optional[datetime], now: datetime) -> bool:
    """Return True if the first-response target was or is being missed.

    Only a human reply stops the clock; automatic acknowledgements do not.
    Best-effort tickets (Free plan) can never breach.
    """
    due = first_response_due(plan, priority, created_at)
    if due is None:
        return False
    return (first_reply_at if first_reply_at is not None else now) > due


def minutes_until_breach(plan: str, priority: str, created_at: datetime,
                         now: datetime) -> Optional[int]:
    """Return minutes left on the target clock (negative once breached)."""
    target = target_for(plan, priority)
    if target is None:
        return None
    if target.around_the_clock:
        return target.minutes - int((now - created_at).total_seconds() // 60)
    due = add_business_minutes(created_at, target.minutes)
    if now <= due:
        return business_minutes_between(now, due)
    return -business_minutes_between(due, now)
