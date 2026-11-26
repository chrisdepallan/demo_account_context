# Datasets

## What is in the data folder?

The `data/` folder holds the numbers behind the reports in `reports/`, as CSV and JSON. Every file is written by `tools/generate_reports.py`. All figures are fictional.

## Which datasets exist and what are their columns?

| File | One row per | Columns |
|------|------|------|
| `data/incident-index.csv` | Incident | incident_id, started_at_utc, severity, service, duration_minutes, regions, accounts_affected, tickets, title, postmortem |
| `data/service-performance-by-month.csv` | Service and month | month, service, uptime_pct, p50_ms, p95_ms, p99_ms, requests_millions, error_rate_pct |
| `data/ticket-volume-by-week.csv` | Week | week_starting, p1, p2, p3, p4, total, first_response_met_pct, satisfaction_pct |
| `data/accounts-by-plan.csv` | Month | month, free, starter, pro, business, enterprise, total |
| `data/storage-usage-by-region.csv` | Region and month | month, region, used_tb, provisioned_tb, used_pct |
| `data/test-run-summary.csv` | Service and weekly test run | week, week_starting, service, tests, passed, failed, skipped, duration_s, line_coverage_pct |
| `data/service-catalog.json` | Service | name, title, team, slack_channel, tier, availability_objective_pct, readme, api_base, operations |

## How do I regenerate the data?

Run `python tools/generate_reports.py` from the repository root. The output is deterministic, so running it twice changes nothing. See `tools/README.md`.

Report date: 2026-11-26
