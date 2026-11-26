# Runbook – Search Index Lag

## When to use this runbook

Use the search index lag runbook when new or changed projects, tasks and files do not appear in Acme Cloud search results soon after they are saved.

- Alert `SearchIndexLagHigh` – the search index is more than **5 minutes** behind the event bus for **10 minutes**.
- Alert `SearchIndexerConsumerStalled` – the search indexer has processed **0** events for **5 minutes** while events are waiting.
- Customers report that a task or file they just created cannot be found by search.

The search index lag runbook is owned by Team Search and Discovery. The Search service is described in `services/search/README.md`.

## Impact

Search index lag makes search results stale. Customers can still open projects, tasks and files directly, so no data is lost and no data is unavailable. Deleted items and items whose sharing was removed can stay visible in results for longer than normal, although opening such an item is still blocked by permission checks.

Search index lag is **SEV3** below **1 hour** of lag and **SEV2** from **1 hour** of lag.

## Diagnosis

1. Check that the indexer is running.

```bash
kubectl --context prod-us-east -n search get pods -l app=search-indexer
kubectl --context prod-us-east -n search logs deploy/search-indexer --since=15m | tail -n 50
```

2. Read the current lag from the indexer metrics.

```text
search_index_lag_seconds{region="us-east"}      # target: below 60
search_indexer_events_per_second{region="us-east"}
```

3. Look for a poison event. The same event ID (format `evt_8K2M4P6R1S`) repeated in the indexer log with an error means that one event blocks the consumer.

```bash
kubectl --context prod-us-east -n search logs deploy/search-indexer --since=15m | grep "index_failed" | sort | uniq -c | sort -rn | head
```

4. Check whether the lag is caused by volume. A bulk import in the Projects service or a bulk upload in the Files service can produce more events than the indexer handles.
5. Check the health of the search index storage: free disk space and whether the index is read-only.
6. Check whether a Search deployment happened in the last **2 hours**.

## Mitigation

1. If the indexer is stalled, restart the indexer with `kubectl rollout restart deploy/search-indexer`.
2. If a poison event blocks the consumer, move that event to the dead-letter queue and record the event ID. Do not skip more than one event without understanding the cause.
3. If the lag is caused by volume, scale `search-indexer` up. Double the replica count and re-check the lag after **10 minutes**.
4. If a Search deployment caused the lag, roll the deployment back with `kubectl rollout undo deploy/search-indexer`.
5. If the index storage is full or read-only, escalate to Team Platform Infrastructure before doing anything else.
6. Start a full reindex of a workspace only as a last resort and only for the affected workspaces (format `ws_4H8P2L`). A full reindex of all workspaces takes several hours and competes with normal indexing.
7. Confirm recovery when the lag is below **60 seconds** for **15 minutes**.

## Escalation

- Team Search and Discovery, `#team-search` – first responder for both alerts.
- Team Platform Infrastructure, `#team-platform` – event bus or storage problems.
- Team Work Management, `#team-projects`, or Team Storage Platform, `#team-storage` – when one of those services produces the event flood.
- Tell Team Customer Support in `#support-escalations` when the lag passes **30 minutes**.

## After the incident

- Replay the events in the dead-letter queue after the bug that caused them is fixed.
- Spot-check **10** recently changed items to confirm that search results are current.
- Confirm that items deleted during the incident no longer appear in search results.
- For a SEV2 incident, write a postmortem within **5 business days**.

Last reviewed: 2026-11-26
