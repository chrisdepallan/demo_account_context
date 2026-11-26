# Sync and Troubleshooting

## How often do integrations sync?

| Kind of sync | When it runs | What it does |
|------|--------------|--------------|
| Event-driven | Within **1 minute** of a change | Applies single changes pushed by the other product |
| Incremental | Every **5 minutes** | Reads everything changed since the sync cursor |
| Full | Every **24 hours**, and when the cursor has expired | Compares every linked item on both sides |
| Manual | When an Owner or Admin selects **Sync now** | Runs an incremental sync straight away |

A manual sync can be requested once every **15 minutes** per install. Sync reads items in pages of **200**.

## What is a sync cursor?

The cursor is an opaque marker that records how far the last incremental sync read. Each run starts from the cursor and saves a new one when it finishes. A cursor is valid for **7 days**. If an install was suspended for longer than that, the next run is a full sync instead of an incremental one.

## What happens when the same item changes on both sides?

Conflicts are settled field by field, not item by item:

- If only one side changed a field, that change is kept.
- If both sides changed the same field, the **later change wins**.
- If both changes were made within **60 seconds** of each other, the **source of truth** wins. The source of truth is Acme Cloud by default and can be switched to the other product under **Settings → Integrations → (install) → Sync settings**.
- Changes to different fields of the same item are both kept.

Every overwritten value is recorded in the task's activity history, so nothing is lost silently.

## What happens when a linked item is deleted?

Deletes are never copied across. If a Jira issue is deleted, the Acme Cloud task stays and is marked **Unlinked**. If an Acme Cloud task is deleted, the Jira issue stays. This prevents a mistake on one side from destroying work on the other.

## How does Jira sync work?

Jira sync is two-way and is set per project under **Project settings → Jira**. One Acme Cloud project maps to one Jira project. These fields sync:

| Acme Cloud field | Jira field |
|------|------------|
| Title | Summary |
| Description | Description |
| Status | Status (mapped by an Admin) |
| Assignee | Assignee (matched by email) |
| Due date | Due date |

Comments and attachments do not sync. An assignee with no matching member is left unassigned in Acme Cloud.

## How does Google Workspace sync work?

- **Drive** – a Drive file attached to a task is stored as a link, not a copy, so it does not use Acme Cloud storage. Renaming the file in Drive updates the name on the task at the next sync.
- **Calendar** – task due dates are written to a Google Calendar named after the project. This is one-way: moving the event in Calendar does not change the task.
- Access to a Drive file is still decided by Google. A member who cannot open the file in Drive cannot open it from the task.

## What happens when a sync fails?

A failed step is retried up to **6 attempts** in total, waiting **1, 2, 4, 8 and 16 minutes** between attempts. If the last attempt fails, the run is marked failed. After **5 consecutive failed runs** the install is suspended and the Owner and Admins are emailed.

## Why has my integration stopped syncing?

1. Open **Settings → Integrations** and check the install's state. If it is `suspended`, select **Reconnect**.
2. Check that the app is still installed on the other side (for example in Slack's app list).
3. Check that the person who connected it still has access there. If they left, another Owner or Admin should reconnect.
4. Check the account state. Sync is paused while an account is `read_only`.
5. Select **Sync now**. If the last sync time does not change within **5 minutes**, contact support.

## Why are some changes missing after a sync?

- The field is not one that syncs, for example Jira comments.
- The change lost a conflict; check the task's activity history.
- The item was unlinked because its partner was deleted.
- The install lost a scope. Review scopes at **Settings → Integrations**.

## What should I send to support?

Email `support@acme-cloud.example` with the workspace ID (for example `ws_4H8P2L`), the integration ID (for example `int_4K9T2M`), the affected task ID and the time the problem started. Never send tokens, passwords or API keys. The service's health is shown at `https://status.acme-cloud.example`.

Last reviewed: 2026-11-26
