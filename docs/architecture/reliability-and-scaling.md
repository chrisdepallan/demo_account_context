# Reliability and Scaling

## Service tiers and availability SLOs

Every Acme Cloud service is in one of **3 tiers**. The tier sets the internal availability SLO, which is stricter than the uptime promised to customers.

| Tier | Services | Monthly availability SLO | Allowed downtime in a 30-day month |
|------|------|------|------|
| Tier 1 | Acme Edge Gateway, auth, accounts, projects, files | **99.995%** | **2.16 minutes** |
| Tier 2 | billing, notifications, webhooks, search, audit-log, integrations | **99.95%** | **21.6 minutes** |
| Tier 3 | analytics, support | **99.9%** | **43.2 minutes** |

- Tier 1 services are the ones a customer needs to sign in and work with projects and files.
- Tier 2 services can be degraded for a short time without stopping core work. For example, search results may be stale or a webhook may arrive late.
- Tier 3 services are not on the path of everyday work.

## Latency SLOs per service tier

| Tier | Latency SLO, measured at the Acme Edge Gateway |
|------|------|
| Tier 1 | **99%** of requests answered within **500 ms** |
| Tier 2 | **99%** of requests answered within **1 second** |
| Tier 3 | **99%** of requests answered within **3 seconds** |

File upload and download routes are excluded from the latency SLOs because their duration depends on file size.

## SLOs for asynchronous work

| Asynchronous step | SLO |
|------|------|
| Event published to the Acme Event Bus after the database commit | **99%** within **5 seconds** |
| Audit entry written after the triggering event | **99%** within **10 seconds** |
| Search index updated after a project, task or file change | **95%** within **30 seconds** |
| First webhook delivery attempt after the event | **99%** within **30 seconds** |
| Email notification handed to the mail provider | **99%** within **60 seconds** |

## How the customer uptime target is measured

The uptime targets in `docs/company-overview.md` are **99.9%** monthly on Starter and Pro, **99.95%** on Business and **99.99%** on Enterprise. The Free plan has no uptime SLA. Uptime is measured as follows.

- Uptime covers the **Tier 1** surface only: signing in, the API and the web app's ability to read and write projects and files.
- Uptime is measured per region. A customer's uptime is the uptime of the region that hosts the customer's workspace.
- Synthetic probes run every **60 seconds** from **3 external locations** against each region. Each probe signs in, reads a project and downloads a small file.
- A minute counts as **down** when at least **2 of the 3** probe locations fail, or when more than **5%** of Tier 1 requests at the Acme Edge Gateway return a `5xx` status in that minute.
- Monthly uptime = (minutes in the month – down minutes) / minutes in the month.
- Maintenance announced on `https://status.acme-cloud.example` at least **7 days** in advance does not count as down time.
- Responses with status `429` or any other `4xx` status do not count as failures.

In a 30-day month, **99.9%** allows **43.2 minutes** of down time, **99.95%** allows **21.6 minutes** and **99.99%** allows **4.32 minutes**. Service credits for a missed SLA are described in `services/billing/docs/refunds.md`.

## Rate limiting at the Acme Edge Gateway

Rate limits are enforced once, at the Acme Edge Gateway, with a token bucket per account held in Redis.

| Plan | API requests per minute |
|------|------|
| Free | **100** |
| Starter | **300** |
| Pro | **1,000** |
| Business | **3,000** |
| Enterprise | **10,000** |

- Limits are counted per account, not per API key and not per workspace.
- A request over the limit gets HTTP **`429 Too Many Requests`** with a `Retry-After` header in seconds.
- The gateway reads the plan from the accounts service's entitlement snapshot, cached for **60 seconds**.
- If Redis is unreachable, the gateway falls back to a local in-memory bucket per gateway instance and keeps serving requests.
- The decision record is `docs/adr/0011-rate-limiting-at-the-gateway.md`. The customer-facing limits are in `services/accounts/docs/plans-and-limits.md`.

## Timeouts, retries and circuit breakers between services

- The Acme Edge Gateway times out a request to a service after **10 seconds**.
- A synchronous call from one service to another times out after **2 seconds**.
- Only idempotent calls are retried, at most **2 times**, with random jitter between attempts.
- A circuit breaker opens when **50%** of at least **20 calls** in a **10-second** window fail. An open breaker rejects calls for **30 seconds**, then lets one test call through.
- Billing writes are safe to retry because of idempotency keys. See `docs/adr/0008-idempotency-keys-on-billing-writes.md`.

## Backpressure when a service is overloaded

- Each service pod has a fixed concurrency limit. A pod at its limit answers **`503 Service Unavailable`** with a `Retry-After` header instead of queueing without bound.
- Work that does not need an immediate answer goes through the Acme Event Bus. When a consumer falls behind, events wait on the bus for up to **7 days**; the producer is not slowed down.
- Consumer lag is an alert. The owning team is paged when a consumer is more than **5 minutes** behind on a Tier 1 or Tier 2 service.
- An event that fails **5 times** moves to the consumer's dead-letter topic so that one bad event cannot block the events behind it.
- When the search, analytics or notifications service is degraded, the projects and files services keep accepting writes. The degraded service catches up from the bus afterwards.

## Capacity approach for Acme Cloud services

- Every Tier 1 and Tier 2 service runs at least **3 replicas** across **3 availability zones**. Tier 3 services run at least **2 replicas**.
- Services scale horizontally on CPU, with a target of **60%** average utilisation.
- Each region is sized so that the loss of **1 availability zone** still leaves enough capacity for peak traffic.
- Each region is load-tested every quarter at **2 times** the highest traffic seen in the previous quarter.
- PostgreSQL databases scale up first. A database is reviewed for splitting or archiving when storage passes **70%** of the provisioned size.
- Capacity is planned per region. Spare capacity in one region is never used to serve another region's customer data, as explained in `docs/architecture/multi-region-and-data-residency.md`.

## Error budgets and what happens when an SLO is missed

- The error budget of a service is the allowed downtime of the service's tier for the month.
- When a service has used **50%** of the monthly error budget, the owning team reviews recent changes before the next deployment.
- When a service has used **100%** of the monthly error budget, the owning team stops feature deployments to that service until the end of the month. Reliability fixes are still deployed.
- A P1 incident opens an incident on the status page within **15 minutes**, as described in `services/support/docs/sla-and-escalation.md`.

Last reviewed: 2026-11-26
