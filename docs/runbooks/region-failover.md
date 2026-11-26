# Runbook – Region Failover

## When to use this runbook

Use the region failover runbook when one Acme Cloud region (`us-east`, `eu-central` or `ap-south`) cannot serve traffic from its primary availability zone.

- Alert `RegionHealthCheckFailing` – the external health check of a region failed from at least **2** probe locations for **3 minutes**.
- Alert `GatewayRegionErrorRateHigh` – more than **10%** of API gateway responses in one region were HTTP 5xx over **5 minutes**.
- Several services in the same region alert at the same time.

The region failover runbook is owned by Team Platform Infrastructure. A region failover is always decided by the incident commander, never by one engineer alone.

## Impact

A failed region makes every workspace in that region unavailable. Workspaces in the other two regions keep working, because each region runs its own service instances, PostgreSQL databases and object storage. A workspace's region is fixed when the workspace is created, as described in `docs/company-overview.md`.

A region failover moves traffic and database primaries to the standby availability zone inside the same region. Customer data is never moved to another region, so data residency for `eu-central` and `ap-south` is preserved. A failed region is **SEV1**.

## Diagnosis

1. Confirm that the problem is regional and not one service.

```bash
for ctx in prod-us-east prod-eu-central prod-ap-south; do
  echo "== $ctx"; kubectl --context "$ctx" get nodes --no-headers | awk '{print $2}' | sort | uniq -c
done
```

2. Check the health of the primary and standby availability zones in the affected region.

```bash
kubectl --context prod-eu-central get nodes -L topology.kubernetes.io/zone
kubectl --context prod-eu-central get pods -A --field-selector=status.phase!=Running | head -n 40
```

3. Check the replication delay of each database standby. A standby that is more than **5 minutes** behind must not be promoted without a decision from the incident commander.

```bash
psql "$PLATFORM_DB_ADMIN_URL" -h accounts-db-standby.eu-central.internal.acme-cloud.example -c "
  SELECT now() - pg_last_xact_replay_timestamp() AS replication_delay;"
```

4. Check the cloud provider's status page for the affected region.
5. Decide between waiting and failing over. Fail over when the primary zone is not expected to recover within **30 minutes**.

## Mitigation

1. The incident commander announces the failover decision in the incident channel and records the time.
2. Stop writes in the affected region by putting the API gateway for that region into maintenance mode. Customers see a maintenance page instead of errors.
3. Promote the database standby of each of the 12 services in the standby zone. Promote the Auth and Accounts databases first, then Billing, then the remaining services.
4. Scale up the service deployments in the standby zone to the normal replica counts.
5. Point the regional gateway at the standby zone and take the gateway out of maintenance mode.
6. Check login, the API, file download and file upload with a test workspace in the affected region.
7. Watch the event bus consumers catch up. Search results, notifications and webhooks are delayed until the consumers have caught up.

The targets for a manual region failover with this runbook are a recovery time of **60 minutes** and a data loss window of at most **5 minutes**. Automatic promotion of a single database standby after the loss of one availability zone has tighter targets: a recovery time of **5 minutes** and no lost transactions. Rebuilding a whole lost region has a recovery time target of **4 hours**. These objectives are defined in `docs/architecture/multi-region-and-data-residency.md`.

## Escalation

- Team Platform Infrastructure, `#team-platform` – leads the failover and is paged by both alerts.
- Every service team's on-call is paged for a region failover and confirms the health of its own service in the incident channel.
- Team Customer Support, `#support-escalations` – posts on `https://status.acme-cloud.example` within **15 minutes** and updates the post every **30 minutes**.
- Team Trust and Compliance, `#team-trust` – is informed of every region failover, because the data loss window must be assessed.

## After the incident

- Do not fail back during the incident. Plan the return to the primary zone as a normal change inside a release window, as described in `docs/engineering/release-process.md`.
- Rebuild the database standbys in the recovered zone before failing back.
- Measure the real recovery time and data loss window and compare them with the targets.
- Calculate the downtime per plan against the uptime targets: **99.9%** on Starter and Pro, **99.95%** on Business and **99.99%** on Enterprise.
- Write a postmortem within **5 business days**. A region failover drill is run every **6 months** in each region.

Last reviewed: 2026-11-26
