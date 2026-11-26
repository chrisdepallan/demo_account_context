"""Scope catalog, validation and least-privilege checks for integrations.

Integrations use the same scope names as API keys. A write scope always
includes the matching read scope, ``billing:read`` can never be granted to an
integration, and ``members:write`` is restricted to Owner approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Set


class ScopeError(ValueError):
    """Raised when a requested set of scopes is not valid for an integration."""


@dataclass(frozen=True)
class Scope:
    """One entry in the scope catalog."""

    name: str
    description: str
    restricted: bool = False
    grantable: bool = True

    @property
    def resource(self) -> str:
        """The part before the colon, for example ``projects``."""
        return self.name.split(":", 1)[0]

    @property
    def access(self) -> str:
        """The part after the colon: ``read`` or ``write``."""
        return self.name.split(":", 1)[1]


SCOPE_CATALOG: Dict[str, Scope] = {
    s.name: s
    for s in (
        Scope("projects:read", "Read projects, tasks and comments"),
        Scope("projects:write", "Create and edit projects, tasks and comments"),
        Scope("files:read", "Read file names, metadata and content"),
        Scope("files:write", "Upload, attach and rename files"),
        Scope("members:read", "Read member names, emails and roles"),
        Scope("members:write", "Invite and remove members", restricted=True),
        Scope("billing:read", "Read invoices and plan", grantable=False),
    )
}

#: Most scopes one install can hold: every scope except ``billing:read``.
MAX_SCOPES_PER_INSTALL = 6

#: Scopes each first-party app asks for.
FIRST_PARTY_SCOPES: Dict[str, FrozenSet[str]] = {
    "slack": frozenset({"projects:read", "projects:write", "members:read"}),
    "github": frozenset({"projects:read", "projects:write"}),
    "jira": frozenset({"projects:read", "projects:write", "members:read"}),
    "google-workspace": frozenset({"files:read", "files:write", "members:read"}),
}

_APPROVER_ROLES = {"owner", "admin"}


def validate_scopes(requested: Iterable[str]) -> List[str]:
    """Return the requested scopes de-duplicated and sorted.

    Raises ``ScopeError`` if the list is empty, has an unknown scope, has a
    scope that cannot be granted to integrations, or has too many scopes.
    """
    unique = sorted({s.strip().lower() for s in requested})
    if not unique:
        raise ScopeError("At least one scope is required.")
    for name in unique:
        scope = SCOPE_CATALOG.get(name)
        if scope is None:
            raise ScopeError(f"Unknown scope: {name}")
        if not scope.grantable:
            raise ScopeError(f"The scope {name} cannot be granted to an integration.")
    if len(unique) > MAX_SCOPES_PER_INSTALL:
        raise ScopeError(f"An install can hold at most {MAX_SCOPES_PER_INSTALL} scopes.")
    return unique


def expand_implied(scopes: Iterable[str]) -> Set[str]:
    """Return the scopes plus every read scope implied by a write scope."""
    expanded = set(scopes)
    for name in list(expanded):
        resource, _, access = name.partition(":")
        if access == "write":
            expanded.add(f"{resource}:read")
    return expanded


def has_scope(granted: Iterable[str], needed: str) -> bool:
    """Return True if the granted scopes allow ``needed``, counting implied reads."""
    return needed in expand_implied(granted)


def excess_scopes(requested: Iterable[str], needed: Iterable[str]) -> List[str]:
    """Return requested scopes that the app's features do not need."""
    return sorted(set(requested) - expand_implied(needed))


def is_least_privilege(requested: Iterable[str], needed: Iterable[str]) -> bool:
    """Return True if nothing is requested beyond what is needed."""
    return not excess_scopes(requested, needed)


def requires_owner_approval(scopes: Iterable[str]) -> bool:
    """Return True if any scope is restricted (currently ``members:write``)."""
    return any(SCOPE_CATALOG[s].restricted for s in scopes if s in SCOPE_CATALOG)


def can_approve(role: str, scopes: Iterable[str]) -> bool:
    """Return True if a person with ``role`` may approve an install with ``scopes``.

    Owners can approve anything. Admins can approve installs with no
    restricted scope. Billing admins, Members and Guests cannot approve.
    """
    role = role.strip().lower()
    if role not in _APPROVER_ROLES:
        return False
    if requires_owner_approval(scopes):
        return role == "owner"
    return True


def needs_reconsent(granted: Iterable[str], requested: Iterable[str]) -> bool:
    """Return True if ``requested`` adds anything not already granted.

    Removing scopes never needs consent. Asking for a read scope that is
    already implied by a granted write scope does not need consent either.
    """
    return bool(set(requested) - expand_implied(granted))
