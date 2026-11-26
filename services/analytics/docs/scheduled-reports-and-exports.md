# Scheduled Reports and Exports

## What is a scheduled report?

A scheduled report is a report that Acme Cloud builds and emails automatically on a daily, weekly or monthly cadence. Four report types are available: **Workspace summary**, **Project progress**, **Team workload** and **Usage**. Schedule IDs look like `rps_3H8W5N1C`.

## How many scheduled reports can I have?

| Plan | Scheduled reports per workspace |
|------|---------------------------------|
| Free | 0 |
| Starter | 2 |
| Pro | 10 |
| Business | 50 |
| Enterprise | 200 |

In words: none on Free, **2** on Starter, **10** on Pro, **50** on Business and **200** on Enterprise. Paused schedules count towards the limit.

## Who can create a scheduled report?

Only the **Owner** and **Admins** can create, edit, pause or delete scheduled reports. Members can receive them and can run one-off exports. Billing admins and Guests cannot create or receive scheduled reports.

## How do I schedule a report?

1. Go to **Analytics → Reports → Scheduled → New schedule**.
2. Choose the report type, any project filter and the file format.
3. Choose the cadence and the send time.
4. Add recipients and select **Save**.

## When are scheduled reports sent?

| Cadence | You choose | Report covers |
|------|------------|---------------|
| Daily | Send hour | The previous day |
| Weekly | Weekday and send hour | The 7 days ending the day before |
| Monthly | Day of month (1–31) and send hour | The previous calendar month |

The send time is a whole hour in the workspace time zone and defaults to **08:00**. If a monthly report is set for a day the month does not have, it is sent on the **last day** of that month: a report set for day **31** goes out on 30 April and on 28 or 29 February. Reports are normally delivered within **15 minutes** of the send time.

## What formats can a report use?

**PDF**, **CSV** and **XLSX**. PDF includes charts; CSV and XLSX contain the data tables only. An attachment can be up to **10 MB**. A larger report is sent as a download link instead, valid for **7 days**.

## Who can receive a scheduled report?

A schedule can have up to **25 recipients**. Every recipient must be an Owner, Admin or Member of the workspace. Outside email addresses and Guests cannot be added. A recipient who is removed from the workspace is dropped from the schedule automatically. Each recipient's copy respects project access, the same as dashboards in `services/analytics/docs/dashboards.md`.

If the Slack integration is installed, a schedule can also post a short summary to **one** Slack channel. See `services/integrations/docs/slack-and-github.md`.

## Why did my scheduled report stop arriving?

- The schedule is **paused**. A schedule pauses itself after **3 consecutive failed deliveries** and the Owner and Admins are emailed. Fix the cause and select **Resume**.
- Every recipient has been removed from the workspace.
- The account is `read_only`. Scheduled reports are not sent while an account is read-only; see `services/accounts/docs/account-lifecycle.md`.
- The email went to spam. Reports come from `support@acme-cloud.example`.

## How do I export data once?

Any Owner, Admin or Member can select **Export** on a dashboard or report and choose CSV, XLSX or PDF. Export IDs look like `exp_6T4R8B2J`.

- Up to **10,000 rows** – the file downloads straight away.
- More than 10,000 rows – the file is prepared in the background and a download link is emailed, normally within **10 minutes**.
- The largest export is **1,000,000 rows**. Narrow the date range or filters to export more.
- Download links are valid for **7 days**.
- Each person can start up to **10 exports per hour**.

One-off exports are available on **all plans**. On Free, only CSV is offered.

## Is an analytics export the same as a workspace export?

No. An analytics export contains report figures only. To export projects, tasks and files, use **Settings → Workspace → Export**, described in `services/accounts/docs/account-lifecycle.md`.

## What happens to scheduled reports when I downgrade?

A downgrade is blocked while the workspace has more scheduled reports than the lower plan allows. Delete schedules first; pausing them is not enough.

Last reviewed: 2026-11-26
