# Email Deliverability

## Which address do notification emails come from?

All notification and digest emails are sent from `notifications@acme-cloud.example`. Replies to that address are not read. To reach a person, write to `support@acme-cloud.example`.

## How fast should a notification email arrive?

Emails are normally handed to your mail provider within **60 seconds** of the event. If nothing arrives after **15 minutes**, follow the checks in the next section.

## Why am I not getting notification emails?

Check these in order:

1. Look in the spam or junk folder and mark the message as "not spam".
2. Confirm the address under **Settings → Profile → Email** is correct and verified.
3. Check that email is switched on for the type under **Settings → Notifications**.
4. Check whether quiet hours are on. Email is held until quiet hours end.
5. Look for a banner in the app saying "We can't deliver email to your address". That means the address is suppressed.
6. Ask your IT team to allow mail from the domain `acme-cloud.example`.

If the problem continues, contact support and include the time and type of the missing email.

## How does Acme Cloud authenticate its email?

Outgoing mail is authenticated with **SPF**, **DKIM** (2048-bit keys) and a **DMARC** policy of `p=reject` on `acme-cloud.example`. Mail that claims to be from Acme Cloud but fails these checks is not from us and should be reported to `support@acme-cloud.example`.

## What happens when an email bounces?

| Bounce type | Example cause | What Acme Cloud does |
|-------------|---------------|----------------------|
| Hard bounce | Address does not exist, domain invalid | Address is suppressed immediately |
| Soft bounce | Mailbox full, mail server temporarily down | Retried **3 times**: after **5 minutes**, **30 minutes** and **2 hours** |
| Repeated soft bounce | **5 messages in a row** soft-bounce after all retries | Address is suppressed for **7 days** |
| Spam complaint | Recipient marks a message as spam | Non-mandatory email is suppressed |

## What does suppression mean?

A suppressed address gets no notification or digest email. In-app and push notifications still work, and the user sees a banner in the app.

- After a **hard bounce**, no email at all can be sent, including mandatory types. The suppression stays until the address is verified again.
- After **repeated soft bounces**, the suppression ends automatically after **7 days**.
- After a **spam complaint**, mandatory types (`security_alert`, `billing_alert`, `account_notice`) are still emailed. Everything else is suppressed until the user turns email back on.

## How do I fix a suppressed address?

Go to **Settings → Profile → Email** and select **Verify again**, or change to a working address. Once the verification link is clicked, the suppression is removed within **5 minutes**. Owners and Admins can see which members are affected under **Settings → Members**, where the member is labelled "Email bouncing".

## How do I unsubscribe from an email?

Every non-mandatory email has an **Unsubscribe** link in the footer and supports one-click unsubscribe in mail clients. Unsubscribing turns off email for **that notification type only** and takes effect immediately. In-app and push settings are not changed. Mandatory emails have no unsubscribe link.

## Are member invitation emails affected by preferences?

No. Invitation emails are sent to people who do not have preferences yet, so they are always sent. An invitation expires after **7 days** and can be resent, as described in `services/accounts/docs/members-and-roles.md`.

## Can notification emails come from our own domain?

Only on **Enterprise**. The customer adds DNS records that Acme Cloud provides, and the Customer Success Manager enables the custom sender once the records verify. On all other plans the sender is `notifications@acme-cloud.example`.

## How do support agents check delivery? (support agents)

1. Open the account in the admin console and select **Notifications → Suppressions**, or call `GET /v2/notifications/{account_id}/suppressions`.
2. Check the reason: `hard_bounce`, `soft_bounce` or `complaint`.
3. Ask the customer to verify the address again. Agents do not remove a `hard_bounce` suppression by hand.
4. The email delivery log covers the last **30 days**. Older deliveries cannot be traced.

Last reviewed: 2026-11-26
