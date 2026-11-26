# Data Export and Deletion

## Who can export workspace data?

The Owner or an Admin of the workspace. Members, Billing admins and Guests cannot start an export. Exports are available on every plan, including Free.

## How do I export a workspace?

1. Go to **Settings → Workspace → Export**.
2. Select **Start export**.
3. Wait for the email that says the export is ready. Most exports finish within **4 hours**; very large workspaces can take up to **24 hours**.
4. Download the ZIP from the link in the email or from the same settings page.

Only **1** export per workspace can run at a time. A second export can be started as soon as the first one finishes or is cancelled.

## What is in an export?

An export is a ZIP archive with JSON files and the original uploaded files.

| Content | Format |
|---------|--------|
| Projects, tasks and comments | JSON |
| Members, guests and roles | JSON |
| Files (current version) | Original file format |
| Workspace settings | JSON |

Earlier file versions, API keys, passwords, MFA secrets and payment details are never included in an export.

## How long is the download link valid?

The download link is valid for **7 days**. After that the archive is deleted and a new export must be started. The link works only for a signed-in Owner or Admin of the workspace.

## Can I start an export with an API key?

No. Customer API keys have no export scope, so exports are started from **Settings → Workspace → Export**. Internally, the web app starts an export with `POST /v2/accounts/{account_id}/workspaces/{workspace_id}/exports` and checks it with `GET` on the same path plus the export ID. Export IDs look like `exp_9T4W2K7B`. A second request while an export is running returns HTTP `409 Conflict`. The full API description is in `services/accounts/openapi.yaml`.

## Can I export data after the account is closed?

Not directly. Members are signed out when an account is closed, so the export page cannot be reached. During the **30 days** after closing, the Owner can restore the account from the link in the closure email and then export. Once the account is `deleted`, no export is possible.

## When is my data deleted?

| Event | When | What happens |
|-------|------|--------------|
| Account closed | Day of closing | Account is `closed`, members are signed out, data is kept |
| Retention ends | 30 days after closing (day 31) | Account is `deleted`, data is erased from primary storage |
| Backups purged | Within a further 35 days | Data is removed from all backups |

Data is kept for **30 days** after closing. On day **31** it is permanently erased from primary storage, and backups are purged within a further **35 days**. All copies are therefore gone at most **65 days** after the account was closed.

## Can I ask for deletion sooner than 30 days?

Yes. The Owner can email `support@acme-cloud.example` from the Owner's email address and ask for immediate deletion of a closed account. Support confirms the request by reply and deletes the account within **3 business days**. Immediate deletion cannot be undone, and the 35-day backup purge still applies.

## How do I delete a single member's personal data?

Removing a member from **Settings → Members** ends their access, but content they created stays in the workspace. To have a person's profile data (name, email address, avatar) erased, the Owner or an Admin emails `support@acme-cloud.example`. Requests are completed within **30 days**. Content the person created is kept and shown as written by "Deleted user".

## Does Acme Cloud keep anything after deletion?

Invoices and billing records are kept for **7 years** to meet tax and accounting rules. They contain the account name, billing address and amounts, but no workspace content. Payment methods are stored only as opaque tokens such as `pm_4K2N8Q` and are removed when the account is deleted.

Last reviewed: 2026-11-26
