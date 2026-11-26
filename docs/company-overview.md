# Acme Cloud – Company Overview

## What Acme Cloud does

Acme Cloud provides hosted project-management and file-storage workspaces for small and mid-sized teams. Customers sign up for an **account**, create one or more **workspaces**, and invite **members**.

## Headquarters and business hours

- Headquarters: Austin, Texas, USA (fictional)
- Standard business hours: Monday–Friday, 08:00–18:00 US Central Time (UTC−6, UTC−5 during daylight saving)
- Company holidays: support runs at reduced staffing on US federal holidays; Enterprise 24/7 coverage is unaffected.

## Regions and data residency

| Region code | Location | Available on |
|-------------|----------|--------------|
| `us-east` | Virginia, USA | All plans (default) |
| `eu-central` | Frankfurt, Germany | Business and Enterprise |
| `ap-south` | Mumbai, India | Enterprise only |

The region is chosen when a workspace is created and cannot be changed afterwards. To move regions, the customer must export data and create a new workspace.

## Services at a glance

- **Accounts** – sign-up, plans, limits, team members, closing accounts. See `services/accounts/README.md`.
- **Billing** – pricing, invoices, payment methods, refunds, taxes. See `services/billing/README.md`.
- **Auth** – login, passwords, MFA, SSO, API keys. See `services/auth/README.md`.
- **Support** – channels, SLAs, escalation. See `services/support/README.md`.
- **Projects** – projects, tasks, boards, comments, automation. See `services/projects/README.md`.
- **Files** – file storage, uploads, versions, sharing links, storage quotas. See `services/files/README.md`.
- **Notifications** – email, in-app and push notifications, digests, preferences. See `services/notifications/README.md`.
- **Webhooks** – outbound event webhooks, signing, retries. See `services/webhooks/README.md`.
- **Search** – full-text search across projects, tasks and files. See `services/search/README.md`.
- **Audit Log** – record of security-relevant actions, export, SIEM streaming. See `services/audit-log/README.md`.
- **Integrations** – app directory and integrations with Slack, GitHub, Jira and Google Workspace. See `services/integrations/README.md`.
- **Analytics** – dashboards, metrics, scheduled reports and exports. See `services/analytics/README.md`.

How the services fit together is described in `docs/architecture/system-overview.md`.

## Status page and uptime target

- Public status page: `https://status.acme-cloud.example`
- Uptime target: 99.9% monthly on Starter and Pro, 99.95% on Business, 99.99% on Enterprise.

Last reviewed: 2026-11-26
