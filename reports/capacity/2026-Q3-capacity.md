# Capacity Report 2026-Q3

## Summary

At the end of **2026-Q3**, object storage in use across the three regions was **951.6 TB**. This capacity report for 2026-Q3 lists storage, database and request growth and gives **4 recommendations**.

## Object storage by region at the end of 2026-Q3

| Region | Used (TB) | Provisioned (TB) | Used |
|------|------|------|------|
| `us-east` | 559.8 | 800.0 | 70.0% |
| `eu-central` | 270.3 | 400.0 | 67.6% |
| `ap-south` | 121.5 | 160.0 | 76.0% |

Capacity is expanded when a region passes **70%** of provisioned storage. Monthly figures are in `data/storage-usage-by-region.csv`.

## Database headroom by service in 2026-Q3

Peak connection use and disk use for each service's database in 2026-Q3:

| Service | Peak connections used | Disk used |
|------|------|------|
| `accounts` | 33% | 62% |
| `auth` | 72% | 65% |
| `billing` | 43% | 38% |
| `support` | 29% | 71% |
| `projects` | 34% | 56% |
| `files` | 74% | 41% |
| `notifications` | 44% | 43% |
| `webhooks` | 65% | 78% |
| `search` | 43% | 75% |
| `audit-log` | 53% | 56% |
| `integrations` | 67% | 56% |
| `analytics` | 70% | 68% |

## Request growth during 2026-Q3

| Service | Requests in 2026-07 (millions) | Requests in 2026-09 (millions) | Change |
|------|------|------|------|
| `accounts` | 379.3 | 360.2 | -5.0% |
| `auth` | 1029.3 | 1046.3 | +1.7% |
| `billing` | 108.4 | 119.6 | +10.3% |
| `support` | 26.6 | 26.6 | +0.0% |
| `projects` | 1516.2 | 1581.9 | +4.3% |
| `files` | 894.2 | 912.1 | +2.0% |
| `notifications` | 646.6 | 647.7 | +0.2% |
| `webhooks` | 218.5 | 213.3 | -2.4% |
| `search` | 490.5 | 524.0 | +6.8% |
| `audit-log` | 160.9 | 163.8 | +1.8% |
| `integrations` | 86.3 | 94.1 | +9.0% |
| `analytics` | 68.3 | 75.0 | +9.8% |

## Recommendations after 2026-Q3

1. Expand object storage in `ap-south`, which is at **76.0%** of provisioned capacity.
2. Raise the connection pool limit or add a read replica for the `auth` service, which peaks at **72%** of connections.
3. Raise the connection pool limit or add a read replica for the `files` service, which peaks at **74%** of connections.
4. Increase database disk for the `webhooks` service, which is at **78%**.

Report date: 2026-10-09
