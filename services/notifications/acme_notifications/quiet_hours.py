"""Quiet hours and per-user hourly rate limits.

Quiet hours hold email and push until the window ends; in-app is always
delivered. Mandatory types ignore both quiet hours and rate limits. Each user
may receive 20 emails and 30 push notifications per rolling 60 minutes;
anything over that is left for the digest.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Deque, Dict, Mapping, Optional, Tuple

from .preferences import CHANNELS, is_mandatory

DEFAULT_START = time(22, 0)
DEFAULT_END = time(7, 0)
HELD_CHANNELS: Tuple[str, ...] = ("email", "push")
HOURLY_LIMITS: Dict[str, int] = {"email": 20, "push": 30}
RATE_WINDOW = timedelta(minutes=60)
SUMMARY_THRESHOLD = 10

SEND = "send"
HOLD = "hold"
DIGEST = "digest"


@dataclass(frozen=True)
class QuietHours:
    """A user's quiet-hours setting. Off by default; default window 22:00-07:00."""

    enabled: bool = False
    start: time = DEFAULT_START
    end: time = DEFAULT_END


def in_quiet_hours(local_now: datetime, quiet: QuietHours) -> bool:
    """Return True if ``local_now`` (user's local time) falls inside the window.

    The start is inclusive and the end exclusive. Windows may cross midnight.
    A window whose start equals its end is empty.
    """
    if not quiet.enabled or quiet.start == quiet.end:
        return False
    current = local_now.time()
    if quiet.start < quiet.end:
        return quiet.start <= current < quiet.end
    return current >= quiet.start or current < quiet.end


def next_release(local_now: datetime, quiet: QuietHours) -> Optional[datetime]:
    """Return when held notifications are released, or None if nothing is held now."""
    if not in_quiet_hours(local_now, quiet):
        return None
    release = local_now.replace(
        hour=quiet.end.hour, minute=quiet.end.minute, second=0, microsecond=0
    )
    if release <= local_now:
        release += timedelta(days=1)
    return release


def release_mode(held_count: int, threshold: int = SUMMARY_THRESHOLD) -> str:
    """Return how held notifications on one channel are released.

    ``"none"`` when nothing was held, ``"individual"`` for up to 10, and
    ``"summary"`` (one combined message) for more than 10.
    """
    if held_count < 0:
        raise ValueError("held_count cannot be negative")
    if held_count == 0:
        return "none"
    return "individual" if held_count <= threshold else "summary"


class RateLimiter:
    """Sliding-window limiter: N notifications per user per channel per hour."""

    def __init__(
        self,
        limits: Optional[Mapping[str, int]] = None,
        window: timedelta = RATE_WINDOW,
    ) -> None:
        self.limits: Dict[str, int] = dict(HOURLY_LIMITS if limits is None else limits)
        self.window = window
        self._sent: Dict[Tuple[str, str], Deque[datetime]] = {}

    def _prune(self, user_id: str, channel: str, now: datetime) -> Deque[datetime]:
        sent = self._sent.setdefault((user_id, channel), deque())
        while sent and now - sent[0] >= self.window:
            sent.popleft()
        return sent

    def remaining(self, user_id: str, channel: str, now: datetime) -> Optional[int]:
        """Return how many more sends are allowed now, or None if unlimited."""
        limit = self.limits.get(channel)
        if limit is None:
            return None
        return max(0, limit - len(self._prune(user_id, channel, now)))

    def allow(self, user_id: str, channel: str, now: datetime, *, mandatory: bool = False) -> bool:
        """Record a send and return True, or return False if the limit is reached.

        Mandatory notifications are always allowed and are not counted.
        """
        if mandatory or channel not in self.limits:
            return True
        sent = self._prune(user_id, channel, now)
        if len(sent) >= self.limits[channel]:
            return False
        sent.append(now)
        return True


def decide_delivery(
    user_id: str,
    channel: str,
    notification_type: str,
    local_now: datetime,
    quiet: QuietHours,
    limiter: RateLimiter,
) -> str:
    """Decide what to do with one notification on one channel.

    Returns ``"send"``, ``"hold"`` (wait for quiet hours to end) or
    ``"digest"`` (over the hourly limit; left for the next digest). The order
    is: in-app always sends, mandatory always sends, quiet hours, rate limit.
    Held notifications are not counted against the limit.
    """
    if channel not in CHANNELS:
        raise ValueError(f"unknown channel: {channel!r}")
    if channel == "in_app" or is_mandatory(notification_type):
        return SEND
    if channel in HELD_CHANNELS and in_quiet_hours(local_now, quiet):
        return HOLD
    if not limiter.allow(user_id, channel, local_now):
        return DIGEST
    return SEND
