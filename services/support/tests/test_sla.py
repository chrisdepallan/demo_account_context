"""Tests for acme_support.sla."""

import unittest
from datetime import datetime

from acme_support import sla

# 2026-11-23 is a Monday; 2026-11-27 is a Friday.
MON_9 = datetime(2026, 11, 23, 9, 0)
FRI_17 = datetime(2026, 11, 27, 17, 0)
SAT_NOON = datetime(2026, 11, 28, 12, 0)


class TargetTests(unittest.TestCase):
    def test_free_is_best_effort(self):
        for priority in sla.PRIORITIES:
            self.assertIsNone(sla.target_for("free", priority))

    def test_business_hour_targets(self):
        self.assertEqual(sla.target_for("starter", "P1").minutes, 24 * 60)
        self.assertEqual(sla.target_for("pro", "P2").minutes, 12 * 60)
        self.assertEqual(sla.target_for("business", "P3").minutes, 8 * 60)

    def test_business_day_targets_are_ten_hours(self):
        self.assertEqual(sla.target_for("starter", "P3").minutes, 3 * 600)
        self.assertEqual(sla.target_for("starter", "P4").minutes, 5 * 600)
        self.assertEqual(sla.target_for("enterprise", "P4").minutes, 600)

    def test_enterprise_p1_and_p2_are_around_the_clock(self):
        self.assertEqual(sla.target_for("enterprise", "P1"), sla.Target(30, True))
        self.assertEqual(sla.target_for("enterprise", "P2"), sla.Target(120, True))
        self.assertFalse(sla.target_for("enterprise", "P3").around_the_clock)

    def test_unknown_plan_or_priority(self):
        with self.assertRaises(ValueError):
            sla.target_for("platinum", "P1")
        with self.assertRaises(ValueError):
            sla.target_for("pro", "P5")


class BusinessTimeTests(unittest.TestCase):
    def test_is_business_time(self):
        self.assertTrue(sla.is_business_time(MON_9))
        self.assertTrue(sla.is_business_time(datetime(2026, 11, 23, 8, 0)))
        self.assertFalse(sla.is_business_time(datetime(2026, 11, 23, 18, 0)))
        self.assertFalse(sla.is_business_time(SAT_NOON))

    def test_next_business_open(self):
        self.assertEqual(sla.next_business_open(SAT_NOON), datetime(2026, 11, 30, 8, 0))
        self.assertEqual(sla.next_business_open(datetime(2026, 11, 23, 6, 30)),
                         datetime(2026, 11, 23, 8, 0))
        self.assertEqual(sla.next_business_open(datetime(2026, 11, 27, 19, 0)),
                         datetime(2026, 11, 30, 8, 0))

    def test_add_business_minutes_same_day(self):
        self.assertEqual(sla.add_business_minutes(MON_9, 240), datetime(2026, 11, 23, 13, 0))

    def test_add_business_minutes_over_weekend(self):
        self.assertEqual(sla.add_business_minutes(FRI_17, 8 * 60), datetime(2026, 11, 30, 15, 0))

    def test_business_minutes_between(self):
        self.assertEqual(sla.business_minutes_between(MON_9, datetime(2026, 11, 23, 13, 0)), 240)
        self.assertEqual(sla.business_minutes_between(FRI_17, datetime(2026, 11, 30, 9, 0)), 120)
        self.assertEqual(sla.business_minutes_between(SAT_NOON, datetime(2026, 11, 29, 12, 0)), 0)
        self.assertEqual(sla.business_minutes_between(MON_9, MON_9), 0)


class BreachTests(unittest.TestCase):
    def test_due_business_plan_p1(self):
        self.assertEqual(sla.first_response_due("business", "P1", MON_9),
                         datetime(2026, 11, 23, 11, 0))

    def test_due_pro_p3_is_next_business_day(self):
        self.assertEqual(sla.first_response_due("pro", "P3", MON_9),
                         datetime(2026, 11, 24, 9, 0))

    def test_due_enterprise_p1_ignores_business_hours(self):
        self.assertEqual(sla.first_response_due("enterprise", "P1", SAT_NOON),
                         datetime(2026, 11, 28, 12, 30))

    def test_due_starter_p1_spans_days(self):
        # 24 business hours from Monday 09:00 = Wednesday 13:00.
        self.assertEqual(sla.first_response_due("starter", "P1", MON_9),
                         datetime(2026, 11, 25, 13, 0))

    def test_breach_with_and_without_reply(self):
        on_time = datetime(2026, 11, 23, 11, 0)
        late = datetime(2026, 11, 23, 11, 1)
        self.assertFalse(sla.is_breached("business", "P1", MON_9, on_time, late))
        self.assertTrue(sla.is_breached("business", "P1", MON_9, late, late))
        self.assertTrue(sla.is_breached("business", "P1", MON_9, None, late))
        self.assertFalse(sla.is_breached("business", "P1", MON_9, None, on_time))

    def test_free_never_breaches(self):
        self.assertFalse(sla.is_breached("free", "P1", MON_9, None, datetime(2027, 1, 1)))
        self.assertIsNone(sla.first_response_due("free", "P1", MON_9))

    def test_minutes_until_breach(self):
        self.assertEqual(sla.minutes_until_breach("business", "P2", MON_9,
                                                  datetime(2026, 11, 23, 10, 0)), 180)
        self.assertEqual(sla.minutes_until_breach("business", "P2", MON_9,
                                                  datetime(2026, 11, 23, 14, 0)), -60)
        self.assertEqual(sla.minutes_until_breach("enterprise", "P1", SAT_NOON,
                                                  datetime(2026, 11, 28, 12, 10)), 20)
        self.assertIsNone(sla.minutes_until_breach("free", "P4", MON_9, MON_9))


if __name__ == "__main__":
    unittest.main()
