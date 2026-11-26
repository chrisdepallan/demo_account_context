"""Version retention and trash expiry.

Implements ``docs/versioning-and-trash.md``: older versions are kept for the
plan's version history window (counted from when they were replaced), a file
keeps at most 100 versions, and trashed files are purged after 30 days.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence

#: Version history window in days. None means unlimited (Enterprise).
VERSION_RETENTION_DAYS: Dict[str, Optional[int]] = {
    "free": 7,
    "starter": 30,
    "pro": 180,
    "business": 365,
    "enterprise": None,
}

MAX_VERSIONS_PER_FILE = 100
TRASH_RETENTION_DAYS = 30


@dataclass(frozen=True)
class FileVersion:
    """One stored version. ``replaced_at`` is None for the current version."""

    number: int
    size_bytes: int
    created_at: datetime
    replaced_at: Optional[datetime] = None

    @property
    def is_current(self) -> bool:
        return self.replaced_at is None


def retention_days(plan: str) -> Optional[int]:
    """Return the plan's version history window in days (None = unlimited)."""
    if plan not in VERSION_RETENTION_DAYS:
        raise ValueError(f"unknown plan: {plan!r}")
    return VERSION_RETENTION_DAYS[plan]


def is_version_expired(version: FileVersion, plan: str, now: datetime) -> bool:
    """Return True if ``version`` has aged out of the plan's window.

    The current version never expires. The window is counted from the moment
    the version was replaced by a newer one.
    """
    days = retention_days(plan)
    if version.replaced_at is None or days is None:
        return False
    return now - version.replaced_at > timedelta(days=days)


def versions_to_prune(
    versions: Sequence[FileVersion], plan: str, now: datetime
) -> List[FileVersion]:
    """Return the versions that should be removed, oldest first.

    A version is pruned when it is outside the plan's window, or when the
    file has more than 100 versions (the oldest go first, even inside the
    window). The current version is never pruned.
    """
    ordered = sorted(versions, key=lambda v: v.number)
    prune = [v for v in ordered if is_version_expired(v, plan, now)]
    kept = [v for v in ordered if v not in prune]
    excess = len(kept) - MAX_VERSIONS_PER_FILE
    for version in kept:
        if excess <= 0:
            break
        if not version.is_current:
            prune.append(version)
            excess -= 1
    return sorted(prune, key=lambda v: v.number)


def stored_bytes(versions: Sequence[FileVersion]) -> int:
    """Every stored version counts towards storage at its full size."""
    return sum(v.size_bytes for v in versions)


def add_version(
    versions: Sequence[FileVersion], size_bytes: int, now: datetime
) -> List[FileVersion]:
    """Return a new version list with a new current version appended.

    The previous current version gets ``replaced_at = now``. Restoring an old
    version uses this too: the old content becomes a new current version.
    """
    updated = [
        FileVersion(v.number, v.size_bytes, v.created_at, now) if v.is_current else v
        for v in versions
    ]
    next_number = max((v.number for v in versions), default=0) + 1
    updated.append(FileVersion(next_number, size_bytes, now))
    return updated


def trash_purge_at(trashed_at: datetime) -> datetime:
    """Return when a trashed file is permanently deleted (30 days later)."""
    return trashed_at + timedelta(days=TRASH_RETENTION_DAYS)


def is_restorable(trashed_at: datetime, now: datetime) -> bool:
    """Return True while a trashed file can still be restored."""
    return now < trash_purge_at(trashed_at)


def days_left_in_trash(trashed_at: datetime, now: datetime) -> int:
    """Return whole days left before purge (0 once the file is purged)."""
    remaining = trash_purge_at(trashed_at) - now
    return max(0, remaining.days)


def can_restore_from_trash(role: str, deleted_by_self: bool) -> bool:
    """Members restore files they deleted; Owners and Admins restore any."""
    if role in ("owner", "admin"):
        return True
    return role == "member" and deleted_by_self
