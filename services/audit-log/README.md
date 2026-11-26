# Audit Log Service

## What it does

The Audit Log service keeps an immutable record of security-relevant actions in an account: sign-ins, member and role changes, security settings, API keys, deletions, billing changes and account closure. Owners and Admins can view, filter and export the log, and stream it to a SIEM. The audit log is available on Pro, Business and Enterprise.

## Key concepts

- **Audit entry** – one recorded action: who did it, what, to which resource, when and from which IP address. IDs look like `aud_7H2KQ9M4XP`.
- **Event type** – the action name in `resource.action` form, for example `member.invited` or `api_key.revoked`.
- **Category** – one of **8** groups used for filtering: authentication, members, security, data, billing, integrations, account, audit.
- **Actor** – who performed the action: a `user`, an `api_key`, the `system`, or `support` (always with a ticket ID like `SUP-48213`).
- **Retention** – how long entries are kept: **90 days** on Pro, **1 year** on Business, **7 years** on Enterprise.
- **Hash chain** – each entry stores the SHA-256 hash of the entry before it, so any change or removal can be detected. There is one chain per account per region.
- **Checkpoint** – the latest hash of each chain, written once a day to write-once storage.
- **Export** – a CSV or JSON Lines file of entries for a date range; IDs look like `exp_3M7Q1Z8K`.
- **Stream** – continuous delivery of new entries to a SIEM; IDs look like `strm_6C2X9R4B`. Business and Enterprise only.

## How to use it

- Customer-facing view: **Settings → Security → Audit log** (Owner and Admin only).
- Exports: **Settings → Security → Audit log → Export**. Streams: **Settings → Security → Audit log → Streaming**.
- Internal API base URL: `https://api.acme-cloud.example/v2/audit-log`
- Common endpoints:
  - `GET /v2/audit-log/{account_id}/entries` – list and filter entries
  - `GET /v2/audit-log/{account_id}/entries/{entry_id}` – one entry with its hashes
  - `POST /v2/audit-log/{account_id}/exports` – start an export
  - `GET /v2/audit-log/{account_id}/exports/{export_id}` – export status and download link
  - `GET /v2/audit-log/{account_id}/streams` – list SIEM streams
  - `POST /v2/audit-log/{account_id}/streams` – create a SIEM stream
  - `DELETE /v2/audit-log/{account_id}/streams/{stream_id}` – delete a SIEM stream
  - `POST /v2/audit-log/{account_id}/verify` – verify the hash chain for a range
  - `GET /v2/audit-log/{account_id}/retention` – retention window and next purge

## Docs in this service

- `docs/recorded-events.md` – which actions are recorded and what an entry contains
- `docs/retention-and-export.md` – retention per plan, purging, CSV and JSON Lines export
- `docs/siem-streaming.md` – streaming entries to a SIEM, delivery and retries
- `docs/access-and-integrity.md` – who can see the log and how tampering is detected

## Code in this service

- `acme_audit_log/entries.py` – entry dataclass, event categories and validation
- `acme_audit_log/hash_chain.py` – SHA-256 hash chain and tamper verification
- `acme_audit_log/retention.py` – retention window per plan and purge eligibility
- `tests/` – unit tests; run `python -m unittest discover -s tests` from this folder
- `openapi.yaml` – OpenAPI 3.0 description of the endpoints above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings

## Owners

Team: Trust and Compliance. Slack channel: `#team-trust` (fictional).
