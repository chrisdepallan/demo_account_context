# Audit Log Retention and Export

## How long are audit log entries kept?

| Plan | Audit log retention |
|------|---------------------|
| Free | No audit log |
| Starter | No audit log |
| Pro | **90 days** |
| Business | **1 year** (365 days) |
| Enterprise | **7 years** (2,555 days) |

These match the plan table in `services/accounts/docs/plans-and-limits.md`. Retention is counted from the time of the action, not from when the entry was viewed or exported.

## What happens to entries older than the retention window?

They are permanently deleted by a purge job that runs once a day at **02:00 UTC**. Deleted entries cannot be recovered by the customer or by support. To keep entries for longer than the plan allows, export them or stream them to a SIEM before they expire.

Entries are always purged oldest first. A checkpoint hash is kept as the new starting point so the remaining entries can still be verified; see `services/audit-log/docs/access-and-integrity.md`.

## What happens to the audit log when I upgrade?

The longer retention applies immediately to every entry that still exists. Entries that were already purged under the old plan do not come back. An account upgrading from Free or Starter to Pro starts with an empty audit log, because nothing was recorded before the upgrade.

## What happens to the audit log when I downgrade?

There is a **30-day** grace period. For 30 days after the downgrade takes effect, nothing is purged under the new, shorter window, so there is time to export. After that the new window applies:

- Business to Pro: entries older than **90 days** are purged.
- Any plan to Starter or Free: all entries are purged, and recording stops on the day the downgrade takes effect.

Downgrades take effect at the end of the billing period, as described in `services/accounts/docs/plans-and-limits.md`.

## What happens to the audit log when an account is closed?

Closing the account is recorded as `account.closed`. The log is kept during the **30-day** data retention window so it is still there if the account is restored, and is deleted with the rest of the account's data after that, when the account reaches the `deleted` state.

## Can retention be paused for a legal hold?

Yes, on **Enterprise only**. The Owner asks the Customer Success Manager or `support@acme-cloud.example` to place a legal hold. While the hold is active no entries are purged, even beyond 7 years. Starting and ending a hold are themselves recorded in the audit log.

## How do I export the audit log?

Owners and Admins go to **Settings → Security → Audit log → Export**, choose a date range, optional filters (category, event type, actor) and a format:

- **CSV** – one row per entry, for spreadsheets.
- **JSON Lines** – one JSON object per line, including the hash chain fields and the daily checkpoints, for scripts and SIEM import.

The export runs in the background. An email with a download link is sent when it is ready, usually within **30 minutes**.

## What are the export limits?

- Up to **1,000,000 entries** per export. Split larger ranges into several exports.
- Up to **5 exports per account per day** (UTC).
- The download link is valid for **24 hours** and works only for signed-in Owners and Admins of the account.
- Only entries inside the retention window can be exported.

Every export is recorded as `audit_log.exported` with the person who requested it and the date range.

## Can I export the audit log through the API?

Yes. Start an export with `POST /v2/audit-log/{account_id}/exports` and poll `GET /v2/audit-log/{account_id}/exports/{export_id}` until its status is `ready`. To read entries directly instead, page through `GET /v2/audit-log/{account_id}/entries`, which returns **50 entries** per page by default and at most **200**.

Last reviewed: 2026-11-26
