# INC-2026-009: Live chat unavailable during business hours

## Summary

Incident **INC-2026-009** was a **SEV3** incident in the Support service (`services/support/README.md`). It started on **2026-05-27 14:06 UTC** and lasted **69 minutes**. Affected regions: `eu-central`. Owning team: Customer Support (`#support-escalations`).

## Impact

- About **46 accounts** were affected during INC-2026-009.
- Customer Support received **20 tickets** linked to INC-2026-009.
- Severity: **SEV3**. Duration: **69 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-05-27 14:06 | Problem began |
| 2026-05-27 14:19 | Detected, 13 minutes after the start |
| 2026-05-27 14:21 | Incident INC-2026-009 declared in `#support-escalations` |
| 2026-05-27 15:01 | Mitigation in place, customer impact ended |
| 2026-05-27 15:15 | Incident resolved and monitoring confirmed normal |

## Root cause

The chat widget configuration was published with an empty availability schedule, so the widget showed as offline for all customers.

## Detection

An automated alert paged the on-call engineer for Customer Support. Time to detect for INC-2026-009 was **13 minutes**.

## Resolution

The previous configuration was restored and the schedule was re-published.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Validate the availability schedule before a chat configuration can be published | Customer Support | 2026-06-30 | Done |
| Add a synthetic check that opens a chat every 5 minutes in business hours | Customer Support | 2026-06-20 | Done |
| Run a game day that reproduces this failure | Customer Support | 2026-06-18 | Done |

## Lessons learned

- Dashboards showed averages, which hid the affected minority of accounts.
- A test covering this case existed but was skipped as flaky.

Report date: 2026-06-01
