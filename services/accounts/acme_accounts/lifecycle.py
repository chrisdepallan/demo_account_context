"""Account state machine and retention windows.

Implements the rules in ``docs/account-lifecycle.md``: the six account
states, which transitions between them are legal, and the time windows
(trial, grace period, retention, backup purge) that drive them.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, FrozenSet

TRIAL_DAYS = 14
GRACE_PERIOD_DAYS = 14
RETENTION_DAYS = 30
BACKUP_PURGE_DAYS = 35
VERIFICATION_LINK_HOURS = 24


class AccountState(str, Enum):
    """The states an account can be in."""

    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    READ_ONLY = "read_only"
    CLOSED = "closed"
    DELETED = "deleted"


class InvalidTransition(ValueError):
    """Raised when an account is moved between two states illegally."""


_S = AccountState

#: Legal transitions: current state -> states it may move to.
TRANSITIONS: Dict[AccountState, FrozenSet[AccountState]] = {
    _S.TRIALING: frozenset({_S.ACTIVE, _S.CLOSED}),
    _S.ACTIVE: frozenset({_S.PAST_DUE, _S.CLOSED}),
    _S.PAST_DUE: frozenset({_S.ACTIVE, _S.READ_ONLY, _S.CLOSED}),
    _S.READ_ONLY: frozenset({_S.ACTIVE, _S.CLOSED}),
    _S.CLOSED: frozenset({_S.ACTIVE, _S.DELETED}),
    _S.DELETED: frozenset(),
}


def can_transition(current: AccountState, target: AccountState) -> bool:
    """Return True if an account may move from ``current`` to ``target``."""
    return target in TRANSITIONS[current]


def transition(current: AccountState, target: AccountState) -> AccountState:
    """Return ``target`` if the move is legal, otherwise raise InvalidTransition."""
    if not can_transition(current, target):
        raise InvalidTransition(f"cannot move from {current.value} to {target.value}")
    return target


def can_log_in(state: AccountState) -> bool:
    """Users can log in unless the account is closed or deleted."""
    return state not in (_S.CLOSED, _S.DELETED)


def can_edit(state: AccountState) -> bool:
    """Users can edit while trialing, active or inside the grace period."""
    return state in (_S.TRIALING, _S.ACTIVE, _S.PAST_DUE)


def trial_end(signed_up_at: datetime) -> datetime:
    """Return when the 14-day Pro trial ends."""
    return signed_up_at + timedelta(days=TRIAL_DAYS)


def plan_after_trial(has_payment_method: bool) -> str:
    """Return the plan an account lands on when its trial ends.

    The account always becomes ``active``: on Pro with a payment method on
    file, on Free without one.
    """
    return "pro" if has_payment_method else "free"


def grace_period_end(payment_failed_at: datetime) -> datetime:
    """Return when the 14-day grace period after a failed payment ends."""
    return payment_failed_at + timedelta(days=GRACE_PERIOD_DAYS)


def state_while_unpaid(payment_failed_at: datetime, now: datetime) -> AccountState:
    """Return ``past_due`` inside the grace period and ``read_only`` after it."""
    if now < grace_period_end(payment_failed_at):
        return _S.PAST_DUE
    return _S.READ_ONLY


def deletion_date(closed_at: datetime) -> datetime:
    """Return when a closed account becomes ``deleted`` (30 days after closing)."""
    return closed_at + timedelta(days=RETENTION_DAYS)


def backup_purge_deadline(closed_at: datetime) -> datetime:
    """Return the latest time by which backups are purged (a further 35 days)."""
    return deletion_date(closed_at) + timedelta(days=BACKUP_PURGE_DAYS)


def can_restore(state: AccountState, closed_at: datetime, now: datetime) -> bool:
    """Return True if a closed account is still inside the retention window."""
    return state is _S.CLOSED and now < deletion_date(closed_at)


def state_after_closing(closed_at: datetime, now: datetime) -> AccountState:
    """Return ``closed`` during retention and ``deleted`` once it has ended."""
    return _S.CLOSED if now < deletion_date(closed_at) else _S.DELETED


def restore(state: AccountState, closed_at: datetime, now: datetime) -> AccountState:
    """Restore a closed account, or raise InvalidTransition if it is too late."""
    if not can_restore(state, closed_at, now):
        raise InvalidTransition("only closed accounts inside the 30-day retention window can be restored")
    return transition(state, _S.ACTIVE)
