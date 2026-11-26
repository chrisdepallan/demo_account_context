# INC-2026-014: Healthy webhook endpoints disabled in error

## Summary

Incident **INC-2026-014** was a **SEV4** incident in the Webhooks service (`services/webhooks/README.md`). It started on **2026-06-21 15:31 UTC** and lasted **43 minutes**. Affected regions: `eu-central`. Owning team: Developer Platform (`#team-developer-platform`).

## Impact

- About **89 accounts** were affected during INC-2026-014.
- Customer Support received **11 tickets** linked to INC-2026-014.
- Severity: **SEV4**. Duration: **43 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-06-21 15:31 | Problem began |
| 2026-06-21 15:51 | Detected, 20 minutes after the start |
| 2026-06-21 15:53 | Incident INC-2026-014 declared in `#team-developer-platform` |
| 2026-06-21 16:05 | Mitigation in place, customer impact ended |
| 2026-06-21 16:14 | Incident resolved and monitoring confirmed normal |

## Root cause

A network fault between one region and the internet made deliveries fail for reasons unrelated to the endpoints. The failure counter still counted them and disabled healthy endpoints.

## Detection

An engineer on Developer Platform noticed the problem on the service dashboard. Time to detect for INC-2026-014 was **20 minutes**.

## Resolution

The affected endpoints were re-enabled and missed events were redelivered.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Do not count failures towards disabling when the failure rate is region-wide | Developer Platform | 2026-07-14 | Done |
| Notify the account Owner before an endpoint is disabled | Developer Platform | 2026-07-15 | Done |
| Review alert thresholds for the Webhooks service | Developer Platform | 2026-07-26 | Done |

## Lessons learned

- Customers were told through the status page later than the internal target of 15 minutes.
- The on-call engineer did not have the access needed for the first mitigation step.

Report date: 2026-06-26
