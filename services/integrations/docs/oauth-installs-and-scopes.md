# OAuth Installs and Scopes

## How does installing an app work?

Every app is installed with the OAuth 2.0 authorization code flow with PKCE. No password or API key is shared with the app.

1. An Owner or Admin selects **Install** at **Settings → Integrations → App directory**. Acme Cloud creates an install in the `pending` state with an ID such as `int_4K9T2M`.
2. The browser is sent to `https://auth.acme-cloud.example/oauth/authorize`, which shows the consent screen listing the scopes.
3. After approval the app receives an authorization code, valid for **10 minutes** and usable once.
4. The app exchanges the code for tokens and the install becomes `active`.

If the flow is not finished within **30 minutes**, the `pending` install expires and is revoked automatically.

## What states can an install be in?

| State | Meaning | Counts towards the install limit |
|------|---------|----------------------------------|
| `pending` | Install started, consent not finished | No |
| `active` | Connected and syncing | Yes |
| `suspended` | Connected but paused; no sync and no API access | Yes |
| `revoked` | Disconnected for good; tokens deleted | No |

Allowed changes are `pending` → `active`, `pending` → `revoked`, `active` → `suspended`, `suspended` → `active`, `active` → `revoked` and `suspended` → `revoked`. A `revoked` install never changes state again; installing the app again creates a new install with a new ID.

## Why was my integration suspended?

An install is suspended when one of these happens:

- **5 consecutive failures** of a sync run or token refresh, for example because the app was removed on the other side.
- The account moves to `read_only` (see `services/accounts/docs/account-lifecycle.md`). The install resumes by itself when the account is `active` again.
- An Owner or Admin selects **Pause**.
- The app's listing is removed from the app directory.

The Owner and Admins are emailed on suspension. To resume, open the install at **Settings → Integrations** and select **Reconnect**. An install left suspended for **60 days** is revoked automatically.

## What scopes can an integration have?

Integrations use the same scope names as API keys (see `services/auth/docs/api-keys.md`).

| Scope | Allows | Notes |
|------|--------|-------|
| `projects:read` | Read projects, tasks and comments | |
| `projects:write` | Create and edit projects, tasks and comments | Includes `projects:read` |
| `files:read` | Read file names, metadata and content | |
| `files:write` | Upload, attach and rename files | Includes `files:read` |
| `members:read` | Read member names, emails and roles | |
| `members:write` | Invite and remove members | Restricted; includes `members:read` |
| `billing:read` | Read invoices and plan | Never granted to integrations |

A write scope always includes the matching read scope. `billing:read` cannot be granted to any integration. An install can hold at most **6 scopes**, which is every scope except `billing:read`.

## Who can approve scopes?

- The **Owner** and **Admins** can approve any install that does not ask for a restricted scope.
- Only the **Owner** can approve an install that asks for the restricted scope `members:write`.
- Billing admins, Members and Guests cannot approve installs.

## What does least privilege mean for apps?

An app should ask only for the scopes its features need. The consent screen shows a warning when an app asks for more than its listing declares. The first-party apps ask for:

| App | Scopes requested |
|------|------------------|
| Slack | `projects:read`, `projects:write`, `members:read` |
| GitHub | `projects:read`, `projects:write` |
| Jira | `projects:read`, `projects:write`, `members:read` |
| Google Workspace | `files:read`, `files:write`, `members:read` |

## What happens when an app needs more scopes?

Adding a scope needs fresh consent. The Owner and Admins see **Review new permissions** on the install. Until someone approves, the install keeps working with its old scopes. The request expires after **14 days**. Removing a scope never needs consent and takes effect within **60 seconds**.

## How long do integration tokens last?

| Token | Lifetime |
|------|----------|
| Authorization code | 10 minutes, single use |
| Access token | 1 hour |
| Refresh token | 90 days, replaced on every use |

Access tokens last **1 hour**. Refresh tokens last **90 days** and are rotated each time they are used, so an install that syncs normally never expires. Using an old refresh token a second time revokes the whole install, because it suggests the token was copied. Revoking an install deletes its tokens within **60 seconds**.

## Do integration requests count against the API rate limit?

Requests from first-party apps do not count. Requests from partner and private apps count against the account's API rate limit in `services/accounts/docs/plans-and-limits.md`, and get HTTP `429` with a `Retry-After` header when over the limit.

Last reviewed: 2026-11-26
