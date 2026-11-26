# Macros and Tone

## What is a macro?

A macro is a saved reply template that a support agent inserts into a ticket and then edits. Macros keep facts such as prices, timelines and steps consistent. A macro is a starting point: every reply must be adjusted to the customer's actual question before it is sent.

## How should a support reply be structured?

Every reply follows the same five parts, in this order:

1. **Greeting** – use the customer's first name.
2. **Answer** – give the answer or the decision in the first two sentences.
3. **Steps** – numbered steps with the exact UI path, for example **Settings → Billing → Invoices**.
4. **What happens next** – say who acts next and by when, with a concrete time such as **5–10 business days**.
5. **Sign-off** – the agent's first name and "Acme Cloud Support".

Keep a reply under **200 words** unless the steps need more.

## What tone do agents use?

- Write in plain, direct sentences. Use the words the customer used.
- Say what can be done before saying what cannot.
- Apologize once, specifically, when Acme Cloud made a mistake. Do not apologize for policy.
- Never blame the customer, another team or a named colleague.
- Avoid internal terms such as "Tier 2", "Jira" or "dunning". Say "our product specialists", "our engineers" or "payment retries".
- Do not promise a fix date for a bug. Promise the next update instead.

## Which macros are available?

| Macro | Use it when |
|-------|-------------|
| `general-need-more-info` | The request lacks the workspace ID, steps or a screenshot |
| `general-pending-reminder` | No customer reply after **3 days** |
| `general-closing-no-reply` | No customer reply after **7 days** |
| `billing-refund-approved` | A refund was issued; states the amount and the **5–10 business day** timeline |
| `billing-refund-declined` | The request is outside the refund policy |
| `billing-payment-failed` | The account is `past_due`; explains retries on Days **1, 3, 7 and 14** |
| `auth-mfa-reset-verification` | A customer asks for an MFA reset; starts identity verification |
| `account-owner-change` | A customer asks to change the account Owner |
| `incident-p1-acknowledged` | First reply on a **P1** ticket; links to `https://status.acme-cloud.example` |
| `bug-confirmed-on-hold` | A bug was passed to engineering and the ticket is `on_hold` |
| `feature-request-logged` | A **P4** feature request was recorded |

## Which placeholders can a macro contain?

Placeholders are filled in automatically from the ticket and the account:

- `{{customer_first_name}}` – first name of the requester
- `{{ticket_id}}` – for example `SUP-58213`
- `{{account_id}}` – for example `acc_7F3K9Q2M`
- `{{plan}}` – Free, Starter, Pro, Business or Enterprise
- `{{invoice_id}}` – for example `INV-2026-004812`
- `{{refund_amount}}` – amount and currency of the refund
- `{{agent_first_name}}` – first name of the replying agent

A reply cannot be sent while it still contains an unfilled placeholder.

## What must a reply never contain?

- A request for a password, a full card number or an MFA code.
- Another customer's data, including names of other accounts affected by the same incident.
- Links to internal tools, Jira issues or Slack channels.
- Payment details beyond the card brand and the last four digits.
- A promise outside policy, such as a refund the agent cannot approve. Refund limits are in `services/billing/docs/refunds.md`.

## How do agents reply to an angry customer?

Acknowledge the problem in one sentence, state what has already been done, and give the next update time. Do not use a macro for the first reply to a complaint. If the customer writes "escalate", a team lead reviews the ticket within **1 business day**, as described in `services/support/docs/sla-and-escalation.md`.

## How are macros created and reviewed?

Any agent can propose a macro in `#support-escalations`. A support team lead approves it before it is published. Every macro has an owner and is reviewed every **6 months**, and immediately after any change to prices, limits or policy. Macros that were not used for **12 months** are archived.

## How many macros can one reply use?

At most **2**. A reply built from more macros reads like a form letter and usually repeats itself. If a ticket needs more, write the reply by hand.

Last reviewed: 2026-11-26
