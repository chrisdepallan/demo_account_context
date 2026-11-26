# Search Limits

## What are the search limits on each plan?

| Limit / feature | Free | Starter | Pro | Business | Enterprise |
|-----------------|------|---------|-----|----------|------------|
| Search projects, tasks and file names | Yes | Yes | Yes | Yes | Yes |
| Search inside file contents | No | No | Yes | Yes | Yes |
| Saved searches per member | 5 | 25 | 50 | 100 | 250 |
| Search API | No | Yes | Yes | Yes | Yes |
| API requests (shared with all other API calls) | – | 300/min | 1,000/min | 3,000/min | 10,000/min |

The API request limits are the account-wide limits from `services/accounts/docs/plans-and-limits.md`. Search does not have a separate API allowance.

## How long can a search query be?

- Up to **512 characters**.
- Up to **32 search terms** (words, phrases, wildcards and excluded words all count).
- Up to **10 filters**.
- A wildcard needs at least **3 characters** before the `*`.

Queries over these limits return `400 invalid_query`. The syntax is described in `services/search/docs/query-syntax.md`.

## How many results does a search return?

A page holds **50 results** by default and at most **200**. In the API, set the page size with `limit` and fetch the next page with the `cursor` value from the previous response.

A single query can page through at most the first **10,000 results**. If a search matches more than that, add filters to narrow it. The `total` field in the response is exact up to **10,000** and reported as `10000` with `total_is_capped: true` above that.

## Is search rate limited?

Yes, in two ways:

- **In the app** – each member can run up to **30 searches per minute**. Autocomplete suggestions do not count.
- **In the API** – search requests count against the account's API rate limit for its plan (for example **1,000/min** on Pro). The limit is per account, not per API key.

Over either limit, the response is HTTP `429 Too Many Requests` with a `Retry-After` header in seconds.

## Can I use search through the API?

Yes, on Starter and above. Free accounts cannot use the API. The API key needs `projects:read` to get projects and tasks in the results, and `files:read` to get files. A key with only one of these scopes gets only that kind of result. Creating keys is described in `services/auth/docs/api-keys.md`.

## How long does a search take before it times out?

A search is stopped after **5 seconds**. If some matches were found by then, they are returned with `partial: true` so the app can show them with a notice. If nothing was found in time, the response is `503 search_timeout`; narrowing the query with filters usually fixes it.

Autocomplete suggestions have a shorter timeout of **500 milliseconds**, need at least **2 characters** and return up to **8 suggestions**.

## How many saved searches can I have?

**5** on Free, **25** on Starter, **50** on Pro, **100** on Business and **250** on Enterprise, per member per workspace. Saved searches are private to the member who created them. Manage them under **Search → Saved searches**. A saved search name can be up to **80 characters**.

After a downgrade, existing saved searches above the new limit are kept, but no new ones can be created until the count is below the limit.

## Are there limits on file content search?

Yes. Content search is available on Pro, Business and Enterprise and covers **txt, md, csv, pdf, docx, xlsx, pptx** files up to **100 MB**, reading the first **10 MB** of text per file. Details are in `services/search/docs/indexing-and-freshness.md`.

## How often can the index be rebuilt?

Owners and Admins can start **1 rebuild per workspace every 24 hours** from **Settings → Workspace → Search**. A second request inside that window returns `429 reindex_cooldown`.

Last reviewed: 2026-11-26
