# ADR 0008: Idempotency Keys on Billing Writes

## Status

Accepted on **2025-03-11**.

## Context

The billing service creates charges, refunds and credits. Callers of the billing service, such as the support admin console and the accounts service, retry a request when the network times out. A retried write that had in fact succeeded the first time caused a duplicate charge or a duplicate refund. Duplicate charges must be refunded in full under the policy in `services/billing/docs/refunds.md`, cost support time and damage customer trust.

Internal calls time out after **2 seconds** and the external payment processor can take longer than that, so timeouts on billing writes are normal, not rare.

## Decision

Every write endpoint of the billing service requires an idempotency key.

- The caller sends the header `Idempotency-Key` with a unique value on every `POST` to the billing service, for example on `POST /v2/billing/{account_id}/refunds` and `POST /v2/billing/{account_id}/credits`.
- A write without the header is rejected with HTTP **`400`**.
- The billing service stores the key, a hash of the request body and the response for **24 hours**.
- A repeated request with the same key and the same body returns the stored response and does not repeat the write.
- A repeated request with the same key and a different body is rejected with HTTP **`409`**.
- A request that arrives while the first request with the same key is still in progress is rejected with HTTP **`409`** and can be retried.
- Keys are scoped to one account, so the same key value used on two accounts does not collide.
- The billing service passes its own idempotency key to the external payment processor, so a retry between the billing service and the processor is also safe.
- Billing event consumers apply the same idea by ignoring an `evt_` ID they have already processed.

## Consequences

- Billing writes are safe to retry, so the shared retry rule of at most **2 retries** can be used for billing calls.
- Duplicate charges and duplicate refunds caused by retries are prevented.
- Every caller of the billing service must generate and send a key. A caller that generates a new key for each retry gets no protection.
- The billing database stores one extra row per write for **24 hours**.
- A retry after more than **24 hours** is treated as a new request, so long-delayed retries need a manual check of the invoice first.

## Alternatives considered

- **Detect duplicates by amount and time window** – catches some duplicates, but also blocks legitimate repeated charges and misses others.
- **No retries on billing writes** – avoids duplicates, but leaves the caller not knowing whether the write happened.
- **Idempotency keys on every write in every service** – useful, but not needed where a duplicate is harmless. Other services may adopt the same header later.
- **Distributed transactions with the payment processor** – not offered by the processor and too complex.

Service details are in `services/billing/README.md`.

Last reviewed: 2026-11-26
