# Repository Tools

## What tools does this repository have?

All tools are plain Python scripts that use the standard library only. They need **Python 3.12 or later** and no installed packages. Run them from the repository root.

| Script | What it does |
|------|------|
| `tools/run_tests.py` | Runs the `unittest` suite of every service under `services/` |
| `tools/check_links.py` | Checks that every backticked file path in the Markdown docs exists, and that every doc has an H1 and at least one `##` section |
| `tools/generate_reports.py` | Writes everything in `reports/` and `data/`, plus each service's `CHANGELOG.md` and generated `fixtures/` |

## How do I run the tests?

Run `python tools/run_tests.py` to test every service, or name the services you want, for example `python tools/run_tests.py billing auth`. Each service is tested from its own folder with `python -m unittest discover -s tests`, so one service can also be tested by hand from inside `services/<service>/`.

## How do I regenerate the reports and datasets?

Run `python tools/generate_reports.py`. The script uses a fixed seed and a fixed reference date of **2026-11-26** instead of the system clock, so running it twice produces identical files. Do not edit generated files by hand: change the script and run it again.

Some generated content is read from the hand-written part of the repo. Test names in the weekly test-run reports come from `services/*/tests/`, and endpoint names in the performance reports come from each service's `openapi.yaml`. After adding a test or an endpoint, run the generator again.

## How do I check that generated files are up to date?

Run `python tools/generate_reports.py --check`. It writes nothing and exits with code **1** if any generated file differs from what the script would produce. CI runs this check on every pull request.

## How do I make the repository larger for load testing?

Run `python tools/generate_reports.py --scale N`. The default scale of **1** covers 12 months and produces about 115 generated files. Each step of scale adds another 12 months of history: 24 more incident postmortems, 20 more weekly test runs, 12 more performance reports, 12 more release notes and 4 more quarters of reviews. A scale of **10** produces about 830 generated files. Running with a smaller scale afterwards does not delete the extra files, so remove `reports/` and `data/` first when scaling down.

Last reviewed: 2026-11-26
