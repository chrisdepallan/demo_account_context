"""Project access rules.

Implements ``docs/permissions-and-sharing.md``: a person's access level on a
project is derived from their workspace role, the project's visibility,
whether they created it, and any explicit grant. Also holds the per-plan
limit on active projects from ``docs/projects-and-tasks.md``.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, Optional

WORKSPACE_ROLES = ("owner", "admin", "billing_admin", "member", "guest")
VISIBILITIES = ("workspace", "private")
PLANS = ("free", "starter", "pro", "business", "enterprise")

#: Active projects per workspace. None means unlimited.
PROJECT_LIMITS: Dict[str, Optional[int]] = {
    "free": 5,
    "starter": 50,
    "pro": 500,
    "business": None,
    "enterprise": None,
}

MAX_EXPLICIT_GRANTS_PER_PROJECT = 500


class Access(IntEnum):
    """Project access levels. Each level includes the ones below it."""

    NONE = 0
    VIEWER = 1
    COMMENTER = 2
    EDITOR = 3
    MANAGER = 4


#: Minimum access level needed for each action.
ACTION_REQUIREMENTS: Dict[str, Access] = {
    "view": Access.VIEWER,
    "export": Access.VIEWER,
    "comment": Access.COMMENTER,
    "create_task": Access.EDITOR,
    "edit_task": Access.EDITOR,
    "delete_own_task": Access.EDITOR,
    "delete_any_task": Access.MANAGER,
    "delete_any_comment": Access.MANAGER,
    "manage_settings": Access.MANAGER,
    "share_project": Access.MANAGER,
    "archive_project": Access.MANAGER,
    "delete_project": Access.MANAGER,
}

#: Guests can never be raised above commenter.
GUEST_MAX_ACCESS = Access.COMMENTER


def _check_role(role: str) -> None:
    if role not in WORKSPACE_ROLES:
        raise ValueError(f"unknown workspace role: {role!r}")


def effective_access(
    role: str,
    visibility: str = "workspace",
    is_creator: bool = False,
    grant: Optional[Access] = None,
) -> Access:
    """Return a person's access level on one project.

    - Owners and Admins manage every project, including private ones.
    - Billing admins cannot open projects at all.
    - Members edit ``workspace`` projects and manage projects they created;
      a grant can raise but never lower that.
    - Guests only get what was granted, capped at commenter.
    """
    _check_role(role)
    if visibility not in VISIBILITIES:
        raise ValueError(f"unknown visibility: {visibility!r}")
    granted = grant if grant is not None else Access.NONE

    if role in ("owner", "admin"):
        return Access.MANAGER
    if role == "billing_admin":
        return Access.NONE
    if role == "guest":
        return min(granted, GUEST_MAX_ACCESS)
    # member
    if is_creator:
        return Access.MANAGER
    base = Access.EDITOR if visibility == "workspace" else Access.NONE
    return max(base, granted)


def can(action: str, access: Access) -> bool:
    """Return True if ``access`` is enough to perform ``action``."""
    if action not in ACTION_REQUIREMENTS:
        raise ValueError(f"unknown action: {action!r}")
    return access >= ACTION_REQUIREMENTS[action]


def can_delete_task(access: Access, is_task_creator: bool) -> bool:
    """Editors delete tasks they created; managers delete any task."""
    if can("delete_any_task", access):
        return True
    return is_task_creator and can("delete_own_task", access)


def can_grant(role: str, level: Access) -> bool:
    """Return True if a person with ``role`` may be granted ``level``.

    Guests are capped at commenter and Billing admins cannot be given
    project access. Owners and Admins are already managers everywhere.
    """
    _check_role(role)
    if level == Access.NONE:
        return False
    if role == "billing_admin":
        return False
    if role == "guest":
        return level <= GUEST_MAX_ACCESS
    return True


def project_limit(plan: str) -> Optional[int]:
    """Return the active-project limit for ``plan`` (None = unlimited)."""
    if plan not in PROJECT_LIMITS:
        raise ValueError(f"unknown plan: {plan!r}")
    return PROJECT_LIMITS[plan]


def can_create_project(role: str, plan: str, active_projects: int) -> bool:
    """Owners, Admins and Members can create projects while under the limit."""
    _check_role(role)
    if role not in ("owner", "admin", "member"):
        return False
    limit = project_limit(plan)
    return limit is None or active_projects < limit
