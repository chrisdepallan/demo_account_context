# ADR 0012: Docs as a Single MCP-Indexed Context Repository

## Status

Accepted on **2026-06-09**.

## Context

Acme Cloud documentation was spread over a wiki, the help center, service repositories and chat threads. AI assistants used by support agents and engineers answer questions through an MCP documentation server, and the server can only answer from what it indexes.

- Answers were inconsistent because the same fact, such as the **30-day** data retention window, was written in several places with different wording.
- The MCP server gives access per library, all or nothing, so a mix of public and restricted pages in one source could not be indexed safely.
- The MCP server splits each Markdown file at its headings. Long pages with vague headings produced sections that made no sense on their own.

## Decision

Acme Cloud keeps its assistant-facing documentation in one repository, indexed by the MCP server as a single library named `acme-account-context` on branch `main`.

- Company-wide documents live in `docs/`, architecture documents in `docs/architecture/` and decision records in `docs/adr/`.
- Each of the **12 services** has a folder `services/<name>/` with a `README.md` and a `docs/` folder.
- The index covers `README.md`, `docs/**`, `services/*/README.md` and `services/*/docs/**`. Fixtures and test data are not indexed.
- Every file has one `# Title` and flat `##` sections. Each `##` section must stand on its own and name its subject, because the section is the unit the server returns.
- Concrete values are written in the prose in bold, not only in tables. File names are kebab-case and dates are ISO 8601.
- Files refer to each other by repository path in backticks, not by hyperlink.
- Every file ends with a `Last reviewed` date, which is updated when the file changes.
- The repository holds no secrets, no real customer data and no restricted documents. Restricted documents go in a separate repository and library.
- There is no automatic sync. The library is re-indexed after every merge to `main`.

## Consequences

- An assistant finds one authoritative answer for each fact, and a fact is corrected in one place.
- Documentation changes are reviewed in pull requests like code, by the team that owns the service.
- Anyone with access to the library can read every file, so authors must keep restricted material out.
- Authors must follow the heading and style rules, which takes more care than writing a wiki page.
- The index can be stale between a merge and the next re-index.
- A single repository grows large. The server must handle about **300 files**, which is tested with this repository.

## Alternatives considered

- **Index the existing wiki and help center directly** – no migration, but the duplicated and conflicting pages would remain.
- **One library per service** – finer access control, but assistants would need to query **12** libraries and cross-service answers would be harder.
- **Keep documentation only next to the code in each service repository** – close to the code, but company-wide and architecture documents would have no home.
- **Generate documentation from `openapi.yaml` files only** – accurate for endpoints, but cannot answer policy questions such as refunds or retention.

The contribution rules are in `README.md`.

Last reviewed: 2026-11-26
