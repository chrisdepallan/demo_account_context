# Security and Access Review 2026-Q2

## Scope

The **2026-Q2** security and access review covered production access for all 12 services, service accounts, break-glass use, dependency scanning and secret scanning. The review is run by Trust and Compliance (`#team-trust`) every 90 days, as required by `docs/security/access-control.md`.

## Findings in 2026-Q2

The 2026-Q2 review raised **7 findings**, of which **0** were High severity.

| Finding | Severity | Service | Description | Due | Status |
|------|------|------|------|------|------|
| FND-2026-Q2-01 | Low | `files` | Log line included a full request path with an account ID in debug mode | 2027-01-10 | Open |
| FND-2026-Q2-02 | Medium | `accounts` | Production database role granted to an engineer who changed teams | 2026-10-12 | Closed |
| FND-2026-Q2-03 | Medium | `projects` | Service account with write access that was not used in 90 days | 2026-10-12 | Closed |
| FND-2026-Q2-04 | Low | `files` | Configuration file referenced a secret by an outdated variable name | 2027-01-10 | Open |
| FND-2026-Q2-05 | Low | `analytics` | Configuration file referenced a secret by an outdated variable name | 2027-01-10 | Open |
| FND-2026-Q2-06 | Low | `files` | Dependency two minor versions behind the latest patched release | 2027-01-10 | Open |
| FND-2026-Q2-07 | Medium | `notifications` | Production database role granted to an engineer who changed teams | 2026-10-12 | Closed |

## Access review results for 2026-Q2

- **397 access grants** were reviewed by the owning team's manager.
- **26 grants** were removed because they were no longer needed.
- Break-glass access was used **0 times** in 2026-Q2.

## Dependency and secret scanning in 2026-Q2

- Secret scanning found **0 committed secrets** in 2026-Q2.
- Dependency scanning reported **3 outdated packages** in build and tooling images. Service code uses the Python standard library only.

## Remediation deadlines

Findings must be fixed within **30 days** for High severity, **90 days** for Medium and **180 days** for Low, counted from the report date. Critical findings are handled as security incidents under `docs/security/incident-response.md`.

Report date: 2026-07-14
