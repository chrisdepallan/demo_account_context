# INC-2026-001: P1 tickets routed to the general queue

## Summary

Incident **INC-2026-001** was a **SEV3** incident in the Support service (`services/support/README.md`). It started on **2026-02-01 18:54 UTC** and lasted **78 minutes**. Affected regions: `eu-central`. Owning team: Customer Support (`#support-escalations`).

## Impact

- About **724 accounts** were affected during INC-2026-001.
- Customer Support received **0 tickets** linked to INC-2026-001.
- Severity: **SEV3**. Duration: **78 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-02-01 18:54 | Problem began |
| 2026-02-01 19:11 | Detected, 17 minutes after the start |
| 2026-02-01 19:13 | Incident INC-2026-001 declared in `#support-escalations` |
| 2026-02-01 19:56 | Mitigation in place, customer impact ended |
| 2026-02-01 20:12 | Incident resolved and monitoring confirmed normal |

## Root cause

A change to the routing rules matched on plan before priority. P1 tickets from Business and Enterprise accounts landed in the general queue instead of the urgent queue.

## Detection

An automated alert paged the on-call engineer for Customer Support. Time to detect for INC-2026-001 was **17 minutes**.

## Resolution

The rule order was corrected and the misrouted tickets were moved and answered.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Add routing tests for every plan and priority combination | Customer Support | 2026-03-10 | Done |
| Alert when a P1 ticket waits more than 15 minutes without an owner | Customer Support | 2026-02-20 | Done |
| Run a game day that reproduces this failure | Customer Support | 2026-02-27 | Done |

## Lessons learned

- Rollback was fast because the release was small. Small releases should stay the norm.
- The alert fired on a symptom, not the cause, which slowed diagnosis.

Report date: 2026-02-06
