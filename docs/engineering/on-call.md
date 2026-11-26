# On-Call

## Who is on call at Acme Cloud?

Every engineering team that owns a service runs its own on-call rotation, and Team Platform Infrastructure runs a rotation for shared infrastructure. Each rotation has a **primary** and a **secondary** on-call engineer at all times. Team Customer Support does not carry an engineering pager. Support raises P1 tickets, which page the on-call engineer of the owning team.

## How does the on-call rotation work?

- A shift lasts **1 week**. The handoff is every **Monday at 10:00 US Central Time**.
- The secondary of one week becomes the primary of the next week.
- A rotation has at least **4 engineers**, so that no engineer is primary more often than **1 week in 4**.
- Swaps are allowed when both engineers agree and the swap is entered in the paging tool before the shift starts.
- New engineers join the rotation after **60 days** and **2 shadow shifts**, as described in `docs/engineering/onboarding.md`.
- At the handoff, the outgoing primary writes a short note in the team channel: open incidents, noisy alerts and risky changes planned for the week.

## What are the incident severity levels?

| Severity | Meaning | Examples |
|----------|---------|----------|
| **SEV1** | Critical. A core function is down in any region, customer data is lost, or a breach of customer data is confirmed. | Login outage, region down, confirmed audit log tampering |
| **SEV2** | Major. A major feature is broken or badly degraded for many customers, or a security event is suspected. | Failed payment spike, file uploads blocked for many accounts |
| **SEV3** | Minor. A feature is degraded for some customers and a workaround exists. | Search results **20 minutes** behind, one workspace's SSO certificate expired |
| **SEV4** | Low. Cosmetic or internal-only, no customer impact. | A dashboard for internal use is wrong |

When the severity is unclear, choose the higher severity. The severity can be lowered later.

## What are the response times for each severity?

| Severity | Paged | Acknowledge | Incident commander assigned | Status page post | Updates |
|----------|-------|-------------|-----------------------------|------------------|---------|
| SEV1 | Yes, 24/7 | **5 minutes** | **15 minutes** | **15 minutes** | Every **30 minutes** |
| SEV2 | Yes, 24/7 | **5 minutes** | **30 minutes** | **30 minutes**, if customers are affected | Every **60 minutes** |
| SEV3 | No, ticket in the team channel | **4 business hours** | Not required | Not required | Daily |
| SEV4 | No, ticket in the backlog | **3 business days** | Not required | Not required | None |

Business hours are Monday–Friday, 08:00–18:00 US Central Time.

## How do incident severities relate to support ticket priorities?

Incident severities (SEV1 to SEV4) describe the state of the system. Support ticket priorities (P1 to P4) describe one customer's request and are defined in `services/support/docs/sla-and-escalation.md`. A P1 ticket pages the on-call engineer immediately and opens an incident on the status page within **15 minutes**. The on-call engineer then sets the incident severity, which is normally SEV1 or SEV2. Many tickets can belong to one incident.

## What happens when a page is not acknowledged?

1. The page goes to the primary on-call engineer.
2. If the page is not acknowledged within **10 minutes**, the page goes to the secondary on-call engineer.
3. If the page is still not acknowledged after **20 minutes**, the page goes to the engineering manager on duty.

Acknowledging a page means that the engineer is at a computer and working on the alert, not only that the engineer has seen the page.

## What does the on-call engineer do when paged?

1. Acknowledge the page within **5 minutes**.
2. Open the runbook named in the alert. Runbooks are in `docs/runbooks/`.
3. Set the severity and, for SEV1 and SEV2, declare an incident in `#incidents`. The incident gets an ID in the format `INC-2026-041` and its own channel.
4. Mitigate first and find the root cause later. A rollback is preferred over a fix under pressure.
5. Ask for help early. Paging another team's on-call is expected, not a failure.
6. Hand over to the incident commander when one is assigned, and keep working on the technical fix.

## What are the incident roles?

- **Incident commander** – decides, coordinates and owns the incident until it is closed. The incident commander does not debug.
- **Technical lead** – usually the primary on-call of the owning team. Leads diagnosis and mitigation.
- **Communications lead** – from Team Customer Support. Writes the status page posts and the customer messages.
- **Scribe** – keeps the timeline in the incident channel. Required for SEV1.

For a security incident, the incident commander comes from Team Trust and Compliance, as described in `docs/security/incident-response.md`.

## What are the rules for alerts?

- Every paging alert has a runbook and an owning team. An alert without a runbook does not page.
- Alert names are `PascalCase` and start with the service or component, for example `AuthLoginSuccessRateLow`.
- An alert that pages more than **3 times** in a week without needing action is fixed or removed within the following week.
- A target of at most **2 pages** per engineer outside business hours per week applies to every rotation.

## What happens after an incident?

A postmortem is required for every SEV1 and SEV2 incident. The draft is due within **5 business days** and is reviewed in a meeting within **10 business days**. Postmortems are blameless: the document describes systems and decisions, not individual fault. Every action item has an owner and a due date. A postmortem is optional for SEV3 and not written for SEV4.

## How is on-call time made sustainable?

An engineer who is paged between **22:00 and 06:00** local time starts late the next day. Engineers do not carry the primary pager for two rotations in a row, except by an agreed swap. On-call engineers are not expected to work on planned project tasks while an incident is open.

Last reviewed: 2026-11-26
