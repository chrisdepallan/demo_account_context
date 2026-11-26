# Data Freshness and Retention

## How up to date are dashboards?

Figures for **today** refresh every **15 minutes**. A change made in a project, such as completing a task, normally shows on a dashboard within 15 minutes. The time of the last refresh is shown at the top right of each dashboard.

| Data | How fresh |
|------|-----------|
| Today's figures | Refreshed every **15 minutes** |
| Yesterday and earlier | Recalculated once a day at **02:00** in the workspace time zone |
| Storage used | Measured once a day, at the end of the day |
| Seat counts | Read from the Accounts service at each refresh |

## When do a day's figures become final?

A day becomes **final 48 hours after it ends**. Until then, late changes are still counted, for example an offline edit that syncs the next morning or a task whose completion date is corrected. After 48 hours the day's figures no longer change. Scheduled reports can therefore differ slightly from a dashboard viewed two days later.

## Which time zone do the figures use?

Days are cut at midnight in the **workspace time zone**, set by an Owner or Admin at **Settings → Workspace → Time zone**. The default is **UTC**. Changing the time zone affects days from then on; days that are already final are not recalculated.

## How far back does analytics history go?

| Plan | Analytics history |
|------|-------------------|
| Free | 30 days |
| Starter | 90 days |
| Pro | 1 year |
| Business | 2 years |
| Enterprise | 5 years |

In words: **30 days** on Free, **90 days** on Starter, **1 year** (365 days) on Pro, **2 years** (730 days) on Business and **5 years** (1,825 days) on Enterprise. History is counted back from today. Analytics history is separate from file version history and audit log retention, which are listed in `services/accounts/docs/plans-and-limits.md`.

## What is kept: every event or only totals?

Individual activity events are kept for **90 days** and are used to recalculate days that are not yet final and to filter by member or label. After 90 days only the daily, weekly and monthly totals are kept. This means that for dates older than 90 days, figures can be split by project but not by member or label.

## What happens to history when I change plan?

- **Upgrade** – the longer history becomes visible straight away, as far back as data still exists.
- **Downgrade** – history older than the new plan allows is hidden at once and deleted after **30 days**. Upgrading again within those 30 days brings it back.

## What happens to analytics data when a member is removed?

Their past activity stays in the totals, so historical figures do not change. In tables that list people, they appear as **Former member**. They stop counting as an active member from the day they are removed.

## What happens to analytics data when an account is closed?

Analytics data follows the account's data retention window: it can be restored for **30 days** after the account is closed and is then permanently deleted with the rest of the account's data. See `services/accounts/docs/account-lifecycle.md`. Export files that were already generated are deleted when their **7-day** download link expires.

## Where is analytics data stored?

Analytics data is stored and processed in the **same region as the workspace**: `us-east`, `eu-central` or `ap-south`. It does not leave that region, and figures are never combined across workspaces in different regions. Regions are listed in `docs/company-overview.md`.

## Why does a number differ between two places?

1. **Different date range or time zone** – check both use the same days.
2. **Project access** – members see totals only for projects they can open.
3. **Not final yet** – figures for the last **48 hours** can still change.
4. **Filters** – a dashboard-level filter applies to every widget.
5. **Definitions** – for example, monthly active members uses a **28-day** window, not a calendar month. See `services/analytics/docs/metric-definitions.md`.

If the numbers still disagree, email `support@acme-cloud.example` with the workspace ID (for example `ws_4H8P2L`), the dashboard ID and the two figures.

## Is Analytics the same as the audit log?

No. Analytics shows totals and trends for running a team. It does not record who did what for security or compliance purposes, and it should not be used as evidence of an individual's actions.

Last reviewed: 2026-11-26
