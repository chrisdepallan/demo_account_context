# INC-2026-019: Gap in SIEM streaming

## Summary

Incident **INC-2026-019** was a **SEV4** incident in the Audit Log service (`services/audit-log/README.md`). It started on **2026-09-19 00:49 UTC** and lasted **40 minutes**. Affected regions: `us-east`. Owning team: Trust and Compliance (`#team-trust`).

## Impact

- About **168 accounts** were affected during INC-2026-019.
- Customer Support received **2 tickets** linked to INC-2026-019.
- Severity: **SEV4**. Duration: **40 minutes**. Regions: `us-east`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-09-19 00:49 | Problem began |
| 2026-09-19 01:02 | Detected, 13 minutes after the start |
| 2026-09-19 01:04 | Incident INC-2026-019 declared in `#team-trust` |
| 2026-09-19 01:21 | Mitigation in place, customer impact ended |
| 2026-09-19 01:29 | Incident resolved and monitoring confirmed normal |

## Root cause

The streaming worker lost its position after a restart and resumed from the newest entry. Entries written while it was down were not streamed.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-019 was **13 minutes**.

## Resolution

The worker position was restored from the last acknowledged entry and the missing entries were replayed.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Persist the stream position after every acknowledged batch | Trust and Compliance | 2026-10-16 | Done |
| Alert on any gap in streamed entry sequence numbers | Trust and Compliance | 2026-10-08 | Done |
| Run a game day that reproduces this failure | Trust and Compliance | 2026-10-20 | Done |

## Lessons learned

- The same class of problem had happened before in another service and the fix was not shared.
- A test covering this case existed but was skipped as flaky.

Report date: 2026-09-24
