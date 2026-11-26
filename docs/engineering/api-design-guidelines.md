# API Design Guidelines

## What do the API design guidelines cover?

The API design guidelines apply to every HTTP API of the 12 Acme Cloud services. Each service describes its API in its own OpenAPI description, and each service's endpoints are summarised in its README, for example `services/projects/README.md`. All APIs are reached through the API gateway at `https://api.acme-cloud.example`.

## How are API URLs built?

- The base URL of a service is `https://api.acme-cloud.example/v2/<service>`, for example `https://api.acme-cloud.example/v2/billing`.
- Resource names are plural nouns in lowercase, with hyphens between words: `/v2/accounts/{account_id}/members`.
- Path parameters are `snake_case` in braces: `{account_id}`, `{workspace_id}`.
- An action that is not a plain create, read, update or delete is a `POST` to a verb under the resource: `POST /v2/accounts/{account_id}/close`.
- URLs never contain personal data such as email addresses, and never contain secrets.

## Which HTTP methods and status codes are used?

| Method | Use | Success status |
|--------|-----|----------------|
| `GET` | Read one resource or a list | **200** |
| `POST` | Create a resource or run an action | **201** for a created resource, **200** for an action, **202** for work that continues in the background |
| `PATCH` | Change some fields of a resource | **200** |
| `PUT` | Replace a resource completely | **200** |
| `DELETE` | Remove a resource | **204** |

Error statuses are **400** for invalid input, **401** for missing or invalid credentials, **403** for missing permission, **404** for an unknown resource, **409** for a conflict with the current state, **422** for input that is well-formed but breaks a business rule, **429** for rate limiting and **500** or **503** for server faults.

## What does a JSON request and response look like?

- Request and response bodies are JSON encoded as UTF-8, with the content type `application/json`.
- Field names are `snake_case`.
- Timestamps are ISO 8601 strings in UTC, for example `2026-11-26T14:30:00Z`. Timestamp field names end in `_at`.
- Money is an integer `amount` in minor units together with a three-letter `currency` code.
- Enumerated values are lowercase `snake_case` strings, for example the account state `past_due`.
- A field that has no value is returned as `null`. Fields are not left out.

## How are identifiers formatted?

Every resource has a string identifier with a fixed prefix. Clients treat identifiers as opaque strings.

| Resource | Format | Example |
|----------|--------|---------|
| Account | `acc_` + 8 characters | `acc_7F3K9Q2M` |
| Workspace | `ws_` + 6 characters | `ws_4H8P2L` |
| Project | `prj_` + 8 characters | `prj_9D4G6W2Z` |
| Task | `tsk_` + 8 characters | `tsk_1B7R5E8U` |
| File | `fil_` + 8 characters | `fil_3N6V8C1X` |
| Webhook endpoint | `whk_` + 8 characters | `whk_5T7Y2B9D` |
| Event | `evt_` + 10 characters | `evt_8K2M4P6R1S` |
| Audit entry | `aud_` + 10 characters | `aud_2H5J7L9N3Q` |

## How do errors look?

Every error response has the same JSON shape:

```text
{
  "error": {
    "code": "storage_limit_reached",
    "message": "The account has reached its storage limit.",
    "request_id": "req_4C8F1A6E9B2D"
  }
}
```

The `code` is a stable `snake_case` string that clients can test. The `message` is a plain English sentence for people and can change. The `request_id` is also returned in the `X-Request-Id` response header and is the value that support asks for. Error messages never reveal whether an email address has an account, and never contain stack traces.

## How does pagination work?

List endpoints use cursor pagination. The query parameter `limit` sets the page size, with a default of **50** and a maximum of **200**. The response contains the list in `data` and a `next_cursor` field. The client passes the value as the `cursor` query parameter to get the next page. A `next_cursor` of `null` means that there are no more results. Page numbers and offsets are not used.

## How do filtering and sorting work?

Filters are query parameters named after the field, for example `?status=open`. Time ranges use the suffixes `_after` and `_before`, for example `?created_after=2026-11-01T00:00:00Z`. Sorting uses `sort` with a field name, and a leading minus sign for descending order, for example `?sort=-created_at`. Each list endpoint documents the fields that can be filtered and sorted.

## How are API requests authenticated and authorised?

Programs send an API key in the `Authorization` header as a bearer token. Production keys start with `acme_live_` and sandbox keys start with `acme_test_`. API keys, their scopes and their expiry are described in `services/auth/docs/api-keys.md`. Every endpoint documents the scope it needs, for example `projects:read`. Every endpoint checks the caller's role (Owner, Admin, Billing admin, Member or Guest) on the server. A resource that the caller may not see returns **404**, not **403**, so that identifiers cannot be probed.

## How does rate limiting work?

Rate limits are counted per account, not per API key: **300** requests per minute on Starter, **1,000** on Pro, **3,000** on Business and **10,000** on Enterprise. Free accounts cannot use the API. A request over the limit gets HTTP **429** with a `Retry-After` header in seconds. Plan limits are listed in `services/accounts/docs/plans-and-limits.md`.

## How do idempotency keys work?

Every `POST` endpoint that creates a resource or moves money accepts an `Idempotency-Key` request header with a client-chosen unique string of up to **64** characters. A repeated request with the same key within **24 hours** returns the first response and does not run the action again. A repeated key with a different request body returns **409**.

## How are API versions and breaking changes handled?

The current public API version is `v2`, shown in the URL. Adding an endpoint, an optional request field or a response field is not a breaking change. Removing or renaming a field, changing a type, adding a required field or changing an error code is a breaking change and needs a new major version. A deprecated version or endpoint keeps working for at least **12 months** after the announcement and returns the `Deprecation` and `Sunset` response headers during that time.

Last reviewed: 2026-11-26
