# Projects and Tasks

## How many projects can I have?

The limit counts **active** projects per workspace. Archived projects and projects in the trash do not count.

| Plan | Active projects per workspace |
|------|-------------------------------|
| Free | 5 |
| Starter | 50 |
| Pro | 500 |
| Business | Unlimited |
| Enterprise | Unlimited |

Free workspaces can have **5** active projects, Starter **50** and Pro **500**. Business and Enterprise have no project limit. When the limit is reached, **New project** is disabled until a project is archived or deleted, or the account is upgraded.

## How do I create a project?

Owners, Admins and Members select **Projects → New project**, enter a name (up to **120 characters**) and choose a visibility: `workspace` (every member can open it) or `private` (invited people only). Billing admins and Guests cannot create projects. Every project gets an ID such as `prj_8K2M4QX7`, shown under **Project → Settings → Details**.

## What are the task limits?

| Limit | Value |
|-------|-------|
| Tasks per project | 10,000 |
| Subtasks per task | 50 |
| Subtask depth | 1 level |
| Assignees per task | 10 |
| Labels per task | 20 |
| Title length | 255 characters |
| Description length | 50,000 characters |
| Comment length | 10,000 characters |

A project holds up to **10,000 tasks**, including completed and cancelled ones. A task can have up to **50 subtasks**, and subtasks cannot have their own subtasks. A task can have up to **10 assignees** and **20 labels**. These limits are the same on every plan. Task IDs look like `tsk_3F9H2L6P`.

## What task statuses are there?

Every task has one of six statuses: `backlog`, `todo`, `in_progress`, `in_review`, `done` or `cancelled`. New tasks start in `backlog` unless another status is chosen.

| From | Can move to |
|------|-------------|
| `backlog` | `todo`, `cancelled` |
| `todo` | `backlog`, `in_progress`, `cancelled` |
| `in_progress` | `todo`, `in_review`, `done`, `cancelled` |
| `in_review` | `in_progress`, `done`, `cancelled` |
| `done` | `in_progress` (reopen) |
| `cancelled` | `backlog` (restore) |

Any other move is rejected with HTTP `409` and the error code `invalid_transition`. A task with subtasks cannot move to `done` while any subtask is still open (not `done` or `cancelled`).

## What priorities can a task have?

Four: `low`, `medium`, `high` and `urgent`. The default is `medium`. Priority is only used for sorting, filtering and automation rules; it does not change notifications by itself.

## When is a task overdue?

A task is overdue when its due date is in the past and its status is not `done` or `cancelled`. Due dates are stored in UTC and shown in each member's own time zone. Overdue tasks get a red due date on boards and lists.

## How do comments work?

Anyone with at least `commenter` access can comment on a task, including Guests on projects shared with them. A comment can be up to **10,000 characters**. Authors can edit their own comment for **15 minutes** after posting and delete it at any time. Project managers can delete any comment. Mention a person with `@` to notify them.

## How do I archive a project?

A project manager selects **Project → Settings → Archive**. An archived project is read-only: tasks and comments can be viewed and searched but not changed, and automation rules stop running. Archived projects do not count towards the project limit and can be unarchived at any time, provided the workspace is under its limit.

## How do I delete a project or task?

- **Task**: open the task and select **Delete**. Editors can delete tasks they created; project managers can delete any task.
- **Project**: a project manager selects **Project → Settings → Delete project**.

Deleted projects and tasks go to **Projects → Trash** and can be restored for **30 days**. After 30 days they are permanently deleted and cannot be recovered by support.

Last reviewed: 2026-11-26
