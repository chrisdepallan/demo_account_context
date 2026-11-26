# Recorded Audit Events

## What is the audit log?

The audit log is a permanent, read-only record of security-relevant actions in an account. It answers "who did what, when and from where". It is available on **Pro, Business and Enterprise**. Free and Starter accounts have no audit log, and nothing is recorded for them.

Owners and Admins open it under **Settings → Security → Audit log**.

## Which actions are recorded?

Events are grouped into **8 categories**:

| Category | Example event types |
|----------|---------------------|
| Authentication | `login.succeeded`, `login.failed`, `password.changed`, `mfa.enabled`, `mfa.disabled`, `session.revoked` |
| Members | `member.invited`, `member.removed`, `member.role_changed`, `guest.added`, `ownership.transferred` |
| Security | `sso.configured`, `scim.enabled`, `security_policy.updated`, `api_key.created`, `api_key.rotated`, `api_key.revoked` |
| Data | `workspace.created`, `project.deleted`, `project.restored`, `task.deleted`, `file.deleted`, `file.shared`, `file.downloaded` |
| Billing | `plan.changed`, `subscription.cancelled`, `invoice.paid`, `payment_method.updated`, `refund.issued` |
| Integrations | `webhook_endpoint.created`, `webhook_endpoint.deleted`, `integration.connected`, `integration.disconnected` |
| Account | `account.closed`, `account.restored` |
| Audit | `audit_log.exported`, `audit_log.stream_created`, `support.accessed` |

Event type names always use the `resource.action` form.

## Which actions are not recorded?

Everyday content work is not in the audit log: creating or editing tasks, writing comments, uploading files, and viewing projects or files. Those changes are visible in each item's own activity history instead.

File downloads (`file.downloaded`) are recorded on **Enterprise only**. On Pro and Business, downloads are not in the audit log.

## What does an audit entry contain?

| Field | Example | Notes |
|-------|---------|-------|
| `id` | `aud_7H2KQ9M4XP` | `aud_` plus 10 characters |
| `occurred_at` | `2026-11-26T09:30:12Z` | Always UTC |
| `event_type` | `member.role_changed` | `resource.action` |
| `category` | `members` | Derived from the event type |
| `actor` | `user` / `admin@customer.example` | Type and identifier of who acted |
| `account_id` | `acc_7F3K9Q2M` | Always present |
| `workspace_id` | `ws_4H8P2L` | Empty for account-level events such as `invoice.paid` |
| `target_id` | `prj_4K7M2Q9X` | The resource acted on, if any |
| `ip_address` | `203.0.113.10` | Empty for `system` actors |
| `region` | `us-east` | Where the entry is stored |
| `metadata` | `{"old_role": "Member", "new_role": "Admin"}` | Up to **20 keys** and **4,096 bytes** |

## Who can be the actor of an entry?

- `user` – a signed-in person, identified by email address.
- `api_key` – an API key, identified by the key's name. The key itself is never stored.
- `system` – an automatic action by Acme Cloud, such as a key revoked after being found in a public repository.
- `support` – an Acme Cloud support agent acting on the account. The entry always carries the support ticket ID, for example `SUP-48213`.

## Are passwords or API keys ever written to the audit log?

No. Entries record that a password or key was changed, never the value. Metadata fields whose names contain `password`, `secret`, `token`, `api_key` or `private_key` are rejected before an entry is written. API keys appear only by name.

## How quickly do actions appear in the audit log?

Normally within **10 seconds**: the target is **99%** of entries written within 10 seconds of the action. Entries are written in the order they happened and each gets the next sequence number in the account's chain for its region.

## Are failed attempts recorded?

Yes, for sign-ins. Every failed sign-in is recorded as `login.failed` with the email address tried and the IP address. Actions that were blocked because the person lacked permission are not recorded.

## Can I find out what happened with a leaked API key?

Yes. Filter the audit log by actor type `api_key` and the key's name to see every recorded action made with that key, then check `api_key.revoked` to confirm when it stopped working. Revoking a key is described in `services/auth/docs/api-keys.md`.

Last reviewed: 2026-11-26
