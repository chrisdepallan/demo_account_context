# Uploads and Limits

## What is the maximum file size?

| Plan | Max file upload |
|------|-----------------|
| Free | 250 MB |
| Starter | 250 MB |
| Pro | 5 GB |
| Business | 5 GB |
| Enterprise | 5 GB |

Free and Starter accounts can upload files up to **250 MB**. Pro, Business and Enterprise accounts can upload files up to **5 GB**. The limit applies to each file, not to a whole upload batch. A larger file is rejected with HTTP `413` and the error code `file_too_large`. The full plan comparison is in `services/accounts/docs/plans-and-limits.md`.

## Who can upload files?

Owners, Admins and Members can upload, rename, move and delete files. Guests can view and comment on files shared with them but cannot upload. Billing admins have no access to files. Uploads are also blocked while the account is `read_only` or over its storage quota; see `services/files/docs/storage-quotas.md`.

## How do I upload a file?

Drag files into **Files**, or select **Files → Upload**. Up to **500 files** can be added in one batch, and **4** upload at the same time. Uploading a file with the same name into the same folder creates a new version instead of a second file; see `services/files/docs/versioning-and-trash.md`.

## How do large uploads work?

Files up to **100 MB** are sent in a single request. Files over **100 MB** use a resumable upload session, which the web and desktop apps start automatically:

- The file is split into chunks of **8 MB** by default. API clients can choose a chunk size from **5 MB** to **64 MB**.
- If the connection drops, the upload resumes from the last finished chunk.
- An upload session expires **24 hours** after it was started. Unfinished chunks are then discarded and do not count towards storage.

Through the API, start a session with `POST /v2/files/{workspace_id}/uploads` and finish it with `POST /v2/files/{workspace_id}/uploads/{upload_id}/complete`.

## Which file types are blocked?

Executable and script files that commonly carry malware cannot be uploaded: `.exe`, `.bat`, `.cmd`, `.scr`, `.msi` and `.vbs`. The upload is rejected with the error code `file_type_blocked`. All other file types are allowed. The block list is the same on every plan and cannot be changed per workspace.

## Are uploads scanned for malware?

Yes. Every file is scanned when the upload completes. A file that fails the scan is moved to quarantine: it cannot be downloaded or shared, and the uploader and the workspace Admins are notified. Quarantined files are deleted after **14 days**. If you believe a file was flagged by mistake, contact `support@acme-cloud.example` with the file ID, for example `fil_6T2R9WQ4`.

## What are the limits on names and folders?

| Limit | Value |
|-------|-------|
| File or folder name length | 255 characters |
| Folder depth | 20 levels |
| Items per folder | 50,000 |
| Files per upload batch | 500 |

A file or folder name can be up to **255 characters** and cannot contain `/` or `\`. Folders can be nested up to **20 levels** deep, and one folder can hold up to **50,000 items**.

## How is upload integrity checked?

The service computes a SHA-256 checksum of every finished upload and returns it in the file metadata. API clients can send their own checksum when completing an upload; if the two differ, the upload fails with `checksum_mismatch` and nothing is stored.

## Why did my upload fail?

| Error code | HTTP status | Meaning |
|------------|-------------|---------|
| `file_too_large` | 413 | The file is over the plan's maximum file size |
| `quota_exceeded` | 507 | The account has used 100% of its storage |
| `file_type_blocked` | 422 | The file extension is on the block list |
| `upload_expired` | 410 | The upload session is older than 24 hours |
| `checksum_mismatch` | 422 | The content did not match the checksum sent |
| `forbidden` | 403 | The role cannot upload, or the account is `read_only` |

Last reviewed: 2026-11-26
