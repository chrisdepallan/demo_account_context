# Frequently Asked Questions

Short answers to the questions customers ask most. Each answer links to the service doc with the full details.

## How much does Acme Cloud cost?

- Free: $0, up to 3 members
- Starter: $8 per seat per month
- Pro: $15 per seat per month
- Business: $29 per seat per month
- Enterprise: custom pricing, minimum 50 seats

Annual billing gives 2 months free. Details: `services/billing/docs/pricing.md`.

## Is there a free trial?

Yes. Every new account gets a **14-day free trial of the Pro plan**, with no credit card required. When the trial ends without a payment method, the account drops to the Free plan automatically. No data is deleted.

## What is the refund policy?

- Annual plans: full refund if requested within **30 days** of the purchase or renewal date.
- Monthly plans: no refunds for the current month; cancel any time to stop the next charge.
- Refunds go back to the original payment method within **5–10 business days**.

Details: `services/billing/docs/refunds.md`.

## How do I cancel my subscription?

The account Owner or a Billing admin goes to **Settings → Billing → Cancel subscription**. The plan stays active until the end of the paid period and then moves to Free.

## How do I close or delete my account?

Only the Owner can close the account, from **Settings → Account → Close account**. Data is kept for **30 days** and can be restored during that time. After 30 days it is permanently deleted. Details: `services/accounts/docs/account-lifecycle.md`.

## How do I reset my password?

Use **Forgot password** on the login page. The reset link is valid for **60 minutes** and can be used once. Details: `services/auth/docs/passwords-and-mfa.md`.

## I lost access to my MFA device. What now?

Use one of your 10 backup codes. If you have none, contact support. Identity verification takes up to **2 business days**. Details: `services/auth/docs/passwords-and-mfa.md`.

## How many members can I add?

- Free: 3 members
- Starter: 10 members
- Pro: 100 members
- Business: 500 members
- Enterprise: unlimited

## How much storage do I get?

- Free: 2 GB total
- Starter: 10 GB per seat
- Pro: 50 GB per seat
- Business: 200 GB per seat
- Enterprise: 1 TB per seat

Maximum single file upload: 250 MB on Free and Starter, 5 GB on Pro and above.

## What payment methods do you accept?

Visa, Mastercard, American Express and Discover cards on all plans. PayPal on Starter to Business (not in India). UPI for Indian accounts. ACH and SEPA bank transfer on annual plans over $1,000. Invoicing with net-30 terms on Enterprise. Details: `services/billing/docs/payment-methods.md`.

## What happens if my payment fails?

Payment is retried on days 1, 3, 7 and 14. The account stays fully active during the **14-day grace period**. After that it becomes read-only. After 30 more days unpaid it is downgraded to Free.

## How do I contact support?

- Email: `support@acme-cloud.example` (all plans)
- Live chat: Pro and above, business hours
- Phone: Business and Enterprise
- 24/7 critical support: Enterprise only

Details: `services/support/docs/sla-and-escalation.md`.

## Can I change the owner of my account?

Yes. The current Owner goes to **Settings → Account → Transfer ownership** and picks an existing Admin. The new Owner must accept within **7 days** or the request expires.

## Do you charge sales tax or VAT?

Yes, where required. US sales tax is charged based on the billing address. EU VAT is charged at the local rate unless a valid VAT ID is provided (reverse charge). Details: `services/billing/docs/invoices-and-taxes.md`.

## How many projects can I have?

Free workspaces can have **5** active projects, Starter **50** and Pro **500**. Business and Enterprise have no limit. Archived projects do not count. Details: `services/projects/docs/projects-and-tasks.md`.

## How do I get a deleted file back?

Open **Files → Trash** and restore the file. Deleted files stay in the trash for **30 days** on every plan and are then removed permanently. Details: `services/files/docs/versioning-and-trash.md`.

## Can I share a file with someone outside my workspace?

Yes. Create a sharing link with the audience set to anyone with the link. Free plans can create view-only public links; password protection needs Starter or above. Details: `services/files/docs/sharing-links.md`.

## How do I stop notification emails at night?

Turn on quiet hours under **Settings → Notifications**. The default window is **22:00–07:00**. Security, billing and account notices are still delivered. Details: `services/notifications/docs/quiet-hours-and-rate-limits.md`.

## Do you support webhooks?

Yes, on Starter and above. Owners and Admins add endpoints under **Settings → Webhooks**. Every delivery is signed, and failed deliveries are retried up to **8 times** over about **45 hours**. Details: `services/webhooks/README.md`.

## Why can't I find something I just created in search?

New and changed projects, tasks and file names normally appear in search within **30 seconds**. Text inside files can take up to **5 minutes** and is searchable on Pro and above only. Details: `services/search/docs/indexing-and-freshness.md`.

## Is there an audit log?

Yes, on Pro and above. Entries are kept for **90 days** on Pro, **1 year** on Business and **7 years** on Enterprise. Only Owners and Admins can view the audit log. Details: `services/audit-log/docs/retention-and-export.md`.

## Which integrations are available?

Slack, GitHub, Jira and Google Workspace are built by Acme Cloud and available on every plan. Free workspaces can install **2** apps, Starter **5**, Pro **20** and Business **50**. Details: `services/integrations/docs/app-directory.md`.

## Can I get reports emailed on a schedule?

Yes, on Starter and above. Owners and Admins can schedule daily, weekly or monthly reports as PDF, CSV or XLSX. Details: `services/analytics/docs/scheduled-reports-and-exports.md`.

## Where can I see past incidents?

Current and past incidents are shown on `https://status.acme-cloud.example`. Internal postmortems are in `reports/incidents/`.

Last reviewed: 2026-11-26
