"""Plan limits table and limit checks.

Implements ``docs/plans-and-limits.md`` and the workspace and region rules
in ``docs/workspaces.md``. ``None`` in a limit means "unlimited".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

GUESTS_PER_PAID_SEAT = 5
STORAGE_WARNING_RATIO = 0.90
STORAGE_PACK_GB = 100
ENTERPRISE_MIN_SEATS = 50
DEFAULT_REGION = "us-east"


@dataclass(frozen=True)
class Plan:
    """Limits and features of one plan."""

    name: str
    max_members: Optional[int]
    workspaces: Optional[int]
    storage_gb: int
    storage_per_seat: bool
    max_upload_mb: int
    version_history_days: Optional[int]
    api_requests_per_minute: int
    sso: bool
    scim: bool
    audit_log_retention_days: Optional[int]
    regions: Tuple[str, ...]
    paid: bool = True


PLANS: Dict[str, Plan] = {
    "free": Plan("free", 3, 1, 2, False, 250, 7, 100, False, False, None, ("us-east",), paid=False),
    "starter": Plan("starter", 10, 1, 10, True, 250, 30, 300, False, False, None, ("us-east",)),
    "pro": Plan("pro", 100, 3, 50, True, 5120, 180, 1000, False, False, 90, ("us-east",)),
    "business": Plan("business", 500, 10, 200, True, 5120, 365, 3000, True, False, 365, ("us-east", "eu-central")),
    "enterprise": Plan(
        "enterprise", None, None, 1024, True, 5120, None, 10000, True, True, 7 * 365,
        ("us-east", "eu-central", "ap-south"),
    ),
}

#: Plans from lowest to highest.
PLAN_ORDER: Tuple[str, ...] = ("free", "starter", "pro", "business", "enterprise")


def get_plan(name: str) -> Plan:
    """Return the plan called ``name`` (case-insensitive) or raise KeyError."""
    return PLANS[name.strip().lower()]


def _within(limit: Optional[int], value: int) -> bool:
    return limit is None or value <= limit


def can_add_members(plan: Plan, current_members: int, to_add: int = 1) -> bool:
    """Return True if ``to_add`` more members fit in the plan's member limit."""
    return _within(plan.max_members, current_members + to_add)


def can_create_workspace(plan: Plan, current_workspaces: int) -> bool:
    """Return True if the account may create one more workspace."""
    return _within(plan.workspaces, current_workspaces + 1)


def region_allowed(plan: Plan, region: str) -> bool:
    """Return True if workspaces on this plan may be created in ``region``."""
    return region in plan.regions


def max_guests(plan: Plan, paid_seats: int) -> int:
    """Return the guest allowance: 5 per paid seat, none on Free."""
    return GUESTS_PER_PAID_SEAT * paid_seats if plan.paid else 0


def storage_limit_gb(plan: Plan, seats: int, storage_packs: int = 0) -> int:
    """Return total storage in GB, including 100 GB storage packs."""
    base = plan.storage_gb * seats if plan.storage_per_seat else plan.storage_gb
    return base + storage_packs * STORAGE_PACK_GB


def storage_status(used_gb: float, limit_gb: float) -> str:
    """Return ``ok``, ``warning`` (90% or more) or ``blocked`` (100% or more)."""
    if used_gb >= limit_gb:
        return "blocked"
    if used_gb >= STORAGE_WARNING_RATIO * limit_gb:
        return "warning"
    return "ok"


def upload_allowed(plan: Plan, file_size_mb: float) -> bool:
    """Return True if a single file of this size may be uploaded."""
    return file_size_mb <= plan.max_upload_mb


def is_upgrade(current: Plan, target: Plan) -> bool:
    """Return True if ``target`` is a higher plan than ``current``."""
    return PLAN_ORDER.index(target.name) > PLAN_ORDER.index(current.name)


def members_converted_to_guests(member_count: int) -> int:
    """Return how many members become guests when a trial ends on Free."""
    return max(0, member_count - (PLANS["free"].max_members or 0))


def downgrade_blockers(
    target: Plan, members: int, workspaces: int, used_storage_gb: float, seats: int
) -> List[str]:
    """Return the reasons a downgrade to ``target`` is blocked (empty if allowed)."""
    reasons: List[str] = []
    if not _within(target.max_members, members):
        reasons.append(f"members: {members} exceeds the limit of {target.max_members}")
    if not _within(target.workspaces, workspaces):
        reasons.append(f"workspaces: {workspaces} exceeds the limit of {target.workspaces}")
    limit = storage_limit_gb(target, seats)
    if used_storage_gb > limit:
        reasons.append(f"storage: {used_storage_gb} GB exceeds the limit of {limit} GB")
    if target.name == "enterprise" and seats < ENTERPRISE_MIN_SEATS:
        reasons.append(f"seats: Enterprise needs at least {ENTERPRISE_MIN_SEATS} seats")
    return reasons
