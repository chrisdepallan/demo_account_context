"""API key rules: prefixes, scopes, expiry and limits.

Implements ``docs/api-keys.md``. This module validates and describes keys;
it never generates key material.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import FrozenSet, Iterable, List, Optional, Tuple

LIVE_PREFIX = "acme_live_"
TEST_PREFIX = "acme_test_"

SCOPES: FrozenSet[str] = frozenset(
    {
        "projects:read",
        "projects:write",
        "files:read",
        "files:write",
        "members:read",
        "members:write",
        "billing:read",
    }
)
#: Scopes limited to certain roles.
RESTRICTED_SCOPES = {"billing:read": frozenset({"owner", "billing_admin"})}
#: Roles that may create, rotate and revoke keys.
KEY_MANAGER_ROLES: FrozenSet[str] = frozenset({"owner", "admin"})
#: Plans that can use the API. Free accounts cannot.
API_PLANS: FrozenSet[str] = frozenset({"starter", "pro", "business", "enterprise"})

ALLOWED_EXPIRY_DAYS: Tuple[int, ...] = (30, 90, 180, 365)
MAX_ACTIVE_KEYS_PER_WORKSPACE = 25
EXPIRY_WARNING_DAYS = 14
ROTATION_OVERLAP_HOURS = 24
REVOCATION_SECONDS = 60

_KEY_PATTERN = re.compile(r"^(acme_live_|acme_test_)[A-Za-z0-9]{12,64}$")


def is_valid_key_format(key: str) -> bool:
    """Return True if ``key`` has a known prefix followed by letters and digits."""
    return bool(_KEY_PATTERN.match(key))


def environment_for(key: str) -> str:
    """Return ``production`` for ``acme_live_`` keys and ``sandbox`` for ``acme_test_`` keys."""
    if key.startswith(LIVE_PREFIX):
        return "production"
    if key.startswith(TEST_PREFIX):
        return "sandbox"
    raise ValueError("API keys start with acme_live_ or acme_test_")


def mask_key(key: str) -> str:
    """Return the key with everything after the prefix hidden, for logs and UI."""
    environment_for(key)
    prefix = LIVE_PREFIX if key.startswith(LIVE_PREFIX) else TEST_PREFIX
    return prefix + "****"


def max_keys_for_plan(plan: str) -> int:
    """Return the active-key limit per workspace: 25 on paid plans, 0 on Free."""
    return MAX_ACTIVE_KEYS_PER_WORKSPACE if plan.lower() in API_PLANS else 0


def can_create_key(plan: str, role: str, active_keys: int) -> bool:
    """Return True if this role on this plan may add another key to the workspace."""
    return role in KEY_MANAGER_ROLES and active_keys < max_keys_for_plan(plan)


def validate_scopes(scopes: Iterable[str], role: str) -> List[str]:
    """Return the sorted, de-duplicated scopes or raise ValueError.

    At least one scope is needed, every scope must exist, and
    ``billing:read`` can only be granted by an Owner or Billing admin.
    """
    requested = sorted(set(scopes))
    if not requested:
        raise ValueError("a key needs at least one scope")
    unknown = [scope for scope in requested if scope not in SCOPES]
    if unknown:
        raise ValueError(f"unknown scopes: {', '.join(unknown)}")
    for scope in requested:
        allowed_roles = RESTRICTED_SCOPES.get(scope)
        if allowed_roles is not None and role not in allowed_roles:
            raise ValueError(f"scope {scope} is not available to role {role}")
    return requested


def has_scope(granted: Iterable[str], needed: str) -> bool:
    """Return True if a key with the ``granted`` scopes may make a ``needed`` call.

    Scopes are matched exactly: ``files:write`` does not imply ``files:read``.
    """
    return needed in SCOPES and needed in set(granted)


def validate_expiry(days: Optional[int], require_expiry: bool = False) -> Optional[int]:
    """Check an expiry choice: 30, 90, 180 or 365 days, or None for "never".

    "Never" is refused when the workspace has **Require key expiry** on.
    """
    if days is None:
        if require_expiry:
            raise ValueError("this workspace requires keys to have an expiry")
        return None
    if days not in ALLOWED_EXPIRY_DAYS:
        raise ValueError(f"expiry must be one of {ALLOWED_EXPIRY_DAYS} days or never")
    return days


def expires_at(created_at: datetime, days: Optional[int]) -> Optional[datetime]:
    """Return the expiry time of a key, or None if it never expires."""
    return None if days is None else created_at + timedelta(days=days)


def is_expired(expiry: Optional[datetime], now: datetime) -> bool:
    """Return True once a key's expiry time has passed."""
    return expiry is not None and now >= expiry


def expiry_warning_due(expiry: Optional[datetime], now: datetime) -> bool:
    """Return True in the 14 days before expiry, when the Owner is emailed."""
    if expiry is None or is_expired(expiry, now):
        return False
    return now >= expiry - timedelta(days=EXPIRY_WARNING_DAYS)


def old_key_usable_after_rotation(rotated_at: datetime, now: datetime) -> bool:
    """A rotated key keeps working for 24 hours after rotation."""
    return now < rotated_at + timedelta(hours=ROTATION_OVERLAP_HOURS)
