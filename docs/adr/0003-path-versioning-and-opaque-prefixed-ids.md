# ADR 0003: Path Versioning and Opaque Prefixed IDs

## Status

Accepted on **2024-04-09**.

## Context

The first Acme Cloud API, `/v1`, was built quickly. The `/v1` API had two problems that affected every service.

- The version was sent in a request header. Customers often forgot the header, support agents could not see the version in a pasted URL, and the gateway could not route by version without reading headers.
- IDs were sequential integers. An integer gave no hint of what the ID referred to, leaked how many accounts existed, and let a caller guess neighbouring IDs.

A second major version was needed for the move to separate services, so both problems could be fixed in one step.

## Decision

Every Acme Cloud API puts the major version in the path, and every resource uses an opaque ID with a type prefix.

- The current version is **`/v2`**. All paths look like `https://api.acme-cloud.example/v2/<service>/...`.
- A new major version is created only for breaking changes. Adding fields or endpoints is not a breaking change and stays in **`/v2`**.
- When a new major version ships, the previous major version stays available for at least **12 months**.
- IDs are a short lowercase prefix, an underscore and random uppercase alphanumerics, for example `acc_7F3K9Q2M` for an account and `ws_4H8P2L` for a workspace.
- The prefixes are `acc_`, `ws_`, `prj_`, `tsk_`, `fil_`, `whk_`, `evt_`, `aud_`, `int_` and `ntf_`. The lengths are listed in `docs/architecture/data-model.md`.
- IDs are random. An ID does not encode the region, the creation time, the plan or the parent entity.
- Two human-facing numbers keep a readable format because customers quote them by phone and email: invoices as `INV-YYYY-NNNNNN` and support tickets as `SUP-NNNNN`.
- API keys follow the same idea with the prefixes `acme_live_` and `acme_test_`, so that leaked keys can be found by automated scanning.

## Consequences

- Anyone can tell the type of an ID from a log line, a URL or a support ticket.
- A wrong ID type, such as a `ws_` ID passed where an `acc_` ID is expected, is rejected with a clear validation error before any database lookup.
- IDs cannot be guessed or counted.
- Because IDs carry no region, the Acme Edge Gateway needs the global routing directory to find the region of an ID. See `docs/architecture/multi-region-and-data-residency.md`.
- The version is visible in every URL, which makes support and debugging easier.
- IDs are strings, so they use more storage than integers and must be compared exactly, including case.

## Alternatives considered

- **Version in a header** – keeps URLs stable across versions, but was the cause of the `/v1` support problems.
- **Date-based versions per account** – flexible, but too costly to test for **12 services**.
- **UUIDs without a prefix** – unguessable, but long and give no hint of the entity type.
- **Sequential integers** – small and fast, but guessable and reveal business volume.
- **IDs that encode the region** – would remove the directory lookup, but the format could never change and the region would leak into every ID.

Last reviewed: 2026-11-26
