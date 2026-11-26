# ADR 0010: Soft Delete with Retention Windows

## Status

Accepted on **2025-08-12**.

## Context

Acme Cloud promises that a closed account can be restored for **30 days**, as described in `services/accounts/docs/account-lifecycle.md`. Before this decision each service handled deletion in its own way. Some services erased rows immediately and others never erased them.

- Restoring a closed account brought back the account but not all of its projects and files.
- Support could not help a customer who deleted a project by mistake.
- Data that should have been erased after the retention window stayed in some databases.

With one database per service, deletion has to be the same pattern in every service to work at all.

## Decision

Every Acme Cloud service deletes customer data in two steps: a soft delete, then a hard delete after a retention window.

- **Soft delete** – the row is marked with a `deleted_at` timestamp and is hidden from every API response and search result. Nothing is erased.
- **Hard delete** – after the retention window, a scheduled job in the owning service erases the row and any object storage content.
- The retention window for a closed account is **30 days**. During the window the account is in the `closed` state and can be restored.
- The default retention window for a single deleted item, such as a project, task or file, is **30 days**. A service may document a different window for its own entities.
- The accounts service drives account-level deletion with events: `account.closed` starts the soft delete in every service, `account.restored` reverses the soft delete, and `account.deleted` on day **31** starts the hard delete.
- Every service must finish the hard delete within **24 hours** of receiving `account.deleted`.
- Database and object storage backups are kept for **35 days**, so erased data leaves the backups within a further **35 days**.
- Soft-deleted files still count towards the storage quota until they are hard-deleted or the account is closed.

## Consequences

- Restoring an account or an item is a metadata change and brings back everything consistently.
- Deletion follows one pattern in all **12 services**, so the full erasure of an account can be tested end to end.
- Every query in every service must filter out soft-deleted rows. The shared internal platform library provides the filter.
- Storage is used for up to **30 days** after a customer deletes something.
- Once an account is `deleted`, the data cannot be recovered by anyone, including Acme Cloud support.

## Alternatives considered

- **Immediate hard delete** – simplest and cheapest, but makes the **30-day** restore promise impossible.
- **Soft delete with no automatic hard delete** – easy restores, but data would be kept forever, against the stated retention policy.
- **Restore from backups on request** – no change to services, but a restore of one account from **12** separate database backups is slow, error-prone and risks overwriting newer data.
- **Move deleted rows to a separate archive database** – keeps live tables small, but doubles the schema work for every change.

The cross-service flow is shown in `docs/architecture/service-map.md`.

Last reviewed: 2026-11-26
