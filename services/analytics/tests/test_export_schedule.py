"""Tests for scheduled report cadence, limits and next-run calculation."""

import unittest
from datetime import date, datetime, timedelta, timezone

from acme_analytics import Cadence, ReportSchedule, ScheduleError
from acme_analytics import export_schedule as es

UTC = timezone.utc


def utc(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


class LimitTests(unittest.TestCase):
    def test_plan_limits(self):
        limits = [es.schedule_limit(p) for p in ("free", "starter", "pro", "Business", "enterprise")]
        self.assertEqual(limits, [0, 2, 10, 50, 200])

    def test_unknown_plan_raises(self):
        with self.assertRaises(ScheduleError):
            es.schedule_limit("platinum")

    def test_only_owner_and_admin_can_create(self):
        self.assertTrue(es.can_create_schedule("pro", 0, "Owner"))
        self.assertTrue(es.can_create_schedule("pro", 9, "admin"))
        self.assertFalse(es.can_create_schedule("pro", 0, "member"))
        self.assertFalse(es.can_create_schedule("pro", 0, "billing admin"))

    def test_limit_blocks_creation(self):
        self.assertFalse(es.can_create_schedule("free", 0, "owner"))
        self.assertFalse(es.can_create_schedule("starter", 2, "owner"))
        self.assertTrue(es.can_create_schedule("starter", 1, "owner"))

    def test_eligible_recipients_exclude_guests_and_billing_admins(self):
        people = [
            ("owner@customer.example", "Owner"),
            ("admin@customer.example", "Admin"),
            ("member@customer.example", "Member"),
            ("finance@customer.example", "Billing admin"),
            ("guest@partner.example", "Guest"),
        ]
        self.assertEqual(
            es.eligible_recipients(people),
            ["owner@customer.example", "admin@customer.example", "member@customer.example"],
        )


class ValidationTests(unittest.TestCase):
    def test_weekly_needs_weekday(self):
        with self.assertRaises(ScheduleError):
            es.validate_schedule(ReportSchedule(Cadence.WEEKLY))
        with self.assertRaises(ScheduleError):
            es.validate_schedule(ReportSchedule(Cadence.WEEKLY, weekday=7))

    def test_monthly_needs_day_1_to_31(self):
        with self.assertRaises(ScheduleError):
            es.validate_schedule(ReportSchedule(Cadence.MONTHLY, day_of_month=0))
        with self.assertRaises(ScheduleError):
            es.validate_schedule(ReportSchedule(Cadence.MONTHLY, day_of_month=32))

    def test_bad_hour_format_and_recipient_count(self):
        with self.assertRaises(ScheduleError):
            es.validate_schedule(ReportSchedule(Cadence.DAILY, send_hour=24))
        with self.assertRaises(ScheduleError):
            es.validate_schedule(ReportSchedule(Cadence.DAILY, report_format="docx"))
        too_many = [f"member{n}@customer.example" for n in range(26)]
        with self.assertRaises(ScheduleError):
            es.validate_schedule(ReportSchedule(Cadence.DAILY, recipients=too_many))
        es.validate_schedule(ReportSchedule(Cadence.DAILY, recipients=too_many[:25]))


class NextRunTests(unittest.TestCase):
    def test_daily_defaults_to_0800(self):
        schedule = ReportSchedule(Cadence.DAILY)
        self.assertEqual(es.next_run(schedule, utc(2026, 11, 26, 7, 59)), utc(2026, 11, 26, 8))
        self.assertEqual(es.next_run(schedule, utc(2026, 11, 26, 8, 0)), utc(2026, 11, 27, 8))

    def test_weekly_on_monday(self):
        schedule = ReportSchedule(Cadence.WEEKLY, weekday=0)
        # 2026-11-26 is a Thursday; the next Monday is 2026-11-30.
        self.assertEqual(es.next_run(schedule, utc(2026, 11, 26, 12)), utc(2026, 11, 30, 8))
        self.assertEqual(es.next_run(schedule, utc(2026, 11, 30, 7)), utc(2026, 11, 30, 8))
        self.assertEqual(es.next_run(schedule, utc(2026, 11, 30, 9)), utc(2026, 12, 7, 8))

    def test_monthly_day_31_clamps_to_last_day(self):
        schedule = ReportSchedule(Cadence.MONTHLY, day_of_month=31)
        self.assertEqual(es.next_run(schedule, utc(2026, 4, 1)), utc(2026, 4, 30, 8))
        self.assertEqual(es.next_run(schedule, utc(2026, 2, 1)), utc(2026, 2, 28, 8))
        self.assertEqual(es.next_run(schedule, utc(2028, 2, 1)), utc(2028, 2, 29, 8))

    def test_monthly_rolls_over_the_year(self):
        schedule = ReportSchedule(Cadence.MONTHLY, day_of_month=1, send_hour=6)
        self.assertEqual(es.next_run(schedule, utc(2026, 12, 15)), utc(2027, 1, 1, 6))

    def test_send_hour_is_in_workspace_time_zone(self):
        mumbai = timezone(timedelta(hours=5, minutes=30))
        schedule = ReportSchedule(Cadence.DAILY, tz=mumbai)
        self.assertEqual(es.next_run(schedule, utc(2026, 11, 26, 0, 0)), utc(2026, 11, 26, 2, 30))
        self.assertEqual(es.next_run(schedule, utc(2026, 11, 26, 3, 0)), utc(2026, 11, 27, 2, 30))

    def test_paused_schedule_has_no_next_run_and_naive_time_is_rejected(self):
        self.assertIsNone(es.next_run(ReportSchedule(Cadence.DAILY, paused=True), utc(2026, 11, 26)))
        with self.assertRaises(ScheduleError):
            es.next_run(ReportSchedule(Cadence.DAILY), datetime(2026, 11, 26))


class DeliveryAndExportTests(unittest.TestCase):
    def test_report_periods(self):
        run_day = date(2026, 11, 30)
        self.assertEqual(es.report_period(Cadence.DAILY, run_day), (date(2026, 11, 29), date(2026, 11, 29)))
        self.assertEqual(es.report_period(Cadence.WEEKLY, run_day), (date(2026, 11, 23), date(2026, 11, 29)))
        self.assertEqual(es.report_period(Cadence.MONTHLY, run_day), (date(2026, 10, 1), date(2026, 10, 31)))
        self.assertEqual(
            es.report_period(Cadence.MONTHLY, date(2027, 1, 1)), (date(2026, 12, 1), date(2026, 12, 31))
        )

    def test_three_failures_pause_the_schedule(self):
        schedule = ReportSchedule(Cadence.DAILY)
        es.record_delivery(schedule, False)
        es.record_delivery(schedule, False)
        self.assertFalse(schedule.paused)
        es.record_delivery(schedule, False)
        self.assertTrue(schedule.paused)
        es.resume(schedule)
        self.assertFalse(schedule.paused)
        self.assertEqual(schedule.consecutive_failures, 0)

    def test_success_resets_failure_count(self):
        schedule = ReportSchedule(Cadence.DAILY)
        es.record_delivery(schedule, False)
        es.record_delivery(schedule, False)
        es.record_delivery(schedule, True)
        es.record_delivery(schedule, False)
        self.assertFalse(schedule.paused)
        self.assertEqual(schedule.consecutive_failures, 1)

    def test_export_mode_and_link_expiry(self):
        self.assertEqual(es.export_mode(10_000), "immediate")
        self.assertEqual(es.export_mode(10_001), "background")
        self.assertEqual(es.export_mode(1_000_000), "background")
        with self.assertRaises(ScheduleError):
            es.export_mode(1_000_001)
        with self.assertRaises(ScheduleError):
            es.export_mode(-1)
        self.assertEqual(es.download_link_expiry(utc(2026, 11, 26, 10)), utc(2026, 12, 3, 10))


if __name__ == "__main__":
    unittest.main()
