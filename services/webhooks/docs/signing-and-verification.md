# Signing and Verification

## Why should I verify webhook signatures?

Your endpoint URL is public, so anyone who learns it can send requests to it. Every delivery from Acme Cloud is signed with a secret that only you and Acme Cloud know. Checking the signature proves the request came from Acme Cloud and that the body was not changed on the way.

## Where do I find the signing secret?

Each endpoint has its own signing secret. It starts with `whsec_` followed by **32 characters** and is shown **only once**, when the endpoint is created or the secret is rotated, under **Settings → Webhooks**. Store it in a secrets manager straight away. If it is lost, rotate the secret to get a new one. Signing secrets are separate from API keys, which start with `acme_live_` or `acme_test_`.

## What does the signature header look like?

Each delivery has an `Acme-Signature` header with a timestamp and a signature:

```text
Acme-Signature: t=1795701782,v1=997b96d8972e0596e0c3b8d2e246d9baaaf64471d49e9a8ce4e7252b7300a7d9
```

- `t` – the time the delivery attempt was signed, as Unix seconds.
- `v1` – the signature: **HMAC-SHA256**, written as 64 lowercase hex characters.

The header can contain more than one `v1` value during a secret rotation. Ignore keys you do not know.

## How is the signature calculated?

1. Take the timestamp from `t`.
2. Join the timestamp, a full stop and the **raw request body**: `1795701782.{"id":"evt_3N7Q1Z8K4B",...}`.
3. Compute HMAC-SHA256 over that string with the signing secret as the key.
4. Write the result as lowercase hex.

Each retry is signed again with a new timestamp, so the signature differs between attempts of the same event.

## How do I verify a delivery?

1. Read the raw body bytes before any JSON parsing.
2. Split the header at commas and read `t` and every `v1`.
3. Reject the request if `t` is more than **5 minutes** (300 seconds) away from your server's current time.
4. Calculate the expected signature as described above.
5. Compare it with each `v1` value using a constant-time comparison. Accept if any one matches.
6. If the check fails, answer with `400` and do not process the event.

A reference implementation is in `services/webhooks/acme_webhooks/signing.py` (`verify_signature`). It can be tested with an obviously fake secret such as `whsec_EXAMPLE_NOT_A_REAL_SECRET`.

## Why is there a 5-minute tolerance?

The timestamp stops replay attacks: a captured request cannot be sent again later, because its timestamp is too old. The tolerance of **5 minutes** allows for network delay and small clock differences. Keep your server clock synchronised. A larger tolerance is less safe and is not recommended.

## Why does verification fail?

The most common causes are:

- The body was parsed and re-serialised before verifying. Use the raw bytes exactly as received.
- The wrong secret is used, for example the secret of another endpoint or an API key.
- The server clock is off by more than 5 minutes.
- A proxy or framework changed the body encoding or stripped the header.
- The secret was rotated more than 24 hours ago and the old one is still configured.

## How do I rotate a signing secret?

Owners and Admins select **Rotate secret** next to the endpoint under **Settings → Webhooks**, or call `POST /v2/webhooks/{workspace_id}/endpoints/{endpoint_id}/rotate-secret`. The new secret is shown once. For the next **24 hours** every delivery carries two `v1` signatures, one made with the new secret and one with the old, so either secret verifies. After 24 hours only the new secret is used. This matches the 24-hour overlap for API keys in `services/auth/docs/api-keys.md`.

## What should I do if a signing secret is leaked?

Rotate the secret immediately and choose **Expire old secret now**. The old secret stops being used within **60 seconds**, without the 24-hour overlap. Update your endpoint with the new secret first if you can, because deliveries signed only with the new secret will fail verification until you do. Failed deliveries are retried as described in `services/webhooks/docs/retries-and-failures.md`.

## Does Acme Cloud send webhooks from fixed IP addresses?

No. Source addresses can change without notice, so do not use an IP allowlist as your only check. Verify the signature instead. Deliveries are always sent from the region of the workspace (`us-east`, `eu-central` or `ap-south`).

## Is the connection encrypted?

Yes. Endpoints must use HTTPS with a valid certificate from a public certificate authority, and **TLS 1.2** or newer. Self-signed and expired certificates cause the delivery to fail.

Last reviewed: 2026-11-26
