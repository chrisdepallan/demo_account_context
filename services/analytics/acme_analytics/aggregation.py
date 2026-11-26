"""Daily, weekly and monthly roll-ups, finality and history cut-offs.

Days are cut at midnight in the workspace time zone. Weeks are ISO weeks
(Monday start) and months are calendar months.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from typing import Callable, Dict, Iterable, List, Mapping

GRANULARITIES = ("daily", "weekly", "monthly")

#: A day's figures become final this long after the day ends.
LATE_EVENT_WINDOW = timedelta(hours=48)

#: Today's figures refresh this often.
REFRESH_INTERVAL = timedelta(minutes=15)

#: Individual events are kept this long; after that only totals remain.
RAW_EVENT_RETENTION_DAYS = 90

#: Analytics history per plan, in days counted back from today.
HISTORY_DAYS: Dict[str, int] = {
    "free": 30,
    "starter": 90,
    "pro": 365,
    "business": 730,
    "enterprise": 1825,
}

_METHODS: Dict[str, Callable[[List[float]], float]] = {
    "sum": lambda values: float(sum(values)),
    "mean": lambda values: sum(values) / len(values),
    "max": lambda values: float(max(values)),
    "last": lambda values: float(values[-1]),
}


def local_day(moment: datetime, tz: tzinfo = timezone.utc) -> date:
    """Return the calendar day of an aware datetime in the workspace time zone."""
    if moment.tzinfo is None:
        raise ValueError("moment must be timezone-aware")
    return moment.astimezone(tz).date()


def daily_counts(moments: Iterable[datetime], tz: tzinfo = timezone.utc) -> Dict[date, int]:
    """Count events per day in the workspace time zone."""
    return dict(Counter(local_day(m, tz) for m in moments))


def bucket_start(day: date, granularity: str) -> date:
    """Return the first day of the bucket that ``day`` falls in."""
    if granularity == "daily":
        return day
    if granularity == "weekly":
        return day - timedelta(days=day.weekday())
    if granularity == "monthly":
        return day.replace(day=1)
    raise ValueError(f"granularity must be one of {GRANULARITIES}")


def rollup(daily: Mapping[date, float], granularity: str, method: str = "sum") -> Dict[date, float]:
    """Combine daily values into buckets keyed by the bucket's first day.

    ``method`` is ``sum`` for counts (tasks completed), ``mean`` or ``max``
    for levels, and ``last`` for end-of-period values such as storage used.
    Active members must not be rolled up this way: recount them instead.
    """
    if method not in _METHODS:
        raise ValueError(f"method must be one of {sorted(_METHODS)}")
    grouped: Dict[date, List[float]] = defaultdict(list)
    for day in sorted(daily):
        grouped[bucket_start(day, granularity)].append(daily[day])
    return {start: _METHODS[method](values) for start, values in grouped.items()}


def fill_gaps(daily: Mapping[date, float], start: date, end: date, fill: float = 0.0) -> Dict[date, float]:
    """Return one value for every day from ``start`` to ``end`` inclusive."""
    if end < start:
        raise ValueError("end must not be before start")
    days = (end - start).days + 1
    return {start + timedelta(days=n): daily.get(start + timedelta(days=n), fill) for n in range(days)}


def is_day_final(day: date, now: datetime, tz: tzinfo = timezone.utc) -> bool:
    """A day is final 48 hours after it ends in the workspace time zone."""
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    day_end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz)
    return now >= day_end + LATE_EVENT_WINDOW


def history_days(plan: str) -> int:
    """Return the analytics history for a plan, in days."""
    key = plan.strip().lower()
    if key not in HISTORY_DAYS:
        raise ValueError(f"Unknown plan: {plan}")
    return HISTORY_DAYS[key]


def history_cutoff(plan: str, today: date) -> date:
    """Return the oldest day the plan can query."""
    return today - timedelta(days=history_days(plan))


def clip_to_history(daily: Mapping[date, float], plan: str, today: date) -> Dict[date, float]:
    """Drop days older than the plan's analytics history."""
    cutoff = history_cutoff(plan, today)
    return {day: value for day, value in daily.items() if day >= cutoff}


def can_split_by_member(day: date, today: date) -> bool:
    """Member and label splits need raw events, which are kept for 90 days."""
    return (today - day).days <= RAW_EVENT_RETENTION_DAYS


def choose_granularity(start: date, end: date, requested: str = "daily") -> str:
    """Daily detail is allowed for ranges of up to 366 days; longer is weekly."""
    if requested not in GRANULARITIES:
        raise ValueError(f"granularity must be one of {GRANULARITIES}")
    span = (end - start).days + 1
    if requested == "daily" and span > 366:
        return "weekly"
    return requested
