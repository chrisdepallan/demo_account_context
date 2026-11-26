"""Retry schedule and automatic disabling of failing endpoints.

A delivery gets at most 8 attempts: the first one plus 7 retries after
1 minute, 5 minutes, 30 minutes, 2 hours, 6 hours, 12 hours and 24 hours.
An endpoint is warned about at 25 consecutive failed attempts and disabled at
50. A ``410 Gone`` response disables the endpoint immediately.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional, Tuple

RETRY_DELAYS_SECONDS: Tuple[int, ...] = (60, 300, 1800, 7200, 21600, 43200, 86400)
MAX_ATTEMPTS = len(RETRY_DELAYS_SECONDS) + 1
MAX_JITTER_FRACTION = 0.10
RETRY_AFTER_CAP_SECONDS = 3600
DELIVERY_TIMEOUT_SECONDS = 10
WARNING_THRESHOLD = 25
DISABLE_THRESHOLD = 50

SUCCESS = "success"
RETRY = "retry"
DISABLE = "disable"

ACTIVE = "active"
PAUSED = "paused"
DISABLED = "disabled"


def classify_response(status_code: Optional[int]) -> str:
    """Classify the outcome of one delivery attempt.

    Any 2xx is a success. ``410 Gone`` disables the endpoint. Everything else,
    including redirects, other 4xx, 5xx and ``None`` (timeout or connection
    error), is a failure that is retried.
    """
    if status_code is not None and 200 <= status_code < 300:
        return SUCCESS
    if status_code == 410:
        return DISABLE
    return RETRY


def next_retry_delay(
    attempt: int,
    retry_after: Optional[float] = None,
    jitter: float = 0.0,
    rng: Optional[random.Random] = None,
) -> Optional[float]:
    """Return the seconds to wait after failed attempt number ``attempt``.

    ``attempt`` counts from 1. Returns None when the delivery has used all 8
    attempts. A ``Retry-After`` value from the receiver is honoured up to one
    hour when it is longer than the scheduled delay. ``jitter`` (0 to 0.10)
    adds up to that fraction of random extra delay; it never shortens it.
    """
    if attempt < 1:
        raise ValueError("attempt numbers start at 1")
    if not 0.0 <= jitter <= MAX_JITTER_FRACTION:
        raise ValueError("jitter must be between 0 and 0.10")
    if attempt >= MAX_ATTEMPTS:
        return None
    delay = float(RETRY_DELAYS_SECONDS[attempt - 1])
    if retry_after is not None and retry_after > 0:
        delay = max(delay, min(float(retry_after), RETRY_AFTER_CAP_SECONDS))
    if jitter:
        delay += delay * jitter * (rng or random).random()
    return delay


def total_retry_window_seconds() -> int:
    """Return the time from the first to the last attempt without jitter."""
    return sum(RETRY_DELAYS_SECONDS)


@dataclass
class EndpointHealth:
    """Tracks consecutive failed attempts for one endpoint."""

    consecutive_failures: int = 0
    state: str = ACTIVE
    warning_sent: bool = False

    @property
    def accepts_deliveries(self) -> bool:
        """True while the endpoint is active (not paused or disabled)."""
        return self.state == ACTIVE

    def record_attempt(self, status_code: Optional[int]) -> Optional[str]:
        """Record one attempt and return the action to take, if any.

        Returns ``"warn"`` once when 25 consecutive attempts have failed,
        ``"disable"`` when the endpoint has just been disabled (50 consecutive
        failures or a 410), otherwise None. A success resets the counter.
        """
        outcome = classify_response(status_code)
        if outcome == SUCCESS:
            self.consecutive_failures = 0
            self.warning_sent = False
            return None
        self.consecutive_failures += 1
        if outcome == DISABLE or self.consecutive_failures >= DISABLE_THRESHOLD:
            already_disabled = self.state == DISABLED
            self.state = DISABLED
            return None if already_disabled else "disable"
        if self.consecutive_failures >= WARNING_THRESHOLD and not self.warning_sent:
            self.warning_sent = True
            return "warn"
        return None

    def pause(self) -> None:
        """Pause an active endpoint by hand. Disabled endpoints stay disabled."""
        if self.state == ACTIVE:
            self.state = PAUSED

    def enable(self) -> None:
        """Re-enable a paused or disabled endpoint and reset the failure counter."""
        self.state = ACTIVE
        self.consecutive_failures = 0
        self.warning_sent = False
