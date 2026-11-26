"""Tests for digest building, quiet hours and the per-user rate limiter."""

import unittest
from datetime import datetime, time, timedelta

from acme_notifications import (
    DigestItem,
    QuietHours,
    RateLimiter,
    build_digest,
    decide_delivery,
    digest_window,
    in_quiet_hours,
    is_digest_due,
    next_release,
    release_mode,
)

NOW = datetime(2026, 11, 26, 8, 0)  # a Thursday
USER = "member@customer.example"


def item(n, hours_ago, project_id="prj_5T8N2W6R", read=False):
    return DigestItem(
        notification_id=f"ntf_{n:010d}",
        notification_type="mention",
        title=f"Notification {n}",
        created_at=NOW - timedelta(hours=hours_ago),
        project_id=project_id,
        read=read,
    )


class DigestTests(unittest.TestCase):
    def test_windows_are_24_hours_and_7_days(self):
        self.assertEqual(digest_window("daily", NOW)[0], NOW - timedelta(hours=24))
        self.assertEqual(digest_window("weekly", NOW)[0], NOW - timedelta(days=7))
        with self.assertRaises(ValueError):
            digest_window("off", NOW)

    def test_empty_or_all_read_gives_no_digest(self):
        self.assertIsNone(build_digest([], "daily", NOW))
        self.assertIsNone(build_digest([item(1, 2, read=True)], "daily", NOW))
        self.assertIsNone(build_digest([item(1, 2)], "off", NOW))

    def test_daily_excludes_items_older_than_24_hours(self):
        digest = build_digest([item(1, 2), item(2, 30)], "daily", NOW)
        self.assertEqual(digest.item_count, 1)
        weekly = build_digest([item(1, 2), item(2, 30)], "weekly", NOW)
        self.assertEqual(weekly.item_count, 2)

    def test_groups_by_project_newest_first_with_other_group(self):
        items = [
            item(1, 5, "prj_AAAAAAA1"),
            item(2, 1, "prj_BBBBBBB2"),
            item(3, 3, None),
            item(4, 2, "prj_AAAAAAA1"),
        ]
        digest = build_digest(items, "daily", NOW)
        self.assertEqual([g.key for g in digest.groups], ["prj_BBBBBBB2", "prj_AAAAAAA1", "Other"])
        first_a = digest.groups[1].items
        self.assertEqual([i.notification_id for i in first_a], ["ntf_0000000004", "ntf_0000000001"])

    def test_caps_at_50_items_and_counts_overflow(self):
        items = [item(n, n * 0.25) for n in range(1, 63)]  # 62 unread, all within 24 hours
        digest = build_digest(items, "daily", NOW)
        self.assertEqual(digest.item_count, 50)
        self.assertEqual(digest.overflow_count, 12)

    def test_daily_digest_due_at_0800_once_per_day(self):
        self.assertFalse(is_digest_due("daily", NOW.replace(hour=7, minute=59), NOW - timedelta(days=1)))
        self.assertTrue(is_digest_due("daily", NOW, NOW - timedelta(days=1)))
        self.assertFalse(is_digest_due("daily", NOW.replace(hour=15), NOW))
        self.assertTrue(is_digest_due("daily", NOW, None))
        self.assertFalse(is_digest_due("off", NOW, None))

    def test_weekly_digest_due_on_monday(self):
        monday = datetime(2026, 11, 23, 8, 0)
        self.assertEqual(monday.weekday(), 0)
        self.assertTrue(is_digest_due("weekly", monday, monday - timedelta(days=7)))
        self.assertFalse(is_digest_due("weekly", NOW, monday))  # Thursday, already sent
        self.assertTrue(is_digest_due("weekly", NOW, monday - timedelta(days=7)))  # catch up


