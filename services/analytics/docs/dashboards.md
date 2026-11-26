# Dashboards

## Where do I find dashboards?

Open **Analytics → Dashboards** in the left-hand menu of any workspace. Dashboards show figures for one workspace at a time. An account with several workspaces has a separate set of dashboards in each.

## Which dashboards are built in?

Every workspace has four built-in dashboards. They cannot be edited or deleted.

| Dashboard | What it shows |
|------|---------------|
| Workspace overview | Active members, tasks created and completed, task completion rate |
| Project progress | Per-project completion rate, overdue tasks, burndown, cycle time |
| Team workload | Open and overdue tasks per member, tasks completed per member |
| Usage | Seats used, seat utilisation, storage used against the plan limit |

The exact meaning of each figure is in `services/analytics/docs/metric-definitions.md`.

## How many custom dashboards can I create?

| Plan | Custom dashboards per workspace |
|------|---------------------------------|
| Free | 0 (built-in dashboards only) |
| Starter | 3 |
| Pro | 20 |
| Business | 100 |
| Enterprise | Unlimited |

In words: none on Free, **3** on Starter, **20** on Pro, **100** on Business and unlimited on Enterprise. Each dashboard holds up to **12 widgets**. Dashboard IDs look like `dsh_7Q2M9K4T`.

## How do I create a custom dashboard?

1. Go to **Analytics → Dashboards → New dashboard** and give it a name.
2. Select **Add widget**, pick a metric, then pick a widget type.
3. Set the date range and any filters, then select **Save**.

To start from an existing dashboard, open it and select **Duplicate**. A duplicate counts towards the plan limit.

## What widget types are there?

- **Number** – one figure with the change against the previous period.
- **Line chart** – a metric over time, by day, week or month.
- **Bar chart** – a metric split by project, member or label.
- **Table** – up to **50 rows**, sortable.
- **Burndown** – remaining open tasks in one project against a target date.

## What date ranges and filters can I use?

Preset ranges are the last **7**, **28** and **90 days**, this month and last month. A custom range can go back as far as the plan's analytics history, described in `services/analytics/docs/data-freshness-and-retention.md`. A custom range can span at most **366 days** at daily detail; longer ranges switch to weekly or monthly detail.

Widgets can be filtered by project, member and label. A dashboard-level filter applies to every widget on it.

## Who can see dashboards?

| Action | Owner | Admin | Billing admin | Member | Guest |
|--------|-------|-------|---------------|--------|-------|
| View built-in dashboards | Yes | Yes | Usage only | Yes | No |
| View shared custom dashboards | Yes | Yes | No | Yes | No |
| Create and edit custom dashboards | Yes | Yes | No | Yes | No |
| Delete someone else's dashboard | Yes | Yes | No | No | No |

Guests cannot open **Analytics** at all. Billing admins see only the **Usage** dashboard, because it covers seats and storage and contains no project content.

## Are custom dashboards private?

A new custom dashboard is **private** to the person who made it. Select **Share with workspace** to let every Owner, Admin and Member in the workspace view it. Only the creator, the Owner and Admins can edit or delete a shared dashboard. Private dashboards still count towards the workspace's plan limit.

## Can members see figures for projects they cannot open?

No. Dashboards respect project access. A member sees totals only for projects they can open, so two people can see different numbers on the same dashboard. The Owner and Admins always see the whole workspace.

## Why does my dashboard look out of date?

Today's figures refresh every **15 minutes**. The time of the last refresh is shown at the top right of each dashboard. Select **Refresh** to reload the page with the newest figures; this does not force a new calculation. More detail is in `services/analytics/docs/data-freshness-and-retention.md`.

## What happens to custom dashboards when I downgrade?

A downgrade is blocked while the workspace has more custom dashboards than the lower plan allows. For example, a Pro workspace with **7** custom dashboards must delete **4** before moving to Starter. This follows the downgrade rule in `services/accounts/docs/plans-and-limits.md`.

Last reviewed: 2026-11-26
