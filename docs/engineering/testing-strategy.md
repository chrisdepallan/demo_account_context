# Testing Strategy

## What kinds of tests does Acme Cloud write?

Acme Cloud services use three kinds of automated tests. All three are written with the standard `unittest` module.

| Kind | What the test covers | Share of tests |
|------|----------------------|----------------|
| Unit test | One function or class, no I/O | About **70%** |
| Service test | One endpoint of one service, with in-memory stand-ins for the database and the event bus | About **25%** |
| Contract test | The service's responses compared with the service's OpenAPI description | About **5%** |

End-to-end checks across several services run in the staging environment as part of the release process and are not stored in the service test folders.

## How do I run the tests?

Run every service's tests from the repository root:

```bash
python tools/run_tests.py
```

Run the tests of one service, for example the Billing service:

```bash
python -m unittest discover -s services/billing/tests -t services/billing
```

The full test run for all 12 services must finish in under **5 minutes** on a developer laptop. A single test that takes longer than **2 seconds** is treated as a defect.

## Where do tests live and how are tests named?

Each service keeps its tests in the tests folder inside the service folder. Test files are named `test_<module>.py`, test classes are named `Test<Subject>` and test methods are named `test_<behaviour>`, for example `test_refund_rejected_after_window`. A test name states the expected behaviour, so that a failing test explains itself in the test report.

## What must be tested?

- Every public function has at least **1** test for the normal case and **1** test for a failure case.
- Every endpoint in a service's OpenAPI description has at least **1** service test for a success response and **1** for each documented error response.
- Every concrete business rule in the documentation has a test. Examples are the **14-day** grace period, the lockout after **5 failed login attempts within 15 minutes** and the **30-day** data retention window.
- Every bug fix comes with a regression test that fails without the fix.
- Permission checks are tested for each role: Owner, Admin, Billing admin, Member and Guest.

## What must tests never do?

- Tests never call the network. Calls to other services and to external providers are replaced with stand-ins.
- Tests never read the real clock. The current time is passed in, so that rules based on days and minutes can be tested exactly.
- Tests never depend on the order in which tests run, and never share state between test methods.
- Tests never contain real customer data, real email addresses, payment details or secrets. Email addresses in tests use the domain `acme-cloud.example`.
- Tests never sleep to wait for a result.

## What are fixtures and how are fixtures used?

Fixtures are small files of sample data that tests load, for example sample invoices. Each service keeps its fixtures in a fixtures folder inside the service folder. Fixtures are fictional, use the documented ID formats such as `acc_7F3K9Q2M` and `INV-2026-004812`, and are excluded from the MCP documentation index. Generated fixtures are produced by `tools/generate_reports.py` and are not edited by hand.

## What does continuous integration check?

The GitHub Actions workflow `.github/workflows/ci.yml` runs on every pull request and on every push to `main`. The workflow runs three checks:

1. `tools/run_tests.py` – every service's `unittest` tests.
2. `tools/check_links.py` – every backticked repository path in a Markdown file must exist.
3. `tools/generate_reports.py` – the generated reports, data files, service changelogs and fixtures must be up to date.

A pull request cannot be merged while any of the three checks fails. A failing check on `main` is fixed or reverted within **1 hour**.

## How are flaky tests handled?

A flaky test is a test that passes and fails without a code change. A flaky test is reported in the owning team's Slack channel and fixed or removed within **2 business days**. Re-running the workflow until a flaky test passes is not an accepted fix. A test may be skipped only with a comment that names the tracking issue, and for at most **14 days**.

## How is test coverage judged?

Acme Cloud does not enforce a line coverage percentage, because the services use the standard library only and no coverage tool is installed in continuous integration. Coverage is judged in code review against the list in "What must be tested?". A reviewer rejects a pull request that changes behaviour without changing a test.

## How is a change tested before release?

1. The author runs `tools/run_tests.py` locally.
2. Continuous integration runs all three checks on the pull request.
3. After the merge, the change is deployed to staging and the end-to-end checks run.
4. The change is released to a canary of **5%** of traffic in `us-east` before the full rollout, as described in `docs/engineering/release-process.md`.

Last reviewed: 2026-11-26
