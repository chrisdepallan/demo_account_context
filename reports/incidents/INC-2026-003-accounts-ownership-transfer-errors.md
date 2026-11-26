# INC-2026-003: Ownership transfers failed with a server error

## Summary

Incident **INC-2026-003** was a **SEV3** incident in the Accounts service (`services/accounts/README.md`). It started on **2026-02-18 20:38 UTC** and lasted **89 minutes**. Affected regions: `us-east`, `ap-south`. Owning team: Accounts Platform (`#team-accounts`).

## Impact

- About **566 accounts** were affected during INC-2026-003.
- Customer Support received **14 tickets** linked to INC-2026-003.
- Severity: **SEV3**. Duration: **89 minutes**. Regions: `us-east`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-02-18 20:38 | Problem began |
| 2026-02-18 20:41 | Detected, 3 minutes after the start |
| 2026-02-18 20:43 | Incident INC-2026-003 declared in `#team-accounts` |
| 2026-02-18 21:49 | Mitigation in place, customer impact ended |
| 2026-02-18 22:07 | Incident resolved and monitoring confirmed normal |

## Root cause

A release switched the role-permission lookup to a cached copy that did not include the pending-owner state. Every transfer request failed the permission check and returned a 500 response.

## Detection

An automated alert paged the on-call engineer for Accounts Platform. Time to detect for INC-2026-003 was **3 minutes**.

## Resolution

The release was rolled back and the cache was rebuilt with the pending-owner state included.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Add an end-to-end test for ownership transfer to the release checks | Accounts Platform | 2026-03-19 | Done |
| Version the role-permission cache so stale copies are rejected | Accounts Platform | 2026-03-04 | Done |
| Add this failure mode to the Accounts service runbook | Accounts Platform | 2026-03-26 | Done |

## Lessons learned

- The dependency was assumed to be reliable and had no timeout or fallback.
- A test covering this case existed but was skipped as flaky.

Report date: 2026-02-23
