# INC-2026-006: Stale plan limits blocked upgrades from taking effect

## Summary

Incident **INC-2026-006** was a **SEV2** incident in the Accounts service (`services/accounts/README.md`). It started on **2026-05-06 17:22 UTC** and lasted **48 minutes**. Affected regions: `eu-central`. Owning team: Accounts Platform (`#team-accounts`).

## Impact

- About **968 accounts** were affected during INC-2026-006.
- Customer Support received **12 tickets** linked to INC-2026-006.
- Severity: **SEV2**. Duration: **48 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-05-06 17:22 | Problem began |
| 2026-05-06 17:37 | Detected, 15 minutes after the start |
| 2026-05-06 17:39 | Incident INC-2026-006 declared in `#team-accounts` |
| 2026-05-06 18:00 | Mitigation in place, customer impact ended |
| 2026-05-06 18:10 | Incident resolved and monitoring confirmed normal |

## Root cause

Plan limits were cached per account and the cache was not invalidated when a plan-change event arrived out of order. Upgraded accounts kept their old limits until the cache expired.

## Detection

An engineer on Accounts Platform noticed the problem on the service dashboard. Time to detect for INC-2026-006 was **15 minutes**.

## Resolution

The cache was flushed for the affected accounts and the consumer was patched to invalidate on every plan-change event.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Invalidate the plan-limit cache on every plan-change event regardless of order | Accounts Platform | 2026-06-12 | Done |
| Add a dashboard comparing cached limits against the database | Accounts Platform | 2026-06-20 | Done |
| Run a game day that reproduces this failure | Accounts Platform | 2026-06-17 | Done |

## Lessons learned

- The alert fired on a symptom, not the cause, which slowed diagnosis.
- Customers were told through the status page later than the internal target of 15 minutes.

Report date: 2026-05-11
