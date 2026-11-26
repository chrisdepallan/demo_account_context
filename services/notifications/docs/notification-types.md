# Notification Types

## What kinds of notifications does Acme Cloud send?

Acme Cloud sends **11** notification types. Each one has a key that appears in **Settings → Notifications** and in the API.

| Type key | Sent when | Who receives it |
|----------|-----------|-----------------|
| `mention` | Someone @mentions you in a comment or task | The mentioned person |
| `task_assigned` | A task is assigned to you | The assignee |
| `task_due_soon` | A task assigned to you is due in 24 hours | The assignee |
| `task_completed` | A task you created or follow is completed | Creator and followers |
| `comment_added` | Someone comments on a task or file you follow | Followers |
| `file_shared` | A file or folder is shared with you | The person it is shared with |
| `member_joined` | An invited member accepts and joins the workspace | Owner and Admins |
| `storage_warning` | Storage reaches 90% or 100% of the plan limit | Owner and Admins |
| `security_alert` | New-device login, password change, MFA change, API key revoked | The affected user; Owner for account-wide events |
| `billing_alert` | Payment failed, invoice issued, grace period ending | Owner and Billing admins |
| `account_notice` | Plan change, ownership transfer, account closing, policy updates | Owner; Admins for workspace-wide notices |

The `task_due_soon` reminder is sent **24 hours** before the due date. The storage thresholds match `services/accounts/docs/plans-and-limits.md`.

## Which channels are available?

There are **3** channels:

- **Email** – sent to the address on your profile from `notifications@acme-cloud.example`.
- **In-app** – shown under the bell icon at `https://app.acme-cloud.example`. In-app notifications are kept for **90 days**, then deleted.
- **Push** – sent to the Acme Cloud mobile apps and to browsers where you allowed notifications. You can register up to **10 devices**. A device that has not opened the app for **60 days** is removed automatically.

All three channels are available on every plan, including Free.

## Which notifications are on by default?

| Type key | Email | In-app | Push |
|----------|-------|--------|------|
| `mention` | On | On | On |
| `task_assigned` | On | On | On |
| `task_due_soon` | On | On | On |
| `task_completed` | Off | On | Off |
| `comment_added` | Off | On | Off |
| `file_shared` | On | On | Off |
| `member_joined` | Off | On | Off |
| `storage_warning` | On | On | Off |
| `security_alert` | Always on | Always on | On |
| `billing_alert` | Always on | Always on | Off |
| `account_notice` | Always on | Always on | Off |

A workspace Owner or Admin can change the defaults for their workspace. See `services/notifications/docs/preferences-and-digests.md`.

## Which notifications can I not turn off?

Three types are **mandatory**: `security_alert`, `billing_alert` and `account_notice`. Email and in-app are always on for these, whatever you or your workspace Admin choose. Only the push setting can be changed. Mandatory notifications also ignore quiet hours and the hourly rate limits described in `services/notifications/docs/quiet-hours-and-rate-limits.md`.

## Do all roles get the same notifications?

No. The role decides which types a person can receive:

- **Owner** – all 11 types.
- **Admin** – all types except `billing_alert`.
- **Billing admin** – `billing_alert`, `security_alert` and `account_notice` only, because Billing admins do not work on projects.
- **Member** – all types except `billing_alert`, `member_joined` and `storage_warning`.
- **Guest** – `mention`, `comment_added`, `file_shared`, `security_alert` and `account_notice` only.

Roles are described in `services/accounts/docs/members-and-roles.md`.

## Do I get notified about my own actions?

No. You never receive a notification for something you did yourself, such as assigning a task to yourself or completing your own task.

## How long are notifications kept?

In-app notifications are kept for **90 days**. Read and unread notifications are deleted on the same schedule. Emails that were already sent stay in your mailbox; Acme Cloud keeps its own email delivery log for **30 days**.

## What does a notification look like in the API?

Each notification has an ID such as `ntf_8K2M4Q7T1X`, a `type`, a `title`, the related `project_id` (for example `prj_5T8N2W6R`) when there is one, a `created_at` timestamp in UTC and a `read_at` timestamp that is empty until the notification is read. The full schema is in `services/notifications/openapi.yaml`.

Last reviewed: 2026-11-26
