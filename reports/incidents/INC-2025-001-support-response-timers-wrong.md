# INC-2025-001: First-response timers ignored business hours

## Summary

Incident **INC-2025-001** was a **SEV2** incident in the Support service (`services/support/README.md`). It started on **2025-10-04 08:27 UTC** and lasted **50 minutes**. Affected regions: `us-east`, `ap-south`. Owning team: Customer Support (`#support-escalations`).

## Impact

- About **1,928 accounts** were affected during INC-2025-001.
- Customer Support received **20 tickets** linked to INC-2025-001.
- Severity: **SEV2**. Duration: **50 minutes**. Regions: `us-east`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2025-10-04 08:27 | Problem began |
| 2025-10-04 08:36 | Detected, 9 minutes after the start |
| 2025-10-04 08:38 | Incident INC-2025-001 declared in `#support-escalations` |
| 2025-10-04 09:07 | Mitigation in place, customer impact ended |
| 2025-10-04 09:17 | Incident resolved and monitoring confirmed normal |

## Root cause

A time zone library update changed how the business-hours calendar was read. Timers counted nights and weekends, so tickets showed as breaching their target early.

## Detection

An engineer on Customer Support noticed the problem on the service dashboard. Time to detect for INC-2025-001 was **9 minutes**.

## Resolution

The calendar loader was fixed and the timers were recalculated for all open tickets.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Pin the time zone data version used by the timer service | Customer Support | 2025-11-08 | Done |
| Add tests for timers that cross a weekend and a daylight-saving change | Customer Support | 2025-10-30 | Done |
| Run a game day that reproduces this failure | Customer Support | 2025-11-11 | Done |

## Lessons learned

- A test covering this case existed but was skipped as flaky.
- Customers were told through the status page later than the internal target of 15 minutes.

Report date: 2025-10-09
