# Preferences and Digests

## How do I change my notification preferences?

Go to **Settings → Notifications**. Every notification type has three switches: email, in-app and push. Changes are saved immediately and apply to notifications created after the change. Every role can change their own preferences, including Guests.

## Which setting wins when my preference and the workspace default differ?

Acme Cloud checks three levels, in this order, for each type and channel:

1. **Your own setting** – if you changed the switch, your choice is used.
2. **The workspace default** – if you never changed it, the default set by the workspace Owner or Admin is used.
3. **The system default** – if neither exists, the default listed in `services/notifications/docs/notification-types.md` is used.

Mandatory types (`security_alert`, `billing_alert`, `account_notice`) are the exception: email and in-app stay on at every level.

## How do Admins set workspace defaults?

Owners and Admins go to **Settings → Workspace → Notification defaults**. A workspace default changes what members get when they have not made their own choice. It does not overwrite a setting a member already changed. Members, Billing admins and Guests cannot edit workspace defaults.

## Why is push or email not sent even though it is switched on?

A channel that is switched on can still be skipped for one of these reasons:

- **Push** – you have no registered device. Open the mobile app or allow browser notifications first.
- **Email** – your address is suppressed after a bounce. See `services/notifications/docs/email-deliverability.md`.
- **Quiet hours** – the notification is held until your quiet hours end.
- **Rate limit** – you passed **20 emails** or **30 push notifications** in the last hour.
- **Role** – your role cannot receive that type. For example, a Member does not get `billing_alert`.

## What is a digest?

A digest is one email that lists your **unread in-app notifications**. It is a safety net for things you did not open in the app. Digests are sent by email only. Notifications you already read are left out.

## When are digests sent?

| Frequency | Sent | Covers |
|-----------|------|--------|
| `daily` (default) | Every day at **08:00** in your time zone | The previous **24 hours** |
| `weekly` | Every **Monday** at **08:00** in your time zone | The previous **7 days** |
| `off` | Never | – |

Your time zone comes from **Settings → Profile → Time zone**. If none is set, **UTC** is used. New users start on the `daily` digest.

## How do I change or turn off the digest?

Go to **Settings → Notifications → Digest** and choose **Daily**, **Weekly** or **Off**. The digest footer also has an unsubscribe link that sets the frequency to `off`.

## What is in a digest?

- Unread notifications are grouped by project, with the most recent activity first.
- Notifications that do not belong to a project, such as `security_alert`, appear in a group called **Other**.
- A digest shows at most **50** notifications. If there are more, the email ends with a line such as "and 12 more" and a link to the in-app inbox.
- Emails and push notifications that were skipped because of the hourly rate limit are still in the in-app inbox, so they show up in the next digest if you have not read them.

## Why did I not get a digest today?

No digest is sent when you have **no unread notifications** in the period. A digest is also not sent when the frequency is `off` or when your email address is suppressed. A digest is sent at most once per day (daily) or once per week (weekly).

## Do digests count towards the hourly email limit?

No. The digest is exempt from the limit of **20 emails per hour** and is not held by quiet hours, because it is sent at a fixed time you can change or turn off.

Last reviewed: 2026-11-26
