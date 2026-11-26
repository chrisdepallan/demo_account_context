"""Storage quotas and upload checks.

Implements ``docs/storage-quotas.md`` and ``docs/uploads-and-limits.md``:
quota per plan and seat, storage packs, the 90% warning and 100% block, the
maximum file size per plan and the blocked file types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

MB = 1024 ** 2
GB = 1024 ** 3
TB = 1024 ** 4

PLANS = ("free", "starter", "pro", "business", "enterprise")

#: Free gets a fixed total; paid plans get this much per paid seat.
FREE_TOTAL_BYTES = 2 * GB
STORAGE_PER_SEAT_BYTES: Dict[str, int] = {
    "starter": 10 * GB,
    "pro": 50 * GB,
    "business": 200 * GB,
    "enterprise": 1 * TB,
}

MAX_FILE_BYTES: Dict[str, int] = {
    "free": 250 * MB,
    "starter": 250 * MB,
    "pro": 5 * GB,
    "business": 5 * GB,
    "enterprise": 5 * GB,
}

STORAGE_PACK_BYTES = 100 * GB
MAX_STORAGE_PACKS = 50
WARNING_THRESHOLD = 0.90
SINGLE_REQUEST_MAX_BYTES = 100 * MB
BLOCKED_EXTENSIONS = (".exe", ".bat", ".cmd", ".scr", ".msi", ".vbs")
UPLOAD_ROLES = ("owner", "admin", "member")


@dataclass(frozen=True)
class UploadDecision:
    """Result of an upload check. ``error`` is the API error code, if any."""

    allowed: bool
    error: Optional[str] = None
    resumable: bool = False


def _check_plan(plan: str) -> None:
    if plan not in PLANS:
        raise ValueError(f"unknown plan: {plan!r}")


def quota_bytes(plan: str, seats: int = 1, storage_packs: int = 0) -> int:
    """Return the account's total storage quota in bytes.

    Free is 2 GB in total regardless of members and cannot add packs. Paid
    plans get the per-seat allowance times seats, plus 100 GB per pack.
    """
    _check_plan(plan)
    if seats < 1:
        raise ValueError("an account has at least one seat")
    if not 0 <= storage_packs <= MAX_STORAGE_PACKS:
        raise ValueError(f"storage packs must be between 0 and {MAX_STORAGE_PACKS}")
    if plan == "free":
        if storage_packs:
            raise ValueError("storage packs are not available on the Free plan")
        return FREE_TOTAL_BYTES
    return STORAGE_PER_SEAT_BYTES[plan] * seats + STORAGE_PACK_BYTES * storage_packs


def percent_used(used_bytes: int, quota: int) -> float:
    """Return usage as a percentage of the quota, rounded to one decimal."""
    if quota <= 0:
        raise ValueError("quota must be positive")
    return round(used_bytes / quota * 100, 1)


def usage_state(used_bytes: int, quota: int) -> str:
    """Return ``ok``, ``warning`` (from 90%) or ``blocked`` (at 100%)."""
    if quota <= 0:
        raise ValueError("quota must be positive")
    if used_bytes >= quota:
        return "blocked"
    if used_bytes >= quota * WARNING_THRESHOLD:
        return "warning"
    return "ok"


def max_file_bytes(plan: str) -> int:
    """Return the largest single file the plan can upload."""
    _check_plan(plan)
    return MAX_FILE_BYTES[plan]


def is_blocked_file_type(name: str) -> bool:
    """Return True if the file name ends in a blocked extension."""
    return name.lower().endswith(BLOCKED_EXTENSIONS)


def check_upload(
    plan: str,
    role: str,
    name: str,
    size_bytes: int,
    used_bytes: int,
    seats: int = 1,
    storage_packs: int = 0,
    account_state: str = "active",
) -> UploadDecision:
    """Decide whether an upload may start, in the order the API checks it."""
    if role not in UPLOAD_ROLES or account_state == "read_only":
        return UploadDecision(False, "forbidden")
    if is_blocked_file_type(name):
        return UploadDecision(False, "file_type_blocked")
    if size_bytes > max_file_bytes(plan):
        return UploadDecision(False, "file_too_large")
    if used_bytes + size_bytes > quota_bytes(plan, seats, storage_packs):
        return UploadDecision(False, "quota_exceeded")
    return UploadDecision(True, None, resumable=size_bytes > SINGLE_REQUEST_MAX_BYTES)


def can_downgrade(
    used_bytes: int, new_plan: str, new_seats: int = 1, new_storage_packs: int = 0
) -> bool:
    """A downgrade is blocked while usage is above the quota it would leave."""
    return used_bytes <= quota_bytes(new_plan, new_seats, new_storage_packs)
