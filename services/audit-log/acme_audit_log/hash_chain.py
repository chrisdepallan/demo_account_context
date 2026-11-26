"""SHA-256 hash chain over audit entries, and tamper verification.

There is one chain per account per region. Every entry in a chain carries a ``sequence`` number, the
hash of the entry before it (``prev_hash``) and its own ``hash``::

    hash = SHA-256(prev_hash + "\\n" + sequence + "\\n" + canonical JSON of the entry)

The first entry of a chain uses :data:`GENESIS_HASH` (64 zeros) as its
``prev_hash``. Changing, removing or reordering any entry breaks every
hash after it, which :func:`verify_chain` detects.

When old entries are purged at the end of the retention window, the hash
of the last purged entry is kept as a checkpoint. Verification of the
remaining entries starts from that checkpoint instead of the genesis hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import timezone
from typing import List, Optional, Sequence

from .entries import AuditEntry, validate_entry

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class ChainedEntry:
    """An entry plus its position and hashes in the chain."""

    entry: AuditEntry
    sequence: int
    prev_hash: str
    hash: str


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of :func:`verify_chain`."""

    valid: bool
    checked: int
    first_invalid_sequence: Optional[int] = None
    reason: Optional[str] = None


def canonical_json(entry: AuditEntry) -> str:
    """Serialise ``entry`` deterministically.

    Keys are sorted, there is no extra whitespace and the timestamp is
    converted to UTC with microsecond precision, so the same entry always
    produces the same bytes on every machine.
    """
    data = asdict(entry)
    data["metadata"] = dict(entry.metadata)
    data["occurred_at"] = (
        entry.occurred_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_hash(prev_hash: str, sequence: int, entry: AuditEntry) -> str:
    """Return the hex SHA-256 hash that links ``entry`` to ``prev_hash``."""
    payload = f"{prev_hash}\n{sequence}\n{canonical_json(entry)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class HashChain:
    """Append-only, in-memory chain for one account in one region.

    There is deliberately no method to update or delete an entry.
    """

    def __init__(self, start_hash: str = GENESIS_HASH, start_sequence: int = 1) -> None:
        self._start_hash = start_hash
        self._next_sequence = start_sequence
        self._entries: List[ChainedEntry] = []

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def head(self) -> str:
        """Hash of the newest entry, or the start hash if the chain is empty."""
        return self._entries[-1].hash if self._entries else self._start_hash

    @property
    def entries(self) -> Sequence[ChainedEntry]:
        """The chained entries, oldest first (read-only copy)."""
        return tuple(self._entries)

    def append(self, entry: AuditEntry) -> ChainedEntry:
        """Validate ``entry``, link it to the head and return the result."""
        validate_entry(entry)
        if self._entries:
            first = self._entries[0].entry
            if (entry.account_id, entry.region) != (first.account_id, first.region):
                raise ValueError("a chain holds entries of one account in one region")
        prev_hash = self.head
        sequence = self._next_sequence
        chained = ChainedEntry(entry, sequence, prev_hash, compute_hash(prev_hash, sequence, entry))
        self._entries.append(chained)
        self._next_sequence += 1
        return chained

    def verify(self) -> VerificationResult:
        """Verify this chain from its own start hash."""
        return verify_chain(self._entries, self._start_hash)


def verify_chain(
    entries: Sequence[ChainedEntry], start_hash: str = GENESIS_HASH
) -> VerificationResult:
    """Check that ``entries`` form an unbroken, unmodified chain.

    :param entries: chained entries, oldest first.
    :param start_hash: :data:`GENESIS_HASH`, or the checkpoint hash kept
        when older entries were purged.
    :return: a result naming the first sequence number that fails, with one
        of the reasons ``prev_hash_mismatch``, ``sequence_gap`` or
        ``hash_mismatch``.
    """
    expected_prev = start_hash
    expected_sequence: Optional[int] = None
    for checked, item in enumerate(entries):
        if item.prev_hash != expected_prev:
            return VerificationResult(False, checked, item.sequence, "prev_hash_mismatch")
        if expected_sequence is not None and item.sequence != expected_sequence:
            return VerificationResult(False, checked, item.sequence, "sequence_gap")
        if compute_hash(item.prev_hash, item.sequence, item.entry) != item.hash:
            return VerificationResult(False, checked, item.sequence, "hash_mismatch")
        expected_prev = item.hash
        expected_sequence = item.sequence + 1
    return VerificationResult(True, len(entries))
