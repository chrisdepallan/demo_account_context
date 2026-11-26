# Projects Service

## What it does

The Projects service is the project-management product of Acme Cloud. It stores projects, tasks, subtasks, boards, views and comments, enforces who can see and change them, and runs templates and automation rules. It reads the plan and member roles from the Accounts service to apply per-plan limits.

## Key concepts

- **Project** – a container for tasks inside a workspace; IDs look like `prj_8K2M4QX7`. Visibility is `workspace` or `private`.
- **Task** – a unit of work with a status, priority, assignees and due date; IDs look like `tsk_3F9H2L6P`.
- **Status workflow** – `backlog`, `todo`, `in_progress`, `in_review`, `done`, `cancelled`, with fixed allowed transitions.
- **Board** – a column view of a project's tasks, one column per status or custom column, with optional work-in-progress limits.
- **Project access level** – `viewer`, `commenter`, `editor` or `manager`, derived from the workspace role and any explicit grant.
- **Template** – a reusable project structure (columns, tasks, custom fields) used to create new projects.
- **Automation rule** – a trigger, optional conditions and one or more actions that run when something happens to a task.

## How to use it

- Customer-facing screens: **Projects** in the left sidebar, project settings under **Project → Settings**, and workspace-wide settings under **Settings → Projects** (Owner and Admin only).
- Internal API base URL: `https://api.acme-cloud.example/v2/projects`
- API keys need the `projects:read` or `projects:write` scope. Free accounts cannot use the API.
- Common endpoints:
  - `GET /v2/projects/{workspace_id}/projects` – list projects in a workspace
  - `POST /v2/projects/{workspace_id}/projects` – create a project
  - `GET /v2/projects/{workspace_id}/projects/{project_id}` – project details
  - `PATCH /v2/projects/{workspace_id}/projects/{project_id}` – rename, archive or change visibility
  - `DELETE /v2/projects/{workspace_id}/projects/{project_id}` – move a project to the trash (managers only)
  - `GET /v2/projects/{workspace_id}/projects/{project_id}/tasks` – list tasks
  - `POST /v2/projects/{workspace_id}/projects/{project_id}/tasks` – create a task
  - `PATCH /v2/projects/{workspace_id}/tasks/{task_id}` – update a task, including its status
  - `POST /v2/projects/{workspace_id}/tasks/{task_id}/comments` – add a comment

## Docs in this service

- `docs/projects-and-tasks.md` – project and task limits, statuses, archiving and deletion
- `docs/boards-and-views.md` – board columns, work-in-progress limits, views and custom fields
- `docs/permissions-and-sharing.md` – project access levels, private projects and guests
- `docs/templates-and-automation.md` – project templates, automation rules and their limits

## Code in this service

- `acme_projects/tasks.py` – task status workflow, allowed transitions and task validation
- `acme_projects/permissions.py` – project access levels by workspace role and per-plan project limits
- `acme_projects/automation.py` – automation rule engine: trigger, conditions and actions
- `tests/` – `unittest` tests; run `python -m unittest discover -s tests` from this folder
- `openapi.yaml` – OpenAPI 3.0 spec for the endpoints above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings

## Owners

Team: Work Management. Slack channel: `#team-projects` (fictional).
