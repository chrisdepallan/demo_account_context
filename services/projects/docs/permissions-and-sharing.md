# Permissions and Sharing

## What project access levels are there?

Every person has one access level on each project they can open.

| Action | Viewer | Commenter | Editor | Manager |
|--------|--------|-----------|--------|---------|
| View tasks, boards and comments | Yes | Yes | Yes | Yes |
| Export tasks as CSV | Yes | Yes | Yes | Yes |
| Comment | No | Yes | Yes | Yes |
| Create and edit tasks | No | No | Yes | Yes |
| Delete tasks they created | No | No | Yes | Yes |
| Delete any task or comment | No | No | No | Yes |
| Change project settings, columns and rules | No | No | No | Yes |
| Share, archive or delete the project | No | No | No | Yes |

The levels are `viewer`, `commenter`, `editor` and `manager`. Each level includes everything the level below it can do.

## How does my workspace role affect project access?

| Workspace role | `workspace` projects | `private` projects |
|----------------|----------------------|--------------------|
| Owner | Manager | Manager |
| Admin | Manager | Manager |
| Member | Editor (Manager if they created it) | No access unless invited |
| Billing admin | No access | No access |
| Guest | No access unless invited | No access unless invited |

Owners and Admins are managers of every project in the workspace, including private ones. Members are editors of every `workspace` project and managers of projects they created. Billing admins manage invoices and payment methods only and cannot open projects. Workspace roles are described in `services/accounts/docs/members-and-roles.md`.

## What is a private project?

A private project is visible only to the people invited to it, plus Owners and Admins. It does not appear in search results or the project list for anyone else. A project manager changes visibility under **Project → Settings → Sharing**. Changing a project from `private` to `workspace` gives every Member `editor` access immediately.

## How do I share a project with someone?

A project manager selects **Project → Share**, picks a person and chooses an access level. Members can be given `viewer`, `commenter`, `editor` or `manager`. An explicit grant can raise a Member's access on a project but never lowers the access their workspace role already gives. A project can have up to **500** explicit grants.

## What can Guests do in a project?

Guests can only open projects that have been shared with them, and their access is capped at `commenter`: they can view and comment but never create, edit or delete tasks. Guests cannot be made editors or managers. To give someone edit access, an Owner or Admin must change them to a Member, which uses a paid seat.

## How many Guests can I invite?

Each paid seat allows **5** Guests across the account, so an account with **10** seats can have up to **50** Guests. Guests are free and are not available on the Free plan. Only Owners and Admins can invite Guests to the workspace; a project manager can then share projects with them.

## Who can delete a project?

Only a project manager: the Member who created it, anyone granted `manager`, or any Owner or Admin. Deleted projects stay in **Projects → Trash** for **30 days**. See `services/projects/docs/projects-and-tasks.md`.

## What happens to projects when a member is removed?

The person loses access immediately. Projects and tasks they created stay in the workspace. Project manager rights they held as the creator pass to the Owner or Admin who removed them, as described in `services/accounts/docs/members-and-roles.md`. Tasks assigned to them stay assigned and show the person as deactivated.

## Can API keys access private projects?

An API key with the `projects:read` or `projects:write` scope acts with the access of an Admin, so it can reach every project in the workspace, including private ones. Only Owners and Admins can create keys. See `services/auth/docs/api-keys.md`.

Last reviewed: 2026-11-26
