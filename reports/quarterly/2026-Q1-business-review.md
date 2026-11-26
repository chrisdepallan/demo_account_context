# Quarterly Business Review 2026-Q1

## Highlights

- Average availability across all 12 services in **2026-Q1** was **99.996%**.
- There were **4 incidents** in 2026-Q1: **0 SEV1**, **0 SEV2**, **4 SEV3** and **0 SEV4**.
- Customer Support handled **8,662 tickets** in 2026-Q1 and met the first-response target on **96.0%** of them.
- Acme Cloud ended 2026-Q1 with **46,135 accounts**.

## Availability by service in 2026-Q1

| Service | Owning team | Average availability |
|------|------|------|
| `accounts` | Accounts Platform | 99.990% |
| `auth` | Identity | 99.997% |
| `billing` | Revenue Engineering | 99.998% |
| `support` | Customer Support | 99.992% |
| `projects` | Work Management | 99.998% |
| `files` | Storage Platform | 99.998% |
| `notifications` | Messaging | 99.997% |
| `webhooks` | Developer Platform | 99.997% |
| `search` | Search and Discovery | 99.993% |
| `audit-log` | Trust and Compliance | 99.998% |
| `integrations` | Ecosystem | 99.997% |
| `analytics` | Data Platform | 99.993% |

## Incidents in 2026-Q1

- **INC-2026-001** (SEV3, `support`, 78 minutes): P1 tickets routed to the general queue. See `reports/incidents/INC-2026-001-support-p1-tickets-misrouted.md`.
- **INC-2026-002** (SEV3, `analytics`, 42 minutes): Task completion rate miscalculated for archived projects. See `reports/incidents/INC-2026-002-analytics-completion-rate-wrong.md`.
- **INC-2026-003** (SEV3, `accounts`, 89 minutes): Ownership transfers failed with a server error. See `reports/incidents/INC-2026-003-accounts-ownership-transfer-errors.md`.
- **INC-2026-004** (SEV3, `search`, 71 minutes): Search results lagged behind recent changes. See `reports/incidents/INC-2026-004-search-index-lag.md`.

## Support in 2026-Q1

Customer Support handled **8,662 tickets** in 2026-Q1: **147 P1**, **849 P2**, **4,130 P3** and **3,536 P4**. The first-response target was met on **96.0%** of tickets and customer satisfaction averaged **93.6%**. Response-time targets are defined in `services/support/docs/sla-and-escalation.md`. Weekly figures are in `data/ticket-volume-by-week.csv`.

## Plan mix at the end of 2026-Q1

| Plan | Accounts | Share |
|------|------|------|
| Free | 26,983 | 58.5% |
| Starter | 8,758 | 19.0% |
| Pro | 6,739 | 14.6% |
| Business | 2,929 | 6.3% |
| Enterprise | 726 | 1.6% |

## Priorities for the next quarter

1. Raise line coverage of the three least-covered services.
2. Complete the quarterly access review within the first two weeks of the quarter.
3. Close every open postmortem action item older than 60 days.
4. Automate regional failover drills and run one per region.

Report date: 2026-04-12
