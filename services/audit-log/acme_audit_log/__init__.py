"""Acme Cloud Audit Log service: entries, hash chain and retention rules.

The rules implemented here are described in the service docs:

- ``docs/recorded-events.md`` – :mod:`acme_audit_log.entries`
- ``docs/access-and-integrity.md`` – :mod:`acme_audit_log.hash_chain`
- ``docs/retention-and-export.md`` – :mod:`acme_audit_log.retention`
"""

from .entries import (
    AuditEntry,
    EntryValidationError,
    EventCategory,
    category_for,
    is_recorded,
    new_entry_id,
    validate_entry,
)
from .hash_chain import (
    GENESIS_HASH,
    ChainedEntry,
    HashChain,
    VerificationResult,
    canonical_json,
    compute_hash,
    verify_chain,
)
from .retention import (
    DOWNGRADE_GRACE_DAYS,
    RETENTION_DAYS,
    expires_at,
    has_audit_log,
    is_purge_eligible,
    next_purge_run,
    retention_days,
    select_purgeable,
)

__all__ = [
    "AuditEntry",
    "ChainedEntry",
    "DOWNGRADE_GRACE_DAYS",
    "EntryValidationError",
    "EventCategory",
    "GENESIS_HASH",
    "HashChain",
    "RETENTION_DAYS",
    "VerificationResult",
    "canonical_json",
    "category_for",
    "compute_hash",
    "expires_at",
    "has_audit_log",
    "is_purge_eligible",
    "is_recorded",
    "new_entry_id",
    "next_purge_run",
    "retention_days",
    "select_purgeable",
    "validate_entry",
    "verify_chain",
]
