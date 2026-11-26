"""Tests for the retry schedule, endpoint auto-disable and the event envelope."""

import json
import random
import unittest
from datetime import datetime, timezone

from acme_webhooks import (
    DISABLE_THRESHOLD,
    EVENT_TYPES,
    MAX_ATTEMPTS,
    MAX_PAYLOAD_BYTES,
    RETRY_DELAYS_SECONDS,
    WARNING_THRESHOLD,
    EndpointHealth,
    PayloadTooLargeError,
    build_envelope,
    classify_response,
    is_account_level,
    matches_subscription,
    new_event_id,
    next_retry_delay,
    serialize_envelope,
    total_retry_window_seconds,
    validate_subscription,
)

ACCOUNT = "acc_7F3K9Q2M"
WORKSPACE = "ws_4H8P2L"


class RetryScheduleTests(unittest.TestCase):
    def test_eight_attempts_with_documented_delays(self):
        self.assertEqual(MAX_ATTEMPTS, 8)
        self.assertEqual(RETRY_DELAYS_SECONDS, (60, 300, 1800, 7200, 21600, 43200, 86400))
        delays = [next_retry_delay(n) for n in range(1, 8)]
        self.assertEqual(delays, [float(d) for d in RETRY_DELAYS_SECONDS])

    def test_no_retry_after_last_attempt(self):
        self.assertIsNone(next_retry_delay(8))
        self.assertIsNone(next_retry_delay(9))

    def test_total_window_is_44_hours_36_minutes(self):
        self.assertEqual(total_retry_window_seconds(), 44 * 3600 + 36 * 60)

    def test_retry_after_is_honoured_up_to_one_hour(self):
        self.assertEqual(next_retry_delay(1, retry_after=120), 120.0)
        self.assertEqual(next_retry_delay(1, retry_after=7200), 3600.0)
        self.assertEqual(next_retry_delay(4, retry_after=120), 7200.0)  # schedule is longer
        self.assertEqual(next_retry_delay(1, retry_after=0), 60.0)

    def test_jitter_only_lengthens_by_at_most_ten_percent(self):
        rng = random.Random(7)
        for _ in range(200):
            delay = next_retry_delay(2, jitter=0.10, rng=rng)
            self.assertGreaterEqual(delay, 300.0)
            self.assertLessEqual(delay, 330.0)

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            next_retry_delay(0)
        with self.assertRaises(ValueError):
            next_retry_delay(1, jitter=0.5)

    def test_classify_response(self):
        for status in (200, 201, 204, 299):
            self.assertEqual(classify_response(status), "success")
        for status in (None, 301, 302, 400, 404, 429, 500, 503):
            self.assertEqual(classify_response(status), "retry")
        self.assertEqual(classify_response(410), "disable")


class EndpointHealthTests(unittest.TestCase):
    def test_warns_once_at_25_and_disables_at_50(self):
        self.assertEqual((WARNING_THRESHOLD, DISABLE_THRESHOLD), (25, 50))
        health = EndpointHealth()
        actions = [health.record_attempt(500) for _ in range(50)]
        self.assertEqual(actions.index("warn"), 24)
        self.assertEqual(actions.count("warn"), 1)
        self.assertEqual(actions.index("disable"), 49)
        self.assertEqual(health.state, "disabled")
        self.assertFalse(health.accepts_deliveries)

    def test_success_resets_the_counter(self):
        health = EndpointHealth()
        for _ in range(49):
            health.record_attempt(None)
        self.assertIsNone(health.record_attempt(200))
        self.assertEqual(health.consecutive_failures, 0)
        self.assertIsNone(health.record_attempt(500))
        self.assertEqual(health.state, "active")

    def test_410_disables_immediately(self):
        health = EndpointHealth()
        self.assertEqual(health.record_attempt(410), "disable")
        self.assertEqual(health.state, "disabled")
        self.assertIsNone(health.record_attempt(410))  # reported only once

    def test_pause_and_enable(self):
        health = EndpointHealth()
        health.pause()
        self.assertEqual(health.state, "paused")
        self.assertFalse(health.accepts_deliveries)
        health.record_attempt(410)
        health.pause()
        self.assertEqual(health.state, "disabled")
        health.enable()
        self.assertEqual((health.state, health.consecutive_failures), ("active", 0))


