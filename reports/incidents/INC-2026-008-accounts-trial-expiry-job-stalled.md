# INC-2026-008: Trial expiry job stalled and accounts stayed in trialing

## Summary

Incident **INC-2026-008** was a **SEV2** incident in the Accounts service (`services/accounts/README.md`). It started on **2026-05-26 03:19 UTC** and lasted **74 minutes**. Affected regions: `eu-central`. Owning team: Accounts Platform (`#team-accounts`).

## Impact

- About **1,896 accounts** were affected during INC-2026-008.
- Customer Support received **40 tickets** linked to INC-2026-008.
- Severity: **SEV2**. Duration: **74 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-05-26 03:19 | Problem began |
| 2026-05-26 03:22 | Detected, 3 minutes after the start |
| 2026-05-26 03:24 | Incident INC-2026-008 declared in `#team-accounts` |
| 2026-05-26 04:18 | Mitigation in place, customer impact ended |
| 2026-05-26 04:33 | Incident resolved and monitoring confirmed normal |

## Root cause

The nightly trial-expiry job held a database lock while a schema migration ran. The job timed out and exited without retrying, so accounts whose trial had ended were not moved out of the `trialing` state.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-008 was **3 minutes**.

## Resolution

The migration was completed, the job was re-run by hand, and every affected account was moved to the correct state.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Alert when the trial-expiry job has not completed within 26 hours | Accounts Platform | 2026-07-06 | Done |
| Make the trial-expiry job resume from a checkpoint instead of starting over | Accounts Platform | 2026-07-08 | Done |
| Add this failure mode to the Accounts service runbook | Accounts Platform | 2026-06-15 | Done |

## Lessons learned

- Dashboards showed averages, which hid the affected minority of accounts.
- The dependency was assumed to be reliable and had no timeout or fallback.

Report date: 2026-05-31
