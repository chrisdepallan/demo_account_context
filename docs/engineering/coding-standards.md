# Coding Standards

## Which languages and versions do Acme Cloud services use?

Every Acme Cloud service is written in Python **3.11** or later and uses the **standard library only**. No third-party packages are imported by service code or by tests. The rule keeps every service runnable on a clean machine and keeps the supply chain small. Repository tools such as `tools/run_tests.py` follow the same rule.

## How is Python code formatted?

- Follow PEP 8 with a maximum line length of **100** characters.
- Indent with **4 spaces**. Do not use tabs.
- Use double quotes for strings.
- Order imports in two groups separated by a blank line: standard library first, then the service's own package.
- Keep functions short. A function longer than **50 lines** needs a reason in the pull request description.
- Files are UTF-8 with Unix line endings and end with a newline.

## How are things named?

- Packages – `acme_<service>`, for example `acme_billing` and `acme_audit_log`.
- Modules, functions and variables – `snake_case`.
- Classes – `PascalCase`.
- Constants – `UPPER_SNAKE_CASE`.
- Test files – `test_<module>.py`, and test methods `test_<behaviour>`.
- Documentation files – kebab-case, for example `account-lifecycle.md`.
- Alerts – `PascalCase` starting with the service or component name, for example `BillingPaymentFailureRateHigh`.

## Are type hints and docstrings required?

Type hints are required on every public function and method. A public function is any function whose name does not start with an underscore. Every public module, class and function has a docstring whose first line says what the function does in one sentence. Comments explain why the code does something, not what the code does.

## How are errors handled?

- Raise specific exception classes defined by the service. Do not raise bare `Exception`.
- Never use a bare `except:` clause. Catch the narrowest exception that the code can handle.
- Never swallow an exception silently. Log the exception or re-raise it.
- Validate input at the edge of the service, in the request handler, and return the error format from `docs/engineering/api-design-guidelines.md`.
- Every outbound call has a timeout. The default timeout for a call to another Acme Cloud service is **5 seconds**.

## How do services log?

Services log with the standard `logging` module and write one JSON object per line. Every log line carries the fields `timestamp` (ISO 8601, UTC), `level`, `service`, `region`, `request_id` and `message`.

- Use `ERROR` only for failures that need a human.
- Never log passwords, MFA codes, API keys, session tokens, payment details or the content of customer files and tasks.
- Log identifiers instead of personal data: an account ID such as `acc_7F3K9Q2M`, not an email address.
- An API key may appear in a log only as its prefix, `acme_live_` or `acme_test_`.

## How is configuration handled?

Each service reads its settings from a default configuration file in the service's config folder. Environment variables override the file. Secrets are never written to a configuration file, to code or to this repository. Secrets reach a service only through environment variables that the deployment platform fills from the secrets manager. Feature flags are named `<service>.<feature>` and are removed within **30 days** after a feature is fully released.

## How are identifiers and timestamps written?

- Identifiers are a short prefix, an underscore and uppercase letters and digits: `acc_` plus **8** characters for accounts, `ws_` plus **6** for workspaces, `prj_`, `tsk_`, `fil_` and `whk_` plus **8**, and `evt_` and `aud_` plus **10**.
- Invoices use `INV-YYYY-NNNNNN`, support tickets use `SUP-NNNNN` and incidents use `INC-YYYY-NNN`.
- Timestamps are stored and returned in UTC in ISO 8601 format, for example `2026-11-26T14:30:00Z`.
- Money is stored as an integer number of minor units (for example cents) together with a three-letter currency code. Floating point numbers are never used for money.

## What are the rules for database access?

- A service reads and writes only its own PostgreSQL database. A service never queries another service's database. Data from another service comes through that service's API or through the event bus.
- SQL statements always use bound parameters. SQL is never built by joining strings with user input.
- Every schema change is backward compatible with the previous release of the service, as described in `docs/engineering/release-process.md`.
- Every transaction is short. No transaction stays open while the service waits for a network call.

## What must every pull request contain?

- Tests for the changed behaviour, as described in `docs/engineering/testing-strategy.md`.
- An updated OpenAPI description when an endpoint, a field or an error code changes.
- Updated documentation when customer-visible behaviour or a concrete value changes, including the `Last reviewed` line of the changed document.
- No secrets, no real customer data and no personal names.

A pull request changes fewer than **400** lines where possible. Larger changes are split.

Last reviewed: 2026-11-26
