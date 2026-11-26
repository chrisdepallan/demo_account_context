#!/usr/bin/env python3
"""Generate the high-volume, repetitive content of this repository.

Writes:
  reports/            incident postmortems, weekly test runs, monthly performance
                      reports, quarterly capacity / security / business reviews,
                      monthly release notes
  data/               CSV and JSON datasets behind those reports
  services/*/CHANGELOG.md
  services/*/fixtures/sample-*.json

The output is deterministic: it uses a fixed seed and a fixed reference date
instead of the system clock, so running the script twice gives identical files.
Standard library only.

Usage:
  python tools/generate_reports.py            # write files
  python tools/generate_reports.py --check    # exit 1 if any file would change
  python tools/generate_reports.py --scale 3  # three times the history
"""
from __future__ import annotations

import argparse
import calendar
import csv
import io
import json
import random
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_DATE = date(2026, 11, 26)
LAST_FULL_MONTH = (2026, 9)  # history ends with the last complete quarter
SEED = 20261126

REGIONS = ["us-east", "eu-central", "ap-south"]
PLANS = ["free", "starter", "pro", "business", "enterprise"]
ALNUM = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# ---------------------------------------------------------------------------
# Service catalogue: the single source of names used in every generated file.
# ---------------------------------------------------------------------------
SERVICES = [
    {"name": "accounts", "title": "Accounts", "team": "Accounts Platform", "channel": "#team-accounts",
     "tier": 1, "p50": 38, "req_m": 310, "nouns": ["account", "workspace", "member invitation", "plan change"]},
    {"name": "auth", "title": "Auth", "team": "Identity", "channel": "#team-identity",
     "tier": 1, "p50": 46, "req_m": 890, "nouns": ["session", "API key", "SSO connection", "MFA enrolment"]},
    {"name": "billing", "title": "Billing", "team": "Revenue Engineering", "channel": "#team-billing",
     "tier": 1, "p50": 72, "req_m": 95, "nouns": ["invoice", "subscription", "credit", "refund"]},
    {"name": "support", "title": "Support", "team": "Customer Support", "channel": "#support-escalations",
     "tier": 3, "p50": 64, "req_m": 22, "nouns": ["ticket", "macro", "escalation", "SLA timer"]},
    {"name": "projects", "title": "Projects", "team": "Work Management", "channel": "#team-projects",
     "tier": 1, "p50": 55, "req_m": 1240, "nouns": ["task", "project", "board", "comment"]},
    {"name": "files", "title": "Files", "team": "Storage Platform", "channel": "#team-storage",
     "tier": 1, "p50": 88, "req_m": 760, "nouns": ["file", "file version", "sharing link", "upload"]},
    {"name": "notifications", "title": "Notifications", "team": "Messaging", "channel": "#team-notifications",
     "tier": 2, "p50": 41, "req_m": 540, "nouns": ["notification", "digest", "email template", "preference"]},
    {"name": "webhooks", "title": "Webhooks", "team": "Developer Platform", "channel": "#team-developer-platform",
     "tier": 2, "p50": 35, "req_m": 180, "nouns": ["webhook endpoint", "delivery", "event", "signing secret"]},
    {"name": "search", "title": "Search", "team": "Search and Discovery", "channel": "#team-search",
     "tier": 2, "p50": 96, "req_m": 420, "nouns": ["query", "index", "saved search", "filter"]},
    {"name": "audit-log", "title": "Audit Log", "team": "Trust and Compliance", "channel": "#team-trust",
     "tier": 2, "p50": 58, "req_m": 130, "nouns": ["audit entry", "export", "stream", "retention policy"]},
    {"name": "integrations", "title": "Integrations", "team": "Ecosystem", "channel": "#team-ecosystem",
     "tier": 3, "p50": 110, "req_m": 75, "nouns": ["integration", "install", "sync job", "OAuth grant"]},
    {"name": "analytics", "title": "Analytics", "team": "Data Platform", "channel": "#team-data",
     "tier": 3, "p50": 140, "req_m": 60, "nouns": ["dashboard", "report", "metric", "scheduled export"]},
]
SERVICE_BY_NAME = {s["name"]: s for s in SERVICES}

# Availability objective by service tier (internal SLO, stricter than the
# customer-facing uptime target in docs/company-overview.md).
TIER_SLO = {1: 99.95, 2: 99.9, 3: 99.5}

