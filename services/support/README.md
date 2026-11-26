# Support Service

## What it does

The Support team and tooling handle customer questions, incidents and escalations. This folder documents the channels customers can use, the response times promised per plan, and how tickets are escalated internally.

## Key concepts

- **Ticket** – a customer request; IDs look like `SUP-58213`.
- **Priority** – P1 (critical) to P4 (low), set by impact.
- **First response time** – time until a human replies, measured in business hours unless the plan includes 24/7 support.
- **Escalation** – moving a ticket to a higher tier or another team.

## How to use it

- Help center: `https://help.acme-cloud.example`
- Email: `support@acme-cloud.example`
- In-app chat: question-mark icon, bottom right (Pro and above)
- Status page: `https://status.acme-cloud.example`

## Docs in this service

- `docs/sla-and-escalation.md` – channels, response times, priorities, escalation paths
- `docs/ticket-lifecycle.md` – ticket statuses, reminders, closing, reopening and merging
- `docs/macros-and-tone.md` – how agents write replies, available macros and placeholders
- `docs/on-call-handoff.md` – on-call shifts, paging and shift handoff notes

## Code in this service

- `acme_support/sla.py` – first-response targets by plan and priority, business-hours arithmetic, breach check
- `acme_support/priority.py` – P1–P4 classification rules and who may change a priority
- `acme_support/escalation.py` – tier routing, escalation thresholds and owning engineering teams
- `openapi.yaml` – OpenAPI 3.0 spec for the `/v2/support` endpoints
- `config/default.yaml` – default service configuration (targets, timeouts, feature flags, per-region settings)
- `tests/` – unit tests; run `python -m unittest discover -s tests` from this folder

## Owners

Team: Customer Support. Slack channel: `#support-escalations` (fictional).
