"""Install state machine and per-plan install limits.

An install is one app connected to one workspace. It moves between the states
``pending``, ``active``, ``suspended`` and ``revoked``; ``revoked`` is final.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, FrozenSet, Iterable, Optional


class InstallError(Exception):
    """Raised when an install action breaks a rule."""


class InstallState(str, Enum):
    """The four states an install can be in."""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


ALLOWED_TRANSITIONS: Dict[InstallState, FrozenSet[InstallState]] = {
    InstallState.PENDING: frozenset({InstallState.ACTIVE, InstallState.REVOKED}),
    InstallState.ACTIVE: frozenset({InstallState.SUSPENDED, InstallState.REVOKED}),
    InstallState.SUSPENDED: frozenset({InstallState.ACTIVE, InstallState.REVOKED}),
    InstallState.REVOKED: frozenset(),
}

#: Active + suspended installs allowed per workspace. ``None`` means unlimited.
PLAN_INSTALL_LIMITS: Dict[str, Optional[int]] = {
    "free": 2,
    "starter": 5,
    "pro": 20,
    "business": 50,
    "enterprise": None,
}

#: App kinds each plan may install.
PLAN_APP_KINDS: Dict[str, FrozenSet[str]] = {
    "free": frozenset({"first_party"}),
    "starter": frozenset({"first_party", "partner"}),
    "pro": frozenset({"first_party", "partner"}),
    "business": frozenset({"first_party", "partner", "private"}),
    "enterprise": frozenset({"first_party", "partner", "private"}),
}

PENDING_EXPIRY = timedelta(minutes=30)
SUSPEND_AFTER_FAILURES = 5
AUTO_REVOKE_SUSPENDED_AFTER = timedelta(days=60)
LINK_RETENTION_AFTER_REVOKE = timedelta(days=30)

_COUNTED_STATES = frozenset({InstallState.ACTIVE, InstallState.SUSPENDED})
_MANAGER_ROLES = frozenset({"owner", "admin"})


@dataclass
class Install:
    """One app connected to one workspace."""

    integration_id: str
    workspace_id: str
    app_slug: str
    created_at: datetime
    state: InstallState = InstallState.PENDING
    state_changed_at: Optional[datetime] = None
    consecutive_failures: int = 0
    suspended_reason: Optional[str] = None
    scopes: FrozenSet[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.state_changed_at is None:
            self.state_changed_at = self.created_at


def _plan_key(plan: str) -> str:
    key = plan.strip().lower()
    if key not in PLAN_INSTALL_LIMITS:
        raise InstallError(f"Unknown plan: {plan}")
    return key


def install_limit(plan: str) -> Optional[int]:
    """Return the install limit for a plan, or ``None`` for unlimited."""
    return PLAN_INSTALL_LIMITS[_plan_key(plan)]


def counted_installs(installs: Iterable[Install]) -> int:
    """Count installs that use up the limit (active and suspended)."""
    return sum(1 for i in installs if i.state in _COUNTED_STATES)


def can_manage_installs(role: str) -> bool:
    """Only the Owner and Admins may install, suspend, resume or revoke."""
    return role.strip().lower() in _MANAGER_ROLES


def can_install(plan: str, existing: Iterable[Install], app_slug: str, app_kind: str = "first_party") -> bool:
    """Return True if the workspace may start installing ``app_slug``.

    Checks the app kind allowed on the plan, the one-install-per-app rule and
    the plan's install limit.
    """
    key = _plan_key(plan)
    existing = list(existing)
    if app_kind not in PLAN_APP_KINDS[key]:
        return False
    if any(i.app_slug == app_slug and i.state is not InstallState.REVOKED for i in existing):
        return False
    limit = PLAN_INSTALL_LIMITS[key]
    return limit is None or counted_installs(existing) < limit


def installs_to_remove_for_plan(plan: str, existing: Iterable[Install]) -> int:
    """Return how many installs must be revoked before downgrading to ``plan``."""
    limit = install_limit(plan)
    if limit is None:
        return 0
    return max(0, counted_installs(existing) - limit)


def transition(install: Install, new_state: InstallState, now: datetime, reason: Optional[str] = None) -> Install:
    """Move ``install`` to ``new_state`` or raise ``InstallError``."""
    if new_state not in ALLOWED_TRANSITIONS[install.state]:
        raise InstallError(f"An install cannot move from {install.state.value} to {new_state.value}.")
    install.state = new_state
    install.state_changed_at = now
    install.suspended_reason = reason if new_state is InstallState.SUSPENDED else None
    if new_state is InstallState.ACTIVE:
        install.consecutive_failures = 0
    return install


def is_pending_expired(install: Install, now: datetime) -> bool:
    """A pending install expires 30 minutes after it was started."""
    return install.state is InstallState.PENDING and now - install.created_at > PENDING_EXPIRY


def record_failure(install: Install, now: datetime) -> Install:
    """Record a failed sync run or token refresh; suspend after 5 in a row."""
    if install.state is not InstallState.ACTIVE:
        return install
    install.consecutive_failures += 1
    if install.consecutive_failures >= SUSPEND_AFTER_FAILURES:
        failures = install.consecutive_failures
        transition(install, InstallState.SUSPENDED, now, reason="sync_failures")
        install.consecutive_failures = failures
    return install


def record_success(install: Install) -> Install:
    """Reset the failure counter after a successful run."""
    install.consecutive_failures = 0
    return install


def expire_stale(install: Install, now: datetime) -> Install:
    """Revoke a pending install past 30 minutes or one suspended for 60 days."""
    if is_pending_expired(install, now):
        return transition(install, InstallState.REVOKED, now)
    if install.state is InstallState.SUSPENDED and now - install.state_changed_at >= AUTO_REVOKE_SUSPENDED_AFTER:
        return transition(install, InstallState.REVOKED, now)
    return install


def links_purge_at(install: Install) -> Optional[datetime]:
    """Return when item links are deleted: 30 days after revocation."""
    if install.state is not InstallState.REVOKED:
        return None
    return install.state_changed_at + LINK_RETENTION_AFTER_REVOKE
