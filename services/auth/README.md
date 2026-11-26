# Auth Service

## What it does

The Auth service handles how people and programs prove who they are: email/password login, multi-factor authentication (MFA), single sign-on (SSO), sessions and API keys.

## Key concepts

- **Session** – a signed-in browser or app; sessions last 14 days of inactivity on web and 90 days on mobile.
- **MFA** – a second factor (authenticator app, security key or SMS) on top of the password.
- **SSO** – login through the customer's identity provider via SAML 2.0 or OIDC (Business and Enterprise).
- **API key** – a secret token for programmatic access, scoped to one workspace.
- **Lockout** – temporary block after too many failed logins.

## How to use it

- Login page: `https://app.acme-cloud.example/login`
- Security settings: **Settings → Security** (Admins and Owner)
- Personal settings: **Profile → Security** (every user)
- Internal API base URL: `https://api.acme-cloud.example/v2/auth`

## Docs in this service

- `docs/passwords-and-mfa.md` – password rules, resets, lockouts, MFA
- `docs/sso.md` – SAML/OIDC setup and troubleshooting
- `docs/api-keys.md` – creating, rotating and revoking API keys
- `docs/sessions-and-devices.md` – session length, signed-in devices, signing out remotely
- `docs/scim-provisioning.md` – SCIM setup, tokens, deactivation and role mapping

## Code in this service

- `acme_auth/password_policy.py` – password rules, history, forced expiry and reset links
- `acme_auth/lockout.py` – failed-login lockout rules
- `acme_auth/api_keys.py` – key prefixes, scopes, expiry and per-workspace limits
- `openapi.yaml` – OpenAPI 3.0 description of the `/v2/auth` endpoints
- `config/default.yaml` – default service configuration (limits, timeouts, feature flags, regions)
- `tests/` – unit tests; run `python -m unittest discover -s tests` from this folder

## Owners

Team: Identity. Slack channel: `#team-identity` (fictional).
