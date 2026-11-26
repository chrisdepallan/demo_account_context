# Capacity Report 2026-Q2

## Summary

At the end of **2026-Q2**, object storage in use across the three regions was **867.6 TB**. This capacity report for 2026-Q2 lists storage, database and request growth and gives **5 recommendations**.

## Object storage by region at the end of 2026-Q2

| Region | Used (TB) | Provisioned (TB) | Used |
|------|------|------|------|
| `us-east` | 511.7 | 640.0 | 79.9% |
| `eu-central` | 244.3 | 320.0 | 76.4% |
| `ap-south` | 111.6 | 160.0 | 69.7% |

Capacity is expanded when a region passes **70%** of provisioned storage. Monthly figures are in `data/storage-usage-by-region.csv`.

## Database headroom by service in 2026-Q2

Peak connection use and disk use for each service's database in 2026-Q2:

| Service | Peak connections used | Disk used |
|------|------|------|
| `accounts` | 41% | 72% |
| `auth` | 68% | 58% |
| `billing` | 30% | 70% |
| `support` | 64% | 41% |
| `projects` | 46% | 53% |
| `files` | 56% | 50% |
| `notifications` | 48% | 52% |
| `webhooks` | 32% | 61% |
| `search` | 36% | 81% |
| `audit-log` | 44% | 56% |
| `integrations` | 72% | 61% |
| `analytics` | 48% | 80% |

## Request growth during 2026-Q2

| Service | Requests in 2026-04 (millions) | Requests in 2026-06 (millions) | Change |
|------|------|------|------|
| `accounts` | 347.5 | 359.5 | +3.5% |
| `auth` | 1031.7 | 1061.4 | +2.9% |
| `billing` | 106.2 | 105.4 | -0.8% |
| `support` | 23.9 | 25.1 | +5.0% |
| `projects` | 1363.6 | 1470.0 | +7.8% |
| `files` | 837.7 | 909.9 | +8.6% |
| `notifications` | 627.8 | 622.3 | -0.9% |
| `webhooks` | 203.8 | 210.9 | +3.5% |
| `search` | 447.1 | 474.8 | +6.2% |
| `audit-log` | 145.0 | 153.8 | +6.1% |
| `integrations` | 83.9 | 85.1 | +1.4% |
| `analytics` | 68.3 | 67.4 | -1.3% |

## Recommendations after 2026-Q2

1. Expand object storage in `us-east`, which is at **79.9%** of provisioned capacity.
2. Expand object storage in `eu-central`, which is at **76.4%** of provisioned capacity.
3. Increase database disk for the `search` service, which is at **81%**.
4. Raise the connection pool limit or add a read replica for the `integrations` service, which peaks at **72%** of connections.
5. Increase database disk for the `analytics` service, which is at **80%**.

Report date: 2026-07-09
