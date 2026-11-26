"""Daily and weekly digest rules.

A digest is one email listing a user's unread in-app notifications. Daily
digests go out at 08:00 local time and cover the previous 24 hours; weekly
digests go out on Monday at 08:00 and cover the previous 7 days. A digest
holds at most 50 items and is not sent when there is nothing unread.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Dict, Iterable, List, Optional, Tuple

FREQUENCIES: Tuple[str, ...] = ("off", "daily", "weekly")
DEFAULT_FREQUENCY = "daily"
SEND_TIME = time(8, 0)
WEEKLY_SEND_WEEKDAY = 0  # Monday, as in datetime.weekday()
MAX_DIGEST_ITEMS = 50
OTHER_GROUP = "Other"

_WINDOWS: Dict[str, timedelta] = {"daily": timedelta(hours=24), "weekly": timedelta(days=7)}


@dataclass(frozen=True)
class DigestItem:
    """One in-app notification that may appear in a digest."""

    notification_id: str
    notification_type: str
    title: str
    created_at: datetime
    project_id: Optional[str] = None
    read: bool = False


@dataclass
class DigestGroup:
    """Notifications for one project (or the "Other" group), newest first."""

    key: str
    items: List[DigestItem] = field(default_factory=list)


@dataclass
class Digest:
    """A digest ready to render. ``overflow_count`` is the "and N more" number."""

    frequency: str
    window_start: datetime
    window_end: datetime
    groups: List[DigestGroup]
    overflow_count: int = 0

    @property
    def item_count(self) -> int:
        """Number of notifications listed in the digest (never above 50)."""
        return sum(len(group.items) for group in self.groups)


def digest_window(frequency: str, now: datetime) -> Tuple[datetime, datetime]:
    """Return the (start, end) period a digest sent at ``now`` covers."""
    _require_sendable(frequency)
    return now - _WINDOWS[frequency], now


def scheduled_send_time(frequency: str, local_now: datetime) -> datetime:
    """Return the most recent scheduled send time at or before ``local_now``.

    ``local_now`` must already be in the user's time zone.
    """
    _require_sendable(frequency)
    candidate = local_now.replace(
        hour=SEND_TIME.hour, minute=SEND_TIME.minute, second=0, microsecond=0
    )
    if frequency == "weekly":
        candidate -= timedelta(days=(candidate.weekday() - WEEKLY_SEND_WEEKDAY) % 7)
    if candidate > local_now:
        candidate -= timedelta(days=1 if frequency == "daily" else 7)
    return candidate


def is_digest_due(
    frequency: str, local_now: datetime, last_sent: Optional[datetime] = None
) -> bool:
    """Return True if a digest should be sent now.

    A digest is due when the latest scheduled send time has passed and no
    digest has been sent since. ``off`` is never due.
    """
    if frequency not in FREQUENCIES:
        raise ValueError(f"unknown digest frequency: {frequency!r}")
    if frequency == "off":
        return False
    scheduled = scheduled_send_time(frequency, local_now)
    return last_sent is None or last_sent < scheduled


def build_digest(
    items: Iterable[DigestItem],
    frequency: str,
    now: datetime,
    max_items: int = MAX_DIGEST_ITEMS,
) -> Optional[Digest]:
    """Build the digest for ``items``, or return None when nothing should be sent.

    Only unread notifications created inside the digest window are included.
    The newest ``max_items`` are kept; the rest are counted in
    ``overflow_count``. Groups are ordered by their most recent notification.
    """
    if frequency == "off":
        return None
    start, end = digest_window(frequency, now)
    unread = [item for item in items if not item.read and start < item.created_at <= end]
    if not unread:
        return None
    unread.sort(key=lambda item: item.created_at, reverse=True)
    kept, overflow = unread[:max_items], max(0, len(unread) - max_items)

    groups: Dict[str, DigestGroup] = {}
    for item in kept:  # dict order keeps groups sorted by newest item
        key = item.project_id or OTHER_GROUP
        groups.setdefault(key, DigestGroup(key=key)).items.append(item)
    return Digest(
        frequency=frequency,
        window_start=start,
        window_end=end,
        groups=list(groups.values()),
        overflow_count=overflow,
    )


def _require_sendable(frequency: str) -> None:
    if frequency not in _WINDOWS:
        raise ValueError(f"digest frequency must be 'daily' or 'weekly', got {frequency!r}")
