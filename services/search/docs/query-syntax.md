# Search Query Syntax

## How do I search for something?

Type words into the search box at the top of any page and press Enter. Search looks at the projects, tasks and files of the current workspace and shows the best matches first. A query can be up to **512 characters** long.

Every word must match by default. Searching `budget review` returns only items that contain both "budget" and "review", in any order, in the title or the content.

## Is search case-sensitive?

No. `Budget`, `budget` and `BUDGET` return the same results. Search also matches simple word forms: `plan` finds "plans", "planned" and "planning", and `file` finds "files".

## Which words are ignored?

Very common English words (stop words) are ignored outside quotes: **a, an, and, are, as, at, be, but, by, for, from, in, is, it, of, on, or, that, the, this, to, was, with**. Searching `the budget for marketing` is the same as searching `budget marketing`.

To search for a stop word, put it inside an exact phrase.

## How do I search for an exact phrase?

Put the words in double quotes: `"launch plan"`. The words must appear next to each other in that order. Inside quotes nothing is ignored and word forms are not matched, so `"state of the art"` matches only that exact wording.

## How do I exclude a word?

Put a minus sign directly in front of it, with no space: `budget -draft` returns items that contain "budget" but not "draft". The minus sign also works on phrases (`-"draft copy"`) and on filters (`-type:file`).

## How do I search for one word or another?

Write `OR` in capital letters between two plain words: `launch OR release` returns items containing either word. `OR` only joins the two words next to it. `launch OR release notes` means "(launch or release) and notes".

`OR` cannot be placed next to a phrase, a filter or an excluded word, and lowercase `or` is treated as a stop word.

## Can I search for the start of a word?

Yes. End the word with an asterisk: `road*` matches "roadmap" and "roadshow". At least **3 characters** are needed before the `*`. The asterisk only works at the end of a word, and a wildcard cannot be excluded with a minus sign.

## How do I combine everything?

All parts can be mixed in one query. For example:

`type:task assignee:me "launch plan" -draft`

returns tasks assigned to you that contain the exact phrase "launch plan" and do not contain "draft". Filters such as `type:` and `assignee:` are explained in `services/search/docs/filters-and-sorting.md`.

## Syntax quick reference

| You type | It means |
|----------|----------|
| `budget review` | Both words, any order |
| `"budget review"` | Exact phrase |
| `budget -draft` | "budget" but not "draft" |
| `launch OR release` | Either word |
| `road*` | Words starting with "road" (minimum **3 characters**) |
| `type:task` | A filter – see `services/search/docs/filters-and-sorting.md` |
| `-type:file` | Everything except files |
| `tsk_8G2K4M1P` | An item by its ID |

## Why do I get an "invalid query" error?

Search returns `400 invalid_query` with a message when:

- the query is empty or contains only stop words
- the query is longer than **512 characters**, has more than **32 search terms** or more than **10 filters**
- a wildcard has fewer than **3 characters** before the `*`
- `OR` is at the start or end of the query, or next to a phrase or filter
- a filter has a value it does not accept, for example `type:folder` or `created:yesterday`

A `key:value` pair whose key is not a known filter is not an error: `colour:blue` simply searches for the words "colour" and "blue".

Last reviewed: 2026-11-26
