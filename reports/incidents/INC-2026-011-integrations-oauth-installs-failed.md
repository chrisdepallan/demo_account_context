# INC-2026-011: New integration installs failed at the consent step

## Summary

Incident **INC-2026-011** was a **SEV2** incident in the Integrations service (`services/integrations/README.md`). It started on **2026-06-08 14:20 UTC** and lasted **92 minutes**. Affected regions: `ap-south`. Owning team: Ecosystem (`#team-ecosystem`).

## Impact

- About **1,648 accounts** were affected during INC-2026-011.
- Customer Support received **28 tickets** linked to INC-2026-011.
- Severity: **SEV2**. Duration: **92 minutes**. Regions: `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-06-08 14:20 | Problem began |
| 2026-06-08 14:38 | Detected, 18 minutes after the start |
| 2026-06-08 14:40 | Incident INC-2026-011 declared in `#team-ecosystem` |
| 2026-06-08 15:34 | Mitigation in place, customer impact ended |
| 2026-06-08 15:52 | Incident resolved and monitoring confirmed normal |

## Root cause

A redirect address was changed in configuration for one region but not registered with the provider. Installs started in that region failed at consent.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-011 was **18 minutes**.

## Resolution

The address was registered and the configuration was made consistent across regions.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Check redirect addresses against the provider registration in CI | Ecosystem | 2026-07-20 | Done |
| Add a synthetic install test in every region | Ecosystem | 2026-07-03 | Done |
| Add this failure mode to the Integrations service runbook | Ecosystem | 2026-06-22 | Done |

## Lessons learned

- The on-call engineer did not have the access needed for the first mitigation step.
- Customers were told through the status page later than the internal target of 15 minutes.

Report date: 2026-06-13
