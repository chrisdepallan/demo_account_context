# INC-2026-004: Search results lagged behind recent changes

## Summary

Incident **INC-2026-004** was a **SEV3** incident in the Search service (`services/search/README.md`). It started on **2026-03-06 13:44 UTC** and lasted **71 minutes**. Affected regions: `eu-central`. Owning team: Search and Discovery (`#team-search`).

## Impact

- About **700 accounts** were affected during INC-2026-004.
- Customer Support received **16 tickets** linked to INC-2026-004.
- Severity: **SEV3**. Duration: **71 minutes**. Regions: `eu-central`.

## Timeline (UTC)

| Time | Event |
|------|------|
| 2026-03-06 13:44 | Problem began |
| 2026-03-06 14:04 | Detected, 20 minutes after the start |
| 2026-03-06 14:06 | Incident INC-2026-004 declared in `#team-search` |
| 2026-03-06 14:41 | Mitigation in place, customer impact ended |
| 2026-03-06 14:55 | Incident resolved and monitoring confirmed normal |

## Root cause

The indexing consumer fell behind after a bulk import produced a burst of change events. New and edited items took much longer than normal to appear in search.

## Detection

Customer Support saw a rise in tickets and escalated in `#support-escalations`. Time to detect for INC-2026-004 was **20 minutes**.

## Resolution

Indexing workers were scaled up and bulk-import events were moved to a lower-priority lane.

## Action items

| Action | Owner | Due | Status |
|------|------|------|------|
| Scale indexing workers automatically on consumer lag | Search and Discovery | 2026-04-02 | Done |
| Index bulk imports on a separate, lower-priority lane | Search and Discovery | 2026-04-03 | Done |
| Add a dashboard panel that shows this condition directly | Search and Discovery | 2026-04-05 | Done |

## Lessons learned

- The on-call engineer did not have the access needed for the first mitigation step.
- The alert fired on a symptom, not the cause, which slowed diagnosis.

Report date: 2026-03-11
