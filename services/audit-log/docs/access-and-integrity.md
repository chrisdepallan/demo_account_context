# Audit Log Access and Integrity

## Who can see the audit log?

| Action | Owner | Admin | Billing admin | Member | Guest |
|--------|-------|-------|---------------|--------|-------|
| View and filter entries | Yes | Yes | No | No | No |
| Export entries | Yes | Yes | No | No | No |
| Create or delete SIEM streams | Yes | Yes | No | No | No |
| Run an integrity check | Yes | Yes | No | No | No |
| Edit or delete entries | No | No | No | No | No |

The log is under **Settings → Security → Audit log**. It covers every workspace in the account; use the workspace filter to narrow it down. Role permissions in general are described in `services/accounts/docs/members-and-roles.md`.

## Can anyone edit or delete audit log entries?

No. Entries are append-only. Nobody can change or delete an entry: not the Owner, not an Admin and not Acme Cloud staff. Entries leave the log only when they pass the plan's retention window, as described in `services/audit-log/docs/retention-and-export.md`.

## Can Acme Cloud support see my audit log?

Only with a reason. A support agent can open an account's audit log when working on a support ticket, and that access is itself recorded as `support.accessed` with the ticket ID, for example `SUP-48213`. Customers can filter by actor type `support` to review every such access.

## How do I filter the audit log?

Entries can be filtered by:

- date range
- category, such as authentication or billing
- event type, such as `member.role_changed`
- actor (email address, API key name, `system` or `support`)
- workspace
- IP address

Filters can be combined. The view shows **50 entries** per page, newest first.

## Can I read the audit log through the API?

Yes, on Pro and above. Use `GET /v2/audit-log/{account_id}/entries` with an API key that has the `members:read` scope. Only Owners and Admins can create API keys, so the same people control API access to the log. Narrow the time range with `occurred_after` and `occurred_before`. A page returns **50 entries** by default and at most **200**; requests count against the account's API rate limit.

## How does Acme Cloud prove that entries were not tampered with?

Every entry is linked to the one before it in a **hash chain**. There is one chain per account per region, so no chain crosses a region:

- Each entry has a `sequence` number, starting at **1** for the chain and increasing by one.
- Each entry stores `prev_hash`, the hash of the previous entry, and its own `hash`.
- The hash is **SHA-256** over the previous hash, the sequence number and the entry's content in a fixed JSON form.
- The first entry of a chain uses a `prev_hash` of **64 zeros**.
- **Once a day** the latest hash of each chain is written as a checkpoint to write-once storage in the same region, so rewriting a whole chain would also be detected.

If any entry were changed, removed or reordered, its hash and every hash after it would no longer match.

## How do I verify the audit log myself?

There are two ways:

- **In the app** – select **Settings → Security → Audit log → Verify integrity** and pick a date range. The check covers up to **100,000 entries** per run and reports either "intact" or the first sequence number that fails.
- **Independently** – export the range as JSON Lines, which includes `sequence`, `prev_hash` and `hash`, and recompute the hashes with your own script. The reference implementation is listed in `services/audit-log/README.md` under "Code in this service".

A failed check is treated as a security incident: contact `support@acme-cloud.example` and it is escalated to the Trust and Compliance team.

## What does verification look like after old entries are purged?

When entries pass the retention window they are purged oldest first, so the log always remains one continuous run of entries. The hash of the last purged entry is kept as a **checkpoint**. Verification of the remaining entries starts from that checkpoint instead of from the 64 zeros. The background to this design is in `docs/adr/0009-hash-chained-audit-log.md`.

## Where are audit log entries stored?

Entries about a workspace are stored in that workspace's region: `us-east`, `eu-central` or `ap-south`. Account-level entries, such as `invoice.paid` or `ownership.transferred`, are stored in the account's home region, which is the region of its first workspace. Entries are encrypted at rest and are not copied to other regions.

Last reviewed: 2026-11-26
