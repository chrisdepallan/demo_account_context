# Sessions and Devices

## What is a session?

A session is one signed-in browser or app. A session starts when a user logs in with a password, MFA or SSO, and ends when the user signs out, the session expires or someone revokes it. Session IDs look like `ses_8K2M4P9X1B` – the prefix `ses_` followed by **10** uppercase letters and digits.

## How long does a session last?

| Client | Expires after |
|--------|---------------|
| Web browser | 14 days of inactivity |
| Mobile app | 90 days of inactivity |

Web sessions expire after **14 days** of inactivity and mobile sessions after **90 days**. Any request made with the session counts as activity and restarts the timer.

## Can an Admin make sessions shorter?

Yes, on Business and Enterprise. Admins go to **Settings → Security → Session length** and set the web inactivity limit to any value between **1 hour** and **14 days**. The mobile limit of 90 days cannot be changed. A shorter limit applies to existing sessions at their next request.

## Where can I see my signed-in devices?

Every user can open **Profile → Security → Sessions**. The list shows each session's device type, browser or app, approximate location, sign-in time and last activity. The session being used is marked **This device**.

## How do I sign out of a device I no longer have?

Open **Profile → Security → Sessions**, find the device and select **Sign out**. To end every session except the current one, select **Sign out everywhere else**. Revocation takes effect within **60 seconds**.

## How many devices can I be signed in on?

Up to **10** sessions per user at the same time. Signing in on an 11th device ends the session that has been inactive the longest.

## Can an Admin sign a member out?

Yes. Owners and Admins go to **Settings → Members**, choose the member and select **Sign out all sessions**. This is useful when a device is lost or a member is leaving. It does not remove the member or free their seat.

## When are sessions ended automatically?

- The user resets or changes their password – all other sessions are signed out.
- An Admin resets the user's MFA – all of the user's sessions are signed out.
- The member is removed from the workspace – access ends immediately.
- The user is deactivated through SCIM – sessions end within **5 minutes**. See `services/auth/docs/scim-provisioning.md`.
- The account is closed – all members are signed out.
- An Admin turns on **Enforce SSO** – password sessions on the verified domain end and users sign in again through the identity provider.

## Will I be told about a new sign-in?

Yes. When a login comes from a device or browser not seen in the last **90 days**, the user gets a "New sign-in" email with the device type, approximate location and time. If the sign-in was not theirs, they should reset the password and review **Profile → Security → Sessions**. Password rules and resets are described in `services/auth/docs/passwords-and-mfa.md`.

## Do API keys use sessions?

No. API keys are separate from sessions and are not affected by session limits or by signing out. To stop programmatic access, revoke the key as described in `services/auth/docs/api-keys.md`.

Last reviewed: 2026-11-26
