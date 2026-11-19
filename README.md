# demo_account_context

Sample context repository for an MCP documentation server. It describes **Acme Cloud**, a fictional SaaS company, and holds the account, billing, auth and support knowledge an AI assistant needs to answer customer and internal questions.

> All companies, people, prices and URLs here are fictional. No real credentials are stored in this repo.

## What this repo is for

- Indexed by the MCP server as a single library (`acme-account-context`, branch `main`).
- Each Markdown file is split at its headings, so every `##` section is a searchable answer.
- Each service folder has a `README.md` describing what the service does, its key concepts and how to use it.

## Repository layout

| Path | Contents |
|------|----------|
| `docs/` | Company-wide docs: overview, glossary, FAQ |
| `services/accounts/` | Account lifecycle, plans, limits, team members |
| `services/billing/` | Pricing, invoices, payment methods, refunds, taxes |
| `services/auth/` | Login, passwords, MFA, SSO, API keys |
| `services/support/` | Support channels, SLAs, escalation |
| `services/*/fixtures/` | Test data, **not** meant for indexing |

## Recommended index globs

Index only the documentation, and skip fixtures and test data:

```text
README.md
docs/**
services/*/README.md
services/*/docs/**
```

## Keeping the index fresh

- There is no auto-sync. Re-index after merging any doc change to `main`.
- Update the "Last reviewed" line at the bottom of a doc when you change it.

## Contributing

1. Use one topic per `##` heading, and phrase headings the way customers ask (for example "## How long do refunds take?").
2. Put concrete values (amounts, durations, limits) in the text, not only in tables or images.
3. Never commit secrets, real customer data or internal-only credentials. The secret filter only skips files by name.
4. Sensitive or restricted docs belong in a separate repo or library, because access is all-or-nothing per library.
