# Versioning and Trash

## How long is version history kept?

| Plan | Version history |
|------|-----------------|
| Free | 7 days |
| Starter | 30 days |
| Pro | 180 days |
| Business | 1 year (365 days) |
| Enterprise | Unlimited |

Older versions of a file are kept for **7 days** on Free, **30 days** on Starter, **180 days** on Pro and **1 year** on Business. Enterprise keeps versions with no time limit. The window is counted from the moment a version was replaced by a newer one. The current version of a file is never removed by these rules.

## When is a new version created?

A new version is created each time a file's content is replaced: by uploading a file with the same name into the same folder, by selecting **Upload new version** on the file, or by completing an API upload that names an existing file ID. Renaming or moving a file does not create a version.

## Is there a limit on the number of versions?

Yes. A file keeps at most **100 versions**, including the current one, on every plan. When a 101st version is saved, the oldest version is removed even if it is still inside the plan's version history window.

## How do I restore an older version?

Open the file, select **Version history**, pick a version and select **Restore**. Restoring copies the old content into a new current version, so nothing is lost and the restore can itself be undone. Owners, Admins and Members can restore versions. Guests can only see the current version.

## Do old versions count towards storage?

Yes. Every stored version counts at its full size. A **100 MB** file with **3** stored versions uses **300 MB**. To free space, delete single versions under **Version history**, or see `services/files/docs/storage-quotas.md`.

## What happens to versions when I downgrade?

The shorter window of the new plan applies from the day the downgrade takes effect. Versions older than the new window are removed within **24 hours**. For example, moving from Pro to Starter removes versions that were replaced more than **30 days** ago.

## How long do deleted files stay in the trash?

Deleted files and folders stay in **Files → Trash** for **30 days** on every plan, then they are permanently deleted together with all their versions. Files in the trash still count towards storage until they are permanently deleted.

## How do I restore a file from the trash?

Go to **Files → Trash**, select the file and choose **Restore**. The file returns to its original folder with its full version history. If the original folder no longer exists, the file is restored to the top level of the workspace. Members can restore files they deleted; Owners and Admins can restore any file.

## Can I delete a file permanently before 30 days?

Yes. In **Files → Trash**, select the file and choose **Delete permanently**. Members can do this for files they deleted. Owners and Admins can also select **Empty trash** to remove everything at once. Permanent deletion frees the storage immediately and cannot be undone.

## Can support recover a permanently deleted file?

No. Once a file has left the trash, whether after **30 days** or by permanent deletion, it cannot be recovered by support. The trash is separate from the **30-day** data retention window for closed accounts described in `docs/glossary.md`.

Last reviewed: 2026-11-26
