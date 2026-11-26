# INC-2026-005: Live chat unavailable during business hours

## Summary

Incident **INC-2026-005** was a **SEV2** incident in the Support service (`services/support/README.md`). It started on **2026-04-22 10:10 UTC** and lasted **67 minutes**. Affected regions: `us-east`. Owning team: Customer Support (`#support-escalations`).

## Impact

- About **2,288 accounts** were affected during INC-2026-005.
- Customer Support received **0 tickets** linked to INC-2026-005.
- Severity: **SEV2**. Duration: **67 minutes**. Regions: `us-east`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-04-22 10:10 | Problem began |
| 2026-04-22 10:15 | Detected, 5 minutes after the start |
| 2026-04-22 10:17 | Incident INC-2026-005 declared in `#support-escalations` |
| 2026-04-22 11:04 | Mitigation in place, customer impact ended |
| 2026-04-22 11:17 | Incident resolved and monitoring confirmed normal |

## Root cause

The chat widget configuration was published with an empty availability schedule, so the widget showed as offline for all customers.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-005 was **5 minutes**.

## Resolution

The previous configuration was restored and the schedule was re-published.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Validate the availability schedule before a chat configuration can be published | Customer Support | 2026-05-09 | Done |
| Add a synthetic check that opens a chat every 5 minutes in business hours | Customer Support | 2026-05-22 | Done |
| Review alert thresholds for the Support service | Customer Support | 2026-05-26 | Done |

## Lessons learned

- A test covering this case existed but was skipped as flaky.
- The alert fired on a symptom, not the cause, which slowed diagnosis.

Report date: 2026-04-27
