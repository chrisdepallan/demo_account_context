# INC-2025-005: Healthy webhook endpoints disabled in error

## Summary

Incident **INC-2025-005** was a **SEV3** incident in the Webhooks service (`services/webhooks/README.md`). It started on **2025-12-25 07:38 UTC** and lasted **86 minutes**. Affected regions: `eu-central`. Owning team: Developer Platform (`#team-developer-platform`).

## Impact

- About **574 accounts** were affected during INC-2025-005.
- Customer Support received **16 tickets** linked to INC-2025-005.
- Severity: **SEV3**. Duration: **86 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2025-12-25 07:38 | Problem began |
| 2025-12-25 07:55 | Detected, 17 minutes after the start |
| 2025-12-25 07:57 | Incident INC-2025-005 declared in `#team-developer-platform` |
| 2025-12-25 08:47 | Mitigation in place, customer impact ended |
| 2025-12-25 09:04 | Incident resolved and monitoring confirmed normal |

## Root cause

A network fault between one region and the internet made deliveries fail for reasons unrelated to the endpoints. The failure counter still counted them and disabled healthy endpoints.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2025-005 was **17 minutes**.

## Resolution

The affected endpoints were re-enabled and missed events were redelivered.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Do not count failures towards disabling when the failure rate is region-wide | Developer Platform | 2026-01-23 | Done |
| Notify the account Owner before an endpoint is disabled | Developer Platform | 2026-01-08 | Done |
| Run a game day that reproduces this failure | Developer Platform | 2026-02-02 | Done |

## Lessons learned

- Rollback was fast because the release was small. Small releases should stay the norm.
- The on-call engineer did not have the access needed for the first mitigation step.

Report date: 2025-12-30
