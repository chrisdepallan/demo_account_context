# Contributing

## What belongs in this repository?

This repository is the context library `acme-account-context`. An MCP documentation server indexes it so AI assistants can answer questions about Acme Cloud. It holds documentation, small service modules with tests, API specs, configuration, reports and datasets. All of the content is fictional.

Do not add secrets, real customer data, payment card numbers, government ID numbers or health records, not even as examples. Access to the library is all-or-nothing, so restricted material belongs in a separate repository.

## How should a Markdown doc be structured?

- Start with one `# Title` line and then use flat `##` sections. Do not use `###` headings and do not put text between the title and the first `##`.
- Write one topic per `##` section. The MCP server splits documents at `##` headings, so each section must make sense when read alone.
- In customer-facing docs, phrase each `##` heading the way a customer would ask the question.
- Put concrete values such as amounts, durations and limits in the sentence text, in **bold**, and not only in a table.
- Refer to other files as backticked paths such as `services/billing/docs/refunds.md`. Do not use Markdown hyperlinks.
- End every doc with a `Last reviewed: YYYY-MM-DD` line and update that line when the doc changes.

## How should a service folder be laid out?

Every service under `services/` uses the same layout:

| Path | Contents |
|------|------|
| `README.md` | What the service does, key concepts, how to use it, its docs, its code, its owners |
| `docs/` | One Markdown file per topic |
| `openapi.yaml` | The API specification of the service |
| `config/default.yaml` | Default configuration. Secrets are named as environment variables only |
| `acme_<service>/` | The Python package. Standard library only |
| `tests/` | `unittest` tests named `test_*.py` |
| `fixtures/` | Sample data. Not meant for indexing |
| `CHANGELOG.md` | Generated. Do not edit by hand |

## What must pass before a change is merged?

Run these three commands from the repository root. CI runs the same three in `.github/workflows/ci.yml`.

1. `python tools/run_tests.py` – every service's tests pass.
2. `python tools/check_links.py` – every referenced file exists and every doc has the required headings.
3. `python tools/generate_reports.py --check` – generated files are up to date.

If the third check fails, run `python tools/generate_reports.py` and commit the result. Details are in `tools/README.md`.

## Which files are generated?

Everything in `reports/` and `data/`, each service's `CHANGELOG.md`, and the `sample-*.json` files in `services/*/fixtures/` are written by `tools/generate_reports.py`. The one exception is `services/billing/fixtures/sample-invoices.json`, which is maintained by hand.

## What should never be committed?

Caches, build output, virtual environments and editor settings are excluded by `.gitignore`. Do not commit `__pycache__` folders, coverage output, local environment files, private keys or anything else that a normal GitHub repository would leave out.

## What happens after a change is merged?

There is no automatic sync. Re-index the library in the MCP server after merging any change to `main`.

Last reviewed: 2026-11-26
