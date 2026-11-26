# ADR 0002: Event Bus for Cross-Service Communication

## Status

Accepted on **2024-03-05**.

## Context

After ADR 0001 gave each service its own database, services needed another way to learn about changes in other services. The first approach was direct synchronous calls: when an account was closed, the accounts service called the auth service, the billing service and every other service one by one.

- One slow or failed downstream service made the whole "close account" request fail.
- Every new service that cared about a change needed a code change in the producing service.
- Tier 1 services such as accounts inherited the lower availability of Tier 3 services they called.

## Decision

Cross-service communication in Acme Cloud is event-first, using the Acme Event Bus (internal name `acme-bus`), a Kafka-compatible log with one cluster per region.

- Each producing service has **one topic** named `<service>.events`, for example `accounts.events` and `billing.events`.
- Event names use the `resource.action` form, for example `account.closed`, `invoice.paid`, `task.completed`, `file.uploaded` and `member.invited`.
- Every event has an ID of `evt_` plus **10** uppercase alphanumerics and the shared envelope described in `docs/architecture/service-map.md`.
- Events are keyed by account ID, so events for one account are delivered in order.
- Delivery is **at least once**. Consumers must be idempotent and ignore an event ID they have already processed.
- Producers use an outbox table written in the same database transaction as the data change. A relay publishes the event, normally within **5 seconds**.
- Events stay on the bus for **7 days**.
- A consumer that fails on one event **5 times** moves the event to the dead-letter topic `<consumer>.dlq`.
- Synchronous internal calls are allowed only when the caller needs the answer before replying, with a **2-second** timeout.

## Consequences

- A producer does not know or care which services consume its events. The notifications, webhooks, search, audit-log and analytics services were added without changes to the producers.
- A degraded consumer no longer breaks the producer. The consumer catches up from the bus afterwards.
- Data in consuming services is eventually consistent, and every consumer must handle duplicate events.
- Event schemas are a public contract between teams. A breaking change needs a new `schema_version` and a migration period.
- The Acme Event Bus is a critical shared component and is operated at the Tier 1 standard defined in `docs/architecture/reliability-and-scaling.md`.

## Alternatives considered

- **Synchronous calls only** – simple to reason about, but couples availability and requires producers to know all consumers.
- **Direct webhooks between services** – no ordering, no replay and each producer would need its own retry logic.
- **Database change-data-capture read by other teams** – exposes internal table layouts and breaks the ownership rule in `docs/adr/0001-one-database-per-service.md`.
- **A traditional message queue with one queue per consumer** – rejected because a log lets a new consumer replay the last **7 days** of events, which a queue does not.

Last reviewed: 2026-11-26
