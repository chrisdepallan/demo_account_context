# Notifications Service

## What it does

The Notifications service tells people about activity that concerns them: mentions, task assignments, shared files, security and billing alerts. It delivers over three channels (email, in-app and push), applies each user's preferences, quiet hours and rate limits, and builds the daily and weekly digest emails. Other services (Projects, Files, Accounts, Billing, Auth) ask it to send; it decides who gets what and on which channel.

## Key concepts

- **Notification** – one message for one recipient; IDs look like `ntf_8K2M4Q7T1X`. In-app notifications are kept for **90 days**.
- **Channel** – `email`, `in_app` or `push`. Each notification type has a default setting per channel.
- **Notification type** – the reason for the message, for example `mention`, `task_assigned` or `security_alert`. There are **11** types.
- **Mandatory type** – `security_alert`, `billing_alert` and `account_notice`. Email and in-app cannot be turned off for these.
- **Preference resolution** – user setting first, then the workspace default, then the system default.
- **Digest** – one email summarising unread in-app notifications; `daily` (default), `weekly` or `off`; at most **50** items.
- **Quiet hours** – a daily window (default **22:00–07:00**, off until enabled) in which email and push are held.
- **Rate limit** – at most **20 emails** and **30 push notifications** per user per hour; the rest wait for the digest.
- **Suppression** – an email address the service has stopped sending to after a hard bounce, repeated soft bounces or a spam complaint.

## How to use it

- Personal settings: **Settings → Notifications** (every role, including Guests).
- Workspace defaults: **Settings → Workspace → Notification defaults** (Owner and Admin only).
- In-app inbox: the bell icon at `https://app.acme-cloud.example`.
- Internal API base URL: `https://api.acme-cloud.example/v2/notifications`
- Common endpoints:
  - `GET /v2/notifications/{account_id}/inbox` – list the calling user's in-app notifications
  - `POST /v2/notifications/{account_id}/inbox/{notification_id}/read` – mark one notification as read
  - `POST /v2/notifications/{account_id}/inbox/read-all` – mark everything as read
  - `GET /v2/notifications/{account_id}/preferences` – the calling user's preferences
  - `PUT /v2/notifications/{account_id}/preferences` – replace the calling user's preferences
  - `GET /v2/notifications/{account_id}/workspaces/{workspace_id}/defaults` – workspace defaults
  - `PUT /v2/notifications/{account_id}/workspaces/{workspace_id}/defaults` – Owner and Admin only
  - `POST /v2/notifications/{account_id}/send` – internal services only
  - `GET /v2/notifications/{account_id}/suppressions` – support agents only

## Docs in this service

- `docs/notification-types.md` – the 11 notification types, channels, defaults and who receives each
- `docs/preferences-and-digests.md` – changing preferences, workspace defaults, daily and weekly digests
- `docs/email-deliverability.md` – sender address, missing emails, bounces, suppression, unsubscribing
- `docs/quiet-hours-and-rate-limits.md` – quiet hours, held notifications, hourly limits per user

## Code in this service

- `acme_notifications/preferences.py` – notification types, role eligibility and channel preference resolution
- `acme_notifications/digest.py` – digest schedule, time window and grouping of unread notifications
- `acme_notifications/quiet_hours.py` – quiet-hours window, release of held notifications and the per-user rate limiter
- `openapi.yaml` – OpenAPI 3.0 spec for the endpoints listed above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings
- `tests/` – `unittest` tests; run `python -m unittest discover -s tests` from this folder

## Owners

Team: Messaging. Slack channel: `#team-notifications` (fictional).
