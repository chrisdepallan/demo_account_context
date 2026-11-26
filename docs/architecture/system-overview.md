# Acme Cloud System Overview

## What the Acme Cloud platform is made of

The Acme Cloud platform is **12 services** behind one API gateway. Each service is a small Python service with its own `openapi.yaml`, `config/default.yaml`, a package named `acme_<name>` and a `tests/` folder. Each service owns its own data and is run by one team.

- Public API host – `https://api.acme-cloud.example`
- Web app host – `https://app.acme-cloud.example`
- API path pattern – `https://api.acme-cloud.example/v2/<service>/...`
- Regions – **`us-east`** (Virginia, default), **`eu-central`** (Frankfurt), **`ap-south`** (Mumbai)
- Every region runs all **12 services** and its own copy of every datastore.

## The 12 Acme Cloud services

| Service | What the service owns | Owning team | README |
|------|------|------|------|
| accounts | Accounts, workspaces, plans, members | Accounts Platform, `#team-accounts` | `services/accounts/README.md` |
| auth | Login, passwords, MFA, SSO, API keys | Identity, `#team-identity` | `services/auth/README.md` |
| billing | Subscriptions, invoices, payments, refunds | Revenue Engineering, `#team-billing` | `services/billing/README.md` |
| support | Tickets, SLAs, escalation | Customer Support, `#support-escalations` | `services/support/README.md` |
| projects | Projects, tasks, boards, comments, automation | Work Management, `#team-projects` | `services/projects/README.md` |
| files | File storage, uploads, versioning, sharing links, quotas | Storage Platform, `#team-storage` | `services/files/README.md` |
| notifications | Email, in-app and push notifications, digests | Messaging, `#team-notifications` | `services/notifications/README.md` |
| webhooks | Outbound event webhooks with HMAC signing and retries | Developer Platform, `#team-developer-platform` | `services/webhooks/README.md` |
| search | Full-text search over projects, tasks and files | Search and Discovery, `#team-search` | `services/search/README.md` |
| audit-log | Immutable, hash-chained security event log, export and SIEM streaming | Trust and Compliance, `#team-trust` | `services/audit-log/README.md` |
| integrations | App directory, OAuth installs, Slack, GitHub, Jira, Google Workspace | Ecosystem, `#team-ecosystem` | `services/integrations/README.md` |
| analytics | Customer dashboards, metrics, scheduled exports | Data Platform, `#team-data` | `services/analytics/README.md` |

## Request path from a client to an Acme Cloud service

Every API request from the web app, the mobile apps or a customer program follows the same **6 steps**.

```text
client
  |  HTTPS, TLS 1.2 or newer
  v
global DNS for api.acme-cloud.example  -> nearest region
  v
Acme Edge Gateway (edge-gateway)
  1. terminate TLS
  2. authenticate the session token or API key (auth service, cached 60 s)
  3. look up the home region in the global routing directory
  4. forward to the home region if the request arrived elsewhere
  5. apply the per-account rate limit
  6. route /v2/<service>/... to the service
  v
service pod (Kubernetes)  ->  the service's own PostgreSQL database
                          ->  Acme Event Bus (acme-bus) for events
```

- The Acme Edge Gateway is the only public entry point. No service is reachable from the internet directly.
- The gateway caches an authentication result for **60 seconds**, which is why revoking an API key takes effect within **60 seconds**.
- The gateway times out a normal request after **10 seconds**. File upload and download routes are streamed and are exempt from the **10-second** limit.
- Service-to-service calls stay inside the regional cluster, use mutual TLS and do not pass through the gateway.

## Internal platform components used by Acme Cloud services

| Component | Technology | Used for |
|------|------|------|
| API gateway | Acme Edge Gateway, internal name `edge-gateway` | TLS, authentication, region routing, rate limiting |
| Orchestration | Kubernetes, **1 cluster per region** across **3 availability zones** | Running all service pods |
| Relational storage | PostgreSQL **16**, **1 database per service per region** | Source-of-truth data for each service |
| Event bus | Acme Event Bus, internal name `acme-bus`, Kafka-compatible | Cross-service events |
| Object storage | S3-compatible object store, **1 bucket set per region** | File content, exports, audit log archives |
| Search cluster | OpenSearch, **1 cluster per region** | Full-text indexes for the search service |
| Cache | Redis, **1 cluster per region** | Rate limit counters and authentication cache |
| Analytics warehouse | ClickHouse, **1 cluster per region** | Aggregated metrics for the analytics service |
| Global routing directory | Small PostgreSQL database written in **`us-east`** with read replicas in **`eu-central`** and **`ap-south`** | Mapping account and workspace IDs to regions |

## How Acme Cloud services talk to each other

Acme Cloud services use two kinds of communication.

- **Synchronous calls** – a service calls another service's internal API when it needs an answer before it can reply, for example the billing service reading the seat count from the accounts service. Internal calls time out after **2 seconds**.
- **Events** – a service publishes a `resource.action` event such as `account.closed` or `file.uploaded` to the Acme Event Bus, and any interested service consumes the event later. Events are the default for anything that does not need an immediate answer.

The full dependency table and the event names are in `docs/architecture/service-map.md`. The reasons for the event-first approach are in `docs/adr/0002-event-bus-for-cross-service-communication.md`.

## API conventions shared by every Acme Cloud service

- The API version is in the path: **`/v2`**. See `docs/adr/0003-path-versioning-and-opaque-prefixed-ids.md`.
- Resource IDs are opaque strings with a type prefix, for example `acc_7F3K9Q2M` for an account and `ws_4H8P2L` for a workspace. All ID formats are listed in `docs/architecture/data-model.md`.
- Requests are authenticated with a session or with an API key that starts with `acme_live_` (production) or `acme_test_` (sandbox). API keys are described in `services/auth/docs/api-keys.md`.
- Requests over the plan's rate limit get HTTP **`429`** with a `Retry-After` header. Limits per plan are in `services/accounts/docs/plans-and-limits.md`.
- Timestamps are ISO 8601 in UTC.

## Where Acme Cloud customer data is stored

Customer data stays in the regions the customer chose. Account-level records stay in the account's **home region**, and workspace content stays in the region picked when the workspace was created. Only a small routing directory and non-customer catalogues are global. Details are in `docs/architecture/multi-region-and-data-residency.md`.

## Where to read more about the Acme Cloud architecture

- `docs/architecture/service-map.md` – service dependencies and event names
- `docs/architecture/data-model.md` – core entities, ID formats and owners
- `docs/architecture/multi-region-and-data-residency.md` – regions, global and regional data, failover
- `docs/architecture/reliability-and-scaling.md` – SLOs, rate limiting, backpressure, uptime measurement
- `docs/adr/` – **12** architecture decision records, `0001` to `0012`
- `docs/company-overview.md` – company facts, regions and uptime targets
- `docs/glossary.md` – customer-facing terms

Last reviewed: 2026-11-26
