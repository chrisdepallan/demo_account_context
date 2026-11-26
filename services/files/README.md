# Files Service

## What it does

The Files service is the file-storage product of Acme Cloud. It handles uploads and downloads, folders, version history, the trash, share links and storage quotas. It reads the plan, seat count and storage packs from the Accounts and Billing services to work out how much storage an account has.

## Key concepts

- **File** – a stored object in a workspace folder; IDs look like `fil_6T2R9WQ4`.
- **Upload session** – a resumable upload made of chunks, required for files over **100 MB**; IDs look like `upl_7N4C1VB8`.
- **Version** – a saved copy of a file's content; kept for the plan's version history window.
- **Trash** – where deleted files stay for **30 days** before permanent deletion.
- **Share link** – a URL that gives `view`, `comment` or `edit` access to a file or folder; IDs look like `lnk_2P8D5KM3`.
- **Storage quota** – total storage of an account: the plan allowance per seat plus any storage packs, pooled across all workspaces.

## How to use it

- Customer-facing screens: **Files** in the left sidebar, **Files → Trash**, usage under **Settings → Storage**, and sharing policy under **Settings → Files → Sharing** (Owner and Admin only).
- Internal API base URL: `https://api.acme-cloud.example/v2/files`
- API keys need the `files:read` or `files:write` scope. Free accounts cannot use the API.
- Common endpoints:
  - `GET /v2/files/{workspace_id}/files` – list files in a folder
  - `POST /v2/files/{workspace_id}/uploads` – start an upload session
  - `POST /v2/files/{workspace_id}/uploads/{upload_id}/complete` – finish an upload and create the file or a new version
  - `GET /v2/files/{workspace_id}/files/{file_id}` – file metadata and download URL
  - `DELETE /v2/files/{workspace_id}/files/{file_id}` – move a file to the trash
  - `POST /v2/files/{workspace_id}/files/{file_id}/restore` – restore a file from the trash
  - `GET /v2/files/{workspace_id}/files/{file_id}/versions` – list versions
  - `POST /v2/files/{workspace_id}/files/{file_id}/share-links` – create a share link
  - `GET /v2/files/{workspace_id}/usage` – storage used and quota

## Docs in this service

- `docs/uploads-and-limits.md` – file size limits, resumable uploads, blocked file types and scanning
- `docs/versioning-and-trash.md` – version history per plan, restoring versions and the trash
- `docs/sharing-links.md` – share link access levels, expiry, passwords and per-plan rules
- `docs/storage-quotas.md` – how storage is calculated, warnings and storage packs

## Code in this service

- `acme_files/quotas.py` – storage quota per plan, usage states and upload checks
- `acme_files/versioning.py` – version retention and trash expiry
- `acme_files/share_links.py` – share link expiry, password and access-level rules
- `tests/` – `unittest` tests; run `python -m unittest discover -s tests` from this folder
- `openapi.yaml` – OpenAPI 3.0 spec for the endpoints above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings

## Owners

Team: Storage Platform. Slack channel: `#team-storage` (fictional).
