# Search Indexing and Freshness

## What does search index?

| Item | Indexed fields |
|------|----------------|
| Project | Name, description, labels, owner, status |
| Task | Title, description, comments, labels, assignee, status, due date |
| File | File name, extension, owner, and the text content on Pro and above |

Each workspace has its own index. Search never returns results from another workspace or another account.

## How long until a change shows up in search?

| Change | Searchable within |
|--------|-------------------|
| Project or task created or edited | **30 seconds** |
| File uploaded or renamed (file name) | **30 seconds** |
| File contents (text extraction) | **5 minutes** |
| Item deleted, moved to trash or access removed | **60 seconds** |

These are targets for 95% of changes. During an incident indexing can lag; the current lag is shown under **Settings → Workspace → Search** and at `https://status.acme-cloud.example`.

## Which file types are searched by content?

On Pro, Business and Enterprise, search reads the text inside these file types: **txt, md, csv, pdf, docx, xlsx, pptx**. Other types, including images and scanned PDFs without a text layer, are searchable by file name only.

- Files larger than **100 MB** are indexed by name only.
- At most the first **10 MB** of extracted text per file is indexed.
- Only the current version of a file is indexed, not older versions.

On Free and Starter, files are searchable by name, extension and owner only.

## Where is the search index stored?

In the same region as the workspace: `us-east`, `eu-central` or `ap-south`. Index data never leaves that region, and it is encrypted at rest. Because the region of a workspace cannot be changed, the index region cannot be changed either.

## Do permissions apply to search results?

Yes. Every result is checked against the searcher's access when the search runs. Members see the projects they belong to, Guests see only the projects shared with them, and API keys see only what their scopes allow (`projects:read` for projects and tasks, `files:read` for files). When access is removed, the item stops appearing within **60 seconds**.

## What happens to the index when items are deleted?

Items moved to the trash are removed from search within **60 seconds** and come back if they are restored. When an account is closed, its indexes are deleted together with the rest of the data at the end of the **30-day** data retention window described in `services/accounts/docs/account-lifecycle.md`.

## How do I rebuild the search index?

Owners and Admins go to **Settings → Workspace → Search → Rebuild index**. A rebuild is rarely needed; use it if results are clearly missing after the times above.

- A workspace can start **1 rebuild every 24 hours**.
- A rebuild processes about **1 million items in up to 4 hours**. Search keeps working from the old index while it runs.
- Progress is shown on the same page and is returned by `GET /v2/search/{workspace_id}/index-status`.

## How does the index stay up to date? (internal)

The Projects and Files services publish change events such as `project.created`, `task.completed` and `file.uploaded`. The indexer consumes them in batches of up to **500 events** or every **2 seconds**, whichever comes first. A failed batch is retried up to **5 times** with exponential backoff, then moved to a dead-letter queue and raised in `#team-search`.

Text is analysed the same way at index time and at query time: lowercased, split into words, stop words removed and word endings reduced to a simple stem. Words longer than **64 characters** are not indexed. The implementation is in `services/search/README.md` under "Code in this service".

Last reviewed: 2026-11-26
