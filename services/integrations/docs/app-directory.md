# App Directory

## What is the app directory?

The app directory lists every app that can be connected to an Acme Cloud workspace. Open it at **Settings → Integrations → App directory**. Each listing shows what the app does, the scopes it asks for, who built it and which plans can install it.

There are three kinds of app:

- **First-party** – built and supported by Acme Cloud: Slack, GitHub, Jira and Google Workspace.
- **Partner** – built by another company and reviewed by Acme Cloud before listing.
- **Private** – built by a customer for their own account and never shown to other customers.

## Which integrations does Acme Cloud offer?

| App | Slug | What it does | Sync direction |
|------|------|--------------|----------------|
| Slack | `slack` | Posts project updates to channels, unfurls links, creates tasks from messages | Acme Cloud → Slack, plus actions from Slack |
| GitHub | `github` | Links pull requests and commits to tasks, can complete a task when a pull request merges | GitHub → Acme Cloud |
| Jira | `jira` | Keeps tasks and Jira issues in step | Two-way |
| Google Workspace | `google-workspace` | Attaches Drive files to tasks, puts due dates on Google Calendar | Two-way for Drive links, Acme Cloud → Calendar |

Setup for Slack and GitHub is in `services/integrations/docs/slack-and-github.md`. Jira and Google Workspace sync is in `services/integrations/docs/sync-and-troubleshooting.md`.

## How many integrations can I install?

The limit is counted per workspace. Installs in the `active` and `suspended` states count. Installs that are `pending` or `revoked` do not.

| Plan | Installs per workspace | App kinds allowed |
|------|------------------------|-------------------|
| Free | 2 | First-party only |
| Starter | 5 | First-party and partner |
| Pro | 20 | First-party and partner |
| Business | 50 | First-party, partner and private |
| Enterprise | Unlimited | First-party, partner and private |

In words: **2** installs on Free, **5** on Starter, **20** on Pro, **50** on Business and unlimited on Enterprise. The same app can be installed only **once** per workspace.

## Who can install an integration?

Only the **Owner** and **Admins** can install, suspend, reconnect or revoke an integration. Billing admins, Members and Guests cannot.

A Member can select **Request this app** on a listing. The Owner and Admins get a notification and can approve or decline. A request that nobody answers expires after **14 days**.

## How do I install an app?

1. Go to **Settings → Integrations → App directory** and open the app.
2. Check the scopes it asks for, then select **Install**.
3. Sign in to the other product (for example Slack) and approve the connection.
4. You are sent back to Acme Cloud and the install shows as `active`.

The sign-in step must be finished within **30 minutes**. After that the `pending` install expires and you need to select **Install** again. The full flow is in `services/integrations/docs/oauth-installs-and-scopes.md`.

## How do I remove an app?

Go to **Settings → Integrations**, open the install and select **Revoke**. The app loses access within **60 seconds**. Links between tasks and the other product (for example task to Jira issue) are kept for **30 days**, so reinstalling the app in that time restores them. After 30 days the links are deleted for good. Content in the workspace is never deleted when an app is removed.

## What are private apps?

Private apps let a customer connect their own internal tools with OAuth instead of a shared API key. They are available on **Business and Enterprise**. An account can register up to **10 private apps** at **Settings → Integrations → Private apps**. A private app follows the same scope rules as any other app and counts towards the install limit of each workspace it is installed in.

## What happens to integrations when I downgrade?

A downgrade is blocked while a workspace has more installs than the lower plan allows, or has an app kind the lower plan does not allow. For example, a Pro workspace with **8** installs must revoke **3** before moving to Starter. This matches the general downgrade rule in `services/accounts/docs/plans-and-limits.md`.

## How do partner apps get listed?

A partner submits the app to the Ecosystem team for review. The review checks that the app asks only for scopes it needs, has a working support contact and handles revocation correctly. Reviews take up to **10 business days**. Acme Cloud can remove a listing at any time; existing installs of a removed app are suspended and the Owner is emailed.

Last reviewed: 2026-11-26
