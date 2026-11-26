# ADR 0007: HMAC-Signed Webhooks

## Status

Accepted on **2024-12-03**.

## Context

The webhooks service sends Acme Cloud events, such as `task.completed` and `file.uploaded`, to URLs that customers register as webhook endpoints. A webhook endpoint is a public URL, so anyone who learns the URL can send fake events to the customer's system. Customers need a way to check that a request really came from Acme Cloud, that the body was not changed on the way, and that an old request is not being replayed.

The check must work in any programming language with no Acme Cloud library, because customers receive webhooks in many different stacks.

## Decision

Every webhook request sent by the webhooks service is signed with HMAC-SHA256 using a secret that belongs to the webhook endpoint.

- Each webhook endpoint (`whk_` plus **8** uppercase alphanumerics) has its own signing secret. The secret is shown to the customer once, when the endpoint is created or the secret is rotated.
- The signature is computed over the timestamp, a full stop and the raw request body, using HMAC-SHA256.
- The request carries the header `Acme-Signature` with the signature and the header `Acme-Timestamp` with the Unix time in seconds.
- Customers should reject a request whose timestamp is more than **5 minutes** old.
- The body contains the event's `evt_` ID. Because delivery is at least once, customers should ignore an event ID they have already processed.
- Webhook endpoints must use HTTPS.
- After a secret rotation, the old secret stays valid for **24 hours**, the same overlap used for API key rotation in `services/auth/docs/api-keys.md`.
- Failed deliveries are retried with increasing delays for up to **24 hours**. Each retry is signed again with a fresh timestamp.

## Consequences

- A customer can verify a webhook with a few lines of standard-library code in any language.
- A leaked endpoint URL alone is not enough to forge events.
- The timestamp check limits replay to a **5-minute** window, and the event ID closes the rest of the gap.
- The signing secret is shared between Acme Cloud and the customer. The webhooks service must store the secret encrypted, and a customer who leaks the secret must rotate it.
- Customers must verify against the raw body. Parsing and re-serialising the JSON before the check breaks the signature, which is a common support question.
- Signing secrets are per endpoint, so one leaked secret does not affect other endpoints.

## Alternatives considered

- **No signature, only a secret token in the URL** – simple, but the token appears in logs and proxies.
- **Asymmetric signatures with a published public key** – no shared secret, but harder for customers to implement and slower to compute at high volume.
- **Mutual TLS** – strong, but most customers cannot configure client certificates on their webhook receivers.
- **A fixed list of source IP addresses only** – useful as an extra, but does not protect the body and changes when the platform scales.

Service details are in `services/webhooks/README.md`.

Last reviewed: 2026-11-26
