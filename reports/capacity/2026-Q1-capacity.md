# Capacity Report 2026-Q1

## Summary

At the end of **2026-Q1**, object storage in use across the three regions was **805.0 TB**. This capacity report for 2026-Q1 lists storage, database and request growth and gives **5 recommendations**.

## Object storage by region at the end of 2026-Q1

| Region | Used (TB) | Provisioned (TB) | Used |
|------|------|------|------|
| `us-east` | 476.9 | 640.0 | 74.5% |
| `eu-central` | 225.6 | 320.0 | 70.5% |
| `ap-south` | 102.5 | 160.0 | 64.1% |

Capacity is expanded when a region passes **70%** of provisioned storage. Monthly figures are in `data/storage-usage-by-region.csv`.

## Database headroom by service in 2026-Q1

Peak connection use and disk use for each service's database in 2026-Q1:

| Service | Peak connections used | Disk used |
|------|------|------|
| `accounts` | 43% | 77% |
| `auth` | 76% | 66% |
| `billing` | 55% | 40% |
| `support` | 67% | 77% |
| `projects` | 42% | 36% |
| `files` | 34% | 74% |
| `notifications` | 53% | 73% |
| `webhooks` | 70% | 71% |
| `search` | 46% | 63% |
| `audit-log` | 39% | 44% |
| `integrations` | 57% | 75% |
| `analytics` | 55% | 55% |

## Request growth during 2026-Q1

| Service | Requests in 2026-01 (millions) | Requests in 2026-03 (millions) | Change |
|------|------|------|------|
| `accounts` | 341.6 | 348.5 | +2.0% |
| `auth` | 958.0 | 952.0 | -0.6% |
| `billing` | 102.0 | 105.1 | +3.0% |
| `support` | 23.3 | 23.9 | +2.6% |
| `projects` | 1288.7 | 1297.9 | +0.7% |
| `files` | 829.4 | 804.0 | -3.1% |
| `notifications` | 561.2 | 577.9 | +3.0% |
| `webhooks` | 196.6 | 189.9 | -3.4% |
| `search` | 452.5 | 452.1 | -0.1% |
| `audit-log` | 138.6 | 139.6 | +0.7% |
| `integrations` | 75.7 | 80.4 | +6.2% |
| `analytics` | 62.2 | 65.8 | +5.8% |

## Recommendations after 2026-Q1

1. Expand object storage in `us-east`, which is at **74.5%** of provisioned capacity.
2. Expand object storage in `eu-central`, which is at **70.5%** of provisioned capacity.
3. Increase database disk for the `accounts` service, which is at **77%**.
4. Raise the connection pool limit or add a read replica for the `auth` service, which peaks at **76%** of connections.
5. Increase database disk for the `support` service, which is at **77%**.

Report date: 2026-04-09
