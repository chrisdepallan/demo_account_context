"""HMAC-SHA256 signing and verification of webhook deliveries.

Every delivery carries an ``Acme-Signature`` header of the form
``t=<unix timestamp>,v1=<hex signature>``. The signature is the HMAC-SHA256 of
``"<timestamp>.<raw request body>"`` keyed with the endpoint's signing secret.
During the 24 hours after a secret rotation the header carries two ``v1``
values, one per secret. Receivers reject timestamps more than 5 minutes off.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import List, Optional, Sequence, Tuple, Union

SIGNATURE_HEADER = "Acme-Signature"
SIGNATURE_VERSION = "v1"
SECRET_PREFIX = "whsec_"
DEFAULT_TOLERANCE_SECONDS = 300
ROTATION_OVERLAP_SECONDS = 24 * 60 * 60

Payload = Union[bytes, str]


class SignatureVerificationError(Exception):
    """Raised when a delivery's signature header is malformed, stale or wrong."""


def generate_secret() -> str:
    """Return a new random signing secret such as ``whsec_`` plus 32 characters."""
    return SECRET_PREFIX + secrets.token_hex(16)


def _to_bytes(payload: Payload) -> bytes:
    return payload.encode("utf-8") if isinstance(payload, str) else payload


def compute_signature(secret: str, timestamp: int, payload: Payload) -> str:
    """Return the lowercase hex HMAC-SHA256 of ``"<timestamp>.<payload>"``."""
    if not secret:
        raise ValueError("signing secret must not be empty")
    signed = str(int(timestamp)).encode("ascii") + b"." + _to_bytes(payload)
    return hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()


def build_signature_header(
    signing_secrets: Union[str, Sequence[str]],
    payload: Payload,
    timestamp: Optional[int] = None,
) -> str:
    """Build the ``Acme-Signature`` header value for a delivery.

    Pass one secret normally, or the new and the old secret (in that order)
    while a rotation overlap is active; each secret adds one ``v1`` entry.
    """
    if isinstance(signing_secrets, str):
        signing_secrets = [signing_secrets]
    if not signing_secrets:
        raise ValueError("at least one signing secret is required")
    ts = int(time.time()) if timestamp is None else int(timestamp)
    parts = [f"t={ts}"]
    parts += [f"{SIGNATURE_VERSION}={compute_signature(s, ts, payload)}" for s in signing_secrets]
    return ",".join(parts)


def parse_signature_header(header: str) -> Tuple[int, List[str]]:
    """Split a header value into its timestamp and list of ``v1`` signatures.

    Unknown keys are ignored so that future signature versions do not break
    existing receivers. Raises SignatureVerificationError if the timestamp or
    all ``v1`` signatures are missing.
    """
    timestamp: Optional[int] = None
    signatures: List[str] = []
    for part in (header or "").split(","):
        key, sep, value = part.strip().partition("=")
        if not sep:
            continue
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError:
                raise SignatureVerificationError("timestamp is not a number") from None
        elif key == SIGNATURE_VERSION:
            signatures.append(value)
    if timestamp is None:
        raise SignatureVerificationError("signature header has no timestamp")
    if not signatures:
        raise SignatureVerificationError("signature header has no v1 signature")
    return timestamp, signatures


def verify_signature(
    secret: str,
    payload: Payload,
    header: str,
    tolerance: int = DEFAULT_TOLERANCE_SECONDS,
    now: Optional[float] = None,
) -> int:
    """Verify a delivery and return its timestamp.

    ``payload`` must be the raw request body, exactly as received. The
    comparison is constant-time. Raises SignatureVerificationError if the
    header is malformed, the timestamp is more than ``tolerance`` seconds from
    ``now`` (in either direction), or no signature matches.
    """
    timestamp, signatures = parse_signature_header(header)
    current = time.time() if now is None else now
    if abs(current - timestamp) > tolerance:
        raise SignatureVerificationError("timestamp is outside the tolerance window")
    expected = compute_signature(secret, timestamp, payload)
    matched = False
    for candidate in signatures:  # check all, so timing does not reveal which one matched
        if hmac.compare_digest(expected.encode("ascii"), candidate.encode("utf-8")):
            matched = True
    if not matched:
        raise SignatureVerificationError("no signature matches the payload")
    return timestamp


def is_valid_signature(
    secret: str,
    payload: Payload,
    header: str,
    tolerance: int = DEFAULT_TOLERANCE_SECONDS,
    now: Optional[float] = None,
) -> bool:
    """Return True if the delivery verifies, False otherwise (never raises)."""
    try:
        verify_signature(secret, payload, header, tolerance, now)
    except (SignatureVerificationError, ValueError):
        return False
    return True
