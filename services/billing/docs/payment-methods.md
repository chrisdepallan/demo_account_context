# Payment Methods

## What payment methods are accepted?

| Method | Plans | Notes |
|--------|-------|-------|
| Credit / debit card (Visa, Mastercard, Amex, Discover) | All paid plans | Default method |
| PayPal | Monthly and annual, Starter to Business | Not available in India |
| UPI | India only, all paid plans | Billed in INR |
| ACH bank transfer (US) | Annual plans over $1,000 | 3–5 business days to clear |
| SEPA bank transfer (EU) | Annual plans over €1,000 | 1–3 business days to clear |
| Invoice, net-30 | Enterprise | PO numbers supported |

## How do I update my card?

The Owner or a Billing admin goes to **Settings → Billing → Payment method → Update**. The new card is verified with a temporary $0 authorization. Acme Cloud never stores full card numbers; cards are held by the payment processor.

## When am I charged?

- Monthly plans: on the same day each month as the first payment. If that day does not exist in a month (for example the 31st), the charge happens on the last day of the month.
- Annual plans: once a year on the renewal date. A reminder email is sent **30 days** and **7 days** before renewal.

## What happens if a payment fails?

1. **Day 0** – the charge fails; the account moves to `past_due` and the Owner and Billing admins are emailed.
2. **Days 1, 3, 7 and 14** – the payment is retried automatically.
3. **Day 14** – if still unpaid, the account becomes `read_only`.
4. **Day 44** – if still unpaid, the account is downgraded to Free. Members over the Free limit become guests.

Updating the payment method at any point triggers an immediate retry. Paying the outstanding balance restores full access within **5 minutes**.

## Why was my card declined?

Common reasons are insufficient funds, an expired card, a wrong billing postcode or a bank blocking an international charge (Acme Cloud bills from the USA). Support cannot see the bank's exact reason; the customer should contact their bank.

Last reviewed: 2026-11-19
