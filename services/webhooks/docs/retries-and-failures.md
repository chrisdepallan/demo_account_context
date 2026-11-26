# Retries and Failures

## What counts as a successful delivery?

A delivery succeeds when your endpoint answers with any `2xx` status code within **10 seconds**. The response body is ignored. Answer quickly and do slow work afterwards in a background job.

## What counts as a failed delivery?

Anything else is a failed attempt:

- no response within **10 seconds** (timeout)
- a connection or TLS error, including an invalid certificate
- a `3xx` redirect (redirects are not followed)
- any `4xx` or `5xx` status code

## How often does Acme Cloud retry a failed delivery?

Each delivery gets at most **8 attempts**: the first one and **7 retries**.

| Attempt | Wait after the previous attempt |
|---------|---------------------------------|
| 1 | Sent at once |
| 2 | **1 minute** |
| 3 | **5 minutes** |
| 4 | **30 minutes** |
| 5 | **2 hours** |
| 6 | **6 hours** |
| 7 | **12 hours** |
| 8 | **24 hours** |

The last attempt is made about **45 hours** (44 hours 36 minutes) after the first. Up to **10%** random extra delay is added to each wait so that retries do not arrive all at once. After the 8th failed attempt the delivery is marked `failed` and is not retried again automatically.

## Can my endpoint ask Acme Cloud to slow down?

Yes. Answer with `429` or `503` and a `Retry-After` header in seconds. If the value is longer than the scheduled wait, Acme Cloud waits that long instead, up to a maximum of **1 hour**. The attempt still counts as failed.

## What do the delivery statuses mean?

| Status | Meaning |
|--------|---------|
| `pending` | Waiting for the first attempt |
| `succeeded` | An attempt got a `2xx` response |
| `retrying` | At least one attempt failed and another is scheduled |
| `failed` | All 8 attempts failed, or the endpoint was disabled |
| `skipped` | The endpoint was paused or disabled when the event happened |

## When is an endpoint disabled automatically?

An endpoint is disabled in two cases:

- **50 consecutive failed attempts**, counted across all deliveries to that endpoint. Any successful attempt sets the count back to zero.
- A `410 Gone` response. This disables the endpoint **immediately**, because it means the URL no longer exists.

When an endpoint is disabled, deliveries that were still retrying are marked `failed`, and new events are logged as `skipped`.

## Will I be warned before an endpoint is disabled?

Yes. At **25 consecutive failed attempts** the Owner and Admins get an email and an in-app notification. A second message is sent when the endpoint is disabled. Both are `account_notice` notifications, which cannot be turned off; see `services/notifications/docs/notification-types.md`.

## How do I turn a disabled endpoint back on?

Fix the receiver, then go to **Settings → Webhooks**, open the endpoint and select **Enable**. It is a good idea to select **Send test event** first. Enabling sets the failure count back to zero. Events that were `skipped` or `failed` in the meantime are not sent again automatically; redeliver them by hand.

## How do I redeliver an event?

Open the endpoint under **Settings → Webhooks → Deliveries**, choose a delivery and select **Redeliver**, or call `POST /v2/webhooks/{workspace_id}/deliveries/{delivery_id}/redeliver`. A redelivery is a new delivery with its own ID and the full schedule of 8 attempts. The event `id` stays the same, so receivers that track event IDs will see it as a duplicate. Up to **100** deliveries can be selected and redelivered at once in the UI.

## How long is the delivery log kept?

| Plan | Delivery log retention |
|------|------------------------|
| Starter | **7 days** |
| Pro | **30 days** |
| Business | **30 days** |
| Enterprise | **90 days** |

The log shows every attempt with its time, status code, response time and the first **1,024 bytes** of the response body. An event can be redelivered only while it is still in the log.

## What happens to webhooks when an account is read-only or closed?

- In the `read_only` state, events are still delivered, but endpoints cannot be created or changed.
- When an account is closed, the `account.closed` event is delivered and then all endpoints are disabled. If the account is restored within **30 days**, the endpoints come back disabled and must be enabled by hand.

Account states are described in `services/accounts/docs/account-lifecycle.md`.

Last reviewed: 2026-11-26
