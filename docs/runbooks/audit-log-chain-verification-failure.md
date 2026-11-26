# Runbook – Audit Log Chain Verification Failure

## When to use this runbook

Use the audit log chain verification failure runbook when the hash chain of the Acme Cloud audit log does not verify. Every audit entry stores the hash of the entry before it, so a changed, deleted or inserted entry breaks the chain.

- Alert `AuditLogChainVerificationFailed` – the scheduled verifier found at least **1** entry whose stored hash does not match the recomputed hash, or whose previous-entry hash does not match the entry before it.
- Alert `AuditLogVerifierStalled` – the scheduled verifier has not completed a run for **2 hours**.
- A customer's SIEM reports a gap or a mismatch in the entries streamed from Acme Cloud.

The audit log chain verification failure runbook is owned by Team Trust and Compliance. The Audit Log service is described in `services/audit-log/README.md`.

## Impact

A broken hash chain means that the audit log can no longer prove that its entries are complete and unchanged from the break onward. The break can be caused by a software bug, by storage corruption or by tampering. Customers on Pro, Business and Enterprise rely on the audit log for investigations, with retention of **90 days**, **1 year** and **7 years**.

An audit log chain verification failure is treated as a security incident until tampering is ruled out. The starting severity is **SEV2**. Confirmed tampering is **SEV1**.

## Diagnosis

1. Read the verifier output to find the first entry that failed. Audit entry IDs look like `aud_2H5J7L9N3Q`.

```bash
kubectl --context prod-us-east -n audit-log logs job/audit-log-verifier | grep -E "chain_break|hash_mismatch" | head -n 20
```

2. Read the failing entry and the two entries around it. Do not change any entry.

```bash
psql "$AUDIT_LOG_DB_READONLY_URL" -h audit-log-db.us-east.internal.acme-cloud.example -c "
  SELECT entry_id, sequence, prev_hash, entry_hash, created_at
  FROM audit_entries
  WHERE workspace_id = 'ws_4H8P2L' AND sequence BETWEEN 10481 AND 10483
  ORDER BY sequence;"
```

3. Work out the kind of break: a missing sequence number, a duplicated sequence number, a changed entry, or two entries that share the same previous-entry hash.
4. Check how far the break reaches: one workspace, many workspaces or a whole region.
5. Check who had write access to the Audit Log database in the time window around the break, and whether any just-in-time access was granted. Access rules are in `docs/security/access-control.md`.
6. Check whether an Audit Log deployment or a database maintenance task happened around the time of the break.

The table and column names in the query are illustrative. Use a read-only database role for every diagnosis step.

## Mitigation

1. Preserve the evidence first. Take a snapshot of the Audit Log database and export the verifier output before any other action.
2. Never repair, rewrite or delete audit entries to make the chain verify again. Never re-run the hashing over existing entries.
3. Keep the Audit Log service accepting new entries. Losing new entries is worse than continuing a chain after a documented break.
4. If a deployment caused the break, roll the deployment back with `kubectl rollout undo deploy/audit-log-api`.
5. If tampering cannot be ruled out within **1 hour**, revoke all standing and just-in-time write access to the Audit Log database and raise the incident to **SEV1**.
6. Record the break as a documented chain break: the workspace, the first and last affected entry, the cause and the incident ID. The verifier then continues from the first valid entry after the break.
7. Compare the affected entries with the copies already delivered to customer SIEM streams and with the database backups, to establish which version is correct.

## Escalation

- Team Trust and Compliance, `#team-trust` – paged by both alerts, at any hour. Team Trust and Compliance leads the incident.
- The security incident process in `docs/security/incident-response.md` applies from the first alert.
- Team Platform Infrastructure, `#team-platform` – for database snapshots and storage checks.
- Team Customer Support, `#support-escalations` – only after Team Trust and Compliance approves the customer message.
- Legal and the executive on duty are informed by the incident commander if tampering is confirmed.

## After the incident

- Tell every affected customer which entries are affected and why, in writing. Affected Enterprise customers are also told by their Customer Success Manager.
- Keep the evidence snapshot for at least **1 year**.
- Add a test to the Audit Log service that reproduces the cause, if the cause was a bug.
- Write a postmortem within **5 business days**. The postmortem is reviewed by Team Trust and Compliance before it is shared.

Last reviewed: 2026-11-26
