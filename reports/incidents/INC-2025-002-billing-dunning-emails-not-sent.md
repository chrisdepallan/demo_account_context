# INC-2025-002: Failed-payment reminder emails were not sent

## Summary

Incident **INC-2025-002** was a **SEV2** incident in the Billing service (`services/billing/README.md`). It started on **2025-10-12 16:01 UTC** and lasted **79 minutes**. Affected regions: `us-east`, `ap-south`. Owning team: Revenue Engineering (`#team-billing`).

## Impact

- About **352 accounts** were affected during INC-2025-002.
- Customer Support received **12 tickets** linked to INC-2025-002.
- Severity: **SEV2**. Duration: **79 minutes**. Regions: `us-east`, `ap-south`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2025-10-12 16:01 | Problem began |
| 2025-10-12 16:04 | Detected, 3 minutes after the start |
| 2025-10-12 16:06 | Incident INC-2025-002 declared in `#team-billing` |
| 2025-10-12 17:04 | Mitigation in place, customer impact ended |
| 2025-10-12 17:20 | Incident resolved and monitoring confirmed normal |

## Root cause

A new field was added to the payment-failed event. The dunning scheduler rejected the unknown field and dropped the events, so reminder emails were not scheduled.

## Detection

A synthetic check failed in us-east and paged the on-call engineer. Time to detect for INC-2025-002 was **3 minutes**.

## Resolution

The scheduler was patched to ignore unknown fields and the dropped events were replayed.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Make all event consumers tolerate unknown fields | Revenue Engineering | 2025-11-06 | Done |
| Alert when dunning email volume falls below half of the weekly average | Revenue Engineering | 2025-11-08 | Done |
| Add this failure mode to the Billing service runbook | Revenue Engineering | 2025-11-13 | Done |

## Lessons learned

- The dependency was assumed to be reliable and had no timeout or fallback.
- Rollback was fast because the release was small. Small releases should stay the norm.

Report date: 2025-10-17
