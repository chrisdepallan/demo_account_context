"""Tests for metric definitions and roll-ups."""

import unittest
from datetime import date, datetime, timedelta, timezone

from acme_analytics import ActivityEvent, Task, aggregation, metrics

NOV1 = date(2026, 11, 1)
NOV30 = date(2026, 11, 30)


def dt(month: int, day: int, hour: int = 12) -> datetime:
    return datetime(2026, month, day, hour, 0, 0)


class ActiveMemberTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            ActivityEvent("m1", date(2026, 11, 26), "task.completed"),
            ActivityEvent("m1", date(2026, 11, 25), "comment.added"),
            ActivityEvent("m2", date(2026, 11, 20), "file.uploaded"),
            ActivityEvent("m3", date(2026, 10, 30), "project.edited"),
            ActivityEvent("m4", date(2026, 11, 26), "session.login"),
            ActivityEvent("g1", date(2026, 11, 26), "comment.added", is_guest=True),
        ]

    def test_daily_weekly_monthly_windows(self):
        end = date(2026, 11, 26)
        self.assertEqual(metrics.active_members(self.events, end, "daily"), 1)
        self.assertEqual(metrics.active_members(self.events, end, "weekly"), 2)
        self.assertEqual(metrics.active_members(self.events, end, "monthly"), 3)

    def test_monthly_window_is_28_days(self):
        # 2026-10-30 is the first day of the 28-day window ending 2026-11-26.
        self.assertEqual(metrics.active_members(self.events, date(2026, 11, 27), "monthly"), 2)

    def test_guests_and_logins_do_not_count(self):
        only = [e for e in self.events if e.member_id in ("m4", "g1")]
        self.assertEqual(metrics.active_members(only, date(2026, 11, 26), "monthly"), 0)

    def test_unknown_window_raises(self):
        with self.assertRaises(ValueError):
            metrics.active_members(self.events, NOV30, "yearly")


class TaskMetricTests(unittest.TestCase):
    def test_completion_rate_example_from_docs(self):
        tasks = [Task(dt(10, 20), completed_at=dt(11, 10)) for _ in range(30)]
        tasks += [Task(dt(11, 5)) for _ in range(10)]
        self.assertEqual(metrics.task_completion_rate(tasks, NOV1, NOV30), 75.0)

    def test_completion_rate_ignores_cancelled_and_out_of_period_tasks(self):
        tasks = [
            Task(dt(11, 2), completed_at=dt(11, 3)),
            Task(dt(11, 2)),
            Task(dt(11, 2), cancelled=True),
            Task(dt(9, 1), completed_at=dt(10, 15)),  # done before the period
            Task(dt(12, 1)),  # created after the period
        ]
        self.assertEqual(metrics.task_completion_rate(tasks, NOV1, NOV30), 50.0)

    def test_completion_rate_is_none_when_nothing_was_open(self):
        self.assertIsNone(metrics.task_completion_rate([], NOV1, NOV30))

    def test_rounding_is_half_up(self):
        self.assertEqual(metrics.round_half_up(74.95), 75.0)
        self.assertEqual(metrics.round_half_up(2.04), 2.0)
        self.assertEqual(metrics.percentage(1, 3), 33.3)
        self.assertEqual(metrics.percentage(1, 8), 12.5)

    def test_cycle_time_needs_a_start(self):
        started = Task(dt(11, 1), started_at=dt(11, 2), completed_at=dt(11, 4))
        never_started = Task(dt(11, 1), completed_at=dt(11, 4))
        self.assertEqual(metrics.cycle_time_days(started), 2.0)
        self.assertIsNone(metrics.cycle_time_days(never_started))
        self.assertEqual(metrics.lead_time_days(never_started), 3.0)
        self.assertGreaterEqual(metrics.lead_time_days(started), metrics.cycle_time_days(started))

    def test_median_and_p85_example_from_docs(self):
        values = [1.0, 2.0, 2.0, 4.0, 10.0]
        self.assertEqual(metrics.median_days(values), 2.0)
        self.assertEqual(metrics.percentile_days(values), 10.0)
        self.assertEqual(metrics.percentile_days(values, 50), 2.0)
        self.assertIsNone(metrics.median_days([]))
        self.assertIsNone(metrics.percentile_days([]))

    def test_cycle_times_only_for_tasks_completed_in_period(self):
        tasks = [
            Task(dt(11, 1), started_at=dt(11, 1), completed_at=dt(11, 2)),
            Task(dt(10, 1), started_at=dt(10, 1), completed_at=dt(10, 5)),
            Task(dt(11, 1), completed_at=dt(11, 2)),
        ]
        self.assertEqual(metrics.cycle_times(tasks, NOV1, NOV30), [1.0])

    def test_overdue_rate(self):
        today = date(2026, 11, 26)
        tasks = [
            Task(dt(11, 1), due_date=date(2026, 11, 25)),  # overdue
            Task(dt(11, 1), due_date=today),  # due today is not overdue
            Task(dt(11, 1)),  # no due date
            Task(dt(11, 1), completed_at=dt(11, 2), due_date=date(2026, 11, 1)),
        ]
        self.assertEqual(metrics.overdue_rate(tasks, today), 50.0)

    def test_seat_utilisation_example_from_docs(self):
        self.assertEqual(metrics.seat_utilisation(18, 24), 75.0)
        self.assertIsNone(metrics.seat_utilisation(0, 0))


