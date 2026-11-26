"""Sync cursor, retry delays and conflict resolution rules.

Incremental sync reads everything changed since a cursor. Conflicts are
settled per field: the later change wins, unless both changes fall within
60 seconds of each other, in which case the source of truth wins.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Mapping, Optional

CURSOR_TTL = timedelta(days=7)
INCREMENTAL_INTERVAL = timedelta(minutes=5)
FULL_INTERVAL = timedelta(hours=24)
MANUAL_COOLDOWN = timedelta(minutes=15)
CONFLICT_WINDOW = timedelta(seconds=60)
PAGE_SIZE = 200
MAX_ATTEMPTS = 6
BASE_RETRY_DELAY = timedelta(minutes=1)

ORIGIN_ACME = "acme"
ORIGIN_REMOTE = "remote"
_ORIGINS = (ORIGIN_ACME, ORIGIN_REMOTE)


@dataclass(frozen=True)
class SyncCursor:
    """Opaque marker of how far the last incremental sync read."""

    value: str
    issued_at: datetime

    def expires_at(self) -> datetime:
        """A cursor is valid for 7 days after it was issued."""
        return self.issued_at + CURSOR_TTL

    def is_expired(self, now: datetime) -> bool:
        """Return True once the cursor is 7 days old or older."""
        return now >= self.expires_at()


@dataclass(frozen=True)
class FieldChange:
    """A change to one field of a linked item on one side."""

    field: str
    value: Any
    changed_at: datetime
    origin: str

    def __post_init__(self) -> None:
        if self.origin not in _ORIGINS:
            raise ValueError(f"origin must be one of {_ORIGINS}")


def next_sync_mode(cursor: Optional[SyncCursor], last_full_at: Optional[datetime], now: datetime) -> str:
    """Return ``"full"`` or ``"incremental"`` for the next run.

    A full sync runs when there is no cursor, the cursor has expired, no full
    sync has ever run, or the last full sync was 24 hours ago or more.
    """
    if cursor is None or cursor.is_expired(now):
        return "full"
    if last_full_at is None or now - last_full_at >= FULL_INTERVAL:
        return "full"
    return "incremental"


def next_scheduled_run(last_run_at: datetime) -> datetime:
    """Incremental sync runs every 5 minutes."""
    return last_run_at + INCREMENTAL_INTERVAL


def can_manual_sync(last_manual_at: Optional[datetime], now: datetime) -> bool:
    """A manual sync is allowed once every 15 minutes per install."""
    return last_manual_at is None or now - last_manual_at >= MANUAL_COOLDOWN


def manual_sync_retry_after(last_manual_at: Optional[datetime], now: datetime) -> int:
    """Return the seconds to wait before another manual sync (0 if allowed)."""
    if can_manual_sync(last_manual_at, now):
        return 0
    remaining = last_manual_at + MANUAL_COOLDOWN - now
    return int(remaining.total_seconds())


def retry_delay(attempt: int) -> Optional[timedelta]:
    """Return the wait after failed attempt number ``attempt`` (1-based).

    Delays are 1, 2, 4, 8 and 16 minutes. After the 6th attempt there is no
    further retry and ``None`` is returned.
    """
    if attempt < 1:
        raise ValueError("attempt starts at 1")
    if attempt >= MAX_ATTEMPTS:
        return None
    return BASE_RETRY_DELAY * (2 ** (attempt - 1))


def page_count(item_count: int) -> int:
    """Return how many pages of 200 are needed to read ``item_count`` items."""
    if item_count < 0:
        raise ValueError("item_count cannot be negative")
    return -(-item_count // PAGE_SIZE)


def resolve_conflict(local: FieldChange, remote: FieldChange, source_of_truth: str = ORIGIN_ACME) -> FieldChange:
    """Pick the winning change when both sides changed the same field.

    The later change wins. If the two changes are within 60 seconds of each
    other, the change from the source of truth wins.
    """
    if local.field != remote.field:
        raise ValueError("resolve_conflict needs two changes to the same field")
    if source_of_truth not in _ORIGINS:
        raise ValueError(f"source_of_truth must be one of {_ORIGINS}")
    if abs(local.changed_at - remote.changed_at) <= CONFLICT_WINDOW:
        return local if local.origin == source_of_truth else remote
    return local if local.changed_at > remote.changed_at else remote


def merge_changes(
    local: Mapping[str, FieldChange],
    remote: Mapping[str, FieldChange],
    source_of_truth: str = ORIGIN_ACME,
) -> Dict[str, FieldChange]:
    """Merge per-field changes from both sides into one winning set.

    Fields changed on only one side are kept as they are. Fields changed on
    both sides go through ``resolve_conflict``.
    """
    merged: Dict[str, FieldChange] = {}
    for name in sorted(set(local) | set(remote)):
        if name in local and name in remote:
            merged[name] = resolve_conflict(local[name], remote[name], source_of_truth)
        else:
            merged[name] = local[name] if name in local else remote[name]
    return merged


def resolve_delete(deleted_origin: str) -> str:
    """Deletes are never copied across: the surviving item is unlinked."""
    if deleted_origin not in _ORIGINS:
        raise ValueError(f"deleted_origin must be one of {_ORIGINS}")
    return "unlink"
