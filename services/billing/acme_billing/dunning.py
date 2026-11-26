"""Failed-payment (dunning) schedule.

Source: ``services/billing/docs/payment-methods.md``.

- Day 0 – the charge fails, the account becomes ``past_due``.
- Days 1, 3, 7 and 14 – the payment is retried automatically.
- Day 14 – if still unpaid, the account becomes ``read_only``.
- Day 44 – if still unpaid, the account is downgraded to Free.

Days 0–13 are the 14-day grace period: the account stays fully active.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Tuple

RETRY_DAYS: Tuple[int, ...] = (1, 3, 7, 14)
GRACE_PERIOD_DAYS = 14
READ_ONLY_DAY = 14
DOWNGRADE_DAY = 44
RESTORE_ACCESS_MINUTES = 5

STATUS_ACTIVE = "active"
STATUS_PAST_DUE = "past_due"
STATUS_READ_ONLY = "read_only"
STATUS_DOWNGRADED = "downgraded_to_free"


@dataclass(frozen=True)
class DunningStep:
    """One step of the schedule: the day offset, its date and what happens."""

    day: int
    on: date
    action: str
    status_after: str


def days_since_failure(failed_on: date, today: date) -> int:
    """Return whole days since the first failed charge (Day 0)."""
    days = (today - failed_on).days
    if days < 0:
        raise ValueError("today is before the failed charge")
    return days


def status_on_day(day: int, paid: bool = False) -> str:
    """Return the account status ``day`` days after the failed charge.

    ``paid`` means the outstanding balance has been settled, which restores
    ``active`` at any point before the Day 44 downgrade.
    """
    if day < 0:
        raise ValueError("day must not be negative")
    if day >= DOWNGRADE_DAY:
        return STATUS_DOWNGRADED
    if paid:
        return STATUS_ACTIVE
    return STATUS_READ_ONLY if day >= READ_ONLY_DAY else STATUS_PAST_DUE


def account_status(failed_on: date, today: date, paid_on: Optional[date] = None) -> str:
    """Return the status on ``today`` for a charge that failed on ``failed_on``.

    A payment made before Day 44 restores ``active``. A payment made on or
    after Day 44 does not undo the downgrade to Free.
    """
    day = days_since_failure(failed_on, today)
    if (paid_on is not None and paid_on <= today
            and days_since_failure(failed_on, paid_on) < DOWNGRADE_DAY):
        return STATUS_ACTIVE
    return status_on_day(day)


def retry_dates(failed_on: date) -> List[date]:
    """Return the four automatic retry dates (Days 1, 3, 7 and 14)."""
    return [failed_on + timedelta(days=d) for d in RETRY_DAYS]


def next_retry(failed_on: date, today: date) -> Optional[date]:
    """Return the next automatic retry on or after ``today``, or ``None``."""
    for retry in retry_dates(failed_on):
        if retry >= today:
            return retry
    return None


def in_grace_period(failed_on: date, today: date) -> bool:
    """Return True while the account is still fully active (Days 0–13)."""
    return 0 <= (today - failed_on).days < GRACE_PERIOD_DAYS


def is_full_access(status: str) -> bool:
    """Return True if members can still create and edit content."""
    return status in (STATUS_ACTIVE, STATUS_PAST_DUE)


def schedule(failed_on: date) -> List[DunningStep]:
    """Return the full dunning timeline for a charge that failed on ``failed_on``."""
    steps = [DunningStep(0, failed_on, "charge_failed_email_owner_and_billing_admins",
                         STATUS_PAST_DUE)]
    for day in RETRY_DAYS:
        final = day == READ_ONLY_DAY
        steps.append(DunningStep(
            day, failed_on + timedelta(days=day),
            "retry_then_read_only_if_unpaid" if final else "retry_payment",
            STATUS_READ_ONLY if final else STATUS_PAST_DUE,
        ))
    steps.append(DunningStep(DOWNGRADE_DAY, failed_on + timedelta(days=DOWNGRADE_DAY),
                             "downgrade_to_free", STATUS_DOWNGRADED))
    return steps
