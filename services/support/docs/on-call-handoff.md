# On-Call Handoff

## What does the support on-call cover?

The support on-call agent covers Enterprise **P1** and **P2** tickets outside business hours, because those tickets have 24/7 first response targets of **30 minutes** and **2 hours**. All other tickets wait for the next business day. Business hours are Monday–Friday, **08:00–18:00** US Central Time. Response targets are listed in `services/support/docs/sla-and-escalation.md`.

## When do on-call shifts start and end?

| Shift | Hours (US Central Time) | Staffed by |
|-------|-------------------------|------------|
| Business hours | Monday–Friday, **08:00–18:00** | Tier 1 and Tier 2 teams |
| Weeknight on-call | Monday–Thursday, **18:00–08:00** | One primary and one secondary Tier 2 agent |
| Weekend on-call | Friday **18:00** to Monday **08:00** | One primary and one secondary Tier 2 agent |

The on-call rotation changes every **Monday at 08:00**. Each agent is primary for at most **1 week in 4**.

## How fast must a page be acknowledged?

The primary on-call agent acknowledges a page within **10 minutes**. If there is no acknowledgement, the secondary agent is paged. After **20 minutes** without any acknowledgement the support team lead is paged. Acknowledging a page is not a first response: the customer must still get a human reply inside the target.

## What happens when a P1 ticket arrives?

1. The on-call engineer of the owning team is paged immediately.
2. The support agent sends the first reply with the `incident-p1-acknowledged` macro.
3. An incident is opened on `https://status.acme-cloud.example` within **15 minutes**.
4. The ticket and the incident are linked and posted in `#support-escalations`.

## When does a handoff happen?

A handoff happens at every shift change: at **08:00** and **18:00** US Central Time on weekdays. The outgoing and incoming agents overlap for **15 minutes**. The outgoing agent stays responsible until the incoming agent confirms the handoff in `#support-escalations`.

## What goes into a handoff note?

The outgoing agent posts one note per shift in `#support-escalations` with these items:

- Every open **P1** and **P2** ticket – ticket ID, account ID, current status and the next action.
- Tickets that will pass an escalation threshold in the next shift – **4 business hours** for P2 and **1 business day** for P3.
- Active incidents on the status page and the time of the next promised update.
- Promised callbacks – who is to be called, about which ticket and by what time.
- Anything waiting on a team lead, such as a refund above **$500**.

If nothing is open, the note says "Nothing to hand off" so the incoming agent knows it was checked.

## Can a handoff happen during an active P1 incident?

Yes, but the outgoing agent does not leave until the incoming agent has read the ticket history, joined the incident channel and sent the next customer update. The handoff is recorded on the ticket as an internal note. The customer is told only if their point of contact changes.

## What can the on-call agent not do alone?

- Approve a refund above **$500** or any goodwill refund. These wait for a support team lead; see `services/billing/docs/refunds.md`.
- Lower the priority of a **P1** ticket.
- Reset MFA or change the account Owner based on email alone.
- Share one customer's data with another.

## What happens on company holidays?

On US federal holidays support runs at reduced staffing and the weekend on-call pattern applies for the whole day. Enterprise 24/7 coverage for **P1** incidents is unaffected.

## What happens after the on-call shift ends?

At **08:00** the on-call agent hands every ticket touched during the shift to the business-hours team. For each **P1** handled overnight, the agent adds an internal summary to the ticket within **1 business day**: timeline, customer impact, what was communicated and what is still open. Ticket statuses are explained in `services/support/docs/ticket-lifecycle.md`.

Last reviewed: 2026-11-26
