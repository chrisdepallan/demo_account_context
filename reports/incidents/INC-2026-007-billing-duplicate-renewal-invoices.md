# INC-2026-007: Renewal invoices issued twice for a subset of accounts

## Summary

Incident **INC-2026-007** was a **SEV3** incident in the Billing service (`services/billing/README.md`). It started on **2026-05-13 15:41 UTC** and lasted **62 minutes**. Affected regions: `eu-central`. Owning team: Revenue Engineering (`#team-billing`).

## Impact

- About **504 accounts** were affected during INC-2026-007.
- Customer Support received **14 tickets** linked to INC-2026-007.
- Severity: **SEV3**. Duration: **62 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-05-13 15:41 | Problem began |
| 2026-05-13 15:48 | Detected, 7 minutes after the start |
| 2026-05-13 15:50 | Incident INC-2026-007 declared in `#team-billing` |
| 2026-05-13 16:31 | Mitigation in place, customer impact ended |
| 2026-05-13 16:43 | Incident resolved and monitoring confirmed normal |

## Root cause

The renewal batch timed out part-way through and was retried without an idempotency key. Accounts processed before the timeout were invoiced a second time.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-007 was **7 minutes**.

## Resolution

The duplicate invoices were voided and every duplicate charge was refunded in full, as required by `services/billing/docs/refunds.md`.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Require an idempotency key on every renewal write | Revenue Engineering | 2026-06-07 | Done |
| Add a reconciliation check for more than one renewal invoice per account per cycle | Revenue Engineering | 2026-05-31 | Done |
| Add a dashboard panel that shows this condition directly | Revenue Engineering | 2026-06-09 | Done |

## Lessons learned

- Customers were told through the status page later than the internal target of 15 minutes.
- A test covering this case existed but was skipped as flaky.

Report date: 2026-05-18
