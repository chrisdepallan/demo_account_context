# ADR 0001: One Database per Service

## Status

Accepted on **2024-02-13**.

## Context

Acme Cloud is split into services that are each owned by one team, for example the accounts service by Accounts Platform and the billing service by Revenue Engineering. The first prototype used one shared PostgreSQL database for every service. In the shared database:

- A schema change by one team broke queries written by another team.
- Services joined directly to each other's tables, so no team could change its own tables safely.
- One slow report query from one service slowed down login and every other service.
- Deleting all data for one closed account meant knowing every table of every team.

## Decision

Each Acme Cloud service has its own PostgreSQL **16** database in each region, and no other service may connect to that database.

- There is **1 database per service per region**, so **12 services** in **3 regions** means **36 databases**.
- Each database has a primary, a synchronous standby in a second availability zone and an asynchronous read replica in a third zone.
- A service stores another service's entity only as an ID string such as `acc_7F3K9Q2M` or `ws_4H8P2L`.
- There are no foreign keys, joins or transactions across service databases.
- A service that needs another service's data either calls that service's internal API or builds a read-only projection from events on the Acme Event Bus.
- Database credentials are issued per service and are not shared between services.

## Consequences

- Each team can change its own schema and deploy without coordinating with other teams.
- A slow query or a full disk in one service's database does not take down other services.
- Cross-service consistency is eventual, not immediate. For example, the search index can lag behind the projects database by up to **30 seconds**.
- Reports that need data from several services must go through the analytics service, which builds its warehouse from events.
- Erasing an account's data is a coordinated flow driven by the `account.deleted` event, described in `docs/architecture/service-map.md`.
- Running **36 databases** costs more than running one and needs automated provisioning, backups and upgrades.

## Alternatives considered

- **One shared database with one schema per service** – cheaper to run, but nothing stops a service from reading another service's schema, and one database remains a single point of failure for all **12 services**.
- **One shared database with strict access rules by convention** – rejected because conventions were already being broken in the prototype.
- **A different database technology per service** – rejected for now. Using PostgreSQL everywhere keeps backups, monitoring and on-call knowledge the same for every team. Specialised stores are allowed in addition, such as OpenSearch for the search service and ClickHouse for the analytics service.

The resulting entity ownership is listed in `docs/architecture/data-model.md`.

Last reviewed: 2026-11-26
