# Proration and Credits

## What is proration?

Proration means paying only for the part of a billing cycle that is actually used. When seats or the plan change in the middle of a cycle, Acme Cloud charges or credits the difference **by day** for the rest of that cycle. Full list prices are in `services/billing/docs/pricing.md`.

## How is a prorated amount calculated?

The formula is the same for monthly and annual billing:

`prorated amount = price per seat for the full cycle × seats changed × remaining days ÷ days in the cycle`

- **Remaining days** – counted from the day of the change to the end of the cycle. The day of the change counts as a remaining day.
- **Days in the cycle** – the real length of the cycle: **28–31 days** for monthly billing and **365 or 366 days** for annual billing.
- **Rounding** – the result is rounded to **2 decimal places**, half up, in the billing currency.

A change made on the first day of a cycle is charged at the full price.

## Can I see some proration examples?

| Change | Cycle | Remaining days | Result |
|--------|-------|----------------|--------|
| Add 4 Pro seats on 2026-11-16 | Monthly, 2026-11-01 to 2026-12-01 (30 days) | 15 | **$30.00** charged immediately |
| Remove 3 Business seats on 2026-11-21 | Monthly, 2026-11-01 to 2026-12-01 (30 days) | 10 | **$29.00** credit on the next invoice |
| Add 2 Pro seats on 2026-10-20 | Annual, 2026-01-01 to 2027-01-01 (365 days) | 73 | **$60.00** charged immediately |
| Upgrade 10 seats from Starter to Pro on 2026-11-16 | Monthly, 2026-11-01 to 2026-12-01 (30 days) | 15 | **$35.00** charged immediately |

## When am I charged for seats I add?

Immediately. Adding seats creates a separate invoice for the prorated amount and charges the default payment method on the same day. The new seats can be used as soon as the charge succeeds. From the next cycle the new seat count is billed at the full price.

## What happens when I remove seats?

The seats are removed straight away and the unused days are returned as **account credit**, which is applied to the next invoice. Removing seats never produces a cash refund. The refund policy is in `services/billing/docs/refunds.md`.

## Is a plan change prorated?

- **Upgrade** – yes. The price difference between the two plans for the remaining days is charged immediately.
- **Downgrade** – no. A downgrade takes effect at the end of the current billing period, so there is nothing to prorate and no partial refund.

Steps for changing a plan are in `services/billing/docs/subscription-changes.md`.

## What is account credit?

Account credit is a balance held on the account in its billing currency. It is used on the next invoice **before** the payment method is charged. Credit comes from four sources:

- Seats removed mid-cycle (prorated by day).
- SLA service credits after an outage, up to **50%** of that month's fee.
- Credits issued by a support agent, for example as a goodwill gesture.
- A refund that bounced and was converted to credit.

## How is credit applied to an invoice?

Credit is subtracted from the invoice total, including tax. If the credit is larger than the invoice, the invoice is closed at **0.00** and the rest of the credit stays on the account for the following invoice. An invoice can never become negative.

## Where do I see my credit balance?

The Owner and Billing admins can see the balance and every credit entry under **Settings → Billing → Credits**. Each invoice PDF also shows the credit that was applied to it.

## Does account credit expire?

No. Credit does not expire while the account is open. Credit cannot be converted to cash, moved to another account or used in a different currency. When an account is closed, unused credit is removed at the end of the **30-day** data retention window.

## How is tax handled on prorated amounts?

Tax is calculated on the prorated amount at the rate for the billing address, in the same way as on a full invoice. Tax rules are in `services/billing/docs/invoices-and-taxes.md`.

## Who can issue a credit? (support agents)

Credits are issued with `POST /v2/billing/{account_id}/credits` or from the admin console. The approval limits match the refund limits: any support agent up to **$500**, a support team lead from **$500.01 to $5,000**, and the billing manager above **$5,000**. Every credit must carry the support ticket number, for example `SUP-58213`, in the reason field.

Last reviewed: 2026-11-26
