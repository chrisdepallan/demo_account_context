"""Scheduled report cadence, limits and next-run calculation.

A schedule is daily, weekly or monthly and is sent at a whole hour in the
workspace time zone (default 08:00). Monthly schedules set for a day the
month does not have are sent on the last day of that month.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple


class ScheduleError(ValueError):
    """Raised when a schedule breaks a rule."""


class Cadence(str, Enum):
    """How often a scheduled report is sent."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


#: Scheduled reports per workspace, paused ones included.
PLAN_SCHEDULE_LIMITS: Dict[str, int] = {
    "free": 0,
    "starter": 2,
    "pro": 10,
    "business": 50,
    "enterprise": 200,
}

FORMATS = frozenset({"pdf", "csv", "xlsx"})
DEFAULT_SEND_HOUR = 8
MAX_RECIPIENTS = 25
PAUSE_AFTER_FAILURES = 3
SYNC_EXPORT_ROW_LIMIT = 10_000
MAX_EXPORT_ROWS = 1_000_000
DOWNLOAD_LINK_TTL = timedelta(days=7)

_MANAGER_ROLES = frozenset({"owner", "admin"})
_RECIPIENT_ROLES = frozenset({"owner", "admin", "member"})


@dataclass
class ReportSchedule:
    """One scheduled report."""

    cadence: Cadence
    send_hour: int = DEFAULT_SEND_HOUR
    weekday: Optional[int] = None  # weekly only; 0 is Monday
    day_of_month: Optional[int] = None  # monthly only; 1-31
    report_format: str = "pdf"
    tz: tzinfo = timezone.utc
    paused: bool = False
    consecutive_failures: int = 0
    recipients: List[str] = field(default_factory=list)


def validate_schedule(schedule: ReportSchedule) -> ReportSchedule:
    """Check the fields of a schedule; raise ``ScheduleError`` if any is wrong."""
    if not 0 <= schedule.send_hour <= 23:
        raise ScheduleError("send_hour must be a whole hour from 0 to 23.")
    if schedule.report_format not in FORMATS:
        raise ScheduleError(f"format must be one of {sorted(FORMATS)}.")
    if schedule.cadence is Cadence.WEEKLY and (schedule.weekday is None or not 0 <= schedule.weekday <= 6):
        raise ScheduleError("A weekly schedule needs a weekday from 0 (Monday) to 6.")
    if schedule.cadence is Cadence.MONTHLY and (
        schedule.day_of_month is None or not 1 <= schedule.day_of_month <= 31
    ):
        raise ScheduleError("A monthly schedule needs a day of month from 1 to 31.")
    if len(schedule.recipients) > MAX_RECIPIENTS:
        raise ScheduleError(f"A schedule can have at most {MAX_RECIPIENTS} recipients.")
    return schedule


def schedule_limit(plan: str) -> int:
    """Return how many scheduled reports a workspace on ``plan`` may have."""
    key = plan.strip().lower()
    if key not in PLAN_SCHEDULE_LIMITS:
        raise ScheduleError(f"Unknown plan: {plan}")
    return PLAN_SCHEDULE_LIMITS[key]


def can_create_schedule(plan: str, existing_count: int, role: str) -> bool:
    """Only the Owner and Admins may create one, and only under the plan limit."""
    return role.strip().lower() in _MANAGER_ROLES and existing_count < schedule_limit(plan)


def eligible_recipients(members: Iterable[Tuple[str, str]]) -> List[str]:
    """Return the emails of people who may receive reports.

    ``members`` is ``(email, role)`` pairs. Owners, Admins and Members are
    eligible; Billing admins and Guests are not.
    """
    return [email for email, role in members if role.strip().lower() in _RECIPIENT_ROLES]


def _monthly_date(year: int, month: int, day_of_month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day_of_month, last_day))


def next_run(schedule: ReportSchedule, after: datetime) -> Optional[datetime]:
    """Return the next send time strictly after ``after``, in UTC.

    Returns None for a paused schedule. ``after`` must be timezone-aware.
    """
    validate_schedule(schedule)
    if after.tzinfo is None:
        raise ScheduleError("after must be timezone-aware.")
    if schedule.paused:
        return None
    local = after.astimezone(schedule.tz)
    send_at = time(schedule.send_hour, 0)

    def at(day: date) -> datetime:
        return datetime.combine(day, send_at, tzinfo=schedule.tz)

    if schedule.cadence is Cadence.DAILY:
        candidate = at(local.date())
        if candidate <= local:
            candidate = at(local.date() + timedelta(days=1))
    elif schedule.cadence is Cadence.WEEKLY:
        days_ahead = (schedule.weekday - local.weekday()) % 7
        candidate = at(local.date() + timedelta(days=days_ahead))
        if candidate <= local:
            candidate = at(local.date() + timedelta(days=days_ahead + 7))
    else:
        candidate = at(_monthly_date(local.year, local.month, schedule.day_of_month))
        if candidate <= local:
            year, month = (local.year + 1, 1) if local.month == 12 else (local.year, local.month + 1)
            candidate = at(_monthly_date(year, month, schedule.day_of_month))
    return candidate.astimezone(timezone.utc)


def report_period(cadence: Cadence, run_day: date) -> Tuple[date, date]:
    """Return the first and last day a report sent on ``run_day`` covers.

    Daily covers the previous day, weekly the 7 days ending the day before,
    and monthly the previous calendar month.
    """
    yesterday = run_day - timedelta(days=1)
    if cadence is Cadence.DAILY:
        return yesterday, yesterday
    if cadence is Cadence.WEEKLY:
        return run_day - timedelta(days=7), yesterday
    last_of_previous = run_day.replace(day=1) - timedelta(days=1)
    return last_of_previous.replace(day=1), last_of_previous


def record_delivery(schedule: ReportSchedule, succeeded: bool) -> ReportSchedule:
    """Track delivery results; pause after 3 consecutive failures."""
    if succeeded:
        schedule.consecutive_failures = 0
        return schedule
    schedule.consecutive_failures += 1
    if schedule.consecutive_failures >= PAUSE_AFTER_FAILURES:
        schedule.paused = True
    return schedule


def resume(schedule: ReportSchedule) -> ReportSchedule:
    """Resume a paused schedule and clear its failure count."""
    schedule.paused = False
    schedule.consecutive_failures = 0
    return schedule


def export_mode(row_count: int) -> str:
    """Return ``"immediate"`` up to 10,000 rows, ``"background"`` above that."""
    if row_count < 0:
        raise ScheduleError("row_count cannot be negative.")
    if row_count > MAX_EXPORT_ROWS:
        raise ScheduleError(f"An export can hold at most {MAX_EXPORT_ROWS} rows.")
    return "immediate" if row_count <= SYNC_EXPORT_ROW_LIMIT else "background"


def download_link_expiry(ready_at: datetime) -> datetime:
    """Download links are valid for 7 days after the export is ready."""
    return ready_at + DOWNLOAD_LINK_TTL
