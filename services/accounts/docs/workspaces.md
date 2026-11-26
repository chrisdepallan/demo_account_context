# Workspaces

## What is a workspace?

A workspace is a container for projects, files and members inside an account. Each workspace has its own members, settings, API keys and data region. Workspace IDs look like `ws_4H8P2L` – the prefix `ws_` followed by **6** uppercase letters and digits. The account that owns the workspace is billed for every seat used in it.

## How many workspaces can an account have?

| Plan | Workspaces |
|------|------------|
| Free | 1 |
| Starter | 1 |
| Pro | 3 |
| Business | 10 |
| Enterprise | Unlimited |

Free and Starter accounts have **1** workspace, Pro accounts up to **3**, Business accounts up to **10** and Enterprise accounts an unlimited number. Archived workspaces still count towards the limit. Workspaces waiting in the 30-day restore window after deletion do not count.

## Who can create a workspace?

The Owner and Admins can create a workspace from **Settings → Account → Workspaces → New workspace**. They choose a name and a data region. The name must be **3–64 characters** long and unique within the account. The person who creates the workspace is added to it as an Admin, unless they are the Owner.

## Which region can a workspace use?

| Region code | Location | Plans |
|-------------|----------|-------|
| `us-east` | Virginia, USA | All plans (default) |
| `eu-central` | Frankfurt, Germany | Business and Enterprise |
| `ap-south` | Mumbai, India | Enterprise only |

New workspaces default to `us-east`. Business accounts can also choose `eu-central`, and Enterprise accounts can choose any of the **3** regions. Different workspaces in the same account can be in different regions.

## Can I change the region of a workspace?

No. The region is chosen when the workspace is created and cannot be changed afterwards. To move regions, export the workspace data, create a new workspace in the target region and import the data there. See `services/accounts/docs/data-export-and-deletion.md` for how exports work.

## Can I rename a workspace?

Yes. The Owner and Admins can rename a workspace at any time from **Settings → Workspace → General**. Renaming does not change the workspace ID, so API keys, SSO connections and integrations keep working.

## What does archiving a workspace do?

Archiving makes a workspace read-only without deleting anything. Members can still view and download content but cannot edit it. The Owner and Admins archive and unarchive from **Settings → Workspace → General → Archive workspace**. An archived workspace still counts towards the plan's workspace limit, and its members still use seats.

## How do I delete a workspace?

1. The Owner goes to **Settings → Workspace → General → Delete workspace**.
2. They type the workspace name to confirm.
3. Members lose access immediately and the workspace's API keys stop working.

Only the Owner can delete a workspace. Admins cannot. A deleted workspace can be restored by the Owner for **30 days** from **Settings → Account → Workspaces → Deleted**. After 30 days the data is permanently erased. An account must always keep at least **1** workspace, so the last workspace cannot be deleted; close the account instead, as described in `services/accounts/docs/account-lifecycle.md`.

## What happens to my workspaces when I downgrade?

A downgrade is blocked while the account has more workspaces than the lower plan allows. For example, a Pro account with 3 workspaces must delete 2 before moving to Starter. The one exception is the end of a trial without a payment method: the account moves to Free, the oldest workspace stays active and any others are archived until the account upgrades.

## Do members belong to the account or to a workspace?

Members are invited to a workspace, and a person can be a member of any number of workspaces. A person who is a member of several workspaces in the same account uses only **1** seat. Roles are set per workspace, except the Owner and Billing admin roles, which apply to the whole account. See `services/accounts/docs/members-and-roles.md`.

Last reviewed: 2026-11-26
