# INC-2026-018: SSO sign-ins rejected because of clock skew

## Summary

Incident **INC-2026-018** was a **SEV3** incident in the Auth service (`services/auth/README.md`). It started on **2026-09-02 07:29 UTC** and lasted **75 minutes**. Affected regions: `ap-south`. Owning team: Identity (`#team-identity`).

## Impact

- About **138 accounts** were affected during INC-2026-018.
- Customer Support received **16 tickets** linked to INC-2026-018.
- Severity: **SEV3**. Duration: **75 minutes**. Regions: `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-09-02 07:29 | Problem began |
| 2026-09-02 07:50 | Detected, 21 minutes after the start |
| 2026-09-02 07:52 | Incident INC-2026-018 declared in `#team-identity` |
| 2026-09-02 08:29 | Mitigation in place, customer impact ended |
| 2026-09-02 08:44 | Incident resolved and monitoring confirmed normal |

## Root cause

Time synchronisation failed on two Auth pods, so their clocks drifted by more than the allowed tolerance. Valid SAML assertions looked expired and were rejected.

## Detection

A synthetic check failed in ap-south and paged the on-call engineer. Time to detect for INC-2026-018 was **21 minutes**.

## Resolution

The two pods were replaced and time synchronisation was restored.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Alert when pod clock drift exceeds 5 seconds | Identity | 2026-09-22 | Done |
| Fail the readiness probe when time synchronisation is unhealthy | Identity | 2026-09-24 | Done |
| Add a dashboard panel that shows this condition directly | Identity | 2026-09-24 | Done |

## Lessons learned

- Dashboards showed averages, which hid the affected minority of accounts.
- The dependency was assumed to be reliable and had no timeout or fallback.

Report date: 2026-09-07