class EventTests(unittest.TestCase):
    def test_catalog_uses_resource_action_names(self):
        self.assertEqual(len(EVENT_TYPES), 22)
        for name in ("project.created", "task.completed", "file.uploaded",
                     "member.invited", "invoice.paid", "account.closed"):
            self.assertIn(name, EVENT_TYPES)
        for name in EVENT_TYPES:
            self.assertRegex(name, r"^[a-z]+\.[a-z_]+$")

    def test_account_level_events(self):
        self.assertTrue(is_account_level("invoice.paid"))
        self.assertTrue(is_account_level("account.closed"))
        self.assertFalse(is_account_level("task.completed"))

    def test_subscription_matching(self):
        self.assertTrue(matches_subscription("task.completed", ["task.completed"]))
        self.assertTrue(matches_subscription("task.completed", ["task.*"]))
        self.assertTrue(matches_subscription("task.completed", ["*"]))
        self.assertFalse(matches_subscription("task.completed", ["project.*", "task.created"]))
        self.assertTrue(matches_subscription("webhook.test", ["project.created"]))

    def test_validate_subscription(self):
        self.assertEqual(
            validate_subscription(["task.*", "invoice.paid", "task.*"]), ["invoice.paid", "task.*"]
        )
        for bad in ([], ["task.exploded"], ["tasks.*"], ["task"]):
            with self.assertRaises(ValueError, msg=str(bad)):
                validate_subscription(bad)

    def test_event_id_format(self):
        self.assertRegex(new_event_id(), r"^evt_[A-Z0-9]{10}$")
        self.assertNotEqual(new_event_id(), new_event_id())

    def test_envelope_fields(self):
        envelope = build_envelope(
            "task.completed",
            ACCOUNT,
            {"id": "tsk_9D3F7H2K", "project_id": "prj_5T8N2W6R"},
            WORKSPACE,
            event_id="evt_3N7Q1Z8K4B",
            created_at=datetime(2026, 11, 26, 14, 3, tzinfo=timezone.utc),
        )
        self.assertEqual(
            list(envelope),
            ["id", "type", "api_version", "created_at", "account_id", "workspace_id", "data"],
        )
        self.assertEqual(envelope["api_version"], "v2")
        self.assertEqual(envelope["created_at"], "2026-11-26T14:03:00Z")
        self.assertEqual(json.loads(serialize_envelope(envelope)), envelope)

    def test_account_level_envelope_has_null_workspace(self):
        envelope = build_envelope("invoice.paid", ACCOUNT, {"id": "INV-2026-004812"})
        self.assertIsNone(envelope["workspace_id"])
        self.assertRegex(envelope["id"], r"^evt_[A-Z0-9]{10}$")
        with self.assertRaises(ValueError):
            build_envelope("invoice.paid", ACCOUNT, {}, WORKSPACE)

    def test_envelope_validation(self):
        with self.assertRaises(ValueError):
            build_envelope("task.exploded", ACCOUNT, {}, WORKSPACE)
        with self.assertRaises(ValueError):
            build_envelope("task.created", "account-1", {}, WORKSPACE)
        with self.assertRaises(ValueError):
            build_envelope("task.created", ACCOUNT, {})
        with self.assertRaises(ValueError):
            build_envelope("task.created", ACCOUNT, {}, WORKSPACE, event_id="evt_short")

    def test_payload_limit_is_256_kb(self):
        self.assertEqual(MAX_PAYLOAD_BYTES, 262144)
        envelope = build_envelope("file.uploaded", ACCOUNT, {"note": "x" * MAX_PAYLOAD_BYTES}, WORKSPACE)
        with self.assertRaises(PayloadTooLargeError):
            serialize_envelope(envelope)


if __name__ == "__main__":
    unittest.main()
