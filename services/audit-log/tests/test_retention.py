"""Tests for acme_audit_log.retention."""

import unittest
from datetime import datetime, timedelta, timezone

from acme_audit_log import (
    DOWNGRADE_GRACE_DAYS,
    RETENTION_DAYS,
    expires_at,
    has_audit_log,
    is_purge_eligible,
    next_purge_run,
    retention_days,
    select_purgeable,
)

NOW = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)


def days_ago(days):
    return NOW - timedelta(days=days)


class RetentionWindowTests(unittest.TestCase):
    def test_windows_match_plan_table(self):
        self.assertEqual(retention_days("Pro"), 90)
        self.assertEqual(retention_days("Business"), 365)
        self.assertEqual(retention_days("Enterprise"), 7 * 365)
        self.assertEqual(set(RETENTION_DAYS), {"free", "starter", "pro", "business", "enterprise"})

    def test_free_and_starter_have_no_audit_log(self):
        self.assertFalse(has_audit_log("Free"))
        self.assertFalse(has_audit_log("starter"))
        self.assertTrue(has_audit_log(" PRO "))

    def test_unknown_plan_raises(self):
        with self.assertRaises(ValueError):
            retention_days("Platinum")

    def test_expires_at(self):
        self.assertEqual(expires_at(NOW, "pro"), NOW + timedelta(days=90))
        self.assertIsNone(expires_at(NOW, "free"))


class PurgeEligibilityTests(unittest.TestCase):
    def test_inside_window_is_kept(self):
        self.assertFalse(is_purge_eligible(days_ago(89), "pro", NOW))
        self.assertFalse(is_purge_eligible(days_ago(364), "business", NOW))

    def test_boundary_is_purgeable(self):
        self.assertTrue(is_purge_eligible(days_ago(90), "pro", NOW))
        self.assertTrue(is_purge_eligible(days_ago(365), "business", NOW))

    def test_enterprise_keeps_seven_years(self):
        self.assertFalse(is_purge_eligible(days_ago(2554), "enterprise", NOW))
        self.assertTrue(is_purge_eligible(days_ago(2555), "enterprise", NOW))

    def test_legal_hold_blocks_purge_on_enterprise_only(self):
        self.assertFalse(is_purge_eligible(days_ago(4000), "enterprise", NOW, legal_hold=True))
        self.assertTrue(is_purge_eligible(days_ago(400), "business", NOW, legal_hold=True))

    def test_downgrade_grace_delays_purge(self):
        occurred = days_ago(200)  # outside Pro's 90 days
        recent = days_ago(DOWNGRADE_GRACE_DAYS - 1)
        self.assertFalse(is_purge_eligible(occurred, "pro", NOW, downgraded_at=recent))
        old = days_ago(DOWNGRADE_GRACE_DAYS)
        self.assertTrue(is_purge_eligible(occurred, "pro", NOW, downgraded_at=old))

    def test_downgrade_grace_never_shortens_retention(self):
        self.assertFalse(is_purge_eligible(days_ago(40), "pro", NOW, downgraded_at=days_ago(35)))

    def test_downgrade_to_plan_without_audit_log(self):
        self.assertFalse(is_purge_eligible(days_ago(5), "starter", NOW, downgraded_at=days_ago(29)))
        self.assertTrue(is_purge_eligible(days_ago(5), "starter", NOW, downgraded_at=days_ago(30)))

    def test_select_purgeable_returns_oldest_prefix(self):
        entries = [
            ("aud_AAAAAAAAA3", days_ago(10)),
            ("aud_AAAAAAAAA1", days_ago(120)),
            ("aud_AAAAAAAAA2", days_ago(91)),
        ]
        self.assertEqual(
            select_purgeable(entries, "pro", NOW), ["aud_AAAAAAAAA1", "aud_AAAAAAAAA2"]
        )
        self.assertEqual(select_purgeable(entries, "business", NOW), [])
        self.assertEqual(select_purgeable(entries, "enterprise", NOW, legal_hold=True), [])

    def test_next_purge_run_is_0200_utc(self):
        self.assertEqual(next_purge_run(NOW), datetime(2026, 11, 27, 2, 0, tzinfo=timezone.utc))
        early = datetime(2026, 11, 26, 1, 59, tzinfo=timezone.utc)
        self.assertEqual(next_purge_run(early), datetime(2026, 11, 26, 2, 0, tzinfo=timezone.utc))
        exactly = datetime(2026, 11, 26, 2, 0, tzinfo=timezone.utc)
        self.assertEqual(next_purge_run(exactly), datetime(2026, 11, 27, 2, 0, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
