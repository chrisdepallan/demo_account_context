# Runbook – Notification Email Bounce Surge

## When to use this runbook

Use the notification email bounce surge runbook when an unusual share of the emails sent by Acme Cloud is rejected by receiving mail servers or marked as spam.

- Alert `NotificationsEmailBounceRateHigh` – more than **5%** of sent emails hard-bounced over **30 minutes**. The normal hard bounce rate is below **1%**.
- Alert `NotificationsEmailComplaintRateHigh` – more than **0.1%** of delivered emails were marked as spam over **24 hours**.
- Customers report that password reset emails, invitations or digests do not arrive.

The notification email bounce surge runbook is owned by Team Messaging. The Notifications service is described in `services/notifications/README.md`.

## Impact

An email bounce surge damages the sending reputation of `acme-cloud.example`. Mailbox providers then delay or reject all Acme Cloud email, including password reset links (valid for **60 minutes**), email verification links (valid for **24 hours**), failed-payment emails and renewal reminders. In-app and push notifications are not affected.

An email bounce surge is **SEV3** while transactional email still arrives. Missing password reset or verification email is **SEV2**.

## Diagnosis

1. Split the bounces by email type. Find out whether digests, invitations or transactional emails bounce.

```bash
psql "$NOTIFICATIONS_DB_URL" -h notifications-db.us-east.internal.acme-cloud.example -c "
  SELECT template, count(*) AS bounces
  FROM email_events
  WHERE event = 'hard_bounce' AND created_at > now() - interval '1 hour'
  GROUP BY template ORDER BY bounces DESC;"
```

2. Split the bounces by recipient domain. One domain suggests a problem at one mailbox provider or one customer. Many domains suggest a problem with Acme Cloud's sending setup.
3. Read the bounce reasons in the sender log.

```bash
kubectl --context prod-us-east -n notifications logs deploy/notifications-worker --since=30m | grep "bounce_reason" | tail -n 50
```

4. Check the DNS records that authenticate Acme Cloud email (SPF, DKIM and DMARC).

```bash
dig +short TXT acme-cloud.example
dig +short TXT _dmarc.acme-cloud.example
```

5. Check whether one account sent an unusual number of invitations. A bulk invitation to bad addresses is a common cause and can be abuse.
6. Check whether a Notifications deployment or a template change happened in the last **24 hours**.

The table and column names in the query are illustrative.

## Mitigation

1. Pause low-priority email first: digests and activity summaries. Keep transactional email (password resets, email verification, security alerts and billing emails) running.
2. If one account causes the surge through bulk invitations, pause invitation email for that account and tell Team Customer Support. Do not close the account without a decision from Team Trust and Compliance.
3. If an authentication record is broken, ask Team Platform Infrastructure to restore the DNS record. Do not resume paused email until the record is verified.
4. If a deployment or template change caused the surge, roll the deployment back with `kubectl rollout undo deploy/notifications-worker`.
5. Check that every hard-bounced address is on the suppression list, so that Acme Cloud stops sending to that address.
6. Resume paused email gradually: **25%** of normal volume for **1 hour**, then **50%** for **1 hour**, then **100%**.
7. Confirm recovery when the hard bounce rate is below **1%** for **2 hours**.

## Escalation

- Team Messaging, `#team-notifications` – first responder for both alerts.
- Team Platform Infrastructure, `#team-platform` – DNS records and outbound mail routing.
- Team Trust and Compliance, `#team-trust` – suspected abuse or a compromised account.
- Team Customer Support, `#support-escalations` – tell Support as soon as password reset or verification emails are delayed.

## After the incident

- Do not remove addresses from the suppression list in bulk. An address is removed only when its owner confirms that the address works.
- Tell users whose address was suppressed by mistake how to get email again.
- Record the bounce rate and complaint rate for the **7 days** after the incident to confirm that the sending reputation recovered.
- For a SEV2 incident, write a postmortem within **5 business days**.

Last reviewed: 2026-11-26
