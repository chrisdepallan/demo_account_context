# ADR 0011: Rate Limiting at the Gateway

## Status

Accepted on **2025-11-18**. Supersedes ADR 0005, `docs/adr/0005-rate-limiting-inside-each-service.md`.

## Context

ADR 0005 put API rate limiting inside each service. By late 2025 Acme Cloud had grown from **4 services** towards **12 services**, and the per-service approach no longer matched what plans promise.

- Plans promise one number per account, for example **1,000 requests per minute** on Pro. With a limiter in each service, a customer could send that number to every service at once.
- Counters lived in each pod's memory, so the effective limit rose whenever a service scaled out.
- Rejected requests still reached the services and used their capacity during traffic spikes.
- Support could not explain why the same account was limited on one endpoint and not on another.

By then the Acme Edge Gateway already authenticated every request and knew the account ID.

## Decision

API rate limiting in Acme Cloud is enforced once, at the Acme Edge Gateway (`edge-gateway`), and the per-service limiters are removed.

- The gateway keeps one token bucket per account in the regional Redis cluster.
- The limits per plan are **100 requests per minute** on Free, **300** on Starter, **1,000** on Pro, **3,000** on Business and **10,000** on Enterprise, as listed in `services/accounts/docs/plans-and-limits.md`.
- Limits are counted per account, not per API key and not per workspace.
- A request over the limit gets HTTP **`429 Too Many Requests`** with a `Retry-After` header in seconds and never reaches a service.
- The gateway reads the plan from the accounts service's entitlement snapshot and caches the plan for **60 seconds**.
- If Redis is unreachable, each gateway instance falls back to a local in-memory bucket and keeps serving requests.
- Services keep their own protection against overload, a fixed concurrency limit that answers **`503`**, which is separate from the plan's rate limit.

## Consequences

- The enforced limit is exactly the number the plan promises, across the whole API.
- Rejected requests cost almost nothing, because they stop at the gateway.
- Limit changes are made in one place, the plan catalogue.
- The gateway now depends on Redis and on plan data. The local fallback bucket keeps the gateway available but is less exact during a Redis outage.
- A plan upgrade can take up to **60 seconds** to raise the limit.
- Limits are counted per region. An account with workspaces in two regions has a separate bucket in each region.
- Internal service-to-service calls do not pass through the gateway and are not counted.

## Alternatives considered

- **Keep per-service limiters and divide the limit between services** – no fair way to split one number across **12 services**.
- **Per-service limiters with shared Redis counters** – fixes the scaling problem but not the wasted capacity, and every service would depend on Redis.
- **Limits per API key** – simple for customers with one key, but a customer could raise the limit by creating more keys, up to **25** per workspace.
- **A separate rate-limit service** – adds a network hop to every request for something the gateway can do in-process.

The operational view is in `docs/architecture/reliability-and-scaling.md`.

Last reviewed: 2026-11-26
