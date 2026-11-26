# Quarterly Business Review 2026-Q3

## Highlights

- Average availability across all 12 services in **2026-Q3** was **99.995%**.
- There were **4 incidents** in 2026-Q3: **0 SEV1**, **1 SEV2**, **2 SEV3** and **1 SEV4**.
- Customer Support handled **9,991 tickets** in 2026-Q3 and met the first-response target on **97.1%** of them.
- Acme Cloud ended 2026-Q3 with **53,007 accounts**.

## Availability by service in 2026-Q3

| Service | Owning team | Average availability |
|------|------|------|
| `accounts` | Accounts Platform | 99.977% |
| `auth` | Identity | 99.991% |
| `billing` | Revenue Engineering | 99.998% |
| `support` | Customer Support | 99.998% |
| `projects` | Work Management | 99.999% |
| `files` | Storage Platform | 99.996% |
| `notifications` | Messaging | 99.993% |
| `webhooks` | Developer Platform | 99.997% |
| `search` | Search and Discovery | 99.998% |
| `audit-log` | Trust and Compliance | 99.999% |
| `integrations` | Ecosystem | 99.999% |
| `analytics` | Data Platform | 99.998% |

## Incidents in 2026-Q3

- **INC-2026-016** (SEV2, `accounts`, 53 minutes): Trial expiry job stalled and accounts stayed in trialing. See `reports/incidents/INC-2026-016-accounts-trial-expiry-job-stalled.md`.
- **INC-2026-017** (SEV3, `notifications`, 75 minutes): Daily digest sent twice. See `reports/incidents/INC-2026-017-notifications-digest-sent-twice.md`.
- **INC-2026-018** (SEV3, `auth`, 75 minutes): SSO sign-ins rejected because of clock skew. See `reports/incidents/INC-2026-018-auth-sso-clock-skew.md`.
- **INC-2026-019** (SEV4, `audit-log`, 40 minutes): Gap in SIEM streaming. See `reports/incidents/INC-2026-019-audit-log-siem-stream-gap.md`.

## Support in 2026-Q3

Customer Support handled **9,991 tickets** in 2026-Q3: **146 P1**, **990 P2**, **4,754 P3** and **4,101 P4**. The first-response target was met on **97.1%** of tickets and customer satisfaction averaged **93.2%**. Response-time targets are defined in `services/support/docs/sla-and-escalation.md`. Weekly figures are in `data/ticket-volume-by-week.csv`.

## Plan mix at the end of 2026-Q3

| Plan | Accounts | Share |
|------|------|------|
| Free | 30,824 | 58.2% |
| Starter | 10,140 | 19.1% |
| Pro | 7,884 | 14.9% |
| Business | 3,379 | 6.4% |
| Enterprise | 780 | 1.5% |

## Priorities for the next quarter

1. Automate regional failover drills and run one per region.
2. Move remaining single-region batch jobs to run in each region.
3. Complete the quarterly access review within the first two weeks of the quarter.
4. Reduce p95 latency of the slowest three services by 15%.

Report date: 2026-10-12
