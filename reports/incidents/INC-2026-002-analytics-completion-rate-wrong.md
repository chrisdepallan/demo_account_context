# INC-2026-002: Task completion rate miscalculated for archived projects

## Summary

Incident **INC-2026-002** was a **SEV3** incident in the Analytics service (`services/analytics/README.md`). It started on **2026-02-17 15:39 UTC** and lasted **42 minutes**. Affected regions: `us-east`, `ap-south`. Owning team: Data Platform (`#team-data`).

## Impact

- About **364 accounts** were affected during INC-2026-002.
- Customer Support received **10 tickets** linked to INC-2026-002.
- Severity: **SEV3**. Duration: **42 minutes**. Regions: `us-east`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-02-17 15:39 | Problem began |
| 2026-02-17 15:54 | Detected, 15 minutes after the start |
| 2026-02-17 15:56 | Incident INC-2026-002 declared in `#team-data` |
| 2026-02-17 16:13 | Mitigation in place, customer impact ended |
| 2026-02-17 16:21 | Incident resolved and monitoring confirmed normal |

## Root cause

Archived projects were excluded from completed tasks but not from total tasks. Accounts with archived projects saw a completion rate lower than the real one.

## Detection

A synthetic check failed in us-east and paged the on-call engineer. Time to detect for INC-2026-002 was **15 minutes**.

## Resolution

The metric was corrected to exclude archived projects from both counts and history was recalculated.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Add metric tests that include archived projects | Data Platform | 2026-03-22 | Done |
| Review every metric definition for consistent filters | Data Platform | 2026-03-11 | Done |
| Run a game day that reproduces this failure | Data Platform | 2026-03-12 | Done |

## Lessons learned

- A test covering this case existed but was skipped as flaky.
- Dashboards showed averages, which hid the affected minority of accounts.

Report date: 2026-02-22
