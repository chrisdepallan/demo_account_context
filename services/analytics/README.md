# Analytics Service

## What it does

The Analytics service provides the in-product dashboards and reports that customers use to see how their workspace is doing: usage metrics, project progress reports, and scheduled reports and exports. It reads activity from the other services, rolls it up into daily, weekly and monthly figures, and serves those to dashboards and report files. It does not hold billing data and is not the audit log.

## Key concepts

- **Metric** – a defined number such as active members, task completion rate or cycle time. Every metric has one definition, used everywhere.
- **Dashboard** – a page of up to **12 widgets**; IDs look like `dsh_7Q2M9K4T`. Four dashboards are built in; custom dashboards depend on the plan.
- **Roll-up** – daily figures combined into ISO weeks (Monday start) and calendar months.
- **Scheduled report** – a report sent daily, weekly or monthly by email; IDs look like `rps_3H8W5N1C`.
- **Export** – a one-off CSV, XLSX or PDF file of report data; IDs look like `exp_6T4R8B2J`. Download links last **7 days**.
- **Data freshness** – today's figures refresh every **15 minutes**; a day becomes final **48 hours** after it ends.
- **Analytics history** – how far back metrics go: **30 days** on Free, **90 days** on Starter, **1 year** on Pro, **2 years** on Business, **5 years** on Enterprise.

## How to use it

- Customer-facing pages: **Analytics → Dashboards** and **Analytics → Reports**. Scheduled reports are managed at **Analytics → Reports → Scheduled** (Owner and Admin only).
- Internal API base URL: `https://api.acme-cloud.example/v2/analytics`
- Common endpoints:
  - `GET /v2/analytics/{workspace_id}/metrics` – query one metric over a date range
  - `GET /v2/analytics/{workspace_id}/dashboards` – list dashboards
  - `POST /v2/analytics/{workspace_id}/dashboards` – create a custom dashboard
  - `GET /v2/analytics/{workspace_id}/dashboards/{dashboard_id}` – one dashboard and its widgets
  - `DELETE /v2/analytics/{workspace_id}/dashboards/{dashboard_id}` – delete a custom dashboard
  - `GET /v2/analytics/{workspace_id}/reports/schedules` – list scheduled reports
  - `POST /v2/analytics/{workspace_id}/reports/schedules` – create a scheduled report
  - `DELETE /v2/analytics/{workspace_id}/reports/schedules/{schedule_id}` – delete a scheduled report
  - `POST /v2/analytics/{workspace_id}/exports` – start a one-off export
  - `GET /v2/analytics/{workspace_id}/exports/{export_id}` – export status and download link

## Docs in this service

- `docs/dashboards.md` – built-in and custom dashboards, widgets, who can see them
- `docs/metric-definitions.md` – exact definitions of every metric
- `docs/scheduled-reports-and-exports.md` – report schedules, formats, recipients, one-off exports
- `docs/data-freshness-and-retention.md` – how current the numbers are and how long history is kept

## Code in this service

- `acme_analytics/metrics.py` – metric definitions and calculations (active members, task completion rate, cycle time)
- `acme_analytics/aggregation.py` – daily, weekly and monthly roll-ups, history cut-offs
- `acme_analytics/export_schedule.py` – scheduled report cadence, limits and next-run calculation
- `openapi.yaml` – OpenAPI 3.0 spec for the endpoints above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings
- `tests/` – `unittest` tests; run `python -m unittest discover -s tests` from this folder

## Owners

Team: Data Platform. Slack channel: `#team-data` (fictional).
