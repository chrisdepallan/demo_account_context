# Storage Quotas

## How much storage do I get?

| Plan | Storage |
|------|---------|
| Free | 2 GB total |
| Starter | 10 GB per seat |
| Pro | 50 GB per seat |
| Business | 200 GB per seat |
| Enterprise | 1 TB per seat |

Free accounts get **2 GB** in total, however many members they have. Paid plans get storage per paid seat: **10 GB** on Starter, **50 GB** on Pro, **200 GB** on Business and **1 TB** on Enterprise. For example, a Pro account with **8** seats has **400 GB**. The full plan comparison is in `services/accounts/docs/plans-and-limits.md`.

## Is storage per person or shared?

Shared. The quota is one pool for the whole account, across all of its workspaces. One member can use more than their seat's share as long as the account total stays under the quota. Guests do not add storage because they do not use seats.

## What counts towards my storage?

- The current version of every file.
- Every older version still kept in version history.
- Files in the trash, until they are permanently deleted.

Files in quarantine, unfinished upload sessions and task comments do not count. Sizes are measured in binary units: **1 GB** is 1,024 MB and **1 TB** is 1,024 GB.

## Where can I see how much storage I am using?

Owners and Admins go to **Settings → Storage**. The page shows total usage against the quota, a breakdown by workspace, and the split between current files, older versions and the trash. Usage figures are refreshed every **15 minutes**. Through the API, use `GET /v2/files/{workspace_id}/usage`.

## What happens when I reach the storage limit?

At **90%** usage the Owner and Admins get an email warning and a banner appears in **Files**. At **100%**, new uploads and new versions are blocked with the error code `quota_exceeded`. Existing files stay accessible and editable, and can still be downloaded, shared, moved and deleted. An upload that would take the account over 100% is rejected as a whole; partial files are never stored.

## How do I free up storage?

- Empty the trash under **Files → Trash** (Owners and Admins).
- Delete old versions of large files under **Version history**.
- Delete files that are no longer needed, then delete them permanently from the trash.

Freed space shows up in the usage figures within **15 minutes**, but the upload block is lifted as soon as usage drops below 100%.

## How do I get more storage?

- **Add seats** – each seat adds the plan's per-seat allowance.
- **Upgrade the plan** – takes effect immediately.
- **Add a storage pack** – **100 GB** for **$10/month** each, under **Settings → Billing → Storage packs** (Owner and Billing admin only).

Any of these lifts an upload block immediately. Storage packs are available on Starter and above, up to **50 packs** per account. Accounts that need more should contact `sales@acme-cloud.example`. Pricing and proration are covered in `services/billing/docs/pricing.md`.

## Can I downgrade if I am using more than the lower plan allows?

No. A downgrade, a seat reduction or removing a storage pack is blocked while current usage is above the quota the account would have afterwards. Reduce usage first, then try again.

## What happens to storage when the account is read-only or closed?

In the `read_only` state, files can be viewed and downloaded but not uploaded or changed. When an account is closed, its files are kept for the **30-day** data retention window and then permanently deleted. See `services/accounts/docs/account-lifecycle.md`.

Last reviewed: 2026-11-26
