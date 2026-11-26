"""Retention window per plan and purge eligibility.

Retention follows ``services/accounts/docs/plans-and-limits.md``:

- Free and Starter – no audit log
- Pro – 90 days
- Business – 1 year (365 days)
- Enterprise – 7 years (2,555 days)

Entries older than the window are removed by a purge job that runs once a
day at 02:00 UTC. Two things delay a purge:

- **Downgrade grace** – after a downgrade to a plan with a shorter window,
  nothing is purged under the new window until 30 days after the downgrade.
- **Legal hold** – Enterprise accounts can pause purging completely.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Tuple

RETENTION_DAYS: Dict[str, int] = {
    "free": 0,
    "starter": 0,
    "pro": 90,
    "business": 365,
    "enterprise": 2555,
}
DOWNGRADE_GRACE_DAYS = 30
PURGE_HOUR_UTC = 2
LEGAL_HOLD_PLANS = ("enterprise",)


def _normalise(plan: str) -> str:
    key = plan.strip().lower()
    if key not in RETENTION_DAYS:
        raise ValueError(f"unknown plan {plan!r}")
    return key


def retention_days(plan: str) -> int:
    """Return the retention window of ``plan`` in days (0 = no audit log).

    :raises ValueError: if the plan name is not known.
    """
    return RETENTION_DAYS[_normalise(plan)]


def has_audit_log(plan: str) -> bool:
    """Return True for Pro, Business and Enterprise."""
    return retention_days(plan) > 0


def expires_at(occurred_at: datetime, plan: str) -> Optional[datetime]:
    """Return when an entry leaves the retention window.

    Returns ``None`` on plans without an audit log, because nothing is
    recorded there in the first place.
    """
    days = retention_days(plan)
    return occurred_at + timedelta(days=days) if days else None


def is_purge_eligible(
    occurred_at: datetime,
    plan: str,
    now: datetime,
    *,
    legal_hold: bool = False,
    downgraded_at: Optional[datetime] = None,
) -> bool:
    """Decide whether the purge job may delete an entry.

    :param occurred_at: when the recorded action happened.
    :param plan: the account's current plan.
    :param now: the time of the purge run.
    :param legal_hold: purging is paused; honoured on Enterprise only.
    :param downgraded_at: when the account moved to its current, shorter
        retention window, if it did.
    """
    plan_key = _normalise(plan)
    if legal_hold and plan_key in LEGAL_HOLD_PLANS:
        return False
    eligible_from = occurred_at + timedelta(days=RETENTION_DAYS[plan_key])
    if downgraded_at is not None:
        grace_end = downgraded_at + timedelta(days=DOWNGRADE_GRACE_DAYS)
        eligible_from = max(eligible_from, grace_end)
    return now >= eligible_from


def select_purgeable(
    entries: Iterable[Tuple[str, datetime]],
    plan: str,
    now: datetime,
    *,
    legal_hold: bool = False,
    downgraded_at: Optional[datetime] = None,
) -> List[str]:
    """Return the IDs of the entries the purge job should delete.

    ``entries`` is an iterable of ``(entry_id, occurred_at)`` pairs. Because
    the log is a hash chain, only a prefix of the log may be purged: the
    scan stops at the first entry that must be kept.
    """
    purgeable: List[str] = []
    for entry_id, occurred_at in sorted(entries, key=lambda pair: pair[1]):
        if not is_purge_eligible(
            occurred_at, plan, now, legal_hold=legal_hold, downgraded_at=downgraded_at
        ):
            break
        purgeable.append(entry_id)
    return purgeable


def next_purge_run(now: datetime) -> datetime:
    """Return the next daily purge run (02:00 UTC) strictly after ``now``."""
    now_utc = now.astimezone(timezone.utc)
    run = datetime.combine(now_utc.date(), time(PURGE_HOUR_UTC), tzinfo=timezone.utc)
    return run if run > now_utc else run + timedelta(days=1)
