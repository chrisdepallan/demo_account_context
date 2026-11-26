# Ticket Lifecycle

## How is a support ticket created?

A ticket is created automatically when a customer emails `support@acme-cloud.example`, starts a live chat, calls the support line or submits the form at `https://help.acme-cloud.example`. Each ticket gets an ID such as `SUP-58213` and the customer receives an automatic acknowledgement with that ID. The channels open to each plan are listed in `services/support/docs/sla-and-escalation.md`.

## What statuses can a ticket have?

| Status | Meaning | Who acts next |
|--------|---------|---------------|
| `new` | Created, no human reply yet | Support |
| `open` | An agent is working on it | Support |
| `pending` | Waiting for the customer's reply | Customer |
| `on_hold` | Waiting for an engineering team or a third party | Engineering |
| `closed` | Solved, or closed after no reply | Nobody |

A ticket moves from `new` to `open` when an agent sends the first reply.

## When does the first response clock start and stop?

The clock starts when the ticket is created and stops at the **first reply from a human agent**. The automatic acknowledgement does not stop the clock. Outside business hours the clock is paused, except for Enterprise **P1** and **P2** tickets, which run 24/7. Business hours are Monday–Friday, **08:00–18:00** US Central Time, so **1 business day** equals **10 business hours**.

## Who sets the priority of a ticket?

The Tier 1 agent sets the priority from **P1** to **P4** during triage, based on impact and not on the customer's plan. The rules are:

- Any agent can raise a priority at any time.
- Any agent can move a ticket between **P2**, **P3** and **P4**.
- Lowering a ticket from **P1** needs a support team lead.
- Data loss is never set lower than **P2**, even when it affects one user.

## What happens when support is waiting for my reply?

The ticket is set to `pending`. If there is no reply, a reminder email is sent after **3 days**. After **7 days** without a reply the ticket is closed automatically. Replying at any point moves the ticket back to `open`.

## What does on hold mean?

`on_hold` means support cannot move forward until another team acts, usually because a confirmed bug has been passed to engineering through a linked Jira issue. While a ticket is on hold the agent sends the customer an update at least every **5 business days**, even if there is no news.

## When is a ticket closed?

A ticket is closed when the customer confirms the answer worked, when the agent has given a full answer and hears nothing back for **7 days**, or when the customer asks to close it. A satisfaction survey is emailed **24 hours** after closing.

## Can I reopen a closed ticket?

Yes. Replying to a closed ticket within **14 days** reopens it with the same ID and the same agent where possible. After **14 days** a reply creates a new ticket that links to the old one. A reopened ticket keeps its priority and does not restart the first response clock.

## What happens to duplicate tickets?

When a customer opens several tickets about the same problem, the agent merges them into the **oldest** ticket. The customer is told which ticket ID stays open. The merged tickets are closed and no survey is sent for them.

## Can a ticket move to another agent or team?

Yes. A ticket is reassigned when it is escalated to Tier 2, when a shift ends, or when it belongs to a specialist queue such as billing. The new owner must read the full history first, so the customer is never asked the same question twice. Escalation rules are in `services/support/docs/sla-and-escalation.md` and shift handoffs are in `services/support/docs/on-call-handoff.md`.

## How long are tickets kept?

Closed tickets are kept for **3 years** and are then anonymized. Attachments are deleted at the same time.

Last reviewed: 2026-11-26
