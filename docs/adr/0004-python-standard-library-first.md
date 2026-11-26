# ADR 0004: Python Standard-Library-First Policy for Service Code

## Status

Accepted on **2024-05-21**.

## Context

Every Acme Cloud service is a small Python service with the same layout: a package named `acme_<name>` (the audit-log service uses `acme_audit_log`), an `openapi.yaml`, a `config/default.yaml` and a `tests/` folder. In early 2024 the services had drifted apart.

- Different services used different third-party libraries for the same job, such as HTTP clients, date handling and retries.
- A security fix in one popular library meant separate upgrades in every service, each with its own version pin.
- Engineers moving between teams had to learn a new stack for each service.
- Several outages were traced to transitive dependencies that nobody had chosen on purpose.

## Decision

Service code in Acme Cloud uses the Python standard library first. A third-party package is allowed only when it is on the approved list.

- All services run on Python **3.12**.
- The standard library is the default for HTTP handling, JSON, dates, hashing, HMAC, logging, data classes and unit tests.
- The approved list has **4** runtime categories: a PostgreSQL driver, the Acme Event Bus client, a YAML parser for `config/default.yaml`, and the shared internal platform library for logging, tracing and health checks.
- Services with a specialised store may add that store's client: the search service an OpenSearch client, the analytics service a ClickHouse client and the files service an object storage client.
- Adding a package to the approved list needs a pull request reviewed by the owning team and by Developer Platform in `#team-developer-platform`.
- Every service pins exact dependency versions, and the pins are updated by an automated weekly job.
- Tests in `tests/` run with the standard library's `unittest` runner.

## Consequences

- Services look alike, so an engineer who knows one service can read any of the **12 services**.
- The number of packages to patch after a security advisory is small and the same everywhere.
- Service containers are small and start quickly, which helps horizontal scaling.
- Some code is written by hand that a library would have provided, for example request routing and retry helpers. The shared internal platform library holds the common parts.
- Teams occasionally wait for an approval before using a new package.

## Alternatives considered

- **One full web framework for all services** – consistent, but brings a large dependency tree and ties every service to the framework's release cycle.
- **Free choice per team** – fastest in the short term, and the cause of the drift described in the context.
- **A different language for performance-critical services** – rejected for now. No service has a workload that Python and horizontal scaling cannot handle, and one language keeps on-call simple.

Last reviewed: 2026-11-26
