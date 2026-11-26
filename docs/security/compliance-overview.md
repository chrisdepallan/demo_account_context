# Compliance Overview

## What does the compliance overview describe?

The compliance overview describes the security and privacy controls that Acme Cloud operates and where each control is documented. Acme Cloud is a fictional company, so the compliance overview describes how the controls are designed. The compliance overview does not state that any certificate or audit report has been issued by an auditor. Team Trust and Compliance owns the control set and can be reached in `#team-trust`.

## Which control areas does Acme Cloud maintain?

| Control area | What the controls cover | Where it is documented |
|--------------|-------------------------|------------------------|
| Access control | Staff sign-in, production access, access reviews | `docs/security/access-control.md` |
| Data protection | Classification, handling, retention | `docs/security/data-classification.md` |
| Incident response | Detection, containment, customer notice | `docs/security/incident-response.md` |
| Change management | Review, testing, rollout, rollback | `docs/engineering/release-process.md` |
| Operations | On-call, severities, runbooks | `docs/engineering/on-call.md` |
| Logging and audit | Tamper-evident audit log | `services/audit-log/README.md` |

The control areas are designed to line up with common security frameworks for cloud services, so that a customer's security questionnaire can be answered from these documents.

## How is customer data protected?

- Data is encrypted in transit with TLS **1.2** or later on every public endpoint under `acme-cloud.example`.
- Data is encrypted at rest in PostgreSQL databases, object storage and backups with **256-bit** keys.
- Each service has its own database, and each workspace's data is separated from every other workspace by checks on every request.
- Passwords are stored only as salted hashes. Full payment card numbers are never stored by Acme Cloud and are held by the payment processor.
- Customer content is classified as Restricted and is not read by staff without the customer's consent or an approved security investigation.

## Where is customer data stored?

Customer data is stored in the region chosen when the workspace is created: `us-east` (Virginia, USA), `eu-central` (Frankfurt, Germany) or `ap-south` (Mumbai, India). `us-east` is the default and is available on all plans, `eu-central` is available on Business and Enterprise, and `ap-south` is available on Enterprise only. The region of a workspace cannot be changed afterwards. A failover moves a workspace to a standby availability zone inside the same region and never to another region, as described in `docs/runbooks/region-failover.md`.

## How does Acme Cloud handle privacy requests?

- **Export** – the Owner or an Admin can export all workspace data from **Settings → Workspace → Export**. The download link is valid for **7 days**.
- **Deletion** – closing an account starts the **30-day** data retention window. After that, data is permanently deleted from primary storage and backups are purged within a further **35 days**. The steps are in `services/accounts/docs/account-lifecycle.md`.
- **Correction** – users correct their own profile data in the product.
- **Other requests** – requests from individuals about their personal data go to `privacy@acme-cloud.example` and are answered within **30 days**.

Enterprise customers can agree a data processing addendum through Sales, as described in `services/accounts/docs/plans-and-limits.md`.

## How are changes to production controlled?

Every change to production goes through a pull request with at least **1 approval**, or **2 approvals** for the Auth, Billing and Audit Log services. Automated checks must pass before a merge. Releases go through staging and a **5%** canary before the full rollout, and can be rolled back within **15 minutes**. No one approves their own change. The full rules are in `docs/engineering/release-process.md`.

## How is activity logged and monitored?

Security-relevant actions by customers and by staff are written to the audit log. Audit log entries are linked in a hash chain, so that a changed or missing entry is detected by a scheduled verifier. Customers see their audit log for **90 days** on Pro, **1 year** on Business and **7 years** on Enterprise, and can stream entries to their own SIEM. Service logs are kept for **30 days** and contain identifiers instead of personal data. Paging alerts cover availability, error rates and integrity, and every paging alert has a runbook in `docs/runbooks/`.

## How does Acme Cloud plan for outages and data loss?

- Databases are backed up every day, and backups are kept for **35 days**.
- A restore from backup is tested every **3 months**.
- Each region has a standby availability zone. The recovery targets for losing a zone are a recovery time of **60 minutes** and a data loss window of at most **5 minutes**.
- A region failover drill is run every **6 months** in each region.
- Uptime targets are **99.9%** monthly on Starter and Pro, **99.95%** on Business and **99.99%** on Enterprise.

## How are vulnerabilities found and fixed?

Services use the Python standard library only, which keeps the number of third-party components small. Base images and infrastructure components are scanned every week. An independent penetration test is planned every **12 months**. Vulnerabilities are fixed within the following times, counted from confirmation.

| Rating | Fix within |
|--------|------------|
| Critical | **7 days** |
| High | **30 days** |
| Medium | **90 days** |
| Low | Next planned release of the affected service |

Security researchers report findings to `security@acme-cloud.example`.

## How are suppliers managed?

Suppliers that process customer data, such as the cloud infrastructure provider, the payment processor and the email delivery provider, are reviewed by Team Trust and Compliance before first use and every **12 months** after that. Each supplier gets only the data its service needs. The list of suppliers that process customer data is published in the help center at `https://help.acme-cloud.example`, and customers are told at least **30 days** before a new supplier is added.

## How are staff trained and controls reviewed?

Every member of staff completes security and data handling training within the first **30 days** and then every **12 months**. Access is reviewed every **90 days**. The security incident process is exercised every **6 months**. Team Trust and Compliance reviews the full control set once every **12 months** and records gaps as tracked action items with owners and due dates.

## How can a customer get compliance information?

Customers on any plan can read the public security pages in the help center. Business and Enterprise customers can send a security questionnaire through their support channel or their Customer Success Manager. Custom terms, security reviews and data processing addenda for Enterprise customers are handled by Sales at `sales@acme-cloud.example`.

Last reviewed: 2026-11-26
