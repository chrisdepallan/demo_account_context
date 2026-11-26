# ADR 0005: Rate Limiting Inside Each Service

## Status

Superseded by ADR 0011 on **2025-11-18**. Originally accepted on **2024-07-02**.

The current rule is in `docs/adr/0011-rate-limiting-at-the-gateway.md`. This record is kept for history only. Do not build new per-service API rate limiters.

## Context

In mid-2024 Acme Cloud had **4 services** (accounts, auth, billing and support) and a thin API gateway that only terminated TLS and routed requests. Plans promised a number of API requests per minute, for example **1,000 per minute** on Pro, but nothing enforced the number. A few customer scripts in tight loops caused slow responses for other customers.

The gateway at the time had no access to plan data and no shared counter store.

## Decision

Each Acme Cloud service enforced the API rate limit itself.

- Each service counted requests per account in its own memory, per pod.
- Each service read the account's plan from the accounts service and cached the plan for **60 seconds**.
- Over the limit, the service returned HTTP **`429`** with a `Retry-After` header.
- The limiter code lived in the shared internal platform library so that services did not write their own.

## Consequences

- Rate limiting shipped quickly, without changes to the gateway.
- The limit was applied per service, not per account across the whole API. A customer on Pro could send **1,000 requests per minute** to each service, which is more than the plan promised.
- Counters were per pod, so the real limit grew whenever a service scaled out.
- Rejected requests still reached the service and used its capacity.
- As the platform grew towards **12 services**, limits became inconsistent and hard to explain to customers.

These consequences led to ADR 0011, which moved rate limiting to the Acme Edge Gateway.

## Alternatives considered

- **Rate limiting at the gateway** – the better design, but in 2024 the gateway had no plan data and no counter store. This alternative was adopted later as ADR 0011.
- **A separate rate-limit service called by every service** – one more synchronous dependency on the path of every request.
- **No enforcement, only monitoring** – rejected because noisy accounts were already affecting other customers.

Last reviewed: 2026-11-26
