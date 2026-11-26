# Runbook – Login Outage

## When to use this runbook

Use the login outage runbook when customers cannot sign in to Acme Cloud at `https://app.acme-cloud.example/login`, or when sign-in is very slow.

- Alert `AuthLoginSuccessRateLow` – fewer than **90%** of login attempts succeeded over **5 minutes**.
- Alert `AuthErrorRateHigh` – more than **5%** of Auth API responses were HTTP 5xx over **5 minutes**.
- Alert `AuthLatencyHigh` – p95 latency of the Auth API was above **2 seconds** for **10 minutes**.
- Support reports a burst of P1 tickets saying that the login page fails or loops.

The login outage runbook is owned by Team Identity. The Auth service is described in `services/auth/README.md`.

## Impact

A login outage stops users from starting new sessions. Users with an existing session normally keep working, because web sessions last **14 days** of inactivity and mobile sessions last **90 days**. A login outage also blocks password resets, MFA challenges and SSO logins, and it can block API calls if API key validation is affected.

A login outage in any region is **SEV1**. Slow but working login is **SEV2**.

## Diagnosis

1. Check whether the outage affects one region or all three regions (`us-east`, `eu-central`, `ap-south`).

```bash
for ctx in prod-us-east prod-eu-central prod-ap-south; do
  kubectl --context "$ctx" -n auth get pods
done
```

2. Read the recent Auth API errors.

```bash
kubectl --context prod-us-east -n auth logs deploy/auth-api --since=15m | grep -E "ERROR|timeout" | tail -n 50
```

3. Check whether the Auth database accepts connections. If connections are exhausted, continue with `docs/runbooks/database-connection-exhaustion.md`.

```bash
psql "$AUTH_DB_URL" -h auth-db.us-east.internal.acme-cloud.example -c "SELECT count(*) FROM pg_stat_activity;"
```

4. Work out which login method fails: password login, MFA, SSO or API keys. If only SSO logins fail, continue with `docs/runbooks/sso-certificate-expiry.md`.
5. Check whether an Auth deployment or a configuration change happened in the last **2 hours**.

```bash
kubectl --context prod-us-east -n auth rollout history deploy/auth-api
```

6. Check whether the failures are lockouts caused by an attack. Normal lockout is **5 failed attempts within 15 minutes**, as described in `services/auth/docs/passwords-and-mfa.md`. A large number of lockouts from few IP ranges points to credential stuffing, which is a security incident.

## Mitigation

1. If a deployment caused the outage, roll the deployment back with `kubectl rollout undo deploy/auth-api` in each affected region.
2. If Auth pods are crashing or overloaded, scale `auth-api` up by **50%** and restart the unhealthy pods.
3. If one region is unhealthy and the other regions are fine, follow `docs/runbooks/region-failover.md`.
4. If the cause is a credential stuffing attack, ask the API gateway owners to rate limit the attacking IP ranges. Do not disable lockouts.
5. Do not extend or re-issue sessions in bulk as a workaround. Do not disable MFA or SSO enforcement for any workspace as a workaround.
6. Confirm recovery by checking that the login success rate is above **98%** for **15 minutes**.

## Escalation

- Page the Team Identity on-call through `#team-identity` immediately. A login outage is always paged.
- Declare a SEV1 incident in `#incidents` and post on `https://status.acme-cloud.example` within **15 minutes**.
- Tell Team Customer Support in `#support-escalations` at once, because P1 tickets arrive within minutes.
- Escalate to Team Trust and Compliance in `#team-trust` if an attack or a credential leak is suspected.

## After the incident

- Check that no user was left locked out. A password reset unlocks an account immediately.
- Check the audit log for unusual logins during the outage window. The audit log is described in `services/audit-log/README.md`.
- Record the incident under an ID in the format `INC-2026-041` and write a postmortem within **5 business days**.
- Add or tune an alert if the outage was noticed by customers before an alert fired.

Last reviewed: 2026-11-26
