# Runbook – Failed Payment Spike

## When to use this runbook

Use the failed payment spike runbook when far more subscription charges fail than normal. The normal payment failure rate at Acme Cloud is **4–6%** of charge attempts.

- Alert `BillingPaymentFailureRateHigh` – more than **15%** of charge attempts failed over **15 minutes**.
- Alert `BillingProcessorErrorsHigh` – more than **5%** of calls to the payment processor returned an error or timed out over **5 minutes**.
- Support reports several tickets in **1 hour** from customers whose accounts moved to `past_due` although their payment method is valid.

The failed payment spike runbook is owned by Team Revenue Engineering. The Billing service is described in `services/billing/README.md`.

## Impact

A failed payment spike moves healthy accounts to `past_due`. Each affected account sends a failed-payment email to the Owner and Billing admins. Accounts stay fully usable during the **14-day** grace period, so there is no immediate loss of access. If the spike is not corrected, the automatic retries on **days 1, 3, 7 and 14** can also fail and accounts become `read_only` on **day 14**. The rules for failed payments are in `services/billing/docs/payment-methods.md`.

A failed payment spike is normally **SEV2**. Raise the incident to **SEV1** if accounts are being moved to `read_only` incorrectly.

## Diagnosis

1. Confirm the failure rate and see which regions are affected.

```bash
kubectl --context prod-us-east -n billing get pods
kubectl --context prod-us-east -n billing logs deploy/billing-worker --since=30m | grep -c "charge_failed"
```

2. Split the failures by reason. Many `processor_unavailable` or `timeout` results point to the payment processor. Many `card_declined` results point to a real decline wave or to a bad request sent by Acme Cloud.

```bash
psql "$BILLING_DB_URL" -h billing-db.us-east.internal.acme-cloud.example -c "
  SELECT failure_reason, count(*)
  FROM charge_attempts
  WHERE created_at > now() - interval '30 minutes' AND status = 'failed'
  GROUP BY failure_reason ORDER BY count(*) DESC;"
```

3. Check whether the failures started right after a Billing deployment.

```bash
kubectl --context prod-us-east -n billing rollout history deploy/billing-api
```

4. Check the payment processor's own status page and compare the start time with the first failed charge.
5. Check whether one payment method (card, PayPal, UPI, ACH, SEPA) or one currency accounts for most failures.

The table and column names in the query are illustrative. Check the Billing service schema before running the query.

## Mitigation

1. If a Billing deployment caused the spike, roll the deployment back with `kubectl rollout undo deploy/billing-api` and `kubectl rollout undo deploy/billing-worker`.
2. If the payment processor is failing, pause the charge and retry workers so that no more retries are consumed. Scale `billing-worker` to **0** replicas and record the time.
3. Do not let the grace period run out because of an Acme Cloud or processor fault. Ask Team Revenue Engineering to extend the grace period for the affected accounts by the length of the incident, rounded up to whole days.
4. When the cause is fixed, scale `billing-worker` back up and re-run the failed charges in batches of **500** accounts. Watch the failure rate return below **6%** before starting the next batch.
5. Accounts that were wrongly moved to `past_due` or `read_only` are restored to `active` after a successful charge. Access returns within **5 minutes** of payment.

## Escalation

- Page the Team Revenue Engineering on-call through `#team-billing` as soon as either alert fires.
- Tell Team Customer Support in `#support-escalations` within **15 minutes** so that agents can answer tickets with one consistent message.
- Escalate to Team Accounts Platform in `#team-accounts` if account states need to be corrected in bulk.
- Declare an incident in `#incidents` if the spike lasts longer than **30 minutes**. Severity rules are in `docs/engineering/on-call.md`.

## After the incident

- Send a correction email to every Owner and Billing admin who received a wrong failed-payment email.
- Confirm that no account reached `read_only` or was downgraded to Free because of the spike.
- List the affected account IDs (format `acc_7F3K9Q2M`) and invoice IDs (format `INV-2026-004812`) in the incident record.
- Write a postmortem within **5 business days** for a SEV1 or SEV2 incident, as described in `docs/security/incident-response.md`.

Last reviewed: 2026-11-26