class AggregationTests(unittest.TestCase):
    def test_bucket_start(self):
        thursday = date(2026, 11, 26)
        self.assertEqual(aggregation.bucket_start(thursday, "daily"), thursday)
        self.assertEqual(aggregation.bucket_start(thursday, "weekly"), date(2026, 11, 23))
        self.assertEqual(aggregation.bucket_start(thursday, "monthly"), NOV1)
        with self.assertRaises(ValueError):
            aggregation.bucket_start(thursday, "yearly")

    def test_weekly_and_monthly_rollup(self):
        daily = {date(2026, 11, 22): 2, date(2026, 11, 23): 3, date(2026, 11, 24): 4, date(2026, 12, 1): 5}
        weekly = aggregation.rollup(daily, "weekly")
        self.assertEqual(weekly, {date(2026, 11, 16): 2.0, date(2026, 11, 23): 7.0, date(2026, 11, 30): 5.0})
        monthly = aggregation.rollup(daily, "monthly")
        self.assertEqual(monthly, {NOV1: 9.0, date(2026, 12, 1): 5.0})

    def test_rollup_methods(self):
        daily = {date(2026, 11, 23): 10, date(2026, 11, 24): 30, date(2026, 11, 25): 20}
        monday = date(2026, 11, 23)
        self.assertEqual(aggregation.rollup(daily, "weekly", "mean")[monday], 20.0)
        self.assertEqual(aggregation.rollup(daily, "weekly", "max")[monday], 30.0)
        self.assertEqual(aggregation.rollup(daily, "weekly", "last")[monday], 20.0)
        with self.assertRaises(ValueError):
            aggregation.rollup(daily, "weekly", "median")

    def test_daily_counts_use_workspace_time_zone(self):
        moment = datetime(2026, 11, 25, 22, 30, tzinfo=timezone.utc)
        mumbai = timezone(timedelta(hours=5, minutes=30))
        self.assertEqual(aggregation.daily_counts([moment]), {date(2026, 11, 25): 1})
        self.assertEqual(aggregation.daily_counts([moment, moment], mumbai), {date(2026, 11, 26): 2})
        with self.assertRaises(ValueError):
            aggregation.local_day(datetime(2026, 11, 25, 22, 30))

    def test_fill_gaps(self):
        filled = aggregation.fill_gaps({date(2026, 11, 2): 4}, NOV1, date(2026, 11, 3))
        self.assertEqual(list(filled.values()), [0.0, 4, 0.0])

    def test_day_is_final_after_48_hours(self):
        day = date(2026, 11, 24)
        self.assertFalse(aggregation.is_day_final(day, datetime(2026, 11, 26, 23, 59, tzinfo=timezone.utc)))
        self.assertTrue(aggregation.is_day_final(day, datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)))

    def test_history_per_plan(self):
        today = date(2026, 11, 26)
        self.assertEqual(
            [aggregation.history_days(p) for p in ("free", "starter", "Pro", "business", "enterprise")],
            [30, 90, 365, 730, 1825],
        )
        self.assertEqual(aggregation.history_cutoff("free", today), date(2026, 10, 27))
        daily = {date(2026, 10, 26): 1, date(2026, 10, 27): 2, today: 3}
        self.assertEqual(sorted(aggregation.clip_to_history(daily, "free", today)), [date(2026, 10, 27), today])
        with self.assertRaises(ValueError):
            aggregation.history_days("platinum")

    def test_member_split_and_granularity_limits(self):
        today = date(2026, 11, 26)
        self.assertTrue(aggregation.can_split_by_member(today - timedelta(days=90), today))
        self.assertFalse(aggregation.can_split_by_member(today - timedelta(days=91), today))
        self.assertEqual(aggregation.choose_granularity(date(2025, 11, 26), today), "daily")
        self.assertEqual(aggregation.choose_granularity(date(2025, 11, 25), today), "weekly")
        self.assertEqual(aggregation.choose_granularity(date(2024, 1, 1), today, "monthly"), "monthly")


if __name__ == "__main__":
    unittest.main()
