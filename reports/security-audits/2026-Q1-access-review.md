# Security and Access Review 2026-Q1

## Scope

The **2026-Q1** security and access review covered production access for all 12 services, service accounts, break-glass use, dependency scanning and secret scanning. The review is run by Trust and Compliance (`#team-trust`) every 90 days, as required by `docs/security/access-control.md`.

## Findings in 2026-Q1

The 2026-Q1 review raised **7 findings**, of which **0** were High severity.

| Finding | Severity | Service | Description | Due | Status |
|------|------|------|------|------|------|
| FND-2026-Q1-01 | Low | `files` | Dependency two minor versions behind the latest patched release | 2026-10-11 | Closed |
| FND-2026-Q1-02 | Low | `audit-log` | Dependency two minor versions behind the latest patched release | 2026-10-11 | Closed |
| FND-2026-Q1-03 | Medium | `projects` | Production database role granted to an engineer who changed teams | 2026-07-13 | Closed |
| FND-2026-Q1-04 | Medium | `search` | Break-glass access used without a linked incident | 2026-07-13 | Closed |
| FND-2026-Q1-05 | Medium | `notifications` | Production database role granted to an engineer who changed teams | 2026-07-13 | Closed |
| FND-2026-Q1-06 | Low | `audit-log` | Dependency two minor versions behind the latest patched release | 2026-10-11 | Closed |
| FND-2026-Q1-07 | Low | `accounts` | Dependency two minor versions behind the latest patched release | 2026-10-11 | Closed |

## Access review results for 2026-Q1

- **447 access grants** were reviewed by the owning team's manager.
- **29 grants** were removed because they were no longer needed.
- Break-glass access was used **4 times** in 2026-Q1.

## Dependency and secret scanning in 2026-Q1

- Secret scanning found **0 committed secrets** in 2026-Q1.
- Dependency scanning reported **5 outdated packages** in build and tooling images. Service code uses the Python standard library only.

## Remediation deadlines

Findings must be fixed within **30 days** for High severity, **90 days** for Medium and **180 days** for Low, counted from the report date. Critical findings are handled as security incidents under `docs/security/incident-response.md`.

Report date: 2026-04-14
