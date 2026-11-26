# INC-2026-013: First-response timers ignored business hours

## Summary

Incident **INC-2026-013** was a **SEV3** incident in the Support service (`services/support/README.md`). It started on **2026-06-20 17:08 UTC** and lasted **36 minutes**. Affected regions: `eu-central`, `ap-south`. Owning team: Customer Support (`#support-escalations`).

## Impact

- About **674 accounts** were affected during INC-2026-013.
- Customer Support received **18 tickets** linked to INC-2026-013.
- Severity: **SEV3**. Duration: **36 minutes**. Regions: `eu-central`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-06-20 17:08 | Problem began |
| 2026-06-20 17:12 | Detected, 4 minutes after the start |
| 2026-06-20 17:14 | Incident INC-2026-013 declared in `#support-escalations` |
| 2026-06-20 17:37 | Mitigation in place, customer impact ended |
| 2026-06-20 17:44 | Incident resolved and monitoring confirmed normal |

## Root cause

A time zone library update changed how the business-hours calendar was read. Timers counted nights and weekends, so tickets showed as breaching their target early.

## Detection

A synthetic check failed in eu-central and paged the on-call engineer. Time to detect for INC-2026-013 was **4 minutes**.

## Resolution

The calendar loader was fixed and the timers were recalculated for all open tickets.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Pin the time zone data version used by the timer service | Customer Support | 2026-07-08 | Done |
| Add tests for timers that cross a weekend and a daylight-saving change | Customer Support | 2026-07-17 | Done |
| Review alert thresholds for the Support service | Customer Support | 2026-07-31 | Done |

## Lessons learned

- The same class of problem had happened before in another service and the fix was not shared.
- Dashboards showed averages, which hid the affected minority of accounts.

Report date: 2026-06-25
