"""Failed-login lockout rules.

Implements "Why is my account locked?" in ``docs/passwords-and-mfa.md``:

- 5 failed attempts within 15 minutes lock the login for 15 minutes.
- 10 failed attempts within 1 hour lock it for 1 hour and email the user.
- Resetting the password unlocks the account immediately.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Sequence

SHORT_MAX_FAILURES = 5
SHORT_WINDOW = timedelta(minutes=15)
SHORT_LOCK = timedelta(minutes=15)

LONG_MAX_FAILURES = 10
LONG_WINDOW = timedelta(hours=1)
LONG_LOCK = timedelta(hours=1)


@dataclass(frozen=True)
class Lock:
    """A lock applied to a login."""

    until: datetime
    duration: timedelta
    notify_user: bool


def failures_in_window(failures: Sequence[datetime], now: datetime, window: timedelta) -> int:
    """Count the failed attempts made within ``window`` before ``now``."""
    return sum(1 for moment in failures if now - window < moment <= now)


def evaluate(failures: Sequence[datetime], now: datetime) -> Optional[Lock]:
    """Return the lock triggered by a failure at ``now``, if any.

    ``failures`` must include the attempt made at ``now``. The 1-hour rule
    wins when both rules match.
    """
    if failures_in_window(failures, now, LONG_WINDOW) >= LONG_MAX_FAILURES:
        return Lock(until=now + LONG_LOCK, duration=LONG_LOCK, notify_user=True)
    if failures_in_window(failures, now, SHORT_WINDOW) >= SHORT_MAX_FAILURES:
        return Lock(until=now + SHORT_LOCK, duration=SHORT_LOCK, notify_user=False)
    return None


class LockoutTracker:
    """Tracks failed logins for one user and decides when the login is locked."""

    def __init__(self) -> None:
        self._failures: List[datetime] = []
        self._lock: Optional[Lock] = None

    def is_locked(self, now: datetime) -> bool:
        """Return True while a lock is in force."""
        return self._lock is not None and now < self._lock.until

    def locked_until(self, now: datetime) -> Optional[datetime]:
        """Return when the current lock ends, or None if not locked."""
        return self._lock.until if self._lock is not None and self.is_locked(now) else None

    def retry_after_seconds(self, now: datetime) -> int:
        """Return the seconds until login may be tried again (0 if not locked)."""
        until = self.locked_until(now)
        return 0 if until is None else int((until - now).total_seconds())

    def record_failure(self, now: datetime) -> Optional[Lock]:
        """Record a failed login and return the lock it triggers, if any.

        Attempts made while the login is locked are rejected before the
        password is checked, so they are not counted.
        """
        if self.is_locked(now):
            return None
        self._failures = [m for m in self._failures if now - LONG_WINDOW < m]
        self._failures.append(now)
        lock = evaluate(self._failures, now)
        if lock is not None:
            self._lock = lock
        return lock

    def record_success(self, now: datetime) -> bool:
        """Record a successful login; return False if the login is locked."""
        if self.is_locked(now):
            return False
        self._failures.clear()
        self._lock = None
        return True

    def reset_password(self) -> None:
        """Resetting the password unlocks the account immediately."""
        self._failures.clear()
        self._lock = None
