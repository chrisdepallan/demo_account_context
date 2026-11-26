"""Tests for the password policy and failed-login lockout rules."""

import unittest
from datetime import datetime, timedelta

from acme_auth import LockoutTracker, PasswordHistory, password_policy, validate_password

T0 = datetime(2026, 11, 1, 12, 0, 0)
EMAIL = "member@customer.example"
FAKE_SALT = b"not-a-real-salt"


class PasswordPolicyTests(unittest.TestCase):
    def test_accepts_good_password(self):
        self.assertEqual(validate_password("fake-example-phrase", EMAIL), [])

    def test_minimum_12_characters(self):
        self.assertEqual(validate_password("x" * 11, EMAIL), [password_policy.TOO_SHORT])
        self.assertEqual(validate_password("x" * 12, EMAIL), [])

    def test_maximum_128_characters(self):
        self.assertEqual(validate_password("x" * 128, EMAIL), [])
        self.assertEqual(validate_password("x" * 129, EMAIL), [password_policy.TOO_LONG])

    def test_rejects_breached_password(self):
        problems = validate_password("example-breached", EMAIL, breached={"example-breached"})
        self.assertEqual(problems, [password_policy.BREACHED])

    def test_rejects_password_containing_email(self):
        problems = validate_password("Member@Customer.Example-2026", EMAIL)
        self.assertEqual(problems, [password_policy.CONTAINS_EMAIL])

    def test_last_5_passwords_cannot_be_reused(self):
        history = PasswordHistory(FAKE_SALT)
        for n in range(1, 7):
            history.add(f"fake-example-phrase-{n}")
        self.assertEqual(len(history), 5)
        self.assertIn(password_policy.REUSED, validate_password("fake-example-phrase-6", EMAIL, history=history))
        self.assertIn(password_policy.REUSED, validate_password("fake-example-phrase-2", EMAIL, history=history))
        # The sixth-oldest password has dropped out of the history.
        self.assertTrue(password_policy.is_valid_password("fake-example-phrase-1", EMAIL, history=history))

    def test_no_forced_expiry_by_default(self):
        self.assertFalse(password_policy.password_expired(T0, T0 + timedelta(days=3650), None))

    def test_forced_expiry_settings(self):
        self.assertFalse(password_policy.password_expired(T0, T0 + timedelta(days=29), 30))
        self.assertTrue(password_policy.password_expired(T0, T0 + timedelta(days=30), 30))
        with self.assertRaises(ValueError):
            password_policy.validate_expiry_setting(45)

    def test_reset_link_valid_for_60_minutes_once(self):
        self.assertTrue(password_policy.reset_link_valid(T0, T0 + timedelta(minutes=59)))
        self.assertFalse(password_policy.reset_link_valid(T0, T0 + timedelta(minutes=60)))
        self.assertFalse(password_policy.reset_link_valid(T0, T0 + timedelta(minutes=5), already_used=True))


class LockoutTests(unittest.TestCase):
    def fail_times(self, tracker, start, count, step_seconds=10):
        """Record ``count`` failures and return the last result."""
        result = None
        for i in range(count):
            result = tracker.record_failure(start + timedelta(seconds=i * step_seconds))
        return result

    def test_four_failures_do_not_lock(self):
        tracker = LockoutTracker()
        self.assertIsNone(self.fail_times(tracker, T0, 4))
        self.assertFalse(tracker.is_locked(T0 + timedelta(minutes=1)))

    def test_five_failures_lock_for_15_minutes(self):
        tracker = LockoutTracker()
        lock = self.fail_times(tracker, T0, 5)
        self.assertEqual(lock.duration, timedelta(minutes=15))
        self.assertFalse(lock.notify_user)
        self.assertTrue(tracker.is_locked(lock.until - timedelta(seconds=1)))
        self.assertFalse(tracker.is_locked(lock.until))

    def test_slow_failures_do_not_lock(self):
        tracker = LockoutTracker()
        self.assertIsNone(self.fail_times(tracker, T0, 5, step_seconds=240))

    def test_ten_failures_in_an_hour_lock_for_1_hour_and_notify(self):
        tracker = LockoutTracker()
        first = self.fail_times(tracker, T0, 5)
        second = self.fail_times(tracker, first.until, 5)
        self.assertEqual(second.duration, timedelta(hours=1))
        self.assertTrue(second.notify_user)
        self.assertEqual(tracker.retry_after_seconds(second.until - timedelta(minutes=10)), 600)

    def test_attempts_while_locked_are_rejected(self):
        tracker = LockoutTracker()
        lock = self.fail_times(tracker, T0, 5)
        during = lock.until - timedelta(minutes=5)
        self.assertIsNone(tracker.record_failure(during))
        self.assertFalse(tracker.record_success(during))

    def test_password_reset_unlocks_immediately(self):
        tracker = LockoutTracker()
        self.fail_times(tracker, T0, 5)
        tracker.reset_password()
        now = T0 + timedelta(minutes=1)
        self.assertFalse(tracker.is_locked(now))
        self.assertTrue(tracker.record_success(now))

    def test_success_clears_failure_count(self):
        tracker = LockoutTracker()
        self.fail_times(tracker, T0, 4)
        tracker.record_success(T0 + timedelta(minutes=1))
        self.assertIsNone(self.fail_times(tracker, T0 + timedelta(minutes=2), 4))


if __name__ == "__main__":
    unittest.main()
