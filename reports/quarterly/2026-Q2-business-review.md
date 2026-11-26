# Quarterly Business Review 2026-Q2

## Highlights

- Average availability across all 12 services in **2026-Q2** was **99.986%**.
- There were **11 incidents** in 2026-Q2: **0 SEV1**, **5 SEV2**, **4 SEV3** and **2 SEV4**.
- Customer Support handled **9,148 tickets** in 2026-Q2 and met the first-response target on **96.4%** of them.
- Acme Cloud ended 2026-Q2 with **49,564 accounts**.

## Availability by service in 2026-Q2

| Service | Owning team | Average availability |
|------|------|------|
| `accounts` | Accounts Platform | 99.952% |
| `auth` | Identity | 99.999% |
| `billing` | Revenue Engineering | 99.995% |
| `support` | Customer Support | 99.965% |
| `projects` | Work Management | 99.998% |
| `files` | Storage Platform | 99.998% |
| `notifications` | Messaging | 99.992% |
| `webhooks` | Developer Platform | 99.998% |
| `search` | Search and Discovery | 99.999% |
| `audit-log` | Trust and Compliance | 99.974% |
| `integrations` | Ecosystem | 99.962% |
| `analytics` | Data Platform | 99.998% |

## Incidents in 2026-Q2

- **INC-2026-005** (SEV2, `support`, 67 minutes): Live chat unavailable during business hours. See `reports/incidents/INC-2026-005-support-live-chat-unavailable.md`.
- **INC-2026-006** (SEV2, `accounts`, 48 minutes): Stale plan limits blocked upgrades from taking effect. See `reports/incidents/INC-2026-006-accounts-stale-plan-limits.md`.
- **INC-2026-007** (SEV3, `billing`, 62 minutes): Renewal invoices issued twice for a subset of accounts. See `reports/incidents/INC-2026-007-billing-duplicate-renewal-invoices.md`.
- **INC-2026-008** (SEV2, `accounts`, 74 minutes): Trial expiry job stalled and accounts stayed in trialing. See `reports/incidents/INC-2026-008-accounts-trial-expiry-job-stalled.md`.
- **INC-2026-009** (SEV3, `support`, 69 minutes): Live chat unavailable during business hours. See `reports/incidents/INC-2026-009-support-live-chat-unavailable.md`.
- **INC-2026-010** (SEV4, `accounts`, 45 minutes): Trial expiry job stalled and accounts stayed in trialing. See `reports/incidents/INC-2026-010-accounts-trial-expiry-job-stalled.md`.
- **INC-2026-011** (SEV2, `integrations`, 92 minutes): New integration installs failed at the consent step. See `reports/incidents/INC-2026-011-integrations-oauth-installs-failed.md`.
- **INC-2026-012** (SEV3, `notifications`, 73 minutes): Notification emails delayed. See `reports/incidents/INC-2026-012-notifications-email-delivery-delays.md`.
- **INC-2026-013** (SEV3, `support`, 36 minutes): First-response timers ignored business hours. See `reports/incidents/INC-2026-013-support-response-timers-wrong.md`.
- **INC-2026-014** (SEV4, `webhooks`, 43 minutes): Healthy webhook endpoints disabled in error. See `reports/incidents/INC-2026-014-webhooks-endpoints-disabled-in-error.md`.
- **INC-2026-015** (SEV2, `audit-log`, 63 minutes): Hash-chain verification raised a false alarm. See `reports/incidents/INC-2026-015-audit-log-chain-verification-false-alarm.md`.

## Support in 2026-Q2

Customer Support handled **9,148 tickets** in 2026-Q2: **115 P1**, **839 P2**, **4,371 P3** and **3,823 P4**. The first-response target was met on **96.4%** of tickets and customer satisfaction averaged **93.1%**. Response-time targets are defined in `services/support/docs/sla-and-escalation.md`. Weekly figures are in `data/ticket-volume-by-week.csv`.

## Plan mix at the end of 2026-Q2

| Plan | Accounts | Share |
|------|------|------|
| Free | 28,589 | 57.7% |
| Starter | 9,551 | 19.3% |
| Pro | 7,502 | 15.1% |
| Business | 3,182 | 6.4% |
| Enterprise | 740 | 1.5% |

## Priorities for the next quarter

1. Raise line coverage of the three least-covered services.
2. Reduce p95 latency of the slowest three services by 15%.
3. Automate regional failover drills and run one per region.
4. Complete the quarterly access review within the first two weeks of the quarter.

Report date: 2026-07-12
