# Billing Service

## What it does

The Billing service handles subscriptions, pricing, invoices, payment methods, taxes, refunds and credits. It reads the plan and seat count from the Accounts service and charges the customer.

## Key concepts

- **Subscription** – the account's plan, seat count and billing cycle (monthly or annual).
- **Invoice** – issued on every charge; IDs look like `INV-2026-004812`.
- **Proration** – partial charges or credits when seats or plans change mid-cycle.
- **Grace period** – 14 days after a failed payment before the account goes read-only.
- **Credit** – account balance applied to the next invoice before charging the card.

## How to use it

- Customer-facing settings: **Settings → Billing** (Owner and Billing admin only).
- Internal API base URL: `https://api.acme-cloud.example/v2/billing`
- Common endpoints:
  - `GET /v2/billing/{account_id}/subscription`
  - `GET /v2/billing/{account_id}/invoices`
  - `POST /v2/billing/{account_id}/refunds` – support agents only
  - `POST /v2/billing/{account_id}/credits` – support agents only

## Docs in this service

- `docs/pricing.md` – prices, billing cycles, discounts
- `docs/payment-methods.md` – accepted methods, failed payments
- `docs/invoices-and-taxes.md` – invoices, sales tax and VAT
- `docs/refunds.md` – refund policy and how to issue refunds
- `docs/proration-and-credits.md` – how mid-cycle changes are prorated and how account credit works
- `docs/subscription-changes.md` – upgrades, downgrades, seat changes, billing cycle switches, cancelling

## Code in this service

- `acme_billing/pricing.py` – price table per plan, billing cycle and currency; discounts; invoice subtotal
- `acme_billing/proration.py` – prorated charges and credits for seat and plan changes; applying account credit
- `acme_billing/dunning.py` – failed-payment schedule (Days 0, 1, 3, 7, 14 and 44) and account status
- `acme_billing/refunds.py` – refund eligibility, approval thresholds and SLA service credits
- `openapi.yaml` – OpenAPI 3.0 spec for the `/v2/billing` endpoints
- `config/default.yaml` – default service configuration (limits, timeouts, feature flags, per-region settings)
- `tests/` – unit tests; run `python -m unittest discover -s tests` from this folder

## Not indexed

`fixtures/` holds sample invoice data for tests. It is excluded from the MCP index.

## Owners

Team: Revenue Engineering. Slack channel: `#team-billing` (fictional).
