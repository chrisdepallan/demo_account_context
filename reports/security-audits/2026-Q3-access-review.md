# Security and Access Review 2026-Q3

## Scope

The **2026-Q3** security and access review covered production access for all 12 services, service accounts, break-glass use, dependency scanning and secret scanning. The review is run by Trust and Compliance (`#team-trust`) every 90 days, as required by `docs/security/access-control.md`.

## Findings in 2026-Q3

The 2026-Q3 review raised **5 findings**, of which **1** were High severity.

| Finding | Severity | Service | Description | Due | Status |
|------|------|------|------|------|------|
| FND-2026-Q3-01 | Low | `files` | Log line included a full request path with an account ID in debug mode | 2027-04-12 | Open |
| FND-2026-Q3-02 | High | `integrations` | Internal endpoint reachable without the gateway's authentication check | 2026-11-13 | Closed |
| FND-2026-Q3-03 | Medium | `search` | Service account with write access that was not used in 90 days | 2027-01-12 | Open |
| FND-2026-Q3-04 | Medium | `search` | Production database role granted to an engineer who changed teams | 2027-01-12 | Open |
| FND-2026-Q3-05 | Low | `files` | Dependency two minor versions behind the latest patched release | 2027-04-12 | Open |

## Access review results for 2026-Q3

- **449 access grants** were reviewed by the owning team's manager.
- **13 grants** were removed because they were no longer needed.
- Break-glass access was used **0 times** in 2026-Q3.

## Dependency and secret scanning in 2026-Q3

- Secret scanning found **0 committed secrets** in 2026-Q3.
- Dependency scanning reported **10 outdated packages** in build and tooling images. Service code uses the Python standard library only.

## Remediation deadlines

Findings must be fixed within **30 days** for High severity, **90 days** for Medium and **180 days** for Low, counted from the report date. Critical findings are handled as security incidents under `docs/security/incident-response.md`.

Report date: 2026-10-14
