# INC-2026-012: Notification emails delayed

## Summary

Incident **INC-2026-012** was a **SEV3** incident in the Notifications service (`services/notifications/README.md`). It started on **2026-06-20 15:06 UTC** and lasted **73 minutes**. Affected regions: `ap-south`. Owning team: Messaging (`#team-notifications`).

## Impact

- About **462 accounts** were affected during INC-2026-012.
- Customer Support received **8 tickets** linked to INC-2026-012.
- Severity: **SEV3**. Duration: **73 minutes**. Regions: `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-06-20 15:06 | Problem began |
| 2026-06-20 15:10 | Detected, 4 minutes after the start |
| 2026-06-20 15:12 | Incident INC-2026-012 declared in `#team-notifications` |
| 2026-06-20 16:04 | Mitigation in place, customer impact ended |
| 2026-06-20 16:19 | Incident resolved and monitoring confirmed normal |

## Root cause

The email provider throttled sending after a burst of digest emails. The send queue grew faster than it drained and transactional emails waited behind digests.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-012 was **4 minutes**.

## Resolution

Digest sending was paused, transactional emails were given their own queue, and the backlog cleared.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Keep transactional and digest emails on separate queues | Messaging | 2026-07-26 | Done |
| Spread digest sending over a longer window | Messaging | 2026-07-05 | Done |
| Add this failure mode to the Notifications service runbook | Messaging | 2026-08-01 | Done |

## Lessons learned

- The alert fired on a symptom, not the cause, which slowed diagnosis.
- Customers were told through the status page later than the internal target of 15 minutes.

Report date: 2026-06-25
