# INC-2025-003: Valid sharing links returned 403

## Summary

Incident **INC-2025-003** was a **SEV4** incident in the Files service (`services/files/README.md`). It started on **2025-10-24 05:01 UTC** and lasted **37 minutes**. Affected regions: `eu-central`, `ap-south`. Owning team: Storage Platform (`#team-storage`).

## Impact

- About **275 accounts** were affected during INC-2025-003.
- Customer Support received **8 tickets** linked to INC-2025-003.
- Severity: **SEV4**. Duration: **37 minutes**. Regions: `eu-central`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2025-10-24 05:01 | Problem began |
| 2025-10-24 05:03 | Detected, 2 minutes after the start |
| 2025-10-24 05:05 | Incident INC-2025-003 declared in `#team-storage` |
| 2025-10-24 05:31 | Mitigation in place, customer impact ended |
| 2025-10-24 05:38 | Incident resolved and monitoring confirmed normal |

## Root cause

A change to link validation compared expiry times in local time instead of UTC. Links in regions ahead of UTC were treated as expired early.

## Detection

An automated alert paged the on-call engineer for Storage Platform. Time to detect for INC-2025-003 was **2 minutes**.

## Resolution

The comparison was corrected to use UTC and the change was redeployed.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Add link-expiry tests that run in every region's time zone | Storage Platform | 2025-12-07 | Done |
| Lint for time comparisons that do not use UTC | Storage Platform | 2025-11-14 | Done |
| Add this failure mode to the Files service runbook | Storage Platform | 2025-11-21 | Done |

## Lessons learned

- Customers were told through the status page later than the internal target of 15 minutes.
- The same class of problem had happened before in another service and the fix was not shared.

Report date: 2025-10-29
