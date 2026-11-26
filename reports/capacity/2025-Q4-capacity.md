# Capacity Report 2025-Q4

## Summary

At the end of **2025-Q4**, object storage in use across the three regions was **740.2 TB**. This capacity report for 2025-Q4 lists storage, database and request growth and gives **5 recommendations**.

## Object storage by region at the end of 2025-Q4

| Region | Used (TB) | Provisioned (TB) | Used |
|------|------|------|------|
| `us-east` | 438.7 | 640.0 | 68.6% |
| `eu-central` | 207.6 | 320.0 | 64.9% |
| `ap-south` | 93.9 | 160.0 | 58.7% |

Capacity is expanded when a region passes **70%** of provisioned storage. Monthly figures are in `data/storage-usage-by-region.csv`.

## Database headroom by service in 2025-Q4

Peak connection use and disk use for each service's database in 2025-Q4:

| Service | Peak connections used | Disk used |
|------|------|------|
| `accounts` | 36% | 74% |
| `auth` | 56% | 39% |
| `billing` | 31% | 64% |
| `support` | 55% | 79% |
| `projects` | 56% | 62% |
| `files` | 73% | 82% |
| `notifications` | 71% | 62% |
| `webhooks` | 51% | 60% |
| `search` | 73% | 44% |
| `audit-log` | 34% | 62% |
| `integrations` | 56% | 31% |
| `analytics` | 36% | 43% |

## Request growth during 2025-Q4

| Service | Requests in 2025-10 (millions) | Requests in 2025-12 (millions) | Change |
|------|------|------|------|
| `accounts` | 320.9 | 335.9 | +4.7% |
| `auth` | 912.9 | 968.1 | +6.0% |
| `billing` | 94.0 | 98.8 | +5.1% |
| `support` | 21.4 | 24.0 | +12.1% |
| `projects` | 1267.0 | 1310.6 | +3.4% |
| `files` | 778.8 | 828.8 | +6.4% |
| `notifications` | 529.0 | 565.1 | +6.8% |
| `webhooks` | 188.0 | 189.7 | +0.9% |
| `search` | 434.6 | 452.6 | +4.1% |
| `audit-log` | 133.0 | 136.8 | +2.9% |
| `integrations` | 76.2 | 74.4 | -2.4% |
| `analytics` | 57.7 | 62.4 | +8.1% |

## Recommendations after 2025-Q4

1. Increase database disk for the `support` service, which is at **79%**.
2. Increase database disk for the `files` service, which is at **82%**.
3. Raise the connection pool limit or add a read replica for the `files` service, which peaks at **73%** of connections.
4. Raise the connection pool limit or add a read replica for the `notifications` service, which peaks at **71%** of connections.
5. Raise the connection pool limit or add a read replica for the `search` service, which peaks at **73%** of connections.

Report date: 2026-01-09
