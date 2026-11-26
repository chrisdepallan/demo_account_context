"""Notification types, role eligibility and channel preference resolution.

Resolution order for each (type, channel) pair is: the user's own setting,
then the workspace default, then the system default. Mandatory types always
keep email and in-app switched on.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Mapping, Optional, Set, Tuple

CHANNELS: Tuple[str, ...] = ("email", "in_app", "push")

#: Types whose email and in-app delivery cannot be turned off.
MANDATORY_TYPES: FrozenSet[str] = frozenset({"security_alert", "billing_alert", "account_notice"})

#: System defaults per type as (email, in_app, push).
_DEFAULT_ROWS: Dict[str, Tuple[bool, bool, bool]] = {
    "mention": (True, True, True),
    "task_assigned": (True, True, True),
    "task_due_soon": (True, True, True),
    "task_completed": (False, True, False),
    "comment_added": (False, True, False),
    "file_shared": (True, True, False),
    "member_joined": (False, True, False),
    "storage_warning": (True, True, False),
    "security_alert": (True, True, True),
    "billing_alert": (True, True, False),
    "account_notice": (True, True, False),
}

SYSTEM_DEFAULTS: Dict[str, Dict[str, bool]] = {
    name: dict(zip(CHANNELS, row)) for name, row in _DEFAULT_ROWS.items()
}

NOTIFICATION_TYPES: Tuple[str, ...] = tuple(SYSTEM_DEFAULTS)

_ALL: FrozenSet[str] = frozenset(NOTIFICATION_TYPES)

#: Which notification types each role can receive.
ROLE_TYPES: Dict[str, FrozenSet[str]] = {
    "owner": _ALL,
    "admin": _ALL - {"billing_alert"},
    "billing_admin": frozenset({"billing_alert", "security_alert", "account_notice"}),
    "member": _ALL - {"billing_alert", "member_joined", "storage_warning"},
    "guest": frozenset(
        {"mention", "comment_added", "file_shared", "security_alert", "account_notice"}
    ),
}

#: Email suppression reasons. Only a spam complaint still lets mandatory email through.
SUPPRESSION_REASONS: FrozenSet[str] = frozenset({"hard_bounce", "soft_bounce", "complaint"})

Preferences = Mapping[str, Mapping[str, bool]]


def is_mandatory(notification_type: str) -> bool:
    """Return True if email and in-app cannot be switched off for this type."""
    return notification_type in MANDATORY_TYPES


def is_eligible(notification_type: str, role: str) -> bool:
    """Return True if a person with ``role`` can receive ``notification_type``."""
    _require_known_type(notification_type)
    try:
        return notification_type in ROLE_TYPES[role]
    except KeyError:
        raise ValueError(f"unknown role: {role!r}") from None


def validate_preferences(prefs: Preferences) -> None:
    """Raise ValueError if ``prefs`` is not a valid preference mapping.

    A valid mapping looks like ``{"mention": {"email": False}}``. Unknown types
    or channels, non-boolean values, and attempts to switch off email or in-app
    for a mandatory type are rejected.
    """
    for notification_type, channels in prefs.items():
        _require_known_type(notification_type)
        for channel, enabled in channels.items():
            if channel not in CHANNELS:
                raise ValueError(f"unknown channel: {channel!r}")
            if not isinstance(enabled, bool):
                raise ValueError(f"{notification_type}.{channel} must be true or false")
            if is_mandatory(notification_type) and channel != "push" and not enabled:
                raise ValueError(f"{channel} cannot be turned off for {notification_type}")


def resolve_setting(
    notification_type: str,
    channel: str,
    user_prefs: Optional[Preferences] = None,
    workspace_defaults: Optional[Preferences] = None,
) -> bool:
    """Resolve one switch: user setting, then workspace default, then system default."""
    _require_known_type(notification_type)
    if channel not in CHANNELS:
        raise ValueError(f"unknown channel: {channel!r}")
    if is_mandatory(notification_type) and channel != "push":
        return True
    for level in (user_prefs, workspace_defaults):
        if level is not None:
            value = level.get(notification_type, {}).get(channel)
            if value is not None:
                return bool(value)
    return SYSTEM_DEFAULTS[notification_type][channel]


def resolve_channels(
    notification_type: str,
    user_prefs: Optional[Preferences] = None,
    workspace_defaults: Optional[Preferences] = None,
    *,
    role: str = "member",
    has_push_device: bool = True,
    email_suppression: Optional[str] = None,
) -> Set[str]:
    """Return the set of channels a notification should be delivered on.

    Returns an empty set when the role cannot receive the type. Push is dropped
    when the user has no registered device. Email is dropped when the address
    is suppressed, except that a ``complaint`` suppression still allows
    mandatory types through.
    """
    if not is_eligible(notification_type, role):
        return set()
    if email_suppression is not None and email_suppression not in SUPPRESSION_REASONS:
        raise ValueError(f"unknown suppression reason: {email_suppression!r}")

    channels = {
        channel
        for channel in CHANNELS
        if resolve_setting(notification_type, channel, user_prefs, workspace_defaults)
    }
    if not has_push_device:
        channels.discard("push")
    if email_suppression is not None:
        complaint_exempt = email_suppression == "complaint" and is_mandatory(notification_type)
        if not complaint_exempt:
            channels.discard("email")
    return channels


def _require_known_type(notification_type: str) -> None:
    if notification_type not in SYSTEM_DEFAULTS:
        raise ValueError(f"unknown notification type: {notification_type!r}")
