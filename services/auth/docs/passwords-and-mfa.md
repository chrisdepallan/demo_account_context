# Passwords and MFA

## What are the password rules?

- At least **12 characters**, at most 128.
- Must not appear in known breached-password lists.
- Must not contain the user's email address.
- The last **5 passwords** cannot be reused.
- There is no forced expiry unless the workspace Admin sets one (30, 60 or 90 days).

## How do I reset my password?

1. Select **Forgot password** on the login page and enter the account email.
2. A reset link is emailed. It is valid for **60 minutes** and can be used once.
3. After resetting, all other sessions are signed out.

Users who log in only through SSO cannot reset their password in Acme Cloud; they must reset it with their identity provider.

## Why is my account locked?

After **5 failed login attempts within 15 minutes**, the login is locked for **15 minutes**. After 10 failed attempts within an hour, it is locked for **1 hour** and the user gets an email. Resetting the password unlocks the account immediately.

## Which MFA methods are supported?

- Authenticator app (TOTP, for example Google Authenticator, Microsoft Authenticator, 1Password)
- Security key (FIDO2/WebAuthn, for example YubiKey) and passkeys
- SMS codes (not available for Admins and Owners on Business and Enterprise)

## Can Admins require MFA?

Yes. Admins on Pro and above can turn on **Settings → Security → Require MFA**. Members without MFA must set it up at their next login, with a **7-day** grace period.

## What are backup codes?

When MFA is set up, the user gets **10 single-use backup codes**. Each code works once. New codes can be generated at any time from **Profile → Security**, which invalidates the old ones.

## I lost my MFA device and backup codes. What now?

- **If the workspace has another Admin**: the Admin can reset the user's MFA from **Settings → Members → Reset MFA**.
- **If the user is the only Admin or the Owner**: contact support. Support verifies identity using the billing details and a video call, and the reset takes up to **2 business days**. Support will never reset MFA based on email alone.

## How long do sessions last?

Web sessions expire after **14 days** of inactivity, mobile sessions after **90 days**. Admins on Business and Enterprise can shorten the web limit to between 1 hour and 14 days.

Last reviewed: 2026-11-19
