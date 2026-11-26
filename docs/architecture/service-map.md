# Acme Cloud Service Map

## How to read the Acme Cloud service map

The Acme Cloud service map shows which of the **12 services** depend on which. A dependency is one of two kinds.

- **Calls** – a synchronous internal API call that must answer before the caller can reply. Internal calls time out after **2 seconds**.
- **Consumes** – the service reads events from the Acme Event Bus (`acme-bus`) after the fact. A slow or stopped consumer never blocks the producer.

The platform overview is in `docs/architecture/system-overview.md`.

## Service dependency table

| Service | Calls (synchronous) | Consumes events from |
|------|------|------|
| accounts | none | billing |
| auth | accounts | accounts |
| billing | accounts | accounts |
| support | accounts, billing | accounts, billing |
| projects | accounts, files | accounts, files |
| files | accounts | accounts, projects |
| notifications | accounts | accounts, auth, billing, support, projects, files, webhooks, integrations, analytics, audit-log |
| webhooks | none | accounts, billing, projects, files, integrations |
| search | none | accounts, projects, files |
| audit-log | none | accounts, auth, billing, projects, files, webhooks, integrations |
| integrations | auth, projects, files | accounts, projects, files |
| analytics | none | accounts, projects, files |

The Acme Edge Gateway calls the auth service to validate every session token and API key, and caches the answer for **60 seconds**.

## Why most services call the accounts service

The accounts service is the source of truth for the plan, the account state and the limits of an account. A service that enforces a limit, for example the files service checking the storage quota, reads the entitlements from the accounts service and caches them for **60 seconds**. The cache is also refreshed as soon as an `account.plan_changed` or `account.state_changed` event arrives.

## Events published by the accounts service

Topic: `accounts.events`.

- `account.created` – a new account finished sign-up
- `account.plan_changed` – the plan was upgraded or downgraded
- `account.state_changed` – the account moved between `trialing`, `active`, `past_due` and `read_only`
- `account.closed` – the account was closed and the **30-day** retention window started
- `account.restored` – a closed account was restored
- `account.deleted` – the retention window ended and every service must erase the account's data
- `workspace.created`, `workspace.deleted`
- `member.invited`, `member.joined`, `member.removed`, `member.role_changed`

## Events published by the auth service

Topic: `auth.events`.

- `session.created`, `session.revoked`
- `login.failed`
- `mfa.enabled`, `mfa.disabled`
- `sso.configured`
- `api_key.created`, `api_key.rotated`, `api_key.revoked`

## Events published by the billing service

Topic: `billing.events`.

- `subscription.created`, `subscription.updated`, `subscription.cancelled`
- `invoice.issued`, `invoice.paid`, `invoice.payment_failed`
- `refund.issued`
- `credit.applied`

The accounts service consumes `invoice.payment_failed` and `invoice.paid` to move an account into and out of `past_due` and `read_only`.

## Events published by the projects service and the files service

Topic `projects.events`:

- `project.created`, `project.archived`, `project.deleted`
- `task.created`, `task.updated`, `task.assigned`, `task.completed`, `task.deleted`
- `comment.created`

Topic `files.events`:

- `file.uploaded`, `file.version_created`, `file.deleted`, `file.restored`
- `file.shared` – a sharing link was created
- `quota.warning` – storage reached **90%** of the limit
- `quota.exceeded` – storage reached **100%** of the limit

## Events published by the other Acme Cloud services

| Service | Topic | Events |
|------|------|------|
| support | `support.events` | `ticket.created`, `ticket.escalated`, `ticket.resolved` |
| notifications | `notifications.events` | `notification.sent`, `notification.bounced` |
| webhooks | `webhooks.events` | `webhook.delivery_failed`, `webhook.endpoint_disabled` |
| integrations | `integrations.events` | `integration.installed`, `integration.uninstalled` |
| analytics | `analytics.events` | `export.completed` |
| audit-log | `audit-log.events` | `audit_export.completed` |
| search | none | The search service only consumes events |

## Event envelope on the Acme Event Bus

Every event on the Acme Event Bus uses the same envelope.

| Field | Meaning |
|------|------|
| `id` | Event ID, `evt_` plus **10** uppercase alphanumerics, for example `evt_4K9D2M7X1B` |
| `type` | The `resource.action` name, for example `task.completed` |
| `occurred_at` | ISO 8601 timestamp in UTC |
| `account_id` | The account the event belongs to, for example `acc_7F3K9Q2M` |
| `workspace_id` | The workspace, or null for account-level events |
| `region` | `us-east`, `eu-central` or `ap-south` |
| `actor` | Who caused the event: a member, an API key, an integration or the system |
| `schema_version` | Integer, starts at **1** |
| `data` | Event-specific fields; IDs and changed values only, never file content |

## Delivery rules on the Acme Event Bus

- Each producing service has **one topic**, named `<service>.events`.
- Events are keyed by account ID, so events for one account arrive in order.
- Delivery is **at least once**. Consumers must ignore an `evt_` ID they have already processed.
- Events are kept on the bus for **7 days**.
- A producer writes the event to an outbox table in the same database transaction as the data change. A relay publishes the event, normally within **5 seconds**.
- A consumer that fails on the same event **5 times** moves the event to a dead-letter topic named `<consumer>.dlq` and alerts the owning team.
- The decision record is `docs/adr/0002-event-bus-for-cross-service-communication.md`.

## What happens across services when an account is closed

1. The accounts service sets the account to `closed` and publishes `account.closed`.
2. The auth service consumes `account.closed` and revokes every session and API key of the account.
3. The billing service consumes `account.closed` and cancels the subscription.
4. The projects, files, search, webhooks, integrations and analytics services mark the account's data as soft-deleted and stop serving the data.
5. After **30 days** the accounts service publishes `account.deleted` and every service erases the account's data from primary storage. Backups are purged within a further **35 days**.

The customer-facing rules are in `services/accounts/docs/account-lifecycle.md`.

Last reviewed: 2026-11-26
