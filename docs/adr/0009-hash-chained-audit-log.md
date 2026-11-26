# ADR 0009: Hash-Chained Audit Log

## Status

Accepted on **2025-05-20**.

## Context

Acme Cloud customers on Pro, Business and Enterprise get an audit log of security events such as logins, role changes, API key changes and sharing link creation. Audit log retention is **90 days** on Pro, **1 year** on Business and **7 years** on Enterprise. Enterprise security reviews asked a specific question: how can the customer be sure that nobody, including an Acme Cloud engineer with database access, has changed or removed an audit entry?

Before this decision, audit entries were ordinary rows in a PostgreSQL table. An administrator could update or delete a row without leaving a trace.

## Decision

The audit-log service stores audit entries as an append-only, hash-chained log.

- Every audit entry has an ID of `aud_` plus **10** uppercase alphanumerics.
- Each entry stores a SHA-256 hash computed over the entry's own content and the hash of the previous entry.
- There is one chain per account per region, so that verifying one account's log never needs another account's data and no chain crosses a region.
- The audit-log service never updates or deletes an entry inside the retention period. The only exception is the erasure of a whole account's chain after the `account.deleted` event. The database role used by the service has insert and read rights only.
- Once a day, the audit-log service writes a checkpoint with the latest hash of each chain to the regional object store with write-once protection.
- Customers can export the log and verify the chain themselves by recomputing the hashes.
- Entries are written from events on the Acme Event Bus, with an SLO of **99%** of entries written within **10 seconds** of the triggering event.
- When the retention period of an entry ends, whole entries are removed from the oldest end of the chain and the oldest remaining checkpoint becomes the new starting point.

## Consequences

- Any change to an old entry changes every later hash, so tampering is detectable by the customer and by Acme Cloud.
- The daily checkpoint in write-once storage means that rewriting the whole chain is also detectable.
- Entries for one account must be written in order, which limits write parallelism to one writer per account chain.
- A mistake in an entry cannot be corrected in place. A correcting entry is appended instead.
- Audit entries hold IDs and event facts, not file content, so that the log can be kept for up to **7 years** without keeping the content.
- Verification of a long chain takes time, so exports include the checkpoints to allow verification in sections.

## Alternatives considered

- **Plain database table with restricted permissions** – simple, but relies on trusting every administrator.
- **Write-once object storage only, without hashes** – protects against deletion, but is slow to query and gives the customer nothing to verify.
- **A public blockchain or external timestamping service** – strong proof, but adds an external dependency and sends data about customer activity outside the region.
- **A Merkle tree per account** – faster partial verification, but more complex for customers to check. A tree can be added on top of the chain later.

Service details are in `services/audit-log/README.md`.

Last reviewed: 2026-11-26
