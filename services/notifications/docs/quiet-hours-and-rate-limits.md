# Quiet Hours and Rate Limits

## What are quiet hours?

Quiet hours are a daily window in which Acme Cloud does not send you email or push notifications. Nothing is lost: held notifications are sent when the window ends. Quiet hours are **off by default**.

## How do I turn on quiet hours?

Go to **Settings → Notifications → Quiet hours** and switch them on. The default window is **22:00–07:00**. You can change the start and end time in steps of **15 minutes**. The window applies every day of the week and uses the time zone from **Settings → Profile → Time zone** (UTC if none is set).

## What happens to notifications during quiet hours?

| Channel | During quiet hours |
|---------|--------------------|
| Email | Held until the window ends |
| Push | Held until the window ends |
| In-app | Delivered as usual |

The window includes the start time and excludes the end time. With the default window, a notification at **22:00** is held and one at **07:00** is sent straight away. A window that starts and ends at the same time is treated as empty.

## Which notifications ignore quiet hours?

The three mandatory types are never held: `security_alert`, `billing_alert` and `account_notice`. A login from a new device, for example, is emailed at once even at night. Digest emails are also not held, because they have their own fixed time of **08:00**.

## What do I receive when quiet hours end?

Held notifications are released at the end time. To avoid a flood:

- If **10 or fewer** notifications were held on a channel, each one is sent separately.
- If **more than 10** were held on a channel, one summary is sent instead, for example "You have 14 new notifications", with a link to the in-app inbox.

## Can an Admin set quiet hours for everyone?

No. Quiet hours are a personal setting. Owners and Admins can set workspace defaults for notification types and channels only, as described in `services/notifications/docs/preferences-and-digests.md`.

## Is there a limit on how many notifications I get?

Yes. Each user has an hourly limit per channel, counted over a rolling **60 minutes**:

| Channel | Limit per user |
|---------|----------------|
| Email | **20 per hour** |
| Push | **30 per hour** |
| In-app | No limit |

The limits are the same on every plan.

## What happens to notifications over the limit?

A notification over the limit is not sent on that channel. It is still stored in the in-app inbox, and if it is still unread it appears in your next digest. It is not sent later as a separate email or push.

## Which notifications are exempt from the rate limit?

Mandatory types (`security_alert`, `billing_alert`, `account_notice`) and digest emails do not count towards the limits and are never blocked by them.

## In what order are the rules applied?

For each notification and channel, Acme Cloud decides in this order:

1. In-app is always delivered.
2. Mandatory types are sent immediately.
3. If quiet hours are active, the notification is held.
4. If the hourly limit is reached, the notification is left for the digest.
5. Otherwise it is sent and counted against the limit.

Held notifications do not count against the limit while they wait.

## Is there a limit for services that send notifications? (internal)

Yes. Each internal service may call `POST /v2/notifications/{account_id}/send` up to **600 times per minute** per account. Over that, the API returns `429` with a `Retry-After` header. One request can address up to **100 recipients**.

Last reviewed: 2026-11-26
