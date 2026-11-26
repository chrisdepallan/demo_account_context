# Event Catalog

## Which events can a webhook receive?

Acme Cloud has **22** event types. Names use the `resource.action` form.

| Event type | Sent when |
|------------|-----------|
| `project.created` | A project is created |
| `project.updated` | A project's name, description or settings change |
| `project.archived` | A project is archived |
| `project.deleted` | A project is deleted |
| `task.created` | A task is created |
| `task.updated` | A task's title, description, due date or status changes |
| `task.assigned` | A task is assigned or reassigned |
| `task.completed` | A task is marked as complete |
| `task.deleted` | A task is deleted |
| `file.uploaded` | A file or a new file version is uploaded |
| `file.shared` | A file or folder is shared |
| `file.deleted` | A file is deleted |
| `member.invited` | A person is invited to the workspace |
| `member.joined` | An invited person accepts and joins |
| `member.removed` | A member is removed from the workspace |
| `member.role_changed` | A member's role changes |
| `invoice.created` | An invoice is issued |
| `invoice.paid` | An invoice is paid |
| `invoice.payment_failed` | A payment attempt for an invoice fails |
| `account.plan_changed` | The account is upgraded or downgraded |
| `account.closed` | The account is closed |
| `webhook.test` | Someone selects **Send test event** for the endpoint |

The same list is available from `GET /v2/webhooks/event-types`.

## How do I choose which events an endpoint gets?

Each endpoint has a subscription with **1–50** entries. An entry can be:

- an exact event type, for example `task.completed`
- a resource wildcard, for example `task.*` for all five task events
- `*` for every event type, including types added later

The `webhook.test` event is always delivered to the endpoint it was requested for, whatever the subscription says.

## What does an event payload look like?

Every delivery is an HTTPS `POST` with a JSON body. All event types share the same envelope:

```json
{
  "id": "evt_3N7Q1Z8K4B",
  "type": "task.completed",
  "api_version": "v2",
  "created_at": "2026-11-26T14:03:00Z",
  "account_id": "acc_7F3K9Q2M",
  "workspace_id": "ws_4H8P2L",
  "data": {
    "id": "tsk_9D3F7H2K",
    "project_id": "prj_5T8N2W6R",
    "title": "Prepare launch checklist",
    "completed_at": "2026-11-26T14:03:00Z"
  }
}
```

- `id` – the event ID, `evt_` plus 10 characters. It is the same on every retry and redelivery.
- `type` – the event type from the table above.
- `api_version` – always `v2`.
- `created_at` – when the event happened, in UTC.
- `account_id` and `workspace_id` – where it happened.
- `data` – the resource the event is about, as it was at the time of the event.

## Which events are account-level?

The `invoice.*` and `account.*` events belong to the account, not to one workspace. For these, `workspace_id` is `null`, and the event is sent to every endpoint in every workspace of the account that subscribes to it. All other events are sent only to endpoints in the workspace where they happened.

## How large can a payload be?

At most **256 KB**. Larger resources are cut down to their ID and core fields, and the receiver can fetch the full resource from the API. File contents are never included in a payload; `file.uploaded` carries the file ID (for example `fil_2B6M8Q4J`), name and size only.

## Are events delivered in order?

Not always. Events are normally delivered within **5 seconds**, but retries and parallel delivery (up to **10** deliveries at once per endpoint) can change the order. Use `created_at` to order events, and do not assume `task.created` arrives before `task.completed`.

## Can I receive the same event twice?

Yes. Delivery is **at least once**. A retry after a timeout, or a manual redelivery, sends the same event again. Store the event `id` and skip IDs you have already handled.

## Which headers come with each delivery?

| Header | Example | Meaning |
|--------|---------|---------|
| `Acme-Signature` | `t=1795701782,v1=997b96d8…` | Timestamp and HMAC-SHA256 signature |
| `Acme-Event-Id` | `evt_3N7Q1Z8K4B` | Same as `id` in the body |
| `Acme-Event-Type` | `task.completed` | Same as `type` in the body |
| `Acme-Delivery-Id` | `dlv_5P8W2K7D3F` | ID of this delivery in the delivery log |
| `Acme-Delivery-Attempt` | `1` | Attempt number, **1–8** |
| `Content-Type` | `application/json` | Always JSON, UTF-8 |
| `User-Agent` | `AcmeCloud-Webhooks/2.0` | Identifies the sender |

How to check the signature is described in `services/webhooks/docs/signing-and-verification.md`.

## Will new event types or fields be added?

Yes. New event types and new fields inside `data` can be added at any time without a version change. Receivers should ignore fields and event types they do not know. Existing fields are not removed or renamed within `v2`.

Last reviewed: 2026-11-26
