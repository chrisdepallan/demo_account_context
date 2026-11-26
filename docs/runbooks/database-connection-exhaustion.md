# Runbook – Database Connection Exhaustion

## When to use this runbook

Use the database connection exhaustion runbook when a service cannot get a connection to its PostgreSQL database. Every Acme Cloud service has its own database, so the runbook applies to any of the 12 services.

- Alert `DatabaseConnectionsNearLimit` – a database used more than **85%** of its maximum connections for **5 minutes**.
- Alert `DatabaseConnectionPoolWaitHigh` – requests waited more than **1 second** on average for a pooled connection over **5 minutes**.
- Service logs show errors such as "too many clients already" or "connection pool timeout".

The database connection exhaustion runbook is owned by the team that owns the affected service, with help from Team Platform Infrastructure.

## Impact

Database connection exhaustion makes the affected service slow and then unavailable. Requests fail with HTTP 5xx or time out. The impact depends on the service: connection exhaustion in the Auth database causes a login outage, and connection exhaustion in the Billing database stops charges and invoices.

Database connection exhaustion is **SEV2** for most services and **SEV1** for the Auth and Accounts databases.

## Diagnosis

1. See how many connections are open and what state the connections are in.

```bash
psql "$SERVICE_DB_URL" -h billing-db.us-east.internal.acme-cloud.example -c "
  SELECT state, count(*) FROM pg_stat_activity GROUP BY state ORDER BY count(*) DESC;"
```

2. See which application and which user holds the connections.

```bash
psql "$SERVICE_DB_URL" -h billing-db.us-east.internal.acme-cloud.example -c "
  SELECT usename, application_name, count(*)
  FROM pg_stat_activity GROUP BY usename, application_name ORDER BY count(*) DESC;"
```

3. Find long-running queries and transactions that were left open. Connections in the state `idle in transaction` for more than **5 minutes** are a common cause.

```bash
psql "$SERVICE_DB_URL" -h billing-db.us-east.internal.acme-cloud.example -c "
  SELECT pid, state, now() - xact_start AS open_for, left(query, 80) AS query
  FROM pg_stat_activity
  WHERE xact_start IS NOT NULL ORDER BY open_for DESC LIMIT 10;"
```

4. Check whether the service was scaled up recently. More pods mean more connection pools.

```bash
kubectl --context prod-us-east -n billing get deploy
kubectl --context prod-us-east -n billing rollout history deploy/billing-api
```

5. Check whether a lock blocks many queries. Blocked queries keep their connections and the pool fills up.

## Mitigation

1. End the transactions that were left open. End only connections in the state `idle in transaction` that are older than **5 minutes**, and record each process ID.

```bash
psql "$SERVICE_DB_URL" -h billing-db.us-east.internal.acme-cloud.example -c "
  SELECT pg_terminate_backend(pid) FROM pg_stat_activity
  WHERE state = 'idle in transaction' AND now() - state_change > interval '5 minutes';"
```

2. If one long-running query blocks other queries, cancel that query with `pg_cancel_backend` before using `pg_terminate_backend`.
3. If a deployment caused a connection leak, roll the deployment back with `kubectl rollout undo`.
4. If the service was scaled up too far, scale the service back down so that the sum of all pool sizes stays below **80%** of the database's maximum connections.
5. Do not raise the database's maximum connections during the incident without Team Platform Infrastructure. A higher limit needs more memory and can make the database unstable.
6. Never restart the database primary as a first step. A restart ends every connection and can trigger a failover.
7. Confirm recovery when connection usage is below **70%** for **15 minutes**.

## Escalation

- The owning service team's on-call is the first responder. Team channels are listed in each service README, for example `services/billing/README.md`.
- Team Platform Infrastructure, `#team-platform` – page when the cause is not found within **15 minutes**, or when the database itself is unhealthy.
- Declare an incident in `#incidents` for the Auth and Accounts databases at once, and for other databases when customers are affected for more than **15 minutes**.
- If login is affected, also follow `docs/runbooks/login-outage.md`.

## After the incident

- Find the code path that left transactions open and add a test for the fix.
- Review the pool size, the replica limits and the statement timeout of the affected service.
- Record every ended process ID and cancelled query in the incident record.
- For a SEV1 or SEV2 incident, write a postmortem within **5 business days**.

Last reviewed: 2026-11-26