# ---------------------------------------------------------------------------
# Incident scenarios: (slug, title, root cause, resolution, [action items])
# ---------------------------------------------------------------------------
SCENARIOS = {
    "accounts": [
        ("trial-expiry-job-stalled", "Trial expiry job stalled and accounts stayed in trialing",
         "The nightly trial-expiry job held a database lock while a schema migration ran. The job timed out and exited without retrying, so accounts whose trial had ended were not moved out of the `trialing` state.",
         "The migration was completed, the job was re-run by hand, and every affected account was moved to the correct state.",
         ["Alert when the trial-expiry job has not completed within 26 hours", "Make the trial-expiry job resume from a checkpoint instead of starting over"]),
        ("ownership-transfer-errors", "Ownership transfers failed with a server error",
         "A release switched the role-permission lookup to a cached copy that did not include the pending-owner state. Every transfer request failed the permission check and returned a 500 response.",
         "The release was rolled back and the cache was rebuilt with the pending-owner state included.",
         ["Add an end-to-end test for ownership transfer to the release checks", "Version the role-permission cache so stale copies are rejected"]),
        ("stale-plan-limits", "Stale plan limits blocked upgrades from taking effect",
         "Plan limits were cached per account and the cache was not invalidated when a plan-change event arrived out of order. Upgraded accounts kept their old limits until the cache expired.",
         "The cache was flushed for the affected accounts and the consumer was patched to invalidate on every plan-change event.",
         ["Invalidate the plan-limit cache on every plan-change event regardless of order", "Add a dashboard comparing cached limits against the database"]),
    ],
    "auth": [
        ("login-latency-spike", "Login latency spike",
         "A node pool resize left the password-hashing worker pool at half its normal size. Login requests queued behind the remaining workers and p95 latency rose above the alert threshold.",
         "The worker pool was scaled back to its normal size and a minimum replica count was set.",
         ["Set a minimum replica count for the password-hashing workers", "Add queue depth to the login dashboard"]),
        ("sso-clock-skew", "SSO sign-ins rejected because of clock skew",
         "Time synchronisation failed on two Auth pods, so their clocks drifted by more than the allowed tolerance. Valid SAML assertions looked expired and were rejected.",
         "The two pods were replaced and time synchronisation was restored.",
         ["Alert when pod clock drift exceeds 5 seconds", "Fail the readiness probe when time synchronisation is unhealthy"]),
        ("api-keys-rejected", "Valid API keys rejected with 401",
         "A rebuild of the API-key lookup index was interrupted and left the index partly populated. Keys missing from the index were treated as unknown.",
         "The index rebuild was completed and lookups fell back to the primary table until it finished.",
         ["Fall back to the primary table whenever the lookup index is rebuilding", "Run index rebuilds against a shadow copy and swap when complete"]),
    ],
    "billing": [
        ("duplicate-renewal-invoices", "Renewal invoices issued twice for a subset of accounts",
         "The renewal batch timed out part-way through and was retried without an idempotency key. Accounts processed before the timeout were invoiced a second time.",
         "The duplicate invoices were voided and every duplicate charge was refunded in full, as required by `services/billing/docs/refunds.md`.",
         ["Require an idempotency key on every renewal write", "Add a reconciliation check for more than one renewal invoice per account per cycle"]),
        ("tax-calculation-timeouts", "Checkout failed while tax calculation timed out",
         "The tax calculation dependency slowed down and the Billing service had no timeout shorter than the gateway timeout. Checkout requests hung and then failed.",
         "A shorter timeout and a retry with backoff were deployed, and checkout recovered.",
         ["Set an explicit timeout and circuit breaker on tax calculation calls", "Queue invoices for later tax calculation when the dependency is down"]),
        ("dunning-emails-not-sent", "Failed-payment reminder emails were not sent",
         "A new field was added to the payment-failed event. The dunning scheduler rejected the unknown field and dropped the events, so reminder emails were not scheduled.",
         "The scheduler was patched to ignore unknown fields and the dropped events were replayed.",
         ["Make all event consumers tolerate unknown fields", "Alert when dunning email volume falls below half of the weekly average"]),
    ],
    "support": [
        ("p1-tickets-misrouted", "P1 tickets routed to the general queue",
         "A change to the routing rules matched on plan before priority. P1 tickets from Business and Enterprise accounts landed in the general queue instead of the urgent queue.",
         "The rule order was corrected and the misrouted tickets were moved and answered.",
         ["Add routing tests for every plan and priority combination", "Alert when a P1 ticket waits more than 15 minutes without an owner"]),
        ("live-chat-unavailable", "Live chat unavailable during business hours",
         "The chat widget configuration was published with an empty availability schedule, so the widget showed as offline for all customers.",
         "The previous configuration was restored and the schedule was re-published.",
         ["Validate the availability schedule before a chat configuration can be published", "Add a synthetic check that opens a chat every 5 minutes in business hours"]),
        ("response-timers-wrong", "First-response timers ignored business hours",
         "A time zone library update changed how the business-hours calendar was read. Timers counted nights and weekends, so tickets showed as breaching their target early.",
         "The calendar loader was fixed and the timers were recalculated for all open tickets.",
         ["Pin the time zone data version used by the timer service", "Add tests for timers that cross a weekend and a daylight-saving change"]),
    ],
    "projects": [
        ("large-boards-failed-to-load", "Boards with many tasks failed to load",
         "A release added a per-task query for assignee details. Boards with more than a few hundred tasks made thousands of queries and exceeded the request timeout.",
         "The per-task query was replaced with a single batched query and the release was redeployed.",
         ["Add a query-count budget to the board endpoint tests", "Load-test board endpoints with large boards before each release"]),
        ("automation-rules-fired-twice", "Automation rules fired twice",
         "The event bus redelivered a batch of task events after a consumer restart. The automation engine did not de-duplicate by event ID, so rules ran twice.",
         "De-duplication by event ID was deployed and duplicate actions were reverted where possible.",
         ["De-duplicate automation triggers by event ID", "Document which automation actions are safe to repeat"]),
        ("comments-out-of-order", "Task comments shown out of order",
         "Comments were ordered by the timestamp of the writing pod. Clock differences between pods put some replies before the comments they answered.",
         "Ordering was switched to a database sequence and existing comments were re-sorted.",
         ["Order comments by a database sequence, not by pod time", "Add a clock-drift alert for Projects pods"]),
    ],
    "files": [
        ("large-uploads-failed", "Large file uploads failed",
         "A configuration change lowered the multipart part size. Large uploads then needed more parts than the object store allows and were rejected at completion.",
         "The part size was restored and failed uploads could be retried.",
         ["Validate part size against the maximum file size at start-up", "Add a synthetic upload of a maximum-size file every hour"]),
        ("storage-usage-overcounted", "Storage usage overcounted after version cleanup",
         "The version-cleanup job deleted old versions but its usage update failed silently. Accounts showed more storage in use than they really had, and some hit their quota.",
         "Usage was recalculated from the object store for all accounts and the job was fixed to fail loudly.",
         ["Recalculate usage from the object store nightly and alert on differences", "Make the cleanup job fail when the usage update fails"]),
        ("sharing-links-denied", "Valid sharing links returned 403",
         "A change to link validation compared expiry times in local time instead of UTC. Links in regions ahead of UTC were treated as expired early.",
         "The comparison was corrected to use UTC and the change was redeployed.",
         ["Add link-expiry tests that run in every region's time zone", "Lint for time comparisons that do not use UTC"]),
    ],
    "notifications": [
        ("email-delivery-delays", "Notification emails delayed",
         "The email provider throttled sending after a burst of digest emails. The send queue grew faster than it drained and transactional emails waited behind digests.",
         "Digest sending was paused, transactional emails were given their own queue, and the backlog cleared.",
         ["Keep transactional and digest emails on separate queues", "Spread digest sending over a longer window"]),
        ("digest-sent-twice", "Daily digest sent twice",
         "The digest scheduler ran on two pods during a deployment because leader election had not completed. Both pods sent the same digest.",
         "Leader election was fixed to complete before the scheduler starts.",
         ["Record sent digests and refuse to send the same digest twice", "Start the scheduler only after leader election completes"]),
        ("push-notifications-dropped", "Push notifications dropped",
         "An expired push credential was not rotated in one region. The push gateway rejected every request from that region and the errors were not retried.",
         "The credential was rotated and the dropped notifications were delivered in-app instead.",
         ["Alert 30 days before any push credential expires", "Retry rejected push requests and fall back to in-app delivery"]),
    ],
    "webhooks": [
        ("delivery-backlog", "Webhook delivery backlog",
         "A small number of very slow customer endpoints held delivery workers until they timed out. Because workers were shared, deliveries to healthy endpoints queued behind them.",
         "Slow endpoints were moved to a separate worker pool and the backlog drained.",
         ["Isolate slow endpoints in their own worker pool", "Alert when the oldest queued delivery is more than 5 minutes old"]),
        ("signatures-failed-after-rotation", "Webhook signatures failed verification after secret rotation",
         "After a signing secret was rotated, deliveries were signed with only the new secret. Customers still verifying with the old secret during the overlap window rejected them.",
         "Deliveries were changed to carry signatures for both secrets during the overlap window.",
         ["Sign with both secrets for the whole overlap window", "Add a rotation test that verifies with the old and the new secret"]),
        ("endpoints-disabled-in-error", "Healthy webhook endpoints disabled in error",
         "A network fault between one region and the internet made deliveries fail for reasons unrelated to the endpoints. The failure counter still counted them and disabled healthy endpoints.",
         "The affected endpoints were re-enabled and missed events were redelivered.",
         ["Do not count failures towards disabling when the failure rate is region-wide", "Notify the account Owner before an endpoint is disabled"]),
    ],
    "search": [
        ("index-lag", "Search results lagged behind recent changes",
         "The indexing consumer fell behind after a bulk import produced a burst of change events. New and edited items took much longer than normal to appear in search.",
         "Indexing workers were scaled up and bulk-import events were moved to a lower-priority lane.",
         ["Scale indexing workers automatically on consumer lag", "Index bulk imports on a separate, lower-priority lane"]),
        ("quoted-phrase-errors", "Searches with quoted phrases returned errors",
         "A parser change mishandled a quoted phrase followed by a filter. Those queries raised an error instead of returning results.",
         "The parser change was reverted and the failing queries were added to the test suite.",
         ["Add property-based tests for the query parser", "Return partial results instead of an error when one clause fails to parse"]),
        ("search-node-loss", "Search degraded after the loss of a cluster node",
         "A search cluster node failed and its replicas were on a node in the same zone that was being drained. Some shards had no available copy until recovery finished.",
         "The shards were recovered from the remaining copies and replica placement was corrected.",
         ["Enforce replica placement across zones", "Block node drains when any shard has a single copy"]),
    ],
    "audit-log": [
        ("siem-stream-gap", "Gap in SIEM streaming",
         "The streaming worker lost its position after a restart and resumed from the newest entry. Entries written while it was down were not streamed.",
         "The worker position was restored from the last acknowledged entry and the missing entries were replayed.",
         ["Persist the stream position after every acknowledged batch", "Alert on any gap in streamed entry sequence numbers"]),
        ("export-timeouts", "Audit log exports timed out for large accounts",
         "Exports were built in a single request. For accounts with many entries the request exceeded the gateway timeout and returned nothing.",
         "Exports were moved to a background job that produces a download when ready.",
         ["Run all exports as background jobs", "Show export progress in the UI"]),
        ("chain-verification-false-alarm", "Hash-chain verification raised a false alarm",
         "The nightly verification job read from a replica that was behind the primary. It saw an incomplete chain and reported tampering that had not happened.",
         "Verification was pointed at the primary and re-run, and the chain was confirmed intact.",
         ["Verify the chain only against a fully caught-up source", "Separate replica-lag alerts from integrity alerts"]),
    ],
    "integrations": [
        ("slack-updates-stopped", "Slack integration stopped posting updates",
         "Token refresh for the Slack integration failed after a scope change, and the failure was logged but not alerted. Installs with expired tokens stopped posting.",
         "Token refresh was fixed and affected installs were refreshed without customer action.",
         ["Alert when token refresh failures exceed 1% of installs", "Show a reconnect banner to Admins when an install cannot refresh"]),
        ("github-sync-duplicates", "GitHub sync created duplicate tasks",
         "The sync cursor was not saved after a partial page failure. The next run re-read the same page and created tasks that already existed.",
         "The cursor is now saved after each item and duplicates were merged.",
         ["Save the sync cursor after each item", "Use the external ID as a uniqueness key when creating tasks"]),
        ("oauth-installs-failed", "New integration installs failed at the consent step",
         "A redirect address was changed in configuration for one region but not registered with the provider. Installs started in that region failed at consent.",
         "The address was registered and the configuration was made consistent across regions.",
         ["Check redirect addresses against the provider registration in CI", "Add a synthetic install test in every region"]),
    ],
    "analytics": [
        ("dashboards-stale", "Dashboards showed stale data",
         "The nightly roll-up job failed on a malformed row and stopped. Dashboards kept showing the previous day's figures with no warning.",
         "The malformed row was quarantined, the roll-up was re-run, and dashboards now show the time of the last successful roll-up.",
         ["Quarantine bad rows instead of stopping the roll-up", "Show data freshness on every dashboard"]),
        ("scheduled-exports-missed", "Scheduled exports were not sent",
         "The export scheduler calculated the next run in local time. After a daylight-saving change, some weekly exports were skipped.",
         "Next-run calculation was moved to UTC and the missed exports were sent.",
         ["Calculate all schedules in UTC", "Alert when an export is more than 1 hour late"]),
        ("completion-rate-wrong", "Task completion rate miscalculated for archived projects",
         "Archived projects were excluded from completed tasks but not from total tasks. Accounts with archived projects saw a completion rate lower than the real one.",
         "The metric was corrected to exclude archived projects from both counts and history was recalculated.",
         ["Add metric tests that include archived projects", "Review every metric definition for consistent filters"]),
    ],
}

