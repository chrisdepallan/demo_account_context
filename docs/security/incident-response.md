# Security Incident Response

## What counts as a security incident at Acme Cloud?

A security incident is any event that harms, or may harm, the confidentiality, integrity or availability of Acme Cloud systems or customer data. Examples of security incidents:

- Customer data seen by someone who should not see it.
- A leaked staff credential, service credential or signing key.
- Malware or an unknown login on a staff laptop or account.
- A failed audit log chain verification, as described in `docs/runbooks/audit-log-chain-verification-failure.md`.
- A credential stuffing attack against the login page.
- Confidential or Restricted data found in the wrong place, as defined in `docs/security/data-classification.md`.

A suspected security incident is handled as a real security incident until it is ruled out.

## How do I report a security incident?

Any member of staff reports a suspected security incident at once in `#team-trust`, or by email to `security@acme-cloud.example`. Outside business hours, page the Team Trust and Compliance on-call. Customers and researchers report security problems to `security@acme-cloud.example`. A report is acknowledged within **1 business day**. Do not investigate alone, do not delete anything and do not discuss the suspected incident in public channels.

## Who leads a security incident?

Team Trust and Compliance leads every security incident and provides the incident commander. The team that owns the affected service provides the technical lead. Team Customer Support provides the communications lead. Legal and the executive on duty join every SEV1 security incident. The general incident roles are described in `docs/engineering/on-call.md`.

## How are security incidents classified?

Security incidents use the same severity levels as all other incidents.

| Severity | Security meaning | Acknowledge | Incident commander assigned |
|----------|------------------|-------------|-----------------------------|
| **SEV1** | Confirmed breach of customer data, confirmed tampering, or an attacker active in production | **5 minutes** | **15 minutes** |
| **SEV2** | Suspected breach, leaked credential with production access, or an integrity failure not yet explained | **5 minutes** | **30 minutes** |
| **SEV3** | Contained event with no customer data involved, for example a lost laptop with an encrypted disk | **4 business hours** | Not required |
| **SEV4** | Policy finding with no exposure, for example an overdue access review | **3 business days** | Not required |

SEV1 and SEV2 security incidents page the Team Trust and Compliance on-call at any hour.

## What are the phases of security incident response?

1. **Detect** – an alert, a staff report or a customer report arrives. The incident gets an ID in the format `INC-2026-041` and a private incident channel.
2. **Triage** – the incident commander sets the severity and names the roles.
3. **Contain** – stop the harm from growing: revoke credentials, block access, isolate systems.
4. **Eradicate** – remove the cause, for example a vulnerable release or a compromised account.
5. **Recover** – restore normal service and confirm that systems and data are in a known good state.
6. **Learn** – write the postmortem and complete the action items.

## How is evidence preserved during a security incident?

- Take snapshots of affected databases and disks before changing them.
- Export the relevant logs and audit log entries and store the export where only Team Trust and Compliance can write.
- Keep a timeline in the incident channel with times in UTC.
- Never repair or delete audit log entries. Never restart or delete an affected system before its state is captured, unless the incident commander decides that containment cannot wait.
- Evidence is kept for at least **1 year** after the incident is closed.

## Which containment actions are used?

- Revoke and rotate every credential that may be exposed. Revoking a customer API key takes effect within **60 seconds**.
- End the active sessions of affected users and require a password reset.
- Remove just-in-time and standing access to the affected system, as described in `docs/security/access-control.md`.
- Roll back a vulnerable release, as described in `docs/engineering/release-process.md`.
- Block attacking IP ranges at the API gateway.

Containment actions that affect customers, such as ending sessions for a whole workspace, are approved by the incident commander.

## When and how are customers notified?

Customers whose data is affected by a confirmed breach are notified without undue delay and at the latest **72 hours** after the breach is confirmed. The notice is sent by email to the account Owner and Admins and states what happened, which data is affected, what Acme Cloud has done and what the customer should do. Enterprise customers are also contacted by their Customer Success Manager. Availability incidents are published on `https://status.acme-cloud.example`. Details of a security incident are not posted on the status page before affected customers have been told. Every customer message is approved by the incident commander and by Legal.

## What must staff not do during a security incident?

- Do not contact a suspected attacker.
- Do not speak to the press or post on social media. Only the communications lead speaks for Acme Cloud.
- Do not copy affected customer data to a laptop, a ticket or a chat message.
- Do not tell a customer that their data is safe before the incident commander has confirmed it.
- Do not close the incident before the incident commander declares it closed.

## What happens after a security incident?

A postmortem is required for every SEV1 and SEV2 security incident. The draft is due within **5 business days** and is reviewed within **10 business days**. The postmortem is blameless and records the timeline, the cause, the affected accounts by ID and the action items with owners and due dates. Team Trust and Compliance tracks the action items until they are done and reports open items to engineering leadership every **month**.

## How is the security incident process tested?

Team Trust and Compliance runs a tabletop exercise of the security incident process every **6 months**, with at least one service team taking part. Every on-call engineer reads the security incident process during onboarding, as described in `docs/engineering/onboarding.md`.

Last reviewed: 2026-11-26
