# Accounts Service

## What it does

The Accounts service owns the customer account: sign-up, plans, workspaces, members, roles, and closing or restoring accounts. It is the source of truth for which plan an account is on and what limits apply.

## Key concepts

- **Account** – billing and legal owner; one Owner per account.
- **Workspace** – container for projects and files; region fixed at creation.
- **Member / Guest** – people with access; members use seats, guests do not.
- **Plan** – Free, Starter, Pro, Business or Enterprise; sets limits and features.
- **Account states** – `trialing`, `active`, `past_due`, `read_only`, `closed`, `deleted`.

## How to use it

- Customer-facing settings live under **Settings → Account** and **Settings → Members**.
- Internal API base URL: `https://api.acme-cloud.example/v2/accounts`
- Common endpoints:
  - `GET /v2/accounts/{account_id}` – account details and current plan
  - `GET /v2/accounts/{account_id}/members` – list members
  - `POST /v2/accounts/{account_id}/members` – invite a member
  - `POST /v2/accounts/{account_id}/close` – close an account (Owner only)
  - `POST /v2/accounts/{account_id}/restore` – restore within 30 days

## Docs in this service

- `docs/account-lifecycle.md` – states, closing, restoring, deletion
- `docs/plans-and-limits.md` – limits and features per plan
- `docs/members-and-roles.md` – inviting, removing and role permissions
- `docs/workspaces.md` – creating, renaming, archiving and deleting workspaces, regions
- `docs/data-export-and-deletion.md` – workspace exports, deletion timeline, personal data erasure

## Code in this service

- `acme_accounts/lifecycle.py` – account state machine, legal transitions and retention windows
- `acme_accounts/plans.py` – plan limits table and limit checks
- `acme_accounts/roles.py` – role permission matrix, invitation and ownership-transfer rules
- `openapi.yaml` – OpenAPI 3.0 description of the `/v2/accounts` endpoints
- `config/default.yaml` – default service configuration (limits, timeouts, feature flags, regions)
- `tests/` – unit tests; run `python -m unittest discover -s tests` from this folder

## Owners

Team: Accounts Platform. Slack channel: `#team-accounts` (fictional).
