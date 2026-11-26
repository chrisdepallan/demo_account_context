"""Metric definitions and calculations.

Each function implements one definition from
``services/analytics/docs/metric-definitions.md``. Percentages and durations
are rounded once, at the end, to 1 decimal place with halves rounded up.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, List, Optional, Sequence

#: Actions that make a member "active". Signing in or viewing does not count.
QUALIFYING_ACTIONS = frozenset(
    {
        "task.created",
        "task.edited",
        "task.completed",
        "comment.added",
        "file.uploaded",
        "file.edited",
        "project.created",
        "project.edited",
    }
)

#: Rolling windows, in days, ending on the selected day.
ACTIVE_WINDOWS = {"daily": 1, "weekly": 7, "monthly": 28}

CYCLE_TIME_PERCENTILE = 85


@dataclass(frozen=True)
class ActivityEvent:
    """One action by one person on one day (workspace time zone)."""

    member_id: str
    day: date
    action: str
    is_guest: bool = False


@dataclass(frozen=True)
class Task:
    """The timestamps of a task that the metrics need."""

    created_at: datetime
    started_at: Optional[datetime] = None  # first move to In progress
    completed_at: Optional[datetime] = None  # last completion if reopened
    cancelled: bool = False
    due_date: Optional[date] = None


def round_half_up(value: float, places: int = 1) -> float:
    """Round to ``places`` decimals with halves rounded up (74.95 -> 75.0)."""
    quantum = Decimal(1).scaleb(-places)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def percentage(numerator: int, denominator: int) -> Optional[float]:
    """Return ``numerator / denominator`` as a percentage, or None if undefined."""
    if denominator <= 0:
        return None
    exact = Decimal(numerator) * 100 / Decimal(denominator)
    return float(exact.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def active_members(events: Iterable[ActivityEvent], end_day: date, window: str = "daily") -> int:
    """Count distinct members with a qualifying action in the window.

    The window is 1, 7 or 28 days ending on ``end_day`` inclusive. Guests are
    never counted.
    """
    if window not in ACTIVE_WINDOWS:
        raise ValueError(f"window must be one of {sorted(ACTIVE_WINDOWS)}")
    start_day = end_day - timedelta(days=ACTIVE_WINDOWS[window] - 1)
    return len(
        {
            e.member_id
            for e in events
            if not e.is_guest and e.action in QUALIFYING_ACTIONS and start_day <= e.day <= end_day
        }
    )


def _was_open_in_period(task: Task, start: date, end: date) -> bool:
    if task.cancelled or task.created_at.date() > end:
        return False
    return task.completed_at is None or task.completed_at.date() >= start


def _completed_in_period(task: Task, start: date, end: date) -> bool:
    return (
        not task.cancelled
        and task.completed_at is not None
        and start <= task.completed_at.date() <= end
    )


def task_completion_rate(tasks: Iterable[Task], start: date, end: date) -> Optional[float]:
    """Tasks completed in the period over tasks open at any time in it.

    Cancelled tasks are left out. Returns None when no task was open.
    """
    tasks = list(tasks)
    open_count = sum(1 for t in tasks if _was_open_in_period(t, start, end))
    done_count = sum(1 for t in tasks if _was_open_in_period(t, start, end) and _completed_in_period(t, start, end))
    return percentage(done_count, open_count)


def _days_between(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / 86400


def cycle_time_days(task: Task) -> Optional[float]:
    """Unrounded days from first In progress to completion, or None."""
    if task.cancelled or task.started_at is None or task.completed_at is None:
        return None
    return _days_between(task.started_at, task.completed_at)


def lead_time_days(task: Task) -> Optional[float]:
    """Unrounded days from creation to completion, or None if not completed."""
    if task.cancelled or task.completed_at is None:
        return None
    return _days_between(task.created_at, task.completed_at)


def cycle_times(tasks: Iterable[Task], start: date, end: date) -> List[float]:
    """Cycle times of tasks completed in the period, sorted ascending."""
    values = [cycle_time_days(t) for t in tasks if _completed_in_period(t, start, end)]
    return sorted(v for v in values if v is not None)


def median_days(values: Sequence[float]) -> Optional[float]:
    """Median of the values, rounded to 1 decimal, or None if empty."""
    if not values:
        return None
    return round_half_up(statistics.median(values))


def percentile_days(values: Sequence[float], percentile: int = CYCLE_TIME_PERCENTILE) -> Optional[float]:
    """Nearest-rank percentile: the value that ``percentile``% are at or below."""
    if not values:
        return None
    if not 0 < percentile <= 100:
        raise ValueError("percentile must be between 1 and 100")
    ordered = sorted(values)
    rank = math.ceil(percentile / 100 * len(ordered))
    return round_half_up(ordered[rank - 1])


def overdue_rate(tasks: Iterable[Task], today: date) -> Optional[float]:
    """Open tasks past their due date over open tasks that have a due date.

    A task is overdue from the day after its due date.
    """
    with_due = [t for t in tasks if not t.cancelled and t.completed_at is None and t.due_date is not None]
    overdue = sum(1 for t in with_due if today > t.due_date)
    return percentage(overdue, len(with_due))


def seat_utilisation(monthly_active_members: int, paid_seats: int) -> Optional[float]:
    """Monthly (28-day) active members over paid seats, as a percentage."""
    return percentage(monthly_active_members, paid_seats)
