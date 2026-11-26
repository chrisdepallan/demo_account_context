# Glossary

## Account

The billing and legal entity that owns one or more workspaces. Every account has exactly one **Owner**. Account IDs look like `acc_7F3K9Q2M`.

## Workspace

A container for projects, files and members. Workspace IDs look like `ws_4H8P2L`. An account can have up to 3 workspaces on Pro, 10 on Business and unlimited on Enterprise.

## Member

A person invited to a workspace. Members count as **seats** for billing. Guests do not count as seats.

## Guest

A limited-access user who can view and comment on shared projects only. Each paid seat allows 5 guests.

## Roles

- **Owner** – full control, including billing and closing the account. One per account.
- **Admin** – manages members, settings and security; cannot close the account or transfer ownership.
- **Billing admin** – manages invoices and payment methods only.
- **Member** – creates and edits content.
- **Guest** – view and comment only.

## Seat

A paid licence for one member. Seats are billed per month or per year depending on the billing cycle.

## Billing cycle

Monthly or annual. Annual billing is 2 months free (about 16.7% cheaper than paying monthly).

## Grace period

The 14 days after a failed payment during which the account stays fully active while payment is retried.

## Data retention window

The 30 days after an account is closed during which data can still be restored. After that, data is permanently deleted.

## SSO

Single sign-on with SAML 2.0 or OpenID Connect. Available on Business and Enterprise.

## SCIM

Automatic user provisioning from an identity provider. Enterprise only.

## Project

A container for tasks inside a workspace. A project is either visible to the whole workspace or private. See `services/projects/docs/projects-and-tasks.md`.

## Task

A unit of work in a project, with a status, a priority, assignees and an optional due date. Task IDs look like `tsk_5M8R3W6K`.

## Automation rule

A rule in a project made of one trigger, optional conditions and one or more actions, for example "when a task is completed, notify the project owner". See `services/projects/docs/templates-and-automation.md`.

## Sharing link

A link that gives access to a file. Its audience is the workspace, invited people or anyone with the link. See `services/files/docs/sharing-links.md`.

## Storage quota

The total storage an account may use, pooled across all its workspaces. Uploads are blocked at **100%** of the quota. See `services/files/docs/storage-quotas.md`.

## Digest

A daily or weekly email that summarises unread in-app notifications. See `services/notifications/docs/preferences-and-digests.md`.

## Webhook endpoint

A customer URL that receives signed event notifications from Acme Cloud. Endpoint IDs look like `whk_6J3V8H1P`. Available on Starter and above. See `services/webhooks/docs/managing-endpoints.md`.

## Signing secret

The secret used to sign webhook deliveries with HMAC-SHA256 so the receiver can verify them. See `services/webhooks/docs/signing-and-verification.md`.

## Audit log

A tamper-evident record of security-relevant actions in an account. Available on Pro and above. See `services/audit-log/README.md`.

## Hash chain

The way audit log entries are linked: each entry stores a SHA-256 hash that covers the previous entry, so any change to history can be detected. See `services/audit-log/docs/access-and-integrity.md`.

## SIEM streaming

Continuous delivery of audit log entries to a customer's security monitoring system. Available on Business and Enterprise. See `services/audit-log/docs/siem-streaming.md`.

## Integration install

A connection between a workspace and an app such as Slack, GitHub, Jira or Google Workspace. Install IDs look like `int_3G7K5W`. See `services/integrations/docs/app-directory.md`.

## Dashboard

A page of charts and figures in Analytics. Built-in dashboards exist on every plan; custom dashboards start on Starter. See `services/analytics/docs/dashboards.md`.

## Incident severity

The internal grading of an incident from **SEV1** (most severe) to **SEV4**. Severity is different from ticket priority (P1 to P4), which grades a customer's support request. See `docs/engineering/on-call.md`.

## Postmortem

The written review of an incident: impact, timeline, root cause and action items. Postmortems are stored in `reports/incidents/`.

## ADR

Architecture decision record. A short document that records one technical decision, its context and its consequences. ADRs are stored in `docs/adr/`.

## Runbook

A step-by-step guide for diagnosing and mitigating one kind of operational problem. Runbooks are stored in `docs/runbooks/`.

Last reviewed: 2026-11-26
