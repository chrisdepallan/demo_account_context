# Boards and Views

## What views does a project have?

| View | What it shows | Available on |
|------|---------------|--------------|
| Board | Tasks as cards in columns | All plans |
| List | Tasks as sortable rows | All plans |
| Calendar | Tasks by due date | Starter and above |
| Timeline | Tasks as bars between start and due date | Pro and above |
| Workload | Open tasks per assignee | Business and Enterprise |

**Board** and **List** are on every plan. **Calendar** needs Starter or above, **Timeline** needs Pro or above, and **Workload** needs Business or Enterprise. Switch views with the tabs at the top of the project.

## How do board columns work?

A new board has one column per task status: Backlog, To do, In progress, In review and Done. Cancelled tasks are hidden from the board by default. Dragging a card to another column changes the task status, so only the transitions allowed by the status workflow work. See `services/projects/docs/projects-and-tasks.md` for the allowed transitions.

Project managers can add custom columns under **Project → Settings → Board**. Each custom column is mapped to one of the six statuses. A board can have up to **20 columns**.

## What is a work-in-progress limit?

A work-in-progress (WIP) limit is the maximum number of cards a column should hold. Project managers set it under **Project → Settings → Board → Column limits**, from **1** to **999** per column. By default the limit is a warning: the column header turns red when it is exceeded. Turn on **Enforce column limits** to block moves into a full column instead.

## How many tasks can a board show?

A board column loads **50 cards** at a time and loads more as you scroll. List view loads **100 rows** per page. The API returns **50** tasks per page by default and at most **200**.

## Can I save a filtered view?

Yes. Set filters and sorting, then select **Save view**. A saved view is private to you unless a project manager marks it as shared.

| Plan | Saved views per project |
|------|-------------------------|
| Free | 3 |
| Starter | 10 |
| Pro | 50 |
| Business | 50 |
| Enterprise | 50 |

Free projects can have **3** saved views, Starter **10**, and Pro, Business and Enterprise **50**.

## What are custom fields?

Custom fields add your own data to tasks, such as a cost estimate or a customer tier. Field types are text, number, date, single select, multi select and checkbox. Project managers add them under **Project → Settings → Custom fields**.

| Plan | Custom fields per project |
|------|---------------------------|
| Free | Not available |
| Starter | 5 |
| Pro | 20 |
| Business | 50 |
| Enterprise | 100 |

Custom fields are not available on Free. Starter allows **5** per project, Pro **20**, Business **50** and Enterprise **100**. A select field can have up to **100 options**.

## Can Guests use boards?

Guests can open the Board and List views of projects shared with them and can comment on tasks. They cannot drag cards, change columns, save shared views or edit custom fields. See `services/projects/docs/permissions-and-sharing.md`.

## Can I export a board?

Anyone with at least `viewer` access can select **Project → Export** to download the tasks of the current view as CSV. An export holds up to **10,000 rows**, which covers a full project. Exports include custom fields but not comments or attachments.

Last reviewed: 2026-11-26
