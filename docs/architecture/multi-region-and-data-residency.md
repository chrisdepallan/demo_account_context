# Multi-Region and Data Residency

## Acme Cloud region topology

Acme Cloud runs **3 regions**. Each region is a complete, independent copy of the platform.

| Region code | Location | Available on |
|------|------|------|
| `us-east` | Virginia, USA | All plans (default) |
| `eu-central` | Frankfurt, Germany | Business and Enterprise |
| `ap-south` | Mumbai, India | Enterprise only |

Each region contains:

- **1** Kubernetes cluster spread over **3 availability zones**, running all **12 services**
- **1** PostgreSQL **16** database per service, with a primary, a synchronous standby in a second zone and an asynchronous read replica in a third zone
- **1** Acme Event Bus (`acme-bus`) cluster with **3 brokers**
- **1** object store, **1** OpenSearch cluster, **1** Redis cluster and **1** ClickHouse warehouse
- **1** set of Acme Edge Gateway instances

Regions do not share databases, buses, buckets or indexes.

## What a home region is

Every account has a **home region**, and every workspace has a **workspace region**.

- **Home region** – where account-level records live: the account, members, subscription, invoices, support tickets and login identities. The home region is the region of the account's first workspace. Self-serve sign-ups start on the Pro trial, so their home region is **`us-east`**.
- **Workspace region** – where the content of one workspace lives: projects, tasks, files, search indexes, analytics, webhook endpoints, installed integrations and audit entries for that workspace. The workspace region is chosen when the workspace is created and cannot be changed afterwards.

An account on Business or Enterprise can have workspaces in more than one region. To move a workspace to another region, the customer exports the data and creates a new workspace, as described in `docs/company-overview.md`.

## What is global in Acme Cloud

Only data that is needed to find the right region, or that is not customer data, is global.

| Global item | Contents | Where the item is written |
|------|------|------|
| Global routing directory | Account ID to home region, workspace ID to workspace region, a one-way hash of each login email to home region, a one-way fingerprint of each API key to workspace region | `us-east`, with read replicas in `eu-central` and `ap-south` |
| Plan catalogue | Plan names, limits and prices | Shipped with each deployment |
| App directory catalogue | The list of available integrations | Shipped with each deployment |
| DNS and status page | `api.acme-cloud.example`, `status.acme-cloud.example` | Outside the regions |

The global routing directory holds no names, no readable email addresses, no file names and no content.

## What is regional in Acme Cloud

Everything a customer creates is regional.

- Account-level records – stored only in the home region.
- Workspace content, file content and file versions – stored only in the workspace region.
- Search indexes, analytics data and audit entries – built and stored in the same region as the data they describe.
- Events on the Acme Event Bus – published and consumed in the region where the change happened.
- Backups – stored in the same region as the database or bucket they protect.
- Logs and metrics that contain customer identifiers – kept in the region that produced them.

## How a request reaches the right region

1. Global DNS sends the client to the nearest Acme Edge Gateway.
2. The gateway reads the workspace ID or account ID from the request, or the fingerprint of the API key.
3. The gateway looks up the region in its local replica of the global routing directory.
4. If the request arrived in a different region, the gateway forwards the request to the gateway of the correct region over a private link. The request body is not stored in the first region.
5. Requests that name a workspace go to the workspace region. Account-level requests, such as `GET /v2/accounts/{account_id}`, go to the home region.

## What crosses regions for an account with workspaces in several regions

An account with workspaces in more than one region needs a small amount of account data in each of those regions. The accounts service in the home region mirrors the following to each workspace region the account uses, and to no other region:

- The entitlement snapshot – account ID, plan, account state and limits
- The membership list for the workspaces in that region – member reference, display name, email address and role
- The events `account.plan_changed`, `account.state_changed`, `account.closed`, `account.restored` and `account.deleted`

Projects, tasks, files, comments, search indexes and analytics data never leave the workspace region. Search and analytics do not combine results across regions; the web app queries each workspace region separately.

## Failover inside one region

- **Loss of one pod or node** – Kubernetes reschedules the pod. Every Tier 1 and Tier 2 service runs at least **3 replicas** across **3 availability zones**.
- **Loss of one availability zone** – the PostgreSQL synchronous standby is promoted. The recovery point objective is **0** lost transactions and the recovery time objective is **5 minutes**.
- **Loss of a bus broker** – the Acme Event Bus keeps **3 copies** of every event and continues with **2 brokers**.

Service tiers are defined in `docs/architecture/reliability-and-scaling.md`.

## Failover when a whole region is lost

Acme Cloud does **not** fail customer data over to another region, because doing so would break the residency rule. If a whole region is lost, the region is rebuilt in place from in-region backups.

- Recovery point objective for a full-region rebuild: **5 minutes** of data, from continuous log archiving.
- Recovery time objective for a full-region rebuild: **4 hours**.
- Database backups are a daily snapshot plus continuous log archiving, kept for **35 days**.
- Workspaces in the other two regions are not affected by the loss of one region.

If `us-east` is lost, the global routing directory is promoted in `eu-central` within **15 minutes**. Until the promotion, existing accounts in `eu-central` and `ap-south` keep working, but new sign-ups and new workspaces are paused.

## Data residency rules for engineers

- Never copy customer data between regions, including for debugging or testing.
- Never add a field with readable customer data to the global routing directory.
- A new service or datastore must be deployed per region, with in-region backups.
- A new cross-region data flow needs a new decision record and a review by Trust and Compliance in `#team-trust`.
- The decision record for region pinning is `docs/adr/0006-region-pinned-customer-data.md`.

Last reviewed: 2026-11-26
