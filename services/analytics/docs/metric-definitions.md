# Metric Definitions

## Why do metrics have fixed definitions?

Every metric is calculated one way, everywhere: on dashboards, in scheduled reports, in exports and in the API. If two numbers with the same name disagree, check that they use the same date range, filters and project access before reporting a bug.

## What counts as an active member?

An **active member** is a member who did at least one qualifying action in the period. Qualifying actions are:

- Creating, editing or completing a task
- Adding a comment
- Uploading or editing a file
- Creating or editing a project

Signing in or only viewing pages does **not** count. **Guests are never counted**, whatever they do.

| Metric | Window |
|------|--------|
| Daily active members | **1 day** |
| Weekly active members | **7 days**, ending on the selected day |
| Monthly active members | **28 days**, ending on the selected day |

The monthly window is 28 days, not a calendar month, so that every window has the same number of weekdays.

## How is task completion rate calculated?

Task completion rate is the tasks completed in the period, divided by all tasks that were open at any time in the period, as a percentage with **1 decimal place**.

- A task was open in the period if it was created on or before the last day and was not completed before the first day.
- Cancelled and archived tasks are left out of both numbers.
- Subtasks count as tasks in their own right.

Example: **40** tasks were open at some point in November and **30** of them were completed in November. The completion rate is 30 ÷ 40 = **75.0%**. If no tasks were open in the period, the rate is shown as **–**, not 0%.

## How is cycle time calculated?

**Cycle time** is the time from when a task first moved to **In progress** to when it was completed, in days with **1 decimal place**.

- A task that was completed without ever being **In progress** has no cycle time and is left out.
- If a task was reopened and completed again, the **last** completion is used.
- Dashboards show the **median** and the **85th percentile**. The median is the middle value. The 85th percentile is the value that 85% of tasks were at or below.
- A task counts in the period in which it was completed.

Example: five tasks took 1.0, 2.0, 2.0, 4.0 and 10.0 days. The median is **2.0 days** and the 85th percentile is **10.0 days**.

## How is lead time different from cycle time?

**Lead time** runs from when the task was **created** to when it was completed. Cycle time starts later, when work began. Lead time is always equal to or longer than cycle time, and every completed task has a lead time.

## How is the overdue rate calculated?

The overdue rate is the open tasks whose due date has passed, divided by all open tasks that have a due date, as a percentage with **1 decimal place**. Tasks with no due date are left out. A task is overdue from the day **after** its due date, in the workspace time zone.

## How is seat utilisation calculated?

Seat utilisation is monthly active members (the **28-day** window) divided by paid seats, as a percentage with **1 decimal place**. Example: **18** active members on **24** seats is **75.0%**. Seat counts come from the Accounts service; seats and guests are explained in `services/accounts/docs/members-and-roles.md`.

## How is storage used measured?

Storage used is the total size of all files in the workspace at the end of each day, including kept versions. It is shown against the plan's storage limit from `services/accounts/docs/plans-and-limits.md`. Drive files attached through the Google Workspace integration are links and use no storage.

## How are weeks and months defined?

- A **day** runs from 00:00 to 24:00 in the workspace time zone.
- A **week** is an ISO week: it starts on **Monday** and ends on Sunday.
- A **month** is a calendar month.

Counts such as tasks completed are **added up** across the days in a week or month. Active members are **recounted** for the whole window, because the same person active on three days is still one active member.

## How are percentages and averages rounded?

Percentages and durations are rounded to **1 decimal place**, with halves rounded up (74.95% shows as 75.0%). Rounding happens once, at the end, so a weekly figure is calculated from the raw counts and not from rounded daily figures.

Last reviewed: 2026-11-26
