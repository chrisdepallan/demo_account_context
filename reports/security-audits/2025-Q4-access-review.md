# Security and Access Review 2025-Q4

## Scope

The **2025-Q4** security and access review covered production access for all 12 services, service accounts, break-glass use, dependency scanning and secret scanning. The review is run by Trust and Compliance (`#team-trust`) every 90 days, as required by `docs/security/access-control.md`.

## Findings in 2025-Q4

The 2025-Q4 review raised **4 findings**, of which **1** were High severity.

| Finding | Severity | Service | Description | Due | Status |
|------|------|------|------|------|------|
| FND-2025-Q4-01 | Medium | `audit-log` | Service account with write access that was not used in 90 days | 2026-04-14 | Closed |
| FND-2025-Q4-02 | High | `search` | Internal endpoint reachable without the gateway's authentication check | 2026-02-13 | Closed |
| FND-2025-Q4-03 | Medium | `accounts` | Break-glass access used without a linked incident | 2026-04-14 | Closed |
| FND-2025-Q4-04 | Medium | `notifications` | Break-glass access used without a linked incident | 2026-04-14 | Closed |

## Access review results for 2025-Q4

- **462 access grants** were reviewed by the owning team's manager.
- **28 grants** were removed because they were no longer needed.
- Break-glass access was used **5 times** in 2025-Q4.

## Dependency and secret scanning in 2025-Q4

- Secret scanning found **0 committed secrets** in 2025-Q4.
- Dependency scanning reported **10 outdated packages** in build and tooling images. Service code uses the Python standard library only.

## Remediation deadlines

Findings must be fixed within **30 days** for High severity, **90 days** for Medium and **180 days** for Low, counted from the report date. Critical findings are handled as security incidents under `docs/security/incident-response.md`.

Report date: 2026-01-14
