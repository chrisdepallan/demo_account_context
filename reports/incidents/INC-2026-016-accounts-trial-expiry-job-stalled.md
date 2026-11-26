# INC-2026-016: Trial expiry job stalled and accounts stayed in trialing

## Summary

Incident **INC-2026-016** was a **SEV2** incident in the Accounts service (`services/accounts/README.md`). It started on **2026-07-18 17:20 UTC** and lasted **53 minutes**. Affected regions: `us-east`, `ap-south`. Owning team: Accounts Platform (`#team-accounts`).

## Impact

- About **3,192 accounts** were affected during INC-2026-016.
- Customer Support received **28 tickets** linked to INC-2026-016.
- Severity: **SEV2**. Duration: **53 minutes**. Regions: `us-east`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-07-18 17:20 | Problem began |
| 2026-07-18 17:30 | Detected, 10 minutes after the start |
| 2026-07-18 17:32 | Incident INC-2026-016 declared in `#team-accounts` |
| 2026-07-18 18:02 | Mitigation in place, customer impact ended |
| 2026-07-18 18:13 | Incident resolved and monitoring confirmed normal |

## Root cause

The nightly trial-expiry job held a database lock while a schema migration ran. The job timed out and exited without retrying, so accounts whose trial had ended were not moved out of the `trialing` state.

## Detection

An engineer on Accounts Platform noticed the problem on the service dashboard. Time to detect for INC-2026-016 was **10 minutes**.

## Resolution

The migration was completed, the job was re-run by hand, and every affected account was moved to the correct state.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Alert when the trial-expiry job has not completed within 26 hours | Accounts Platform | 2026-08-31 | Done |
| Make the trial-expiry job resume from a checkpoint instead of starting over | Accounts Platform | 2026-08-18 | Done |
| Add this failure mode to the Accounts service runbook | Accounts Platform | 2026-08-28 | Done |

## Lessons learned

- Dashboards showed averages, which hid the affected minority of accounts.
- Customers were told through the status page later than the internal target of 15 minutes.

Report date: 2026-07-23
