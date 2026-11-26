# Search Service

## What it does

The Search service provides full-text search across the projects, tasks and files of a workspace. It parses the query, applies filters, ranks the matches and returns only results the person searching is allowed to see. It keeps its own index, which is updated from change events sent by the Projects and Files services.

## Key concepts

- **Query** – the text typed into the search box, up to **512 characters**: words, `"exact phrases"`, `-excluded` words and `key:value` filters.
- **Filter** – a `key:value` condition such as `type:task` or `assignee:me` that narrows results without affecting relevance.
- **Index** – the per-workspace search data, stored in the workspace's region (`us-east`, `eu-central` or `ap-south`).
- **Freshness** – how quickly a change becomes searchable: **30 seconds** for projects, tasks and file names, **5 minutes** for file contents.
- **Relevance score** – term frequency, a **3×** title boost and a recency decay with a **30-day** half-life.
- **Content search** – searching inside file contents, available on Pro, Business and Enterprise.
- **Saved search** – a query stored by a member for reuse; IDs look like `srch_5T8W2N6C`.

## How to use it

- Customer-facing search: the search box at the top of every page, or **Search → Advanced search** for the filter builder.
- Saved searches: **Search → Saved searches**. Index status and rebuild: **Settings → Workspace → Search** (Owner and Admin only).
- Internal API base URL: `https://api.acme-cloud.example/v2/search`
- Common endpoints:
  - `GET /v2/search/{workspace_id}/query` – run a search
  - `GET /v2/search/{workspace_id}/suggest` – autocomplete suggestions
  - `GET /v2/search/{workspace_id}/saved-searches` – list the caller's saved searches
  - `POST /v2/search/{workspace_id}/saved-searches` – save a search
  - `DELETE /v2/search/{workspace_id}/saved-searches/{saved_search_id}` – delete a saved search
  - `GET /v2/search/{workspace_id}/index-status` – index health and lag
  - `POST /v2/search/{workspace_id}/reindex` – rebuild the index (Owner and Admin only)

## Docs in this service

- `docs/query-syntax.md` – words, phrases, exclusions, OR and wildcards
- `docs/filters-and-sorting.md` – every filter, date ranges, sort orders and ranking
- `docs/indexing-and-freshness.md` – what is indexed, how fast, and how to rebuild
- `docs/search-limits.md` – query, result, rate and per-plan limits

## Code in this service

- `acme_search/tokenizer.py` – lowercasing, stop words and simple stemming
- `acme_search/query_parser.py` – turns a query string into terms, phrases, exclusions and filters
- `acme_search/ranking.py` – relevance scoring: term frequency, title boost, recency decay
- `tests/` – unit tests; run `python -m unittest discover -s tests` from this folder
- `openapi.yaml` – OpenAPI 3.0 description of the endpoints above
- `config/default.yaml` – default limits, timeouts, feature flags and per-region settings

## Owners

Team: Search and Discovery. Slack channel: `#team-search` (fictional).
