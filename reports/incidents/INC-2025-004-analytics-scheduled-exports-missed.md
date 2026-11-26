# INC-2025-004: Scheduled exports were not sent

## Summary

Incident **INC-2025-004** was a **SEV2** incident in the Analytics service (`services/analytics/README.md`). It started on **2025-11-20 22:07 UTC** and lasted **38 minutes**. Affected regions: `us-east`, `ap-south`. Owning team: Data Platform (`#team-data`).

## Impact

- About **2,536 accounts** were affected during INC-2025-004.
- Customer Support received **0 tickets** linked to INC-2025-004.
- Severity: **SEV2**. Duration: **38 minutes**. Regions: `us-east`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2025-11-20 22:07 | Problem began |
| 2025-11-20 22:17 | Detected, 10 minutes after the start |
| 2025-11-20 22:19 | Incident INC-2025-004 declared in `#team-data` |
| 2025-11-20 22:37 | Mitigation in place, customer impact ended |
| 2025-11-20 22:45 | Incident resolved and monitoring confirmed normal |

## Root cause

The export scheduler calculated the next run in local time. After a daylight-saving change, some weekly exports were skipped.

## Detection

An engineer on Data Platform noticed the problem on the service dashboard. Time to detect for INC-2025-004 was **10 minutes**.

## Resolution

Next-run calculation was moved to UTC and the missed exports were sent.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Calculate all schedules in UTC | Data Platform | 2025-12-07 | Done |
| Alert when an export is more than 1 hour late | Data Platform | 2025-12-10 | Done |
| Review alert thresholds for the Analytics service | Data Platform | 2025-12-19 | Done |

## Lessons learned

- Customers were told through the status page later than the internal target of 15 minutes.
- The alert fired on a symptom, not the cause, which slowed diagnosis.

Report date: 2025-11-25