DETECTION = [
    "An automated alert paged the on-call engineer for {team}.",
    "Customer Support saw a rise in tickets and escalated in `#support-escalations`.",
    "An engineer on {team} noticed the problem on the service dashboard.",
    "A synthetic check failed in {region} and paged the on-call engineer.",
]
GENERIC_ACTIONS = [
    "Add this failure mode to the {title} service runbook",
    "Add a dashboard panel that shows this condition directly",
    "Review alert thresholds for the {title} service",
    "Run a game day that reproduces this failure",
]
LESSONS = [
    "The alert fired on a symptom, not the cause, which slowed diagnosis.",
    "Rollback was fast because the release was small. Small releases should stay the norm.",
    "The on-call engineer did not have the access needed for the first mitigation step.",
    "Customers were told through the status page later than the internal target of 15 minutes.",
    "The dependency was assumed to be reliable and had no timeout or fallback.",
    "A test covering this case existed but was skipped as flaky.",
    "The same class of problem had happened before in another service and the fix was not shared.",
    "Dashboards showed averages, which hid the affected minority of accounts.",
]
FAIL_REASONS = [
    "assertion failed after a change to the expected error message",
    "timed out waiting for a fixture to load",
    "depended on the current date and failed at a month boundary",
    "failed because a shared test account was at its plan limit",
    "failed on an ordering assumption in dictionary output",
    "compared floating-point totals without rounding",
]
CHANGE_TEMPLATES = [
    ("Added", "Added bulk {noun} export to the API."),
    ("Added", "Added an `updated_since` filter when listing {nouns}."),
    ("Added", "Added per-region metrics for {noun} operations."),
    ("Added", "Added an audit entry whenever a {noun} is deleted."),
    ("Added", "Added pagination cursors to {noun} listings."),
    ("Added", "Added a dry-run mode for {noun} imports."),
    ("Changed", "Reduced p95 latency of {noun} lookups."),
    ("Changed", "{Noun} validation errors now return a machine-readable `code` field."),
    ("Changed", "Moved {noun} clean-up to an off-peak window in each region."),
    ("Changed", "Structured logs for {noun} operations now include the account ID and region."),
    ("Changed", "{Noun} writes are now retried once on a transient database error."),
    ("Fixed", "Fixed a race when two requests updated the same {noun}."),
    ("Fixed", "Fixed {noun} listings returning duplicates across pages."),
    ("Fixed", "Fixed a server error when listing {nouns} for an account that has none."),
    ("Fixed", "Fixed time zone handling so {noun} timestamps are always UTC."),
    ("Fixed", "Fixed retries creating a second {noun} after a gateway timeout."),
    ("Fixed", "Fixed incorrect counts after a {noun} was restored."),
]
SECURITY_FINDINGS = [
    ("Medium", "Service account with write access that was not used in 90 days"),
    ("Low", "Dependency two minor versions behind the latest patched release"),
    ("Medium", "Production database role granted to an engineer who changed teams"),
    ("Low", "Log line included a full request path with an account ID in debug mode"),
    ("High", "Internal endpoint reachable without the gateway's authentication check"),
    ("Low", "Configuration file referenced a secret by an outdated variable name"),
    ("Medium", "Break-glass access used without a linked incident"),
    ("Low", "Rate limit missing on a low-traffic internal endpoint"),
]
NEXT_PRIORITIES = [
    "Reduce p95 latency of the slowest three services by 15%.",
    "Close every open postmortem action item older than 60 days.",
    "Bring test coverage of every service to at least 85%.",
    "Complete the quarterly access review within the first two weeks of the quarter.",
    "Cut P1 first-response misses to zero for Enterprise accounts.",
    "Move remaining single-region batch jobs to run in each region.",
    "Automate regional failover drills and run one per region.",
]
TICKET_SUBJECTS = [
    "Cannot log in after enabling SSO", "Invoice shows the wrong seat count", "How do I export my data?",
    "Upload fails for a large file", "Webhook deliveries are failing", "Need to change the account Owner",
    "Search does not find a recent task", "Charged after cancelling", "How do I add a guest?",
    "Dashboard numbers look out of date",
]
TASK_TITLES = [
    "Draft launch checklist", "Review onboarding copy", "Fix broken link in help center", "Plan sprint demo",
    "Update pricing page screenshots", "Collect feedback from beta group", "Archive completed milestones",
    "Prepare quarterly roadmap",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def rng(section: str) -> random.Random:
    """Independent, reproducible random stream for one section of output."""
    return random.Random(f"{SEED}:{section}")


def make_id(r: random.Random, prefix: str, length: int) -> str:
    return prefix + "".join(r.choice(ALNUM) for _ in range(length))


def plural(noun: str) -> str:
    if noun.endswith("y") and noun[-2] not in "aeiou":
        return noun[:-1] + "ies"
    if noun.endswith(("ch", "s", "x")):
        return noun + "es"
    return noun + "s"


def table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("------" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def month_list(scale: int) -> list[tuple[int, int]]:
    y, m = LAST_FULL_MONTH
    months = []
    for _ in range(12 * scale):
        months.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return list(reversed(months))


def ym(month: tuple[int, int]) -> str:
    return f"{month[0]}-{month[1]:02d}"


def quarter_of(month: tuple[int, int]) -> str:
    return f"{month[0]}-Q{(month[1] - 1) // 3 + 1}"


def month_end(month: tuple[int, int]) -> date:
    return date(month[0], month[1], calendar.monthrange(*month)[1])


def csv_text(headers: list[str], rows: list[list[object]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue()


class Output:
    """Collects files, then writes them or compares them with what is on disk."""

    def __init__(self, check: bool) -> None:
        self.check = check
        self.written = 0
        self.changed: list[str] = []

    def write(self, rel: str, text: str, keep_existing: bool = False) -> None:
        path = ROOT / rel
        if not text.endswith("\n"):
            text += "\n"
        if keep_existing and path.exists():
            return
        current = path.read_text(encoding="utf-8") if path.exists() else None
        self.written += 1
        if current == text:
            return
        self.changed.append(rel)
        if not self.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)


# ---------------------------------------------------------------------------
# Facts read from the hand-written part of the repo
# ---------------------------------------------------------------------------
def discover_endpoints(service: str) -> list[str]:
    """Operations declared in services/<service>/openapi.yaml, e.g. 'GET /v2/x'."""
    spec = ROOT / "services" / service / "openapi.yaml"
    found: list[str] = []
    if spec.exists():
        current = None
        for line in spec.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^  (/[^\s:]+):\s*$", line)
            if m:
                current = m.group(1)
                continue
            m = re.match(r"^    (get|post|put|patch|delete):\s*$", line)
            if m and current:
                found.append(f"{m.group(1).upper()} {current}")
    return found or [f"GET /v2/{service}/health"]


def discover_tests(service: str) -> list[str]:
    """Test IDs found in services/<service>/tests/, as path::Class::method."""
    tests: list[str] = []
    folder = ROOT / "services" / service / "tests"
    for path in sorted(folder.glob("test_*.py")):
        cls = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^class (\w+)", line)
            if m:
                cls = m.group(1)
            m = re.match(r"^\s+def (test_\w+)", line)
            if m:
                tests.append(f"services/{service}/tests/{path.name}::{cls}::{m.group(1)}")
    return tests or [f"services/{service}/tests/test_smoke.py::SmokeTest::test_imports"]


# ---------------------------------------------------------------------------
# Model: build every number once, so all reports agree with each other
# ---------------------------------------------------------------------------
def build_incidents(months: list[tuple[int, int]], scale: int) -> list[dict]:
    r = rng("incidents")
    first = date(months[0][0], months[0][1], 1)
    span = (month_end(months[-1]) - first).days
    raw = []
    for _ in range(24 * scale):
        svc = r.choice(SERVICES)
        slug, title, cause, fix, actions = r.choice(SCENARIOS[svc["name"]])
        sev = r.choices(["SEV1", "SEV2", "SEV3", "SEV4"], weights=[5, 25, 50, 20])[0]
        lo, hi = {"SEV1": (60, 180), "SEV2": (30, 120), "SEV3": (15, 90), "SEV4": (10, 60)}[sev]
        start = datetime.combine(first + timedelta(days=r.randrange(span + 1)), datetime.min.time())
        start += timedelta(minutes=r.randrange(24 * 60))
        regions = REGIONS if sev == "SEV1" else r.sample(REGIONS, r.choice([1, 1, 2]))
        raw.append({
            "service": svc["name"], "slug": slug, "title": title, "cause": cause, "fix": fix,
            "actions": actions, "sev": sev, "start": start, "duration": r.randrange(lo, hi + 1),
            "detect_after": r.randrange(2, 25), "regions": sorted(regions, key=REGIONS.index),
            "tickets": r.randrange(0, 12) * {"SEV1": 9, "SEV2": 4, "SEV3": 2, "SEV4": 1}[sev],
            "accounts": r.randrange(20, 400) * {"SEV1": 40, "SEV2": 8, "SEV3": 2, "SEV4": 1}[sev],
            "detection": r.choice(DETECTION), "lessons": r.sample(LESSONS, 2),
            "generic_action": r.choice(GENERIC_ACTIONS), "due_days": [r.randrange(14, 46) for _ in range(3)],
        })
    raw.sort(key=lambda i: i["start"])
    counters: dict[int, int] = {}
    for inc in raw:
        year = inc["start"].year
        counters[year] = counters.get(year, 0) + 1
        inc["id"] = f"INC-{year}-{counters[year]:03d}"
        inc["path"] = f"reports/incidents/{inc['id']}-{inc['service']}-{inc['slug']}.md"
        inc["month"] = (inc["start"].year, inc["start"].month)
    return raw


def build_service_months(months: list[tuple[int, int]], incidents: list[dict]) -> dict:
    """Uptime and latency per (service, month)."""
    weight = {"SEV1": 1.0, "SEV2": 0.5, "SEV3": 0.1, "SEV4": 0.0}
    stats = {}
    for svc in SERVICES:
        r = rng(f"service-months:{svc['name']}")
        for month in months:
            minutes = calendar.monthrange(*month)[1] * 1440
            down = r.uniform(0, 6)
            hit = [i for i in incidents if i["service"] == svc["name"] and i["month"] == month]
            down += sum(i["duration"] * weight[i["sev"]] for i in hit)
            bump = 1 + 0.12 * len(hit)
            p50 = svc["p50"] * r.uniform(0.93, 1.07) * bump
            p95 = p50 * r.uniform(2.3, 2.9)
            growth = 1 + 0.02 * months.index(month)
            stats[(svc["name"], month)] = {
                "uptime": round(100 * (1 - down / minutes), 3),
                "p50": round(p50), "p95": round(p95), "p99": round(p95 * r.uniform(1.6, 2.1)),
                "requests_m": round(svc["req_m"] * growth * r.uniform(0.95, 1.05), 1),
                "error_rate": round(r.uniform(0.02, 0.18) * bump, 3),
            }
    return stats


def build_changes(months: list[tuple[int, int]]) -> dict:
    """Changelog entries per (service, month), with a version and release date."""
    changes = {}
    for svc in SERVICES:
        r = rng(f"changes:{svc['name']}")
        pool = [(k, t, n) for k, t in CHANGE_TEMPLATES for n in svc["nouns"]]
        r.shuffle(pool)
        pos = 0
        for idx, month in enumerate(months):
            entries = []
            for _ in range(r.randrange(2, 5)):
                kind, template, noun = pool[pos % len(pool)]
                pos += 1
                text = template.format(noun=noun, nouns=plural(noun), Noun=noun[0].upper() + noun[1:])
                entries.append((kind, text))
            entries.sort(key=lambda e: ["Added", "Changed", "Fixed"].index(e[0]))
            changes[(svc["name"], month)] = {
                "version": f"2.{idx + 1}.{r.randrange(0, 4)}",
                "date": date(month[0], month[1], r.randrange(3, 27)),
                "entries": entries,
            }
    return changes


def build_weeks(months: list[tuple[int, int]]) -> list[date]:
    """Mondays of every complete week from the first month to the reference date."""
    day = date(months[0][0], months[0][1], 1)
    day += timedelta(days=(7 - day.weekday()) % 7)
    weeks = []
    while day + timedelta(days=6) < REFERENCE_DATE:
        weeks.append(day)
        day += timedelta(days=7)
    return weeks


def build_tickets(weeks: list[date]) -> list[dict]:
    r = rng("tickets")
    rows = []
    for i, monday in enumerate(weeks):
        base = 620 * (1 + 0.006 * i)
        p = {"P1": round(base * r.uniform(0.008, 0.02)), "P2": round(base * r.uniform(0.07, 0.11)),
             "P3": round(base * r.uniform(0.42, 0.5)), "P4": round(base * r.uniform(0.36, 0.44))}
        rows.append({"week": monday, **p, "total": sum(p.values()),
                     "first_response_met_pct": round(r.uniform(93.5, 99.4), 1),
                     "satisfaction_pct": round(r.uniform(90.0, 96.5), 1)})
    return rows


def build_plan_mix(months: list[tuple[int, int]]) -> list[dict]:
    r = rng("plan-mix")
    total = 41000.0
    rows = []
    for month in months:
        total *= r.uniform(1.012, 1.028)
        shares = [58 + r.uniform(-1, 1), 19 + r.uniform(-0.6, 0.6), 15 + r.uniform(-0.5, 0.5),
                  6.5 + r.uniform(-0.3, 0.3), 1.5 + r.uniform(-0.1, 0.1)]
        counts = [round(total * s / sum(shares)) for s in shares]
        rows.append({"month": month, **dict(zip(PLANS, counts)), "total": sum(counts)})
    return rows


def build_storage(months: list[tuple[int, int]]) -> list[dict]:
    r = rng("storage")
    used = {"us-east": 410.0, "eu-central": 190.0, "ap-south": 85.0}
    provisioned = {"us-east": 640.0, "eu-central": 320.0, "ap-south": 160.0}
    rows = []
    for month in months:
        for region in REGIONS:
            used[region] *= r.uniform(1.018, 1.04)
            if used[region] / provisioned[region] > 0.82:
                provisioned[region] *= 1.25
            rows.append({"month": month, "region": region, "used_tb": round(used[region], 1),
                         "provisioned_tb": round(provisioned[region], 1),
                         "used_pct": round(100 * used[region] / provisioned[region], 1)})
    return rows


def build_test_runs(weeks: list[date], scale: int) -> list[dict]:
    all_tests = {s["name"]: discover_tests(s["name"]) for s in SERVICES}
    weeks = weeks[-20 * scale:]
    runs = []
    for i, monday in enumerate(weeks):
        r = rng(f"test-run:{monday.isoformat()}")
        grown = 0.7 + 0.3 * (i + 1) / len(weeks)
        per_service, failures, flaky = [], [], []
        for svc in SERVICES:
            tests = all_tests[svc["name"]]
            active = tests[: max(1, round(len(tests) * grown))]
            failed = r.sample(active, 1) if r.random() < 0.12 else []
            skipped = 1 if r.random() < 0.15 and len(active) > 3 else 0
            for t in failed:
                failures.append((t, r.choice(FAIL_REASONS)))
            if r.random() < 0.08:
                flaky.append(r.choice(active))
            per_service.append({
                "service": svc["name"], "total": len(active), "failed": len(failed), "skipped": skipped,
                "passed": len(active) - len(failed) - skipped,
                "duration_s": round(len(active) * r.uniform(0.02, 0.06), 2),
                "coverage": round(min(97.0, 78 + 14 * grown + r.uniform(-3, 3)), 1),
            })
        iso = monday.isocalendar()
        runs.append({"week": monday, "label": f"{iso[0]}-W{iso[1]:02d}", "services": per_service,
                     "failures": failures, "flaky": flaky,
                     "commit": "".join(r.choice("0123456789abcdef") for _ in range(7))})
    return runs


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def render_incident(inc: dict) -> str:
    svc = SERVICE_BY_NAME[inc["service"]]
    start = inc["start"]
    detected = start + timedelta(minutes=inc["detect_after"])
    mitigated = start + timedelta(minutes=max(inc["detect_after"] + 3, round(inc["duration"] * 0.8)))
    resolved = start + timedelta(minutes=inc["duration"])
    fmt = "%Y-%m-%d %H:%M"
    regions = ", ".join(f"`{r}`" for r in inc["regions"])
    detection = inc["detection"].format(team=svc["team"], region=inc["regions"][0])
    actions = inc["actions"] + [inc["generic_action"].format(title=svc["title"])]
    rows = []
    for text, days in zip(actions, inc["due_days"]):
        due = start.date() + timedelta(days=days)
        status = "Done" if due < REFERENCE_DATE - timedelta(days=20) else ("In progress" if due < REFERENCE_DATE else "Open")
        rows.append([text, svc["team"], due.isoformat(), status])
    return f"""# {inc['id']}: {inc['title']}

## Summary

Incident **{inc['id']}** was a **{inc['sev']}** incident in the {svc['title']} service (`services/{svc['name']}/README.md`). It started on **{start.strftime(fmt)} UTC** and lasted **{inc['duration']} minutes**. Affected regions: {regions}. Owning team: {svc['team']} (`{svc['channel']}`).

## Impact

- About **{inc['accounts']:,} accounts** were affected during {inc['id']}.
- Customer Support received **{inc['tickets']} tickets** linked to {inc['id']}.
- Severity: **{inc['sev']}**. Duration: **{inc['duration']} minutes**. Regions: {regions}.

## Timeline (UTC)

{table(['Time', 'Event'], [
    [start.strftime(fmt), 'Problem began'],
    [detected.strftime(fmt), f'Detected, {inc["detect_after"]} minutes after the start'],
    [(detected + timedelta(minutes=2)).strftime(fmt), f'Incident {inc["id"]} declared in `{svc["channel"]}`'],
    [mitigated.strftime(fmt), 'Mitigation in place, customer impact ended'],
    [resolved.strftime(fmt), 'Incident resolved and monitoring confirmed normal'],
])}

## Root cause

{inc['cause']}

## Detection

{detection} Time to detect for {inc['id']} was **{inc['detect_after']} minutes**.

## Resolution

{inc['fix']}

## Action items

{table(['Action', 'Owner', 'Due', 'Status'], rows)}

## Lessons learned

- {inc['lessons'][0]}
- {inc['lessons'][1]}

Report date: {(start.date() + timedelta(days=5)).isoformat()}
"""


def render_test_run(run: dict) -> str:
    total = sum(s["total"] for s in run["services"])
    failed = sum(s["failed"] for s in run["services"])
    skipped = sum(s["skipped"] for s in run["services"])
    duration = sum(s["duration_s"] for s in run["services"])
    result = "passed" if failed == 0 else "failed"
    rows = [[f"`{s['service']}`", s["total"], s["passed"], s["failed"], s["skipped"], f"{s['duration_s']:.2f}",
             f"{s['coverage']}%"] for s in run["services"]]
    fails = "\n".join(f"- `{t}` – {why}." for t, why in run["failures"]) or f"No tests failed in the {run['label']} run."
    flaky = "\n".join(f"- `{t}` – passed on retry; tracked as flaky." for t in run["flaky"]) or f"No flaky tests were seen in the {run['label']} run."
    lowest = min(run["services"], key=lambda s: s["coverage"])
    return f"""# Test Run Report {run['label']}

## Summary

The weekly full test run for **{run['label']}** (week starting {run['week'].isoformat()}) **{result}**. It ran **{total} tests** across **{len(run['services'])} services**: **{total - failed - skipped} passed**, **{failed} failed**, **{skipped} skipped**. Total duration was **{duration:.2f} seconds**. Commit: `{run['commit']}`. The run uses `tools/run_tests.py`.

## Results by service

{table(['Service', 'Tests', 'Passed', 'Failed', 'Skipped', 'Duration (s)', 'Line coverage'], rows)}

## Failures

{fails}

## Flaky tests

{flaky}

## Coverage

The lowest line coverage in the {run['label']} run was **{lowest['coverage']}%** in the `{lowest['service']}` service. The target for every service is **85%**.

Report date: {(run['week'] + timedelta(days=6)).isoformat()}
"""


def render_performance(month, stats, incidents, endpoints) -> str:
    label = ym(month)
    r = rng(f"performance:{label}")
    rows, slo_rows, misses = [], [], []
    for svc in SERVICES:
        s = stats[(svc["name"], month)]
        rows.append([f"`{svc['name']}`", s["p50"], s["p95"], s["p99"], s["requests_m"], f"{s['error_rate']}%"])
        target = TIER_SLO[svc["tier"]]
        met = s["uptime"] >= target
        if not met:
            misses.append(svc["name"])
        slo_rows.append([f"`{svc['name']}`", f"Tier {svc['tier']}", f"{target}%", f"{s['uptime']}%", "Met" if met else "Missed"])
    slow = []
    for svc in sorted(SERVICES, key=lambda v: -stats[(v["name"], month)]["p95"])[:5]:
        ep = r.choice(endpoints[svc["name"]])
        slow.append([f"`{ep}`", f"`{svc['name']}`", round(stats[(svc["name"], month)]["p95"] * r.uniform(1.2, 1.9))])
    region_rows = [[f"`{reg}`", f"{share}%", round(62 * factor), f"{round(r.uniform(0.04, 0.14), 3)}%"]
                   for reg, share, factor in zip(REGIONS, (57, 29, 14), (1.0, 1.06, 1.18))]
    month_inc = [i for i in incidents if i["month"] == month]
    notable = "\n".join(f"- **{i['id']}** ({i['sev']}, `{i['service']}`): {i['title']}. See `{i['path']}`." for i in month_inc) \
        or f"No incidents affected performance in {label}."
    slowest = max(SERVICES, key=lambda v: stats[(v["name"], month)]["p95"])
    total_req = sum(stats[(v["name"], month)]["requests_m"] for v in SERVICES)
    miss_text = ("Services that missed their availability objective in " + label + ": " +
                 ", ".join(f"`{m}`" for m in misses) + ".") if misses else f"Every service met its availability objective in {label}."
    return f"""# Performance Report {label}

## Summary

In **{label}** the platform served **{total_req:,.0f} million requests** across 12 services. The slowest service by p95 latency was `{slowest['name']}` at **{stats[(slowest['name'], month)]['p95']} ms**. {miss_text}

## Latency by service

Latency is measured at the API gateway, in milliseconds, over the whole of {label}.

{table(['Service', 'p50 (ms)', 'p95 (ms)', 'p99 (ms)', 'Requests (millions)', 'Error rate'], rows)}

## Slowest endpoints

The five slowest endpoints in {label} by p95 latency:

{table(['Endpoint', 'Service', 'p95 (ms)'], slow)}

## Regional breakdown

{table(['Region', 'Share of requests', 'Median latency (ms)', 'Error rate'], region_rows)}

## Availability against objectives

Internal availability objectives are **99.95%** for Tier 1 services, **99.9%** for Tier 2 and **99.5%** for Tier 3. Customer-facing uptime targets are in `docs/company-overview.md`.

{table(['Service', 'Tier', 'Objective', 'Measured in ' + label, 'Result'], slo_rows)}

## Incidents that affected performance

{notable}

Report date: {(month_end(month) + timedelta(days=4)).isoformat()}
"""


def render_release_notes(month, changes) -> str:
    label = ym(month)
    buckets = {"Added": [], "Changed": [], "Fixed": []}
    versions = []
    for svc in SERVICES:
        c = changes[(svc["name"], month)]
        versions.append([f"`{svc['name']}`", c["version"], c["date"].isoformat(), f"`services/{svc['name']}/CHANGELOG.md`"])
        for kind, text in c["entries"]:
            buckets[kind].append(f"- **{svc['title']}** – {text}")
    count = sum(len(v) for v in buckets.values())
    return f"""# Release Notes {label}

## Summary

In **{label}**, **12 services** shipped **{count} changes**: **{len(buckets['Added'])} additions**, **{len(buckets['Changed'])} improvements** and **{len(buckets['Fixed'])} fixes**. Each service's full history is in its `CHANGELOG.md`.

## New in {label}

{chr(10).join(buckets['Added'])}

## Improved in {label}

{chr(10).join(buckets['Changed'])}

## Fixed in {label}

{chr(10).join(buckets['Fixed'])}

## Versions released in {label}

{table(['Service', 'Version', 'Released', 'Changelog'], versions)}

Report date: {month_end(month).isoformat()}
"""


def render_changelog(svc, months, changes) -> str:
    parts = [f"# Changelog – {svc['title']} Service"]
    for month in reversed(months):
        c = changes[(svc["name"], month)]
        lines = "\n".join(f"- {kind}: {text[len(kind) + 1:] if text.startswith(kind + ' ') else text}" for kind, text in c["entries"])
        parts.append(f"## {svc['title']} {c['version']} – {c['date'].isoformat()}\n\n{lines}")
    parts.append(f"Generated by `tools/generate_reports.py`. Monthly summaries are in `reports/release-notes/`.")
    return "\n\n".join(parts) + "\n"


def render_business_review(quarter, q_months, stats, incidents, tickets, plan_mix) -> str:
    r = rng(f"business-review:{quarter}")
    up_rows = []
    for svc in SERVICES:
        avg = sum(stats[(svc["name"], m)]["uptime"] for m in q_months) / len(q_months)
        up_rows.append([f"`{svc['name']}`", svc["team"], f"{avg:.3f}%"])
    platform = sum(float(row[2][:-1]) for row in up_rows) / len(up_rows)
    q_inc = [i for i in incidents if i["month"] in q_months]
    by_sev = {s: sum(1 for i in q_inc if i["sev"] == s) for s in ("SEV1", "SEV2", "SEV3", "SEV4")}
    inc_lines = "\n".join(f"- **{i['id']}** ({i['sev']}, `{i['service']}`, {i['duration']} minutes): {i['title']}. See `{i['path']}`." for i in q_inc) \
        or f"There were no incidents in {quarter}."
    q_tickets = [t for t in tickets if (t["week"].year, t["week"].month) in q_months]
    t_total = sum(t["total"] for t in q_tickets)
    met = sum(t["first_response_met_pct"] for t in q_tickets) / len(q_tickets)
    sat = sum(t["satisfaction_pct"] for t in q_tickets) / len(q_tickets)
    mix = next(p for p in plan_mix if p["month"] == q_months[-1])
    mix_rows = [[p.capitalize(), f"{mix[p]:,}", f"{100 * mix[p] / mix['total']:.1f}%"] for p in PLANS]
    priorities = "\n".join(f"{n}. {text}" for n, text in enumerate(r.sample(NEXT_PRIORITIES, 4), 1))
    return f"""# Quarterly Business Review {quarter}

## Highlights

- Average availability across all 12 services in **{quarter}** was **{platform:.3f}%**.
- There were **{len(q_inc)} incidents** in {quarter}: **{by_sev['SEV1']} SEV1**, **{by_sev['SEV2']} SEV2**, **{by_sev['SEV3']} SEV3** and **{by_sev['SEV4']} SEV4**.
- Customer Support handled **{t_total:,} tickets** in {quarter} and met the first-response target on **{met:.1f}%** of them.
- Acme Cloud ended {quarter} with **{mix['total']:,} accounts**.

## Availability by service in {quarter}

{table(['Service', 'Owning team', 'Average availability'], up_rows)}

## Incidents in {quarter}

{inc_lines}

## Support in {quarter}

Customer Support handled **{t_total:,} tickets** in {quarter}: **{sum(t['P1'] for t in q_tickets):,} P1**, **{sum(t['P2'] for t in q_tickets):,} P2**, **{sum(t['P3'] for t in q_tickets):,} P3** and **{sum(t['P4'] for t in q_tickets):,} P4**. The first-response target was met on **{met:.1f}%** of tickets and customer satisfaction averaged **{sat:.1f}%**. Response-time targets are defined in `services/support/docs/sla-and-escalation.md`. Weekly figures are in `data/ticket-volume-by-week.csv`.

## Plan mix at the end of {quarter}

{table(['Plan', 'Accounts', 'Share'], mix_rows)}

## Priorities for the next quarter

{priorities}

Report date: {(month_end(q_months[-1]) + timedelta(days=12)).isoformat()}
"""


def render_capacity(quarter, q_months, stats, storage) -> str:
    r = rng(f"capacity:{quarter}")
    last = q_months[-1]
    st_rows, recs = [], []
    for row in (s for s in storage if s["month"] == last):
        st_rows.append([f"`{row['region']}`", row["used_tb"], row["provisioned_tb"], f"{row['used_pct']}%"])
        if row["used_pct"] > 70:
            recs.append(f"Expand object storage in `{row['region']}`, which is at **{row['used_pct']}%** of provisioned capacity.")
    db_rows = []
    for svc in SERVICES:
        conn, disk = round(r.uniform(28, 78)), round(r.uniform(31, 83))
        db_rows.append([f"`{svc['name']}`", f"{conn}%", f"{disk}%"])
        if disk > 75:
            recs.append(f"Increase database disk for the `{svc['name']}` service, which is at **{disk}%**.")
        if conn > 70:
            recs.append(f"Raise the connection pool limit or add a read replica for the `{svc['name']}` service, which peaks at **{conn}%** of connections.")
    req_rows = []
    for svc in SERVICES:
        a, b = stats[(svc["name"], q_months[0])]["requests_m"], stats[(svc["name"], last)]["requests_m"]
        req_rows.append([f"`{svc['name']}`", a, b, f"{100 * (b - a) / a:+.1f}%"])
    rec_text = "\n".join(f"{n}. {t}" for n, t in enumerate(recs, 1)) or f"No capacity changes are needed after {quarter}."
    total_used = sum(float(x[1]) for x in st_rows)
    return f"""# Capacity Report {quarter}

## Summary

At the end of **{quarter}**, object storage in use across the three regions was **{total_used:,.1f} TB**. This capacity report for {quarter} lists storage, database and request growth and gives **{len(recs)} recommendations**.

## Object storage by region at the end of {quarter}

{table(['Region', 'Used (TB)', 'Provisioned (TB)', 'Used'], st_rows)}

Capacity is expanded when a region passes **70%** of provisioned storage. Monthly figures are in `data/storage-usage-by-region.csv`.

## Database headroom by service in {quarter}

Peak connection use and disk use for each service's database in {quarter}:

{table(['Service', 'Peak connections used', 'Disk used'], db_rows)}

## Request growth during {quarter}

{table(['Service', f'Requests in {ym(q_months[0])} (millions)', f'Requests in {ym(last)} (millions)', 'Change'], req_rows)}

## Recommendations after {quarter}

{rec_text}

Report date: {(month_end(last) + timedelta(days=9)).isoformat()}
"""


def render_access_review(quarter, q_months) -> str:
    r = rng(f"access-review:{quarter}")
    end = month_end(q_months[-1])
    rows = []
    for n in range(1, r.randrange(4, 8) + 1):
        sev, text = r.choice(SECURITY_FINDINGS)
        svc = r.choice(SERVICES)
        days = {"High": 7, "Medium": 30, "Low": 90}[sev]
        due = end + timedelta(days=14 + days)
        rows.append([f"FND-{quarter}-{n:02d}", sev, f"`{svc['name']}`", text, due.isoformat(),
                     "Closed" if due < REFERENCE_DATE else "Open"])
    reviewed, removed = r.randrange(380, 520), r.randrange(9, 41)
    high = sum(1 for row in rows if row[1] == "High")
    return f"""# Security and Access Review {quarter}

## Scope

The **{quarter}** security and access review covered production access for all 12 services, service accounts, break-glass use, dependency scanning and secret scanning. The review is run by Trust and Compliance (`#team-trust`).

## Findings in {quarter}

The {quarter} review raised **{len(rows)} findings**, of which **{high}** were High severity.

{table(['Finding', 'Severity', 'Service', 'Description', 'Due', 'Status'], rows)}

## Access review results for {quarter}

- **{reviewed} access grants** were reviewed by the owning team's manager.
- **{removed} grants** were removed because they were no longer needed.
- Break-glass access was used **{r.randrange(0, 6)} times** in {quarter}.

## Dependency and secret scanning in {quarter}

- Secret scanning found **0 committed secrets** in {quarter}.
- Dependency scanning reported **{r.randrange(2, 15)} outdated packages** in build and tooling images. Service code uses the Python standard library only.

## Remediation deadlines

Findings must be fixed within **7 days** for High severity, **30 days** for Medium and **90 days** for Low, counted from the report date.

Report date: {(end + timedelta(days=14)).isoformat()}
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def build_fixtures() -> dict[str, tuple[str, list[dict]]]:
    r = rng("fixtures")
    accounts = [make_id(r, "acc_", 8) for _ in range(8)]
    workspaces = [make_id(r, "ws_", 6) for _ in range(8)]
    projects = [make_id(r, "prj_", 8) for _ in range(4)]
    endpoints = [make_id(r, "whk_", 8) for _ in range(3)]

    def day(lo: int = 1, hi: int = 300) -> str:
        return (REFERENCE_DATE - timedelta(days=r.randrange(lo, hi))).isoformat()

    def stamp() -> str:
        return f"{day(1, 60)}T{r.randrange(24):02d}:{r.randrange(60):02d}:00Z"

    fx: dict[str, tuple[str, list[dict]]] = {}
    fx["accounts"] = ("sample-accounts.json", [
        {"account_id": a, "name": f"Example Account {i + 1:02d}", "plan": r.choice(PLANS),
         "state": r.choice(["trialing", "active", "active", "active", "past_due", "read_only", "closed"]),
         "home_region": r.choice(REGIONS), "seats": r.randrange(1, 120), "created_at": day(30, 900)}
        for i, a in enumerate(accounts)])
    fx["auth"] = ("sample-api-keys.json", [
        {"key_id": make_id(r, "key_", 6), "account_id": r.choice(accounts),
         "prefix": r.choice(["acme_live_", "acme_test_"]),
         "scopes": sorted(r.sample(["projects:read", "projects:write", "files:read", "files:write",
                                    "members:read", "billing:read"], r.randrange(1, 4))),
         "created_at": day(60, 400), "last_used_at": day(1, 30)} for _ in range(8)])
    fx["billing"] = ("sample-subscriptions.json", [
        {"account_id": a, "plan": r.choice(PLANS[1:4]), "billing_cycle": r.choice(["monthly", "annual"]),
         "seats": r.randrange(2, 80), "currency": r.choice(["USD", "EUR", "GBP", "INR"]),
         "status": r.choice(["active", "active", "past_due", "cancelled"]),
         "payment_method": make_id(r, "pm_", 6), "current_period_end": (REFERENCE_DATE + timedelta(days=r.randrange(1, 300))).isoformat()}
        for a in accounts])
    fx["support"] = ("sample-tickets.json", [
        {"ticket_id": f"SUP-{r.randrange(50000, 60000)}", "account_id": r.choice(accounts), "plan": r.choice(PLANS),
         "priority": r.choice(["P1", "P2", "P3", "P3", "P4"]), "channel": r.choice(["email", "chat", "phone"]),
         "status": r.choice(["open", "pending", "solved", "closed"]), "subject": r.choice(TICKET_SUBJECTS),
         "opened_at": stamp(), "first_response_minutes": r.randrange(4, 600)} for _ in range(10)])
    fx["projects"] = ("sample-tasks.json", [
        {"task_id": make_id(r, "tsk_", 8), "project_id": r.choice(projects), "workspace_id": r.choice(workspaces),
         "title": r.choice(TASK_TITLES), "priority": r.choice(["low", "medium", "high"]),
         "comment_count": r.randrange(0, 14), "created_at": stamp()} for _ in range(10)])
    fx["files"] = ("sample-files.json", [
        {"file_id": make_id(r, "fil_", 8), "workspace_id": r.choice(workspaces),
         "name": r.choice(["roadmap.pdf", "budget.xlsx", "logo.png", "kickoff-notes.docx", "demo.mp4", "export.csv"]),
         "size_bytes": r.randrange(2_000, 900_000_000), "version": r.randrange(1, 9),
         "region": r.choice(REGIONS), "uploaded_at": stamp()} for _ in range(10)])
    fx["notifications"] = ("sample-notifications.json", [
        {"notification_id": make_id(r, "ntf_", 10), "account_id": r.choice(accounts),
         "channel": r.choice(["email", "in_app", "push"]),
         "event_type": r.choice(["task.assigned", "task.completed", "file.shared", "member.invited", "invoice.paid"]),
         "status": r.choice(["sent", "sent", "delivered", "bounced", "suppressed"]), "created_at": stamp()}
        for _ in range(10)])
    fx["webhooks"] = ("sample-deliveries.json", [
        {"event_id": make_id(r, "evt_", 10), "endpoint_id": r.choice(endpoints),
         "event_type": r.choice(["project.created", "task.completed", "file.uploaded", "member.invited", "invoice.paid"]),
         "attempt": r.randrange(1, 5), "status_code": r.choice([200, 200, 200, 204, 500, 503, 410]),
         "duration_ms": r.randrange(40, 4000), "delivered_at": stamp()} for _ in range(10)])
    fx["search"] = ("sample-queries.json", [
        {"query": q, "workspace_id": r.choice(workspaces), "result_count": r.randrange(0, 240),
         "took_ms": r.randrange(12, 380)}
        for q in ["launch checklist", "type:task assignee:me", "\"quarterly roadmap\"", "type:file budget",
                  "onboarding -archived", "type:task status:open pricing", "kickoff notes", "logo type:file"]])
    fx["audit-log"] = ("sample-entries.json", [
        {"entry_id": make_id(r, "aud_", 10), "account_id": r.choice(accounts),
         "actor_role": r.choice(["Owner", "Admin", "Billing admin", "Member"]),
         "action": r.choice(["member.invited", "member.removed", "api_key.created", "sso.enabled",
                             "plan.changed", "file.shared", "account.owner_transferred"]),
         "region": r.choice(REGIONS), "occurred_at": stamp()} for _ in range(10)])
    fx["integrations"] = ("sample-installs.json", [
        {"integration_id": make_id(r, "int_", 6), "account_id": r.choice(accounts),
         "app": r.choice(["slack", "github", "jira", "google-workspace"]),
         "state": r.choice(["active", "active", "active", "suspended", "revoked"]), "installed_at": day(10, 500)}
        for _ in range(8)])
    fx["analytics"] = ("sample-daily-metrics.json", [
        {"account_id": accounts[i % 3], "date": (REFERENCE_DATE - timedelta(days=i + 1)).isoformat(),
         "active_members": r.randrange(4, 90), "tasks_created": r.randrange(5, 200),
         "tasks_completed": r.randrange(3, 180), "storage_used_gb": round(r.uniform(1, 480), 1)}
        for i in range(9)])
    return fx


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def generate(out: Output, scale: int) -> None:
    months = month_list(scale)
    incidents = build_incidents(months, scale)
    stats = build_service_months(months, incidents)
    changes = build_changes(months)
    weeks = build_weeks(months)
    tickets = build_tickets(weeks)
    plan_mix = build_plan_mix(months)
    storage = build_storage(months)
    runs = build_test_runs(weeks, scale)
    endpoints = {s["name"]: discover_endpoints(s["name"]) for s in SERVICES}

    for inc in incidents:
        out.write(inc["path"], render_incident(inc))
    for run in runs:
        out.write(f"reports/test-runs/{run['label']}.md", render_test_run(run))
    for month in months:
        out.write(f"reports/performance/{ym(month)}.md", render_performance(month, stats, incidents, endpoints))
        out.write(f"reports/release-notes/{ym(month)}.md", render_release_notes(month, changes))
    quarters: dict[str, list[tuple[int, int]]] = {}
    for month in months:
        quarters.setdefault(quarter_of(month), []).append(month)
    for quarter, q_months in quarters.items():
        out.write(f"reports/quarterly/{quarter}-business-review.md",
                  render_business_review(quarter, q_months, stats, incidents, tickets, plan_mix))
        out.write(f"reports/capacity/{quarter}-capacity.md", render_capacity(quarter, q_months, stats, storage))
        out.write(f"reports/security-audits/{quarter}-access-review.md", render_access_review(quarter, q_months))

    out.write("reports/README.md", f"""# Reports

## What is in the reports folder?

Everything under `reports/` is written by `tools/generate_reports.py`. Do not edit these files by hand: change the generator and run it again. This copy holds **{len(incidents)} incident postmortems**, **{len(runs)} weekly test runs**, **{len(months)} monthly performance reports**, **{len(months)} monthly release notes** and **{len(quarters)} quarters** of capacity, security and business reviews.

## Which report types exist?

{table(['Folder', 'Contents', 'File name'], [
    ['`reports/incidents/`', 'Incident postmortems', '`INC-YYYY-NNN-<service>-<slug>.md`'],
    ['`reports/test-runs/`', 'Weekly full test run results', '`YYYY-Www.md`'],
    ['`reports/performance/`', 'Monthly latency, volume and availability', '`YYYY-MM.md`'],
    ['`reports/release-notes/`', 'Monthly summary of all service changes', '`YYYY-MM.md`'],
    ['`reports/quarterly/`', 'Quarterly business review', '`YYYY-Qn-business-review.md`'],
    ['`reports/capacity/`', 'Quarterly capacity report', '`YYYY-Qn-capacity.md`'],
    ['`reports/security-audits/`', 'Quarterly security and access review', '`YYYY-Qn-access-review.md`'],
])}

## How are incidents numbered and graded?

Incident IDs look like `INC-2026-007`: the year, then a sequence number that restarts each year. Severity runs from **SEV1** (most severe) to **SEV4**. The full list of incidents with dates, services and durations is in `data/incident-index.csv`.

## Where is the data behind the reports?

The numbers in these reports are also published as CSV and JSON files in `data/`. See `data/README.md` for the columns of each file.

Report date: {REFERENCE_DATE.isoformat()}
""")

    for svc in SERVICES:
        out.write(f"services/{svc['name']}/CHANGELOG.md", render_changelog(svc, months, changes))
    for service, (name, records) in build_fixtures().items():
        out.write(f"services/{service}/fixtures/{name}", json.dumps(records, indent=2))

    # Datasets
    out.write("data/incident-index.csv", csv_text(
        ["incident_id", "started_at_utc", "severity", "service", "duration_minutes", "regions", "accounts_affected", "tickets", "title", "postmortem"],
        [[i["id"], i["start"].strftime("%Y-%m-%dT%H:%M:00Z"), i["sev"], i["service"], i["duration"],
          " ".join(i["regions"]), i["accounts"], i["tickets"], i["title"], i["path"]] for i in incidents]))
    out.write("data/service-performance-by-month.csv", csv_text(
        ["month", "service", "uptime_pct", "p50_ms", "p95_ms", "p99_ms", "requests_millions", "error_rate_pct"],
        [[ym(m), s["name"], *(stats[(s["name"], m)][k] for k in ("uptime", "p50", "p95", "p99", "requests_m", "error_rate"))]
         for m in months for s in SERVICES]))
    out.write("data/ticket-volume-by-week.csv", csv_text(
        ["week_starting", "p1", "p2", "p3", "p4", "total", "first_response_met_pct", "satisfaction_pct"],
        [[t["week"].isoformat(), t["P1"], t["P2"], t["P3"], t["P4"], t["total"], t["first_response_met_pct"], t["satisfaction_pct"]] for t in tickets]))
    out.write("data/accounts-by-plan.csv", csv_text(
        ["month", *PLANS, "total"], [[ym(p["month"]), *(p[k] for k in PLANS), p["total"]] for p in plan_mix]))
    out.write("data/storage-usage-by-region.csv", csv_text(
        ["month", "region", "used_tb", "provisioned_tb", "used_pct"],
        [[ym(s["month"]), s["region"], s["used_tb"], s["provisioned_tb"], s["used_pct"]] for s in storage]))
    out.write("data/test-run-summary.csv", csv_text(
        ["week", "week_starting", "service", "tests", "passed", "failed", "skipped", "duration_s", "line_coverage_pct"],
        [[run["label"], run["week"].isoformat(), s["service"], s["total"], s["passed"], s["failed"], s["skipped"], s["duration_s"], s["coverage"]]
         for run in runs for s in run["services"]]))
    out.write("data/service-catalog.json", json.dumps([
        {"name": s["name"], "title": s["title"], "team": s["team"], "slack_channel": s["channel"], "tier": s["tier"],
         "availability_objective_pct": TIER_SLO[s["tier"]], "readme": f"services/{s['name']}/README.md",
         "api_base": f"https://api.acme-cloud.example/v2/{s['name']}", "operations": endpoints[s["name"]]}
        for s in SERVICES], indent=2))
    out.write("data/README.md", f"""# Datasets

## What is in the data folder?

The `data/` folder holds the numbers behind the reports in `reports/`, as CSV and JSON. Every file is written by `tools/generate_reports.py`. All figures are fictional.

## Which datasets exist and what are their columns?

{table(['File', 'One row per', 'Columns'], [
    ['`data/incident-index.csv`', 'Incident', 'incident_id, started_at_utc, severity, service, duration_minutes, regions, accounts_affected, tickets, title, postmortem'],
    ['`data/service-performance-by-month.csv`', 'Service and month', 'month, service, uptime_pct, p50_ms, p95_ms, p99_ms, requests_millions, error_rate_pct'],
    ['`data/ticket-volume-by-week.csv`', 'Week', 'week_starting, p1, p2, p3, p4, total, first_response_met_pct, satisfaction_pct'],
    ['`data/accounts-by-plan.csv`', 'Month', 'month, free, starter, pro, business, enterprise, total'],
    ['`data/storage-usage-by-region.csv`', 'Region and month', 'month, region, used_tb, provisioned_tb, used_pct'],
    ['`data/test-run-summary.csv`', 'Service and weekly test run', 'week, week_starting, service, tests, passed, failed, skipped, duration_s, line_coverage_pct'],
    ['`data/service-catalog.json`', 'Service', 'name, title, team, slack_channel, tier, availability_objective_pct, readme, api_base, operations'],
])}

## How do I regenerate the data?

Run `python tools/generate_reports.py` from the repository root. The output is deterministic, so running it twice changes nothing. See `tools/README.md`.

Report date: {REFERENCE_DATE.isoformat()}
""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--scale", type=int, default=1, help="multiply the amount of history (default 1)")
    parser.add_argument("--check", action="store_true", help="do not write; exit 1 if any file would change")
    args = parser.parse_args()
    if args.scale < 1:
        parser.error("--scale must be 1 or more")
    out = Output(check=args.check)
    generate(out, args.scale)
    if args.check:
        for rel in out.changed:
            print(f"out of date: {rel}")
        print(f"{out.written} files checked, {len(out.changed)} out of date")
        return 1 if out.changed else 0
    print(f"{out.written} files generated, {len(out.changed)} changed on disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
