# Search Filters and Sorting

## What filters can I use in a search?

A filter is written as `key:value` with no space around the colon. A query can contain up to **10 filters**.

| Filter | Accepted values | Example |
|--------|-----------------|---------|
| `type:` | `project`, `task`, `file` | `type:task` |
| `status:` | `open`, `completed`, `archived` | `status:open` |
| `assignee:` | `me`, `none` or an email address | `assignee:me` |
| `owner:` | `me` or an email address | `owner:me` |
| `project:` | a project ID | `project:prj_4K7M2Q9X` |
| `label:` | a label name; quote it if it has spaces | `label:"q3 launch"` |
| `ext:` | a file extension | `ext:pdf` |
| `in:` | `title`, `content` | `in:title` |
| `has:` | `attachment`, `comment`, `due` | `has:attachment` |
| `created:`, `updated:`, `due:` | a date or date range | `updated:>=2026-11-01` |

Filters narrow the results but do not change the relevance score.

## How do I find tasks assigned to me?

Search `type:task assignee:me`. Add `status:open` to hide completed tasks. `assignee:none` finds tasks nobody is assigned to, and `assignee:` followed by a member's email address finds that member's tasks.

## How do I filter by date?

Dates use the ISO format `YYYY-MM-DD` and are interpreted in UTC.

- `created:2026-11-26` – on that day
- `updated:>=2026-11-01` – on or after that day (`>`, `>=`, `<` and `<=` are supported)
- `due:2026-12-01..2026-12-31` – between two days, both included

Words such as "today" or "yesterday" are not accepted and return `400 invalid_query`.

## What happens when I use the same filter twice?

- The same filter repeated matches **any** of the values: `type:task type:file` returns tasks and files.
- Different filters must **all** match: `type:task status:open` returns only open tasks.
- Date filters are the exception: repeated date filters must all match, so `created:>=2026-01-01 created:<2026-02-01` means January 2026.

## Can I exclude with a filter?

Yes. Put a minus sign in front: `-type:file` hides files and `-label:internal` hides items with that label.

## How do I search only in titles?

Add `in:title`. Without it, search looks at titles and content. `in:content` does the opposite and ignores titles. Searching inside file contents needs the Pro plan or above; see `services/search/docs/search-limits.md`.

## How are results sorted?

By default results are sorted by **relevance**, best match first. In the app, use the **Sort** menu above the results; in the API, use the `sort` and `order` parameters.

| Sort | Meaning | Default order |
|------|---------|---------------|
| `relevance` | Best match first (default) | `desc` only |
| `updated_at` | Last change | `desc` |
| `created_at` | Creation date | `desc` |
| `title` | Alphabetical by title | `asc` |
| `due_date` | Task due date; items without one come last | `asc` |

A query that has only filters and no words, such as `type:file ext:pdf`, has no relevance to compute, so it is returned most recently updated first.

## How is relevance calculated?

Three things decide the score:

- **How often the words appear** – more matches score higher, but with diminishing returns: the tenth mention adds far less than the first.
- **Where they appear** – a match in the title counts **3 times** as much as a match in the content. An exact phrase match adds a further bonus.
- **How recent the item is** – the score is multiplied by a recency factor that starts at **1.0** and halves its distance to **0.5** every **30 days**. An item updated 30 days ago keeps **75%** of its score; a very old item keeps **50%**.

Items with the same score are ordered by most recently updated.

## Why do I not see an item I know exists?

- You may not have access to it. Search only returns items you can open; Guests see only the projects shared with them.
- It may be in the trash. Trashed items are not searchable.
- It may be in another workspace. Search covers one workspace at a time.
- It may be too new. See `services/search/docs/indexing-and-freshness.md` for how long indexing takes.

Last reviewed: 2026-11-26
