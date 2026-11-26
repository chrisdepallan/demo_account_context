"""Acme Cloud Webhooks service: event envelope, signing and retry rules.

The rules implemented here are documented in ``docs/event-catalog.md``,
``docs/signing-and-verification.md`` and ``docs/retries-and-failures.md``.
"""

from . import events, retry, signing
from .events import (
    EVENT_TYPES,
    MAX_PAYLOAD_BYTES,
    PayloadTooLargeError,
    build_envelope,
    is_account_level,
    is_valid_event_type,
    matches_subscription,
    new_event_id,
    serialize_envelope,
    validate_subscription,
)
from .retry import (
    DISABLE_THRESHOLD,
    MAX_ATTEMPTS,
    RETRY_DELAYS_SECONDS,
    WARNING_THRESHOLD,
    EndpointHealth,
    classify_response,
    next_retry_delay,
    total_retry_window_seconds,
)
from .signing import (
    DEFAULT_TOLERANCE_SECONDS,
    SIGNATURE_HEADER,
    SignatureVerificationError,
    build_signature_header,
    compute_signature,
    generate_secret,
    is_valid_signature,
    parse_signature_header,
    verify_signature,
)

__version__ = "2.0.0"

__all__ = [
    "DEFAULT_TOLERANCE_SECONDS",
    "DISABLE_THRESHOLD",
    "EVENT_TYPES",
    "EndpointHealth",
    "MAX_ATTEMPTS",
    "MAX_PAYLOAD_BYTES",
    "PayloadTooLargeError",
    "RETRY_DELAYS_SECONDS",
    "SIGNATURE_HEADER",
    "SignatureVerificationError",
    "WARNING_THRESHOLD",
    "build_envelope",
    "build_signature_header",
    "classify_response",
    "compute_signature",
    "events",
    "generate_secret",
    "is_account_level",
    "is_valid_event_type",
    "is_valid_signature",
    "matches_subscription",
    "new_event_id",
    "next_retry_delay",
    "parse_signature_header",
    "retry",
    "serialize_envelope",
    "signing",
    "total_retry_window_seconds",
    "validate_subscription",
    "verify_signature",
]
