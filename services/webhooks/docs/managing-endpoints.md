# Managing Endpoints

## Which plans include webhooks?

Webhooks are available on **Starter and above**. Free accounts cannot use webhooks, the same as the API (see `services/auth/docs/api-keys.md`). Accounts in the 14-day trial are on Pro and get the Pro limits.

## Who can manage webhook endpoints?

Only **Owners and Admins**. Members, Billing admins and Guests cannot see the **Settings → Webhooks** page or the signing secrets.

## How many endpoints can a workspace have?

| Plan | Endpoints per workspace |
|------|-------------------------|
| Free | Not available |
| Starter | **3** |
| Pro | **10** |
| Business | **25** |
| Enterprise | **100** |

Paused and disabled endpoints count towards the limit. Delete an endpoint to free a slot.

## How do I add a webhook endpoint?

1. Go to **Settings → Webhooks → Add endpoint**.
2. Enter the endpoint URL and an optional description (up to **200 characters**).
3. Choose the event types, a wildcard such as `task.*`, or all events. See `services/webhooks/docs/event-catalog.md`.
4. Select **Create**. The signing secret is shown **only once**; copy it into a secrets manager.
5. Select **Send test event** to check that your endpoint answers with `2xx`.

The same can be done with `POST /v2/webhooks/{workspace_id}/endpoints`. A new endpoint is `active` at once and gets an ID such as `whk_6R2T9B4M`.

## What are the rules for an endpoint URL?

- It must start with `https://`. Plain `http://` is rejected.
- It must use port **443**, the default HTTPS port.
- The host must be a public DNS name. IP addresses, `localhost` and private or internal network addresses are rejected.
- The URL can be up to **2,048 characters** long and may contain a query string.
- The certificate must be valid and issued by a public certificate authority.
- The same URL can be registered only once per workspace.

## How do I test an endpoint?

Select **Send test event** next to the endpoint, or call `POST /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}/test`. Acme Cloud sends a `webhook.test` event, signed like a real one, and shows the status code and response time. A test event is attempted **once** and is not retried. Test events can be sent up to **10 times per minute** per endpoint.

## What is the difference between paused and disabled?

| State | Set by | Events during this state | How to leave it |
|-------|--------|--------------------------|-----------------|
| `active` | Default | Delivered | – |
| `paused` | An Owner or Admin, by hand | Logged as `skipped`, not delivered | Select **Resume** |
| `disabled` | Acme Cloud, after repeated failures or a `410` response | Logged as `skipped`, not delivered | Select **Enable** |

Events that were skipped are not sent automatically when the endpoint becomes active again. They can be redelivered by hand while they are still in the delivery log. The failure rules are in `services/webhooks/docs/retries-and-failures.md`.

## How do I change an endpoint?

Open the endpoint under **Settings → Webhooks** and edit the URL, description or event types. Changes apply to events that happen after the change, within **60 seconds**. Changing the URL does not change the signing secret. Deliveries that are already retrying keep going to the old URL.

## How do I delete an endpoint?

Select **Delete** and confirm. Deliveries that are still retrying are cancelled, and the delivery log for the endpoint is removed. Deletion cannot be undone; a new endpoint with the same URL gets a new ID and a new signing secret.

## Can I manage endpoints with the API?

Yes, with an API key created by an Owner or Admin. Requests to the webhook management endpoints count towards the account's API rate limit (**300/min** on Starter, **1,000/min** on Pro, **3,000/min** on Business, **10,000/min** on Enterprise). Outgoing webhook deliveries do not count towards that limit.

## What happens to endpoints when the plan changes?

- **Upgrade** – the higher endpoint limit and longer delivery log apply immediately.
- **Downgrade** – blocked while a workspace has more endpoints than the lower plan allows. Delete endpoints first. This follows the downgrade rule in `services/accounts/docs/plans-and-limits.md`.
- **Move to Free** – all endpoints are disabled, because Free does not include webhooks. They are kept for **30 days** and can be enabled again after upgrading; after that they are deleted.

## Who is told when an endpoint changes?

Creating, changing, rotating the secret of, or deleting an endpoint is recorded in the audit log on Pro and above. The Owner and Admins are notified when an endpoint is close to being disabled and when it is disabled.

Last reviewed: 2026-11-26
