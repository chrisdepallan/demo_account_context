"""Share link rules.

Implements ``docs/sharing-links.md``: which access levels a public link can
give on each plan, default and longest expiry, when a password is required,
and the lock after repeated wrong passwords.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

AUDIENCES = ("workspace", "invited", "anyone")
ACCESS_LEVELS = ("view", "comment", "edit")
CREATOR_ROLES = ("owner", "admin", "member")

#: Access levels an ``anyone`` (public) link may give, per plan.
PUBLIC_ACCESS: Dict[str, Tuple[str, ...]] = {
    "free": ("view",),
    "starter": ("view", "comment"),
    "pro": ("view", "comment", "edit"),
    "business": ("view", "comment", "edit"),
    "enterprise": ("view", "comment", "edit"),
}
#: Default expiry of a public link in days.
PUBLIC_DEFAULT_EXPIRY_DAYS: Dict[str, int] = {
    "free": 7, "starter": 30, "pro": 30, "business": 30, "enterprise": 30,
}
#: Longest expiry of a public link in days. None means "no expiry" is allowed.
PUBLIC_MAX_EXPIRY_DAYS: Dict[str, Optional[int]] = {
    "free": 7, "starter": 30, "pro": 365, "business": None, "enterprise": None,
}
PASSWORD_PLANS = ("starter", "pro", "business", "enterprise")

PASSWORD_MIN_CHARS = 8
MAX_FAILED_ATTEMPTS = 5
LOCK_MINUTES = 15
MAX_LINKS_PER_FILE = 50

#: Marker for "use the plan default" (None already means "no expiry").
DEFAULT = "default"


class ShareLinkError(ValueError):
    """Raised when a link request breaks the sharing rules."""

    code = "share_link_not_allowed"


@dataclass
class ShareLink:
    """A validated share link. The password itself is never kept here."""

    audience: str
    access: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    password_protected: bool = False
    revoked: bool = False
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None


def password_required(audience: str, access: str, require_policy: bool = False) -> bool:
    """Public edit links always need a password; the Admin policy covers all public links."""
    if audience != "anyone":
        return False
    return access == "edit" or require_policy


def effective_access(link_access: str, viewer_role: str) -> str:
    """Guests are limited to view and comment even on an edit link."""
    if viewer_role == "guest" and link_access == "edit":
        return "comment"
    return link_access


def create_link(
    plan: str,
    creator_role: str,
    audience: str,
    access: str,
    now: datetime,
    expires_in_days: object = DEFAULT,
    password: Optional[str] = None,
    require_password_policy: bool = False,
    public_links_enabled: bool = True,
    existing_links: int = 0,
) -> ShareLink:
    """Validate a link request and return the ShareLink, or raise ShareLinkError.

    ``expires_in_days`` is DEFAULT for the plan default, None for no expiry,
    or a positive number of days.
    """
    if plan not in PUBLIC_ACCESS:
        raise ValueError(f"unknown plan: {plan!r}")
    if audience not in AUDIENCES or access not in ACCESS_LEVELS:
        raise ShareLinkError("unknown audience or access level")
    if creator_role not in CREATOR_ROLES:
        raise ShareLinkError("guests and billing admins cannot create share links")
    if existing_links >= MAX_LINKS_PER_FILE:
        raise ShareLinkError(f"a file can have at most {MAX_LINKS_PER_FILE} active links")

    public = audience == "anyone"
    if public and not public_links_enabled:
        raise ShareLinkError("public links are turned off for this workspace")
    if public and access not in PUBLIC_ACCESS[plan]:
        raise ShareLinkError(f"public {access} links are not available on the {plan} plan")

    if password is not None:
        if plan not in PASSWORD_PLANS:
            raise ShareLinkError("link passwords are not available on the free plan")
        if len(password) < PASSWORD_MIN_CHARS:
            raise ShareLinkError(f"passwords need at least {PASSWORD_MIN_CHARS} characters")
    elif password_required(audience, access, require_password_policy):
        raise ShareLinkError("this public link needs a password")

    if expires_in_days == DEFAULT:
        expires_in_days = PUBLIC_DEFAULT_EXPIRY_DAYS[plan] if public else None
    if expires_in_days is not None and (
        not isinstance(expires_in_days, int) or expires_in_days < 1
    ):
        raise ShareLinkError("expiry must be a positive number of days")
    if public:
        longest = PUBLIC_MAX_EXPIRY_DAYS[plan]
        if longest is not None and (expires_in_days is None or expires_in_days > longest):
            raise ShareLinkError(
                f"public links on the {plan} plan expire after at most {longest} days"
            )

    expires_at = None if expires_in_days is None else now + timedelta(days=expires_in_days)
    return ShareLink(audience, access, now, expires_at, password is not None)


def is_active(link: ShareLink, now: datetime, file_trashed: bool = False) -> bool:
    """A link works unless it is revoked, expired or its file is in the trash."""
    if link.revoked or file_trashed:
        return False
    return link.expires_at is None or now < link.expires_at


def is_locked(link: ShareLink, now: datetime) -> bool:
    """Return True while the link is locked after too many wrong passwords."""
    return link.locked_until is not None and now < link.locked_until


def record_password_attempt(link: ShareLink, correct: bool, now: datetime) -> bool:
    """Record a password attempt; return True if access is granted.

    After 5 wrong attempts the link is locked for 15 minutes. Attempts made
    while locked are refused, even with the right password.
    """
    if is_locked(link, now):
        return False
    if correct:
        link.failed_attempts = 0
        link.locked_until = None
        return True
    link.failed_attempts += 1
    if link.failed_attempts >= MAX_FAILED_ATTEMPTS:
        link.locked_until = now + timedelta(minutes=LOCK_MINUTES)
        link.failed_attempts = 0
    return False
