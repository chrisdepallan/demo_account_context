# Webhooks Service

## What it does

The Webhooks service sends events to HTTPS endpoints that customers register. When something happens in a workspace (a task is completed, a file is uploaded, an invoice is paid), it builds an event, signs it with the endpoint's secret, delivers it with `POST`, retries failures and keeps a delivery log. It receives events from the other services and does not create them itself.

## Key concepts

- **Endpoint** – a customer HTTPS URL that receives events; IDs look like `whk_6R2T9B4M`. States are `active`, `paused` and `disabled`.
- **Event** – one thing that happened; IDs look like `evt_3N7Q1Z8K4B`. Types use the `resource.action` form, for example `task.completed`. There are **22** event types.
- **Subscription** – the event types an endpoint wants: exact names, a wildcard such as `task.*`, or `*` for everything.
- **Delivery** – one event sent to one endpoint, with up to **8** attempts; IDs look like `dlv_5P8W2K7D3F`.
- **Signing secret** – starts with `whsec_`, shown only once, used to compute the `Acme-Signature` header (HMAC-SHA256).
- **Retry schedule** – 7 retries over about **45 hours**: 1 minute, 5 minutes, 30 minutes, 2 hours, 6 hours, 12 hours, 24 hours.
- **Auto-disable** – an endpoint is disabled after **50** consecutive failed attempts, or at once on `410 Gone`.
- **Delivery log** – every attempt with status code and response time; kept **7 days** on Starter, **30 days** on Pro and Business, **90 days** on Enterprise.

## How to use it

- Customer-facing settings: **Settings → Webhooks** (Owner and Admin only, Starter plan and above).
- Internal API base URL: `https://api.acme-cloud.example/v2/webhooks`
- Common endpoints:
  - `GET /v2/webhooks/event-types` – list the event catalog
  - `GET /v2/webhooks/{workspace_id}/endpoints` – list endpoints
  - `POST /v2/webhooks/{workspace_id}/endpoints` – register an endpoint; the response shows the signing secret once
  - `GET /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}` – endpoint details and health
  - `PATCH /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}` – change URL, subscription or state
  - `DELETE /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}` – delete an endpoint
  - `POST /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}/rotate-secret` – issue a new signing secret
  - `POST /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}/test` – send a `webhook.test` event
  - `GET /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}/deliveries` – delivery log
  - `POST /v2/webhooks/{workspace_id}/deliveries/{delivery_id}/redeliver` – send a logged event again

## Docs in this service

- `docs/event-catalog.md` – the 22 event types, the payload envelope, ordering and duplicates
- `docs/signing-and-verification.md` – the `Acme-Signature` header, how to verify it, secret rotation
- `docs/retries-and-failures.md` – what counts as a failure, the retry schedule, auto-disable, redelivery
- `docs/managing-endpoints.md` – who can register endpoints, limits per plan, URL rules, pausing and testing

## Code in this service

- `acme_webhooks/events.py` – event type catalog, subscription matching and the payload envelope
- `acme_webhooks/signing.py` – HMAC-SHA256 signature creation and constant-time verification with timestamp tolerance
- `acme_webhooks/retry.py` – retry schedule, response classification and endpoint auto-disable
- `openapi.yaml` – OpenAPI 3.0 spec for the endpoints listed above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings
- `tests/` – `unittest` tests; run `python -m unittest discover -s tests` from this folder

## Owners

Team: Developer Platform. Slack channel: `#team-developer-platform` (fictional).
