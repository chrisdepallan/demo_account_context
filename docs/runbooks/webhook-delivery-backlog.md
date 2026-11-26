# Runbook – Webhook Delivery Backlog

## When to use this runbook

Use the webhook delivery backlog runbook when outbound webhooks are delivered late or not at all.

- Alert `WebhooksDeliveryBacklogHigh` – more than **50,000** deliveries are pending, or the oldest pending delivery is older than **15 minutes**.
- Alert `WebhooksDeliveryFailureRateHigh` – more than **25%** of delivery attempts failed over **15 minutes** across all endpoints.
- Customers report that their integrations receive events late.

The webhook delivery backlog runbook is owned by Team Developer Platform. The Webhooks service, its signing scheme and its retry rules are described in `services/webhooks/README.md`.

## Impact

A webhook delivery backlog delays events for customers who have registered webhook endpoints. Events are not lost while they are queued, but customer automations that depend on the events run late. Data inside Acme Cloud is not affected.

A webhook delivery backlog is **SEV3** while the oldest pending delivery is younger than **1 hour**, and **SEV2** after that.

## Diagnosis

1. Check that the delivery workers are running and see how many replicas exist.

```bash
kubectl --context prod-us-east -n webhooks get deploy webhooks-worker
kubectl --context prod-us-east -n webhooks logs deploy/webhooks-worker --since=15m | tail -n 50
```

2. Measure the backlog and the age of the oldest pending delivery.

```bash
psql "$WEBHOOKS_DB_URL" -h webhooks-db.us-east.internal.acme-cloud.example -c "
  SELECT count(*) AS pending, min(created_at) AS oldest
  FROM deliveries WHERE status = 'pending';"
```

3. Find out whether a few endpoints cause most of the backlog. A slow or failing customer endpoint holds worker time.

```bash
psql "$WEBHOOKS_DB_URL" -h webhooks-db.us-east.internal.acme-cloud.example -c "
  SELECT endpoint_id, count(*) AS pending
  FROM deliveries WHERE status = 'pending'
  GROUP BY endpoint_id ORDER BY pending DESC LIMIT 10;"
```

4. Check whether an upstream service is producing an unusual number of events, for example a bulk import in the Projects service or a bulk upload in the Files service.
5. Check whether the workers can reach the public internet. A network egress problem makes every endpoint fail at once.

The table and column names in the queries are illustrative. Endpoint IDs look like `whk_5T7Y2B9D` and event IDs look like `evt_8K2M4P6R1S`.

## Mitigation

1. If the workers are healthy but too few, scale `webhooks-worker` up. Double the replica count and re-check the backlog after **10 minutes**.
2. If a few endpoints cause most of the backlog, move those endpoints to the slow lane so that deliveries to healthy endpoints are not held up. Do not delete the pending deliveries.
3. If one upstream service floods the event bus, ask the owning team to slow down the bulk job.
4. If a Webhooks deployment caused the backlog, roll the deployment back with `kubectl rollout undo deploy/webhooks-worker`.
5. If network egress is broken, escalate to Team Platform Infrastructure and wait. Scaling the workers does not help.
6. Never disable HMAC signing and never skip retries to drain the backlog faster.
7. Confirm recovery when the oldest pending delivery is younger than **1 minute** for **15 minutes**.

## Escalation

- Team Developer Platform, `#team-developer-platform` – first responder for both alerts.
- Team Platform Infrastructure, `#team-platform` – network egress or event bus problems.
- Team Customer Support, `#support-escalations` – tell Support when the oldest pending delivery is older than **30 minutes**, so that agents can answer tickets.
- Declare an incident in `#incidents` when the backlog reaches **SEV2**.

## After the incident

- Confirm that every queued event was delivered or reached the end of its retry schedule.
- Tell affected customers the start and end time of the delay if the delay was longer than **1 hour**.
- Review the worker autoscaling limits if manual scaling was needed.
- For a SEV2 incident, write a postmortem within **5 business days**.

Last reviewed: 2026-11-26
