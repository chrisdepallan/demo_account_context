"""Acme Cloud Notifications service: preference, digest and quiet-hours rules.

The rules implemented here are documented in ``docs/notification-types.md``,
``docs/preferences-and-digests.md`` and ``docs/quiet-hours-and-rate-limits.md``.
"""

from . import digest, preferences, quiet_hours
from .digest import Digest, DigestGroup, DigestItem, build_digest, digest_window, is_digest_due
from .preferences import (
    CHANNELS,
    MANDATORY_TYPES,
    NOTIFICATION_TYPES,
    SYSTEM_DEFAULTS,
    is_eligible,
    is_mandatory,
    resolve_channels,
    validate_preferences,
)
from .quiet_hours import (
    HOURLY_LIMITS,
    QuietHours,
    RateLimiter,
    decide_delivery,
    in_quiet_hours,
    next_release,
    release_mode,
)

__version__ = "2.0.0"

__all__ = [
    "CHANNELS",
    "Digest",
    "DigestGroup",
    "DigestItem",
    "HOURLY_LIMITS",
    "MANDATORY_TYPES",
    "NOTIFICATION_TYPES",
    "QuietHours",
    "RateLimiter",
    "SYSTEM_DEFAULTS",
    "build_digest",
    "decide_delivery",
    "digest",
    "digest_window",
    "in_quiet_hours",
    "is_digest_due",
    "is_eligible",
    "is_mandatory",
    "next_release",
    "preferences",
    "quiet_hours",
    "release_mode",
    "resolve_channels",
    "validate_preferences",
]