class QuietHoursTests(unittest.TestCase):
    QUIET = QuietHours(enabled=True)

    def test_off_by_default_with_default_window(self):
        default = QuietHours()
        self.assertFalse(default.enabled)
        self.assertEqual((default.start, default.end), (time(22, 0), time(7, 0)))
        self.assertFalse(in_quiet_hours(NOW.replace(hour=23), default))

    def test_overnight_window_start_inclusive_end_exclusive(self):
        self.assertTrue(in_quiet_hours(NOW.replace(hour=22, minute=0), self.QUIET))
        self.assertTrue(in_quiet_hours(NOW.replace(hour=3), self.QUIET))
        self.assertFalse(in_quiet_hours(NOW.replace(hour=7, minute=0), self.QUIET))
        self.assertFalse(in_quiet_hours(NOW.replace(hour=21, minute=59), self.QUIET))

    def test_same_day_and_empty_windows(self):
        lunch = QuietHours(True, time(12, 0), time(13, 0))
        self.assertTrue(in_quiet_hours(NOW.replace(hour=12, minute=30), lunch))
        self.assertFalse(in_quiet_hours(NOW.replace(hour=13), lunch))
        self.assertFalse(in_quiet_hours(NOW, QuietHours(True, time(9, 0), time(9, 0))))

    def test_next_release_is_end_of_window(self):
        self.assertEqual(
            next_release(datetime(2026, 11, 26, 23, 30), self.QUIET), datetime(2026, 11, 27, 7, 0)
        )
        self.assertEqual(
            next_release(datetime(2026, 11, 26, 2, 0), self.QUIET), datetime(2026, 11, 26, 7, 0)
        )
        self.assertIsNone(next_release(NOW.replace(hour=12), self.QUIET))

    def test_release_mode_summarises_above_ten(self):
        self.assertEqual(release_mode(0), "none")
        self.assertEqual(release_mode(10), "individual")
        self.assertEqual(release_mode(11), "summary")
        with self.assertRaises(ValueError):
            release_mode(-1)


class RateLimitTests(unittest.TestCase):
    def test_email_limit_is_20_per_hour(self):
        limiter = RateLimiter()
        results = [limiter.allow(USER, "email", NOW + timedelta(minutes=i)) for i in range(21)]
        self.assertEqual(results.count(True), 20)
        self.assertFalse(results[-1])
        self.assertEqual(limiter.remaining(USER, "email", NOW + timedelta(minutes=21)), 0)

    def test_push_limit_is_30_and_in_app_is_unlimited(self):
        limiter = RateLimiter()
        self.assertEqual(limiter.remaining(USER, "push", NOW), 30)
        self.assertIsNone(limiter.remaining(USER, "in_app", NOW))
        self.assertTrue(all(limiter.allow(USER, "in_app", NOW) for _ in range(500)))

    def test_window_slides_and_users_are_independent(self):
        limiter = RateLimiter()
        for _ in range(20):
            limiter.allow(USER, "email", NOW)
        self.assertFalse(limiter.allow(USER, "email", NOW + timedelta(minutes=59)))
        self.assertTrue(limiter.allow("other@customer.example", "email", NOW))
        self.assertTrue(limiter.allow(USER, "email", NOW + timedelta(minutes=60)))

    def test_mandatory_is_exempt_and_not_counted(self):
        limiter = RateLimiter({"email": 1})
        self.assertTrue(limiter.allow(USER, "email", NOW, mandatory=True))
        self.assertTrue(limiter.allow(USER, "email", NOW))
        self.assertFalse(limiter.allow(USER, "email", NOW))
        self.assertTrue(limiter.allow(USER, "email", NOW, mandatory=True))


class DecisionTests(unittest.TestCase):
    NIGHT = datetime(2026, 11, 26, 23, 0)
    QUIET = QuietHours(enabled=True)

    def test_quiet_hours_hold_email_and_push_but_not_in_app(self):
        limiter = RateLimiter()
        for channel, expected in (("email", "hold"), ("push", "hold"), ("in_app", "send")):
            self.assertEqual(
                decide_delivery(USER, channel, "mention", self.NIGHT, self.QUIET, limiter), expected
            )
        self.assertEqual(limiter.remaining(USER, "email", self.NIGHT), 20)  # held is not counted

    def test_mandatory_bypasses_quiet_hours_and_limits(self):
        limiter = RateLimiter({"email": 0})
        self.assertEqual(
            decide_delivery(USER, "email", "security_alert", self.NIGHT, self.QUIET, limiter), "send"
        )

    def test_over_limit_goes_to_digest(self):
        limiter = RateLimiter({"push": 2})
        off = QuietHours()
        decisions = [decide_delivery(USER, "push", "mention", NOW, off, limiter) for _ in range(3)]
        self.assertEqual(decisions, ["send", "send", "digest"])

    def test_unknown_channel_is_rejected(self):
        with self.assertRaises(ValueError):
            decide_delivery(USER, "sms", "mention", NOW, QuietHours(), RateLimiter())


if __name__ == "__main__":
    unittest.main()
