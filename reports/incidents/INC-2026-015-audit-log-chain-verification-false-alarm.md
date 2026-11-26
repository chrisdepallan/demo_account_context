# INC-2026-015: Hash-chain verification raised a false alarm

## Summary

Incident **INC-2026-015** was a **SEV2** incident in the Audit Log service (`services/audit-log/README.md`). It started on **2026-06-22 06:33 UTC** and lasted **63 minutes**. Affected regions: `eu-central`. Owning team: Trust and Compliance (`#team-trust`).

## Impact

- About **2,680 accounts** were affected during INC-2026-015.
- Customer Support received **36 tickets** linked to INC-2026-015.
- Severity: **SEV2**. Duration: **63 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-06-22 06:33 | Problem began |
| 2026-06-22 06:40 | Detected, 7 minutes after the start |
| 2026-06-22 06:42 | Incident INC-2026-015 declared in `#team-trust` |
| 2026-06-22 07:23 | Mitigation in place, customer impact ended |
| 2026-06-22 07:36 | Incident resolved and monitoring confirmed normal |

## Root cause

The nightly verification job read from a replica that was behind the primary. It saw an incomplete chain and reported tampering that had not happened.

## Detection

An engineer on Trust and Compliance noticed the problem on the service dashboard. Time to detect for INC-2026-015 was **7 minutes**.

## Resolution

Verification was pointed at the primary and re-run, and the chain was confirmed intact.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Verify the chain only against a fully caught-up source | Trust and Compliance | 2026-07-13 | Done |
| Separate replica-lag alerts from integrity alerts | Trust and Compliance | 2026-07-22 | Done |
| Add this failure mode to the Audit Log service runbook | Trust and Compliance | 2026-08-03 | Done |

## Lessons learned

- The on-call engineer did not have the access needed for the first mitigation step.
- The alert fired on a symptom, not the cause, which slowed diagnosis.

Report date: 2026-06-27
