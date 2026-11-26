"""Password rules, history, expiry and reset links.

Implements ``docs/passwords-and-mfa.md``: 12 to 128 characters, not in a
breached-password list, must not contain the user's email address, and
the last 5 passwords cannot be reused.
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Collection, List, Optional, Tuple

MIN_LENGTH = 12
MAX_LENGTH = 128
HISTORY_SIZE = 5
ALLOWED_EXPIRY_DAYS: Tuple[int, ...] = (30, 60, 90)
RESET_LINK_MINUTES = 60
PBKDF2_ITERATIONS = 100_000

TOO_SHORT = "too_short"
TOO_LONG = "too_long"
BREACHED = "breached"
CONTAINS_EMAIL = "contains_email"
REUSED = "reused"


def hash_password(password: str, salt: bytes) -> bytes:
    """Return a salted PBKDF2-SHA256 hash of ``password``."""
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)


class PasswordHistory:
    """Salted hashes of a user's most recent passwords (newest last).

    Only the last 5 are kept, which is exactly the set that may not be
    reused.
    """

    def __init__(self, salt: bytes) -> None:
        self._salt = salt
        self._hashes: List[bytes] = []

    def __len__(self) -> int:
        return len(self._hashes)

    def add(self, password: str) -> None:
        """Record a newly set password and drop entries older than the last 5."""
        self._hashes.append(hash_password(password, self._salt))
        del self._hashes[:-HISTORY_SIZE]

    def contains(self, password: str) -> bool:
        """Return True if ``password`` is one of the last 5 passwords."""
        candidate = hash_password(password, self._salt)
        return any(hmac.compare_digest(candidate, stored) for stored in self._hashes)


def validate_password(
    password: str,
    email: str,
    breached: Collection[str] = (),
    history: Optional[PasswordHistory] = None,
) -> List[str]:
    """Return the list of rules ``password`` breaks (empty if acceptable).

    ``breached`` is the set of known breached passwords to check against.
    """
    problems: List[str] = []
    if len(password) < MIN_LENGTH:
        problems.append(TOO_SHORT)
    if len(password) > MAX_LENGTH:
        problems.append(TOO_LONG)
    if password in breached:
        problems.append(BREACHED)
    if email and email.strip().lower() in password.lower():
        problems.append(CONTAINS_EMAIL)
    if history is not None and history.contains(password):
        problems.append(REUSED)
    return problems


def is_valid_password(
    password: str,
    email: str,
    breached: Collection[str] = (),
    history: Optional[PasswordHistory] = None,
) -> bool:
    """Return True if ``password`` breaks no rule."""
    return not validate_password(password, email, breached, history)


def validate_expiry_setting(days: Optional[int]) -> Optional[int]:
    """Check a workspace's forced-expiry setting: None (off), 30, 60 or 90 days."""
    if days is not None and days not in ALLOWED_EXPIRY_DAYS:
        raise ValueError(f"password expiry must be one of {ALLOWED_EXPIRY_DAYS} days or off")
    return days


def password_expired(changed_at: datetime, now: datetime, expiry_days: Optional[int]) -> bool:
    """Return True if a forced expiry is set and the password is older than it."""
    if validate_expiry_setting(expiry_days) is None:
        return False
    return now >= changed_at + timedelta(days=expiry_days or 0)


def reset_link_valid(issued_at: datetime, now: datetime, already_used: bool = False) -> bool:
    """A reset link works once, for 60 minutes after it was issued."""
    if already_used:
        return False
    return issued_at <= now < issued_at + timedelta(minutes=RESET_LINK_MINUTES)
