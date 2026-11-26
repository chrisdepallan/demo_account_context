# Integrations Service

## What it does

The Integrations service runs the app directory and the first-party integrations with Slack, GitHub, Jira and Google Workspace. It handles OAuth app installs, the scopes each install is granted, and the background sync that keeps linked tasks, files and messages up to date. It reads the plan and member roles from the Accounts service to decide how many installs a workspace may have and who may approve them.

## Key concepts

- **App** – an entry in the app directory, identified by a slug such as `slack`, `github`, `jira` or `google-workspace`.
- **Install** – one app connected to one workspace; IDs look like `int_4K9T2M`.
- **Install states** – `pending`, `active`, `suspended`, `revoked`. `revoked` is final.
- **Scope** – a permission granted to an install, such as `projects:read`. Integrations use the same scope names as API keys.
- **Install limit** – active and suspended installs per workspace: **2** on Free, **5** on Starter, **20** on Pro, **50** on Business, unlimited on Enterprise.
- **Sync cursor** – an opaque marker of how far an incremental sync has read; it expires after **7 days**.
- **Source of truth** – the side that wins when the same field changes on both sides within **60 seconds**; Acme Cloud by default.

## How to use it

- Customer-facing settings: **Settings → Integrations** (Owner and Admin only). The app directory is at **Settings → Integrations → App directory**.
- Internal API base URL: `https://api.acme-cloud.example/v2/integrations`
- Common endpoints:
  - `GET /v2/integrations/apps` – list apps in the directory
  - `GET /v2/integrations/apps/{app_slug}` – one app and the scopes it asks for
  - `GET /v2/integrations/{workspace_id}/installs` – list installs in a workspace
  - `POST /v2/integrations/{workspace_id}/installs` – start an install (returns a `pending` install and an authorize URL)
  - `GET /v2/integrations/{workspace_id}/installs/{integration_id}` – install details
  - `PATCH /v2/integrations/{workspace_id}/installs/{integration_id}` – suspend or resume an install
  - `DELETE /v2/integrations/{workspace_id}/installs/{integration_id}` – revoke an install
  - `GET /v2/integrations/{workspace_id}/installs/{integration_id}/sync` – sync status
  - `POST /v2/integrations/{workspace_id}/installs/{integration_id}/sync` – request a manual resync

## Docs in this service

- `docs/app-directory.md` – what apps exist, plan limits, who can install
- `docs/oauth-installs-and-scopes.md` – the OAuth install flow, install states, scopes and token lifetimes
- `docs/slack-and-github.md` – what the Slack and GitHub integrations do and how to set them up
- `docs/sync-and-troubleshooting.md` – sync timing, conflict rules, Jira and Google Workspace sync, fixing common problems

## Code in this service

- `acme_integrations/scopes.py` – scope catalog, validation and least-privilege checks
- `acme_integrations/installs.py` – install state machine and per-plan install limits
- `acme_integrations/sync.py` – sync cursor, retry delays and conflict resolution rules
- `openapi.yaml` – OpenAPI 3.0 spec for the endpoints above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings
- `tests/` – `unittest` tests; run `python -m unittest discover -s tests` from this folder

## Owners

Team: Ecosystem. Slack channel: `#team-ecosystem` (fictional).
