# demo_account_context

Sample context repository for an MCP documentation server. It describes **Acme Cloud**, a fictional SaaS company, and holds the account, billing, auth and support knowledge an AI assistant needs to answer customer and internal questions.

> All companies, people, prices and URLs here are fictional. No real credentials are stored in this repo.

## What this repo is for

- Indexed by the MCP server as a single library (`acme-account-context`, branch `main`).
- Each Markdown file is split at its headings, so every `##` section is a searchable answer.
- Each service folder has a `README.md` describing what the service does, its key concepts and how to use it.
- The repo is sized to test the server on a large library: 12 services with docs, code, tests, API specs and config, plus a year of generated reports and datasets.

## Repository layout

| Path | Contents |
|------|----------|
| `docs/` | Company-wide docs: overview, glossary, FAQ |
| `docs/architecture/` | System overview, service map, data model, regions, reliability |
| `docs/adr/` | Architecture decision records, numbered `0001` onwards |
| `docs/runbooks/` | Step-by-step guides for operational incidents |
| `docs/engineering/` | Onboarding, coding standards, testing, releases, on-call, API design |
| `docs/security/` | Data classification, access control, incident response, compliance |
| `services/accounts/` | Account lifecycle, plans, limits, team members |
| `services/billing/` | Pricing, invoices, payment methods, refunds, taxes |
| `services/auth/` | Login, passwords, MFA, SSO, API keys |
| `services/support/` | Support channels, SLAs, escalation |
| `services/projects/` | Projects, tasks, boards, automation |
| `services/files/` | File storage, uploads, versions, sharing links, quotas |
| `services/notifications/` | Email, in-app and push notifications, digests |
| `services/webhooks/` | Outbound webhooks, signing, retries |
| `services/search/` | Full-text search, query syntax, indexing |
| `services/audit-log/` | Audit entries, retention, export, SIEM streaming |
| `services/integrations/` | App directory, OAuth installs, sync |
| `services/analytics/` | Dashboards, metrics, scheduled exports |
| `services/*/docs/` | One Markdown file per topic for that service |
| `services/*/acme_*/` and `services/*/tests/` | The service's Python package and its `unittest` tests |
| `services/*/openapi.yaml` and `services/*/config/` | API specification and default configuration |
| `services/*/CHANGELOG.md` | Generated release history of the service |
| `services/*/fixtures/` | Test data, **not** meant for indexing |
| `reports/` | Generated incident postmortems, test runs, performance, capacity, security and quarterly reviews, release notes |
| `data/` | Generated CSV and JSON datasets behind the reports, **not** meant for indexing |
| `tools/` | Scripts to run the tests, check the docs and regenerate reports |

## Recommended index globs

To index the documentation and reports only, and skip code, fixtures and datasets:

```text
README.md
CONTRIBUTING.md
docs/**
services/*/README.md
services/*/CHANGELOG.md
services/*/docs/**
reports/**
tools/README.md
```

To also test the server on code, specs and config, add:

```text
services/*/acme_*/**
services/*/tests/**
services/*/openapi.yaml
services/*/config/**
tools/*.py
```

Leave out `services/*/fixtures/**` and `data/**` unless the test is specifically about structured data.

## Working with the repo

- Run the tests with `python tools/run_tests.py`.
- Check doc structure and file references with `python tools/check_links.py`.
- Regenerate `reports/`, `data/`, changelogs and fixtures with `python tools/generate_reports.py`. Add `--scale N` to produce N years of history and make the repo larger.
- Details are in `tools/README.md` and `CONTRIBUTING.md`.

## Keeping the index fresh

- There is no auto-sync. Re-index after merging any doc change to `main`.
- Update the "Last reviewed" line at the bottom of a doc when you change it.

## Contributing

The full rules are in `CONTRIBUTING.md`. In short:

1. Use one topic per `##` heading, and phrase headings the way customers ask (for example "## How long do refunds take?").
2. Put concrete values (amounts, durations, limits) in the text, not only in tables or images.
3. Never commit secrets, real customer data or internal-only credentials. The secret filter only skips files by name.
4. Sensitive or restricted docs belong in a separate repo or library, because access is all-or-nothing per library.
