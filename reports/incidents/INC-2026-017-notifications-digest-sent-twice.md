# INC-2026-017: Daily digest sent twice

## Summary

Incident **INC-2026-017** was a **SEV3** incident in the Notifications service (`services/notifications/README.md`). It started on **2026-08-07 08:36 UTC** and lasted **75 minutes**. Affected regions: `us-east`. Owning team: Messaging (`#team-notifications`).

## Impact

- About **598 accounts** were affected during INC-2026-017.
- Customer Support received **18 tickets** linked to INC-2026-017.
- Severity: **SEV3**. Duration: **75 minutes**. Regions: `us-east`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-08-07 08:36 | Problem began |
| 2026-08-07 08:45 | Detected, 9 minutes after the start |
| 2026-08-07 08:47 | Incident INC-2026-017 declared in `#team-notifications` |
| 2026-08-07 09:36 | Mitigation in place, customer impact ended |
| 2026-08-07 09:51 | Incident resolved and monitoring confirmed normal |

## Root cause

The digest scheduler ran on two pods during a deployment because leader election had not completed. Both pods sent the same digest.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-017 was **9 minutes**.

## Resolution

Leader election was fixed to complete before the scheduler starts.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Record sent digests and refuse to send the same digest twice | Messaging | 2026-09-17 | Done |
| Start the scheduler only after leader election completes | Messaging | 2026-09-20 | Done |
| Add a dashboard panel that shows this condition directly | Messaging | 2026-09-13 | Done |

## Lessons learned

- Customers were told through the status page later than the internal target of 15 minutes.
- Dashboards showed averages, which hid the affected minority of accounts.

Report date: 2026-08-12
