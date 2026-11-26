"""Audit entry model, event categories and validation.

An audit entry records who did what, to which resource, when and from
where. Entries are immutable once written (the dataclass is frozen) and
never contain secrets: metadata keys that look like credentials are
rejected by :func:`validate_entry`.
"""

from __future__ import annotations

import ipaddress
import json
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Mapping, Optional

_ID_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_ENTRY_ID_RE = re.compile(r"^aud_[A-Z0-9]{10}$")
_ACCOUNT_ID_RE = re.compile(r"^acc_[A-Z0-9]{8}$")
_WORKSPACE_ID_RE = re.compile(r"^ws_[A-Z0-9]{6}$")
_EVENT_TYPE_RE = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")
_TICKET_RE = re.compile(r"^SUP-\d{5}$")

ACTOR_TYPES = ("user", "api_key", "system", "support")
REGIONS = ("us-east", "eu-central", "ap-south")
MAX_METADATA_KEYS = 20
MAX_METADATA_BYTES = 4096
FORBIDDEN_METADATA_WORDS = ("password", "secret", "token", "api_key", "private_key")

#: Plans that have an audit log at all.
AUDIT_PLANS = ("pro", "business", "enterprise")
#: Read-style events that are only recorded on the Enterprise plan.
ENTERPRISE_ONLY_EVENTS = frozenset({"file.downloaded"})


class EventCategory(str, Enum):
    """The eight categories shown in the audit log filter."""

    AUTHENTICATION = "authentication"
    MEMBERS = "members"
    SECURITY = "security"
    DATA = "data"
    BILLING = "billing"
    INTEGRATIONS = "integrations"
    ACCOUNT = "account"
    AUDIT = "audit"


_RESOURCES = {
    EventCategory.AUTHENTICATION: ("login", "session", "password", "mfa"),
    EventCategory.MEMBERS: ("member", "guest", "ownership"),
    EventCategory.SECURITY: ("sso", "scim", "security_policy", "api_key"),
    EventCategory.DATA: ("workspace", "project", "task", "file"),
    EventCategory.BILLING: ("plan", "subscription", "invoice", "payment_method", "refund"),
    EventCategory.INTEGRATIONS: ("webhook_endpoint", "integration"),
    EventCategory.ACCOUNT: ("account",),
    EventCategory.AUDIT: ("audit_log", "support"),
}
CATEGORY_BY_RESOURCE: Dict[str, EventCategory] = {
    resource: category for category, resources in _RESOURCES.items() for resource in resources
}


class EntryValidationError(ValueError):
    """Raised when an entry breaks a rule and must not be written."""


@dataclass(frozen=True)
class AuditEntry:
    """One immutable audit log entry."""

    id: str
    account_id: str
    occurred_at: datetime
    event_type: str
    actor_type: str
    actor_id: str
    workspace_id: Optional[str] = None
    target_id: Optional[str] = None
    ip_address: Optional[str] = None
    region: str = "us-east"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def category(self) -> EventCategory:
        """The category derived from the resource part of ``event_type``."""
        return category_for(self.event_type)


def new_entry_id() -> str:
    """Return a new random entry ID such as ``aud_7H2KQ9M4XP``."""
    return "aud_" + "".join(secrets.choice(_ID_ALPHABET) for _ in range(10))


def category_for(event_type: str) -> EventCategory:
    """Map an event type such as ``member.invited`` to its category.

    :raises EntryValidationError: if the name is not ``resource.action``
        or the resource is not one the audit log records.
    """
    if not _EVENT_TYPE_RE.match(event_type or ""):
        raise EntryValidationError(f"event type {event_type!r} is not in resource.action form")
    resource = event_type.split(".", 1)[0]
    try:
        return CATEGORY_BY_RESOURCE[resource]
    except KeyError:
        raise EntryValidationError(f"{resource!r} events are not recorded") from None


def is_recorded(event_type: str, plan: str) -> bool:
    """Return True if ``event_type`` is written to the log on ``plan``.

    Free and Starter have no audit log. ``file.downloaded`` is recorded on
    Enterprise only. Unknown resources are never recorded.
    """
    plan = plan.strip().lower()
    if plan not in AUDIT_PLANS:
        return False
    try:
        category_for(event_type)
    except EntryValidationError:
        return False
    return plan == "enterprise" or event_type not in ENTERPRISE_ONLY_EVENTS


def validate_entry(entry: AuditEntry) -> AuditEntry:
    """Check every field of ``entry`` and return it unchanged.

    :raises EntryValidationError: with a message naming the broken rule.
    """
    if not _ENTRY_ID_RE.match(entry.id):
        raise EntryValidationError("id must look like aud_7H2KQ9M4XP")
    if not _ACCOUNT_ID_RE.match(entry.account_id):
        raise EntryValidationError("account_id must look like acc_7F3K9Q2M")
    if entry.workspace_id is not None and not _WORKSPACE_ID_RE.match(entry.workspace_id):
        raise EntryValidationError("workspace_id must look like ws_4H8P2L")
    if entry.occurred_at.tzinfo is None or entry.occurred_at.utcoffset() is None:
        raise EntryValidationError("occurred_at must be timezone-aware")
    category_for(entry.event_type)
    if entry.actor_type not in ACTOR_TYPES:
        raise EntryValidationError(f"actor_type must be one of {', '.join(ACTOR_TYPES)}")
    if not entry.actor_id:
        raise EntryValidationError("actor_id is required")
    if entry.actor_type == "support" and not _TICKET_RE.match(entry.actor_id):
        raise EntryValidationError("support actions must carry a ticket ID like SUP-48213")
    if entry.region not in REGIONS:
        raise EntryValidationError(f"region must be one of {', '.join(REGIONS)}")
    if entry.ip_address is not None:
        try:
            ipaddress.ip_address(entry.ip_address)
        except ValueError:
            raise EntryValidationError("ip_address is not a valid IPv4 or IPv6 address") from None
    _validate_metadata(entry.metadata)
    return entry


def _validate_metadata(metadata: Mapping[str, Any]) -> None:
    if len(metadata) > MAX_METADATA_KEYS:
        raise EntryValidationError(f"metadata has more than {MAX_METADATA_KEYS} keys")
    for key, value in metadata.items():
        if not isinstance(key, str) or not key:
            raise EntryValidationError("metadata keys must be non-empty strings")
        if any(word in key.lower() for word in FORBIDDEN_METADATA_WORDS):
            raise EntryValidationError(f"metadata key {key!r} looks like a secret")
        if value is not None and not isinstance(value, (str, int, float, bool)):
            raise EntryValidationError(f"metadata value for {key!r} must be a scalar")
    size = len(json.dumps(dict(metadata), ensure_ascii=False).encode("utf-8"))
    if size > MAX_METADATA_BYTES:
        raise EntryValidationError(f"metadata is larger than {MAX_METADATA_BYTES} bytes")
