"""Event type catalog, subscription matching and the payload envelope.

Event types use the ``resource.action`` form. An endpoint subscribes with
exact names, a resource wildcard such as ``task.*`` or ``*`` for everything.
Every delivery body is an envelope with the same top-level fields.
"""

from __future__ import annotations

import json
import re
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

API_VERSION = "v2"
MAX_PAYLOAD_BYTES = 256 * 1024
MAX_SUBSCRIPTION_ENTRIES = 50
TEST_EVENT_TYPE = "webhook.test"

EVENT_TYPES: Dict[str, str] = {
    "project.created": "A project was created",
    "project.updated": "A project's name, description or settings changed",
    "project.archived": "A project was archived",
    "project.deleted": "A project was deleted",
    "task.created": "A task was created",
    "task.updated": "A task's title, description, due date or status changed",
    "task.assigned": "A task was assigned or reassigned",
    "task.completed": "A task was marked as complete",
    "task.deleted": "A task was deleted",
    "file.uploaded": "A file or a new file version was uploaded",
    "file.shared": "A file or folder was shared",
    "file.deleted": "A file was deleted",
    "member.invited": "A person was invited to the workspace",
    "member.joined": "An invited person accepted and joined",
    "member.removed": "A member was removed from the workspace",
    "member.role_changed": "A member's role changed",
    "invoice.created": "An invoice was issued",
    "invoice.paid": "An invoice was paid",
    "invoice.payment_failed": "A payment attempt for an invoice failed",
    "account.plan_changed": "The account was upgraded or downgraded",
    "account.closed": "The account was closed",
    TEST_EVENT_TYPE: "A test event sent from the endpoint settings",
}

#: Resources whose events belong to the account, not to one workspace.
ACCOUNT_LEVEL_RESOURCES = frozenset({"invoice", "account"})

_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
_EVENT_ID = re.compile(r"^evt_[A-Z0-9]{10}$")
_ACCOUNT_ID = re.compile(r"^acc_[A-Z0-9]{8}$")
_WORKSPACE_ID = re.compile(r"^ws_[A-Z0-9]{6}$")


class PayloadTooLargeError(ValueError):
    """Raised when a serialized envelope is larger than 256 KB."""


def is_valid_event_type(event_type: str) -> bool:
    """Return True if ``event_type`` is in the catalog."""
    return event_type in EVENT_TYPES


def is_account_level(event_type: str) -> bool:
    """Return True for ``invoice.*`` and ``account.*`` events (no workspace)."""
    return event_type.partition(".")[0] in ACCOUNT_LEVEL_RESOURCES


def validate_subscription(patterns: Iterable[str]) -> List[str]:
    """Validate an endpoint's subscription and return it de-duplicated and sorted.

    Allowed entries are ``*``, a resource wildcard such as ``task.*`` for a
    resource that exists in the catalog, or an exact event type. At least one
    and at most 50 entries are allowed.
    """
    unique = sorted(set(patterns))
    if not unique:
        raise ValueError("subscribe to at least one event type")
    if len(unique) > MAX_SUBSCRIPTION_ENTRIES:
        raise ValueError(f"at most {MAX_SUBSCRIPTION_ENTRIES} subscription entries are allowed")
    resources = {name.partition(".")[0] for name in EVENT_TYPES}
    for pattern in unique:
        if pattern == "*" or is_valid_event_type(pattern):
            continue
        if pattern.endswith(".*") and pattern[:-2] in resources:
            continue
        raise ValueError(f"unknown event type or pattern: {pattern!r}")
    return unique


def matches_subscription(event_type: str, patterns: Iterable[str]) -> bool:
    """Return True if an endpoint subscribed to ``patterns`` receives ``event_type``.

    The test event is delivered to every endpoint regardless of subscription.
    """
    if event_type == TEST_EVENT_TYPE:
        return True
    resource = event_type.partition(".")[0]
    return any(p in ("*", event_type, f"{resource}.*") for p in patterns)


def new_event_id() -> str:
    """Return a new event ID: ``evt_`` plus 10 uppercase letters and digits."""
    return "evt_" + "".join(secrets.choice(_ALPHABET) for _ in range(10))


def build_envelope(
    event_type: str,
    account_id: str,
    data: Mapping[str, Any],
    workspace_id: Optional[str] = None,
    *,
    event_id: Optional[str] = None,
    created_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Build the envelope that is sent as the body of a delivery.

    Workspace-level events need a ``workspace_id``; account-level events
    (``invoice.*``, ``account.*``) must not have one and carry ``null``.
    """
    if not is_valid_event_type(event_type):
        raise ValueError(f"unknown event type: {event_type!r}")
    if not _ACCOUNT_ID.match(account_id):
        raise ValueError(f"invalid account ID: {account_id!r}")
    if is_account_level(event_type):
        if workspace_id is not None:
            raise ValueError(f"{event_type} is account-level and has no workspace")
    elif workspace_id is None or not _WORKSPACE_ID.match(workspace_id):
        raise ValueError(f"{event_type} needs a valid workspace ID")
    event_id = event_id or new_event_id()
    if not _EVENT_ID.match(event_id):
        raise ValueError(f"invalid event ID: {event_id!r}")
    moment = (created_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return {
        "id": event_id,
        "type": event_type,
        "api_version": API_VERSION,
        "created_at": moment.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "account_id": account_id,
        "workspace_id": workspace_id,
        "data": dict(data),
    }


def serialize_envelope(envelope: Mapping[str, Any]) -> bytes:
    """Serialize an envelope to the exact UTF-8 bytes that are signed and sent."""
    body = json.dumps(envelope, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if len(body) > MAX_PAYLOAD_BYTES:
        raise PayloadTooLargeError(f"payload is {len(body)} bytes; the limit is {MAX_PAYLOAD_BYTES}")
    return body
