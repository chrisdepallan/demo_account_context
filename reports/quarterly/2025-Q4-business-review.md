# Quarterly Business Review 2025-Q4

## Highlights

- Average availability across all 12 services in **2025-Q4** was **99.992%**.
- There were **5 incidents** in 2025-Q4: **0 SEV1**, **3 SEV2**, **1 SEV3** and **1 SEV4**.
- Customer Support handled **8,066 tickets** in 2025-Q4 and met the first-response target on **97.0%** of them.
- Acme Cloud ended 2025-Q4 with **43,521 accounts**.

## Availability by service in 2025-Q4

| Service | Owning team | Average availability |
|------|------|------|
| `accounts` | Accounts Platform | 99.997% |
| `auth` | Identity | 99.999% |
| `billing` | Revenue Engineering | 99.969% |
| `support` | Customer Support | 99.979% |
| `projects` | Work Management | 99.999% |
| `files` | Storage Platform | 99.998% |
| `notifications` | Messaging | 99.998% |
| `webhooks` | Developer Platform | 99.992% |
| `search` | Search and Discovery | 99.997% |
| `audit-log` | Trust and Compliance | 99.998% |
| `integrations` | Ecosystem | 99.997% |
| `analytics` | Data Platform | 99.984% |

## Incidents in 2025-Q4

- **INC-2025-001** (SEV2, `support`, 50 minutes): First-response timers ignored business hours. See `reports/incidents/INC-2025-001-support-response-timers-wrong.md`.
- **INC-2025-002** (SEV2, `billing`, 79 minutes): Failed-payment reminder emails were not sent. See `reports/incidents/INC-2025-002-billing-dunning-emails-not-sent.md`.
- **INC-2025-003** (SEV4, `files`, 37 minutes): Valid sharing links returned 403. See `reports/incidents/INC-2025-003-files-sharing-links-denied.md`.
- **INC-2025-004** (SEV2, `analytics`, 38 minutes): Scheduled exports were not sent. See `reports/incidents/INC-2025-004-analytics-scheduled-exports-missed.md`.
- **INC-2025-005** (SEV3, `webhooks`, 86 minutes): Healthy webhook endpoints disabled in error. See `reports/incidents/INC-2025-005-webhooks-endpoints-disabled-in-error.md`.

## Support in 2025-Q4

Customer Support handled **8,066 tickets** in 2025-Q4: **125 P1**, **734 P2**, **3,918 P3** and **3,289 P4**. The first-response target was met on **97.0%** of tickets and customer satisfaction averaged **94.2%**. Response-time targets are defined in `services/support/docs/sla-and-escalation.md`. Weekly figures are in `data/ticket-volume-by-week.csv`.

## Plan mix at the end of 2025-Q4

| Plan | Accounts | Share |
|------|------|------|
| Free | 25,138 | 57.8% |
| Starter | 8,253 | 19.0% |
| Pro | 6,656 | 15.3% |
| Business | 2,822 | 6.5% |
| Enterprise | 652 | 1.5% |

## Priorities for the next quarter

1. Cut P1 first-response misses to zero for Enterprise accounts.
2. Close every open postmortem action item older than 60 days.
3. Automate regional failover drills and run one per region.
4. Raise line coverage of the three least-covered services.

Report date: 2026-01-12
