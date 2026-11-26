"""Role permission matrix and invitation rules.

Implements ``docs/members-and-roles.md``: which role can perform which
action, which roles use a seat, and the limits on invitations and
ownership transfers.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, FrozenSet, List, Sequence

INVITE_BATCH_MAX = 50
INVITATION_EXPIRY_DAYS = 7
OWNERSHIP_ACCEPT_DAYS = 7


class Role(str, Enum):
    """The five roles a person can hold."""

    OWNER = "owner"
    ADMIN = "admin"
    BILLING_ADMIN = "billing_admin"
    MEMBER = "member"
    GUEST = "guest"


class Action(str, Enum):
    """Actions governed by the permission matrix."""

    EDIT_PROJECTS = "edit_projects"
    COMMENT = "comment"
    MANAGE_MEMBERS = "manage_members"
    CHANGE_SECURITY_SETTINGS = "change_security_settings"
    VIEW_AND_PAY_INVOICES = "view_and_pay_invoices"
    CHANGE_PLAN_OR_PAYMENT_METHOD = "change_plan_or_payment_method"
    TRANSFER_OWNERSHIP = "transfer_ownership"
    CLOSE_ACCOUNT = "close_account"
    EXPORT_DATA = "export_data"


_R, _A = Role, Action

#: Action -> roles allowed to perform it.
PERMISSIONS: Dict[Action, FrozenSet[Role]] = {
    _A.EDIT_PROJECTS: frozenset({_R.OWNER, _R.ADMIN, _R.MEMBER}),
    _A.COMMENT: frozenset({_R.OWNER, _R.ADMIN, _R.MEMBER, _R.GUEST}),
    _A.MANAGE_MEMBERS: frozenset({_R.OWNER, _R.ADMIN}),
    _A.CHANGE_SECURITY_SETTINGS: frozenset({_R.OWNER, _R.ADMIN}),
    _A.VIEW_AND_PAY_INVOICES: frozenset({_R.OWNER, _R.BILLING_ADMIN}),
    _A.CHANGE_PLAN_OR_PAYMENT_METHOD: frozenset({_R.OWNER, _R.BILLING_ADMIN}),
    _A.TRANSFER_OWNERSHIP: frozenset({_R.OWNER}),
    _A.CLOSE_ACCOUNT: frozenset({_R.OWNER}),
    _A.EXPORT_DATA: frozenset({_R.OWNER, _R.ADMIN}),
}


def can(role: Role, action: Action) -> bool:
    """Return True if ``role`` may perform ``action``."""
    return role in PERMISSIONS[action]


def allowed_actions(role: Role) -> FrozenSet[Action]:
    """Return every action ``role`` may perform."""
    return frozenset(action for action, roles in PERMISSIONS.items() if role in roles)


def uses_seat(role: Role) -> bool:
    """Every role except Guest is a member and uses a paid seat."""
    return role is not Role.GUEST


def seats_needed(roles: Sequence[Role]) -> int:
    """Return the number of seats a list of people with these roles uses."""
    return sum(1 for role in roles if uses_seat(role))


def can_invite_as(inviter: Role, invited_role: Role) -> bool:
    """Owners and Admins may invite; nobody can be invited as Owner."""
    return can(inviter, Action.MANAGE_MEMBERS) and invited_role is not Role.OWNER


def validate_invite_batch(emails: Sequence[str]) -> List[str]:
    """Return the cleaned, de-duplicated batch or raise ValueError.

    A batch holds 1 to 50 email addresses.
    """
    cleaned: List[str] = []
    for email in emails:
        address = email.strip().lower()
        if "@" not in address or address.startswith("@") or address.endswith("@"):
            raise ValueError(f"not an email address: {email!r}")
        if address not in cleaned:
            cleaned.append(address)
    if not cleaned:
        raise ValueError("an invitation batch needs at least 1 email address")
    if len(cleaned) > INVITE_BATCH_MAX:
        raise ValueError(f"an invitation batch holds at most {INVITE_BATCH_MAX} email addresses")
    return cleaned


def invitation_expired(sent_at: datetime, now: datetime) -> bool:
    """Invitations expire 7 days after they were sent (or resent)."""
    return now >= sent_at + timedelta(days=INVITATION_EXPIRY_DAYS)


def can_receive_ownership(target_role: Role) -> bool:
    """Ownership can only be transferred to an existing Admin."""
    return target_role is Role.ADMIN


def transfer_ownership(actor: Role, target: Role) -> Dict[str, Role]:
    """Return the new roles of the previous and new Owner after a transfer."""
    if not can(actor, Action.TRANSFER_OWNERSHIP):
        raise PermissionError("only the Owner can transfer ownership")
    if not can_receive_ownership(target):
        raise ValueError("ownership can only be transferred to an existing Admin")
    return {"previous_owner": Role.ADMIN, "new_owner": Role.OWNER}


def transfer_offer_expired(offered_at: datetime, now: datetime) -> bool:
    """The new Owner must accept a transfer within 7 days."""
    return now >= offered_at + timedelta(days=OWNERSHIP_ACCEPT_DAYS)
