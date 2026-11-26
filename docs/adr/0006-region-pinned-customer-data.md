# ADR 0006: Region-Pinned Customer Data

## Status

Accepted on **2024-09-17**.

## Context

Until 2024 Acme Cloud ran only in **`us-east`** (Virginia). Business and Enterprise customers in Europe and India asked for their data to be stored in their own jurisdiction, and several would not sign without a firm guarantee. Adding the regions **`eu-central`** (Frankfurt) and **`ap-south`** (Mumbai) raised a design question: should data be replicated between regions for resilience, or pinned to one region?

## Decision

Customer data in Acme Cloud is pinned to the region the customer chose and is never replicated to another region.

- Every account has a **home region** for account-level records: the account, members, subscription, invoices, support tickets and login identities.
- Every workspace has a **workspace region**, chosen when the workspace is created. The workspace region cannot be changed afterwards.
- Each region runs all services with its own PostgreSQL databases, Acme Event Bus cluster, object store, OpenSearch cluster, Redis cluster and ClickHouse warehouse.
- Backups stay in the region of the data they protect.
- The only global data is the global routing directory, which maps account IDs and workspace IDs to regions and holds no readable customer data. The directory is written in **`us-east`** with read replicas in **`eu-central`** and **`ap-south`**.
- The Acme Edge Gateway forwards a request that arrives in the wrong region to the correct region without storing the request.
- Region availability follows the plan: **`us-east`** on all plans, **`eu-central`** on Business and Enterprise, **`ap-south`** on Enterprise only.

## Consequences

- Acme Cloud can give a clear residency statement: workspace content never leaves the workspace region.
- A whole-region outage cannot be solved by failing over to another region. The region is rebuilt in place, with a recovery time objective of **4 hours** and a recovery point objective of **5 minutes**.
- Moving a workspace to another region is not a setting. The customer exports the data and creates a new workspace.
- An account with workspaces in several regions needs a small mirrored entitlement snapshot and membership list in each of those regions.
- Search and analytics cannot combine results across regions.
- Every new datastore must be deployed **3 times**, once per region.

The full topology is in `docs/architecture/multi-region-and-data-residency.md`.

## Alternatives considered

- **Replicate everything to all regions** – best resilience and lowest latency, but breaks the residency guarantee customers asked for.
- **One global database with a region column** – simple routing, but the data would physically sit in one place.
- **Replicate between regions only for Enterprise customers who opt in** – possible later, but doubles the number of failure modes. A future change would need a new decision record.
- **Separate deployments per customer** – strongest isolation, but too costly below the largest Enterprise contracts.

Last reviewed: 2026-11-26
