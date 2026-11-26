# Reports

## What is in the reports folder?

Everything under `reports/` is written by `tools/generate_reports.py`. Do not edit these files by hand: change the generator and run it again. This copy holds **24 incident postmortems**, **20 weekly test runs**, **12 monthly performance reports**, **12 monthly release notes** and **4 quarters** of capacity, security and business reviews.

## Which report types exist?

| Folder | Contents | File name |
|------|------|------|
| `reports/incidents/` | Incident postmortems | `INC-YYYY-NNN-<service>-<slug>.md` |
| `reports/test-runs/` | Weekly full test run results | `YYYY-Www.md` |
| `reports/performance/` | Monthly latency, volume and availability | `YYYY-MM.md` |
| `reports/release-notes/` | Monthly summary of all service changes | `YYYY-MM.md` |
| `reports/quarterly/` | Quarterly business review | `YYYY-Qn-business-review.md` |
| `reports/capacity/` | Quarterly capacity report | `YYYY-Qn-capacity.md` |
| `reports/security-audits/` | Quarterly security and access review | `YYYY-Qn-access-review.md` |

## How are incidents numbered and graded?

Incident IDs look like `INC-2026-007`: the year, then a sequence number that restarts each year. Severity runs from **SEV1** (most severe) to **SEV4**. The full list of incidents with dates, services and durations is in `data/incident-index.csv`.

## Where is the data behind the reports?

The numbers in these reports are also published as CSV and JSON files in `data/`. See `data/README.md` for the columns of each file.

Report date: 2026-11-26
