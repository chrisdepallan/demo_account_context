# Slack and GitHub Integrations

## What does the Slack integration do?

- Posts project updates (task created, completed, assigned, comment added, due date changed) to Slack channels you choose.
- Unfurls Acme Cloud links pasted in Slack into a preview with the task title, status, assignee and due date.
- Creates a task from a Slack message with the **Create task** message action or the `/acme` command.
- Sends personal reminders by direct message when a task assigned to you is due within **24 hours**.

The Slack integration is available on **all plans** and counts as one install.

## How do I connect Slack?

1. An Owner or Admin goes to **Settings → Integrations → App directory → Slack** and selects **Install**.
2. Sign in to the Slack workspace and approve the connection. You need permission to add apps in Slack.
3. Back in Acme Cloud, open a project and go to **Project settings → Slack** to choose a channel.

One Acme Cloud workspace connects to **one** Slack workspace. Each project can post to up to **5 channels**. To post to a private channel, first invite the app to it in Slack with `/invite @Acme Cloud`.

## Which Slack notifications can I turn on?

Each channel link has its own switches under **Project settings → Slack**:

| Event | Default |
|------|---------|
| Task completed | On |
| Task created | On |
| Task assigned or reassigned | Off |
| Comment added | Off |
| Due date changed | Off |
| Project status report (weekly) | Off |

Updates to the same task within **2 minutes** are grouped into one message, so a busy project does not flood the channel.

## What can I do with the /acme command?

| Command | Result |
|------|--------|
| `/acme create <title>` | Creates a task in the channel's linked project |
| `/acme find <words>` | Shows up to **5** matching tasks |
| `/acme mine` | Lists your open tasks due in the next **7 days** |
| `/acme help` | Lists the commands |

Slack users are matched to Acme Cloud members by email address. Someone with no matching member account sees a prompt to ask an Admin for an invitation, and cannot create tasks.

## What does the GitHub integration do?

- Links pull requests, branches and commits to a task when its ID (for example `tsk_8D3N6R2W`) appears in the pull request title, the branch name or a commit message.
- Shows the linked pull request's state (open, draft, merged, closed) and check results on the task.
- Optionally moves the task to **Done** when a linked pull request is merged.

The GitHub integration is available on **all plans**. It reads from GitHub and writes only to Acme Cloud; it never changes code, issues or pull requests.

## How do I connect GitHub?

1. An Owner or Admin goes to **Settings → Integrations → App directory → GitHub** and selects **Install**.
2. Choose the GitHub organisation and pick which repositories to share. You must be an organisation owner in GitHub.
3. In Acme Cloud, go to **Project settings → GitHub** and link repositories to the project.

One install can cover up to **100 repositories**. A repository can be linked to any number of projects.

## How do I make a merged pull request complete a task?

Turn on **Complete task on merge** under **Project settings → GitHub**. It is **off** by default. When it is on, a task moves to **Done** only when every pull request linked to it is merged. A pull request that is closed without merging does not change the task.

## Why is my pull request not linked to the task?

- The task ID must be exact and complete: `tsk_` followed by **8** uppercase letters and digits.
- The repository must be shared with the install and linked to the task's project.
- GitHub events normally arrive within **1 minute**. If the event was missed, the link appears at the next incremental sync, at most **5 minutes** later.
- The install must be `active`. A `suspended` install does not process events; see `services/integrations/docs/oauth-installs-and-scopes.md`.

## Does Acme Cloud scan my GitHub repositories for leaked keys?

Yes, but that is separate from this integration. Acme Cloud scans public GitHub repositories for exposed `acme_live_` keys whether or not the GitHub app is installed. See `services/auth/docs/api-keys.md`.

Last reviewed: 2026-11-26
