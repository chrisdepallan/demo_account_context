# Templates and Automation

## What is a project template?

A template is a reusable project structure: board columns, custom fields, labels, automation rules and starter tasks. Creating a project from a template copies that structure but not comments, assignees or due dates. Acme Cloud ships **12** built-in templates, such as a sprint board, a content calendar and a bug tracker.

## How many custom templates can I save?

| Plan | Custom templates per workspace |
|------|--------------------------------|
| Free | Built-in templates only |
| Starter | 5 |
| Pro | 50 |
| Business | Unlimited |
| Enterprise | Unlimited |

Free workspaces can use the built-in templates only. Starter can save **5** custom templates, Pro **50**, and Business and Enterprise have no limit. A template can hold up to **200** starter tasks.

## How do I save a project as a template?

A project manager selects **Project → Settings → Save as template** and gives the template a name. The template then appears under **Projects → New project → From template** for every Member of the workspace. Owners and Admins manage and delete templates under **Settings → Projects → Templates**.

## What is an automation rule?

A rule has three parts:

- **Trigger** – the event that starts the rule.
- **Conditions** – optional checks on the task; all of them must be true.
- **Actions** – what the rule does to the task, in order.

For example: when a task's status changes (trigger) and its priority is `urgent` (condition), assign it to the on-call lead and add the label `escalated` (actions). Project managers create rules under **Project → Settings → Automation**.

## What triggers, conditions and actions are available?

| Part | Options |
|------|---------|
| Triggers | `task.created`, `task.status_changed`, `task.assigned`, `task.due_date_passed`, `comment.added` |
| Condition operators | `equals`, `not_equals`, `contains`, `in`, `is_empty` |
| Actions | `set_status`, `set_priority`, `assign`, `add_label`, `notify` |

A rule has exactly one trigger, up to **5** conditions and up to **5** actions. A `set_status` action must follow the status workflow in `services/projects/docs/projects-and-tasks.md`; if the move is not allowed, the action fails and the remaining actions of that rule are skipped.

## How many automation rules can I have?

| Plan | Rules per project | Rule runs per month (per workspace) |
|------|-------------------|-------------------------------------|
| Free | Not available | – |
| Starter | 5 | 1,000 |
| Pro | 25 | 10,000 |
| Business | 100 | 50,000 |
| Enterprise | 250 | 250,000 |

Automation is not available on Free. Starter allows **5** rules per project and **1,000** runs per month, Pro **25** rules and **10,000** runs, Business **100** rules and **50,000** runs, and Enterprise **250** rules and **250,000** runs. A run is counted each time a rule's conditions pass and its actions start. The counter resets on the first day of each calendar month (UTC).

## What happens when I use up my rule runs?

Rules stop running until the counter resets or the account is upgraded. Owners and Admins get an email at **80%** and at **100%** of the monthly allowance. Tasks can still be changed by hand, and no events are queued for later.

## Can one rule trigger another?

Yes. An action such as `set_status` raises a new event that other rules can react to. To prevent loops, a chain stops after **5** rule steps, and a rule never runs twice in the same chain.

## Why was my rule turned off?

A rule is disabled automatically after **10** failed runs in a row, for example because it assigns tasks to a removed member. The project managers are notified and the rule shows **Disabled – needs attention**. Fix the rule and switch it back on under **Project → Settings → Automation**. Rules also stop while a project is archived or the account is `read_only`.

## Where can I see what a rule did?

**Project → Settings → Automation → Run history** lists each run with its trigger, the task and the result. Run history is kept for **30 days**.

Last reviewed: 2026-11-26
