# Runbook – Storage Quota Miscount

## When to use this runbook

Use the storage quota miscount runbook when the storage usage that Acme Cloud shows for an account does not match the files the account really stores.

- Alert `FilesQuotaDriftDetected` – the nightly reconciliation job found an account whose recorded usage differs from the measured usage by more than **1%** or more than **1 GB**.
- Alert `FilesQuotaReconciliationFailed` – the nightly reconciliation job did not finish within **6 hours**.
- A customer reports that uploads are blocked although the account is well below its storage limit, or that usage did not go down after files were deleted.

The storage quota miscount runbook is owned by Team Storage Platform. The Files service is described in `services/files/README.md`.

## Impact

A storage quota miscount that is too high blocks uploads wrongly. At **100%** recorded usage, new uploads are blocked, and at **90%** the Owner and Admins get a warning email. A storage quota miscount that is too low lets an account store more than its plan allows. Existing files stay accessible in both cases. Storage limits per plan are listed in `services/accounts/docs/plans-and-limits.md`.

A storage quota miscount for a few accounts is **SEV3**. Wrongly blocked uploads for many accounts is **SEV2**.

## Diagnosis

1. Compare the recorded usage with the measured usage for the affected account.

```bash
psql "$FILES_DB_URL" -h files-db.us-east.internal.acme-cloud.example -c "
  SELECT u.account_id, u.recorded_bytes, sum(v.size_bytes) AS measured_bytes
  FROM storage_usage u JOIN file_versions v ON v.account_id = u.account_id
  WHERE u.account_id = 'acc_7F3K9Q2M' AND v.deleted_at IS NULL
  GROUP BY u.account_id, u.recorded_bytes;"
```

2. Check how many accounts are affected. One account suggests a single failed operation. Many accounts suggest a bug or a missed batch of events.

```bash
kubectl --context prod-us-east -n files logs job/files-quota-reconcile | grep "drift" | wc -l
```

3. Check what the difference consists of. Common causes are listed below.
4. Check whether a Files deployment happened shortly before the drift started.

Common causes of a storage quota miscount:

- Old file versions that passed the plan's version history limit but were not removed.
- Uploads that failed part-way and left incomplete parts in object storage.
- Files in the trash that still count although the trash was emptied.
- A usage event that was lost or applied twice.

The table and column names in the query are illustrative. File IDs look like `fil_3N6V8C1X`.

## Mitigation

1. For a single account, run the reconciliation for that account only. The reconciliation job sets the recorded usage to the measured usage.

```bash
kubectl --context prod-us-east -n files create job quota-fix-acc-7f3k9q2m \
  --from=cronjob/files-quota-reconcile -- --account acc_7F3K9Q2M
```

2. If uploads are blocked wrongly for many accounts, ask Team Storage Platform to raise the upload block threshold temporarily for the affected accounts until the reconciliation has finished.
3. If a deployment caused the drift, roll the deployment back with `kubectl rollout undo deploy/files-api` before reconciling, otherwise the drift returns.
4. Never delete customer files or file versions by hand to make the numbers match.
5. Confirm recovery by checking that the recorded usage equals the measured usage for **5** sample accounts.

## Escalation

- Team Storage Platform, `#team-storage` – first responder for both alerts.
- Team Accounts Platform, `#team-accounts` – when plan limits or storage packs appear to be applied wrongly.
- Team Revenue Engineering, `#team-billing` – when a customer bought a storage pack or seats only because of the miscount and a refund or credit is needed. Refund rules are in `services/billing/docs/refunds.md`.
- Team Customer Support, `#support-escalations` – for replies to affected customers.

## After the incident

- Reply on every related support ticket with the corrected usage figure.
- List the affected account IDs and the size of the correction in the incident record.
- Add a regression test for the cause to the Files service tests.
- For a SEV2 incident, write a postmortem within **5 business days**.

Last reviewed: 2026-11-26
