# INC-2026-010: Trial expiry job stalled and accounts stayed in trialing

## Summary

Incident **INC-2026-010** was a **SEV4** incident in the Accounts service (`services/accounts/README.md`). It started on **2026-05-30 12:36 UTC** and lasted **45 minutes**. Affected regions: `us-east`, `eu-central`. Owning team: Accounts Platform (`#team-accounts`).

## Impact

- About **26 accounts** were affected during INC-2026-010.
- Customer Support received **5 tickets** linked to INC-2026-010.
- Severity: **SEV4**. Duration: **45 minutes**. Regions: `us-east`, `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-05-30 12:36 | Problem began |
| 2026-05-30 12:57 | Detected, 21 minutes after the start |
| 2026-05-30 12:59 | Incident INC-2026-010 declared in `#team-accounts` |
| 2026-05-30 13:12 | Mitigation in place, customer impact ended |
| 2026-05-30 13:21 | Incident resolved and monitoring confirmed normal |

## Root cause

The nightly trial-expiry job held a database lock while a schema migration ran. The job timed out and exited without retrying, so accounts whose trial had ended were not moved out of the `trialing` state.

## Detection

A synthetic check failed in us-east and paged the on-call engineer. Time to detect for INC-2026-010 was **21 minutes**.

## Resolution

The migration was completed, the job was re-run by hand, and every affected account was moved to the correct state.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Alert when the trial-expiry job has not completed within 26 hours | Accounts Platform | 2026-07-06 | Done |
| Make the trial-expiry job resume from a checkpoint instead of starting over | Accounts Platform | 2026-07-14 | Done |
| Review alert thresholds for the Accounts service | Accounts Platform | 2026-07-05 | Done |

## Lessons learned

- The on-call engineer did not have the access needed for the first mitigation step.
- The same class of problem had happened before in another service and the fix was not shared.

Report date: 2026-06-04
