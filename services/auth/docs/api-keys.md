# API Keys

## Who can create API keys?

Owners and Admins on Starter and above. Free accounts cannot use the API.

## How do I create an API key?

Go to **Settings → API keys → Create key**, give it a name, choose its scopes and an expiry. The full key is shown **only once**; store it in a secrets manager straight away. Keys start with `acme_live_` for production and `acme_test_` for the sandbox.

## What scopes are available?

- `projects:read`, `projects:write`
- `files:read`, `files:write`
- `members:read`, `members:write`
- `billing:read` (Owner and Billing admin only)

Give each key only the scopes it needs.

## How long do API keys last?

Expiry can be 30, 90, 180 or 365 days, or never. Keys set to "never" are not allowed when the workspace Admin turns on **Require key expiry**. Owners are emailed **14 days** before a key expires.

## How many keys can a workspace have?

Up to **25 active keys** per workspace.

## How do I rotate a key?

Select **Rotate** next to the key. A new key is issued and the old one keeps working for **24 hours** so integrations can be updated without downtime.

## What should I do if a key is leaked?

Select **Revoke** immediately; revocation takes effect within **60 seconds**. Then check the audit log (Pro and above) for requests made with the key. Acme Cloud also scans public GitHub repositories and revokes exposed `acme_live_` keys automatically, emailing the Owner.

## How are API requests rate limited?

Limits are per account: 300/min on Starter, 1,000/min on Pro, 3,000/min on Business and 10,000/min on Enterprise. Over the limit, the API returns `429` with a `Retry-After` header.

Last reviewed: 2026-11-19
