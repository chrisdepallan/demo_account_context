# Subscription Changes

## Who can change the subscription?

Only the **Owner** and **Billing admins** can change the plan, the seat count or the billing cycle. All changes are made under **Settings → Billing → Subscription**. Enterprise subscriptions are changed through Sales at `sales@acme-cloud.example`.

## How do I upgrade my plan?

Go to **Settings → Billing → Subscription → Change plan** and choose the higher plan. The upgrade takes effect **immediately**. The price difference for the rest of the billing period is charged right away, prorated by day. The calculation is explained in `services/billing/docs/proration-and-credits.md`.

## How do I downgrade my plan?

Choose the lower plan under **Settings → Billing → Subscription → Change plan**. The downgrade is scheduled for the **end of the current billing period** and no partial refund is issued. Until then the account keeps every feature of the current plan.

- A downgrade is blocked if current usage is above the lower plan's limits, for example more members or more storage. Usage must be reduced first. Limits are listed in `services/accounts/docs/plans-and-limits.md`.
- A scheduled downgrade can be cancelled at any time before the period ends.

## How many seats can I have on each plan?

| Plan | Minimum seats | Maximum seats |
|------|---------------|---------------|
| Starter | **1** | **10** |
| Pro | **1** | **100** |
| Business | **1** | **500** |
| Enterprise | **50** | Unlimited |

Adding seats is charged immediately and removing seats gives a prorated credit on the next invoice. Guests do not use seats.

## How do I switch from monthly to annual billing?

Select **Settings → Billing → Subscription → Billing cycle → Annual**. The switch happens **immediately**:

1. A new annual period starts on the day of the switch.
2. The unused days of the current month are credited, prorated by day.
3. The annual invoice is issued, the credit is applied to it and the rest is charged.

Annual billing charges **10 months** for 12 months of service.

## How do I switch from annual to monthly billing?

Select **Monthly** in the same menu. The switch is scheduled for the **renewal date**, because annual plans are not refunded after the first **30 days**. Monthly billing then starts on the renewal date at the monthly list price.

## How do I cancel my subscription?

The Owner or a Billing admin goes to **Settings → Billing → Cancel subscription**. The plan stays active until the end of the paid period and then the account moves to **Free**. No data is deleted. Members over the Free limit of **3** become guests.

A cancellation can be undone under **Settings → Billing → Subscription → Resume** at any time before the paid period ends. Refunds after cancelling follow `services/billing/docs/refunds.md`.

## How do I subscribe again after moving to Free?

Choose a paid plan under **Settings → Billing → Subscription → Change plan**. A new billing period starts that day, and that day becomes the new charge date. Former members who became guests must be changed back to members by an Owner or Admin.

## Can I change my subscription while a payment is overdue?

No. While the account is `past_due` or `read_only`, upgrades, added seats and billing cycle changes are blocked. Updating the payment method is always allowed and triggers an immediate retry. Once the balance is paid, full access returns within **5 minutes**. The retry schedule is in `services/billing/docs/payment-methods.md`.

## Can I change my billing currency?

Not in the app. The billing currency is set at the first payment and can only be changed by support. Email `billing@acme-cloud.example` from the Owner's address.

## What is different for Enterprise?

Enterprise has a minimum of **50 seats** and an annual contract only. Seats can be added during the term at the contract price, prorated by day. Seat reductions and plan changes apply at renewal.

Last reviewed: 2026-11-26
