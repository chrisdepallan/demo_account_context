"""Tests for acme_billing.dunning and acme_billing.refunds."""

import unittest
from datetime import date
from decimal import Decimal

from acme_billing import dunning, refunds

FAILED = date(2026, 11, 2)


class DunningTests(unittest.TestCase):
    def test_retry_dates(self):
        self.assertEqual(
            dunning.retry_dates(FAILED),
            [date(2026, 11, 3), date(2026, 11, 5), date(2026, 11, 9), date(2026, 11, 16)])

    def test_status_by_day(self):
        self.assertEqual(dunning.status_on_day(0), "past_due")
        self.assertEqual(dunning.status_on_day(13), "past_due")
        self.assertEqual(dunning.status_on_day(14), "read_only")
        self.assertEqual(dunning.status_on_day(43), "read_only")
        self.assertEqual(dunning.status_on_day(44), "downgraded_to_free")

    def test_payment_restores_access(self):
        self.assertEqual(
            dunning.account_status(FAILED, date(2026, 11, 20), paid_on=date(2026, 11, 19)),
            "active")
        self.assertEqual(dunning.account_status(FAILED, date(2026, 11, 20)), "read_only")

    def test_payment_after_downgrade_does_not_restore(self):
        self.assertEqual(
            dunning.account_status(FAILED, date(2026, 12, 20), paid_on=date(2026, 12, 18)),
            "downgraded_to_free")

    def test_next_retry(self):
        self.assertEqual(dunning.next_retry(FAILED, date(2026, 11, 4)), date(2026, 11, 5))
        self.assertEqual(dunning.next_retry(FAILED, date(2026, 11, 16)), date(2026, 11, 16))
        self.assertIsNone(dunning.next_retry(FAILED, date(2026, 11, 17)))

    def test_grace_period(self):
        self.assertTrue(dunning.in_grace_period(FAILED, date(2026, 11, 15)))
        self.assertFalse(dunning.in_grace_period(FAILED, date(2026, 11, 16)))
        self.assertTrue(dunning.is_full_access("past_due"))
        self.assertFalse(dunning.is_full_access("read_only"))

    def test_schedule(self):
        steps = dunning.schedule(FAILED)
        self.assertEqual([s.day for s in steps], [0, 1, 3, 7, 14, 44])
        self.assertEqual(steps[-1].on, date(2026, 12, 16))
        self.assertEqual(steps[4].status_after, "read_only")

    def test_negative_day_rejected(self):
        with self.assertRaises(ValueError):
            dunning.days_since_failure(FAILED, date(2026, 11, 1))


class RefundTests(unittest.TestCase):
    def test_approver_thresholds(self):
        self.assertEqual(refunds.required_approver(Decimal("500.00")), "support_agent")
        self.assertEqual(refunds.required_approver(Decimal("500.01")), "support_team_lead")
        self.assertEqual(refunds.required_approver(Decimal("5000.00")), "support_team_lead")
        self.assertEqual(refunds.required_approver(Decimal("5000.01")), "billing_manager")

    def test_goodwill_needs_team_lead(self):
        self.assertEqual(refunds.required_approver(Decimal("20"), goodwill=True),
                         "support_team_lead")
        self.assertFalse(refunds.can_approve("support_agent", Decimal("20"), goodwill=True))
        self.assertTrue(refunds.can_approve("billing_manager", Decimal("20"), goodwill=True))

    def test_can_approve(self):
        self.assertTrue(refunds.can_approve("support_agent", Decimal("180")))
        self.assertFalse(refunds.can_approve("support_team_lead", Decimal("10800")))
        with self.assertRaises(ValueError):
            refunds.required_approver(Decimal("0"))

    def test_annual_refund_window(self):
        bought = date(2026, 9, 14)
        self.assertTrue(refunds.is_refundable("annual", bought, date(2026, 10, 14)))
        self.assertFalse(refunds.is_refundable("annual", bought, date(2026, 10, 15)))

    def test_monthly_not_refundable_except_errors(self):
        bought = date(2026, 11, 1)
        day_after = date(2026, 11, 2)
        self.assertFalse(refunds.is_refundable("monthly", bought, day_after))
        self.assertTrue(refunds.is_refundable("monthly", bought, day_after, "duplicate_charge"))
        self.assertTrue(refunds.is_refundable("monthly", bought, day_after, "charged_after_cancel"))
        self.assertFalse(refunds.is_refundable("annual", bought, day_after, "seats_removed"))

    def test_goodwill_once_per_twelve_months(self):
        self.assertTrue(refunds.goodwill_allowed(None, date(2026, 11, 26)))
        self.assertFalse(refunds.goodwill_allowed(date(2026, 3, 1), date(2026, 11, 26)))
        self.assertTrue(refunds.goodwill_allowed(date(2025, 11, 26), date(2026, 11, 26)))

    def test_sla_credit_bands_business(self):
        self.assertEqual(refunds.sla_credit_percent("business", Decimal("99.95")), 0)
        self.assertEqual(refunds.sla_credit_percent("business", Decimal("99.5")), 10)
        self.assertEqual(refunds.sla_credit_percent("business", Decimal("99.0")), 10)
        self.assertEqual(refunds.sla_credit_percent("business", Decimal("98.99")), 25)
        self.assertEqual(refunds.sla_credit_percent("business", Decimal("94.9")), 50)

    def test_sla_credit_amount_and_free_plan(self):
        self.assertEqual(
            refunds.sla_credit_amount("business", Decimal("97"), Decimal("1160.00")),
            Decimal("290.00"))
        with self.assertRaises(ValueError):
            refunds.sla_credit_percent("free", Decimal("90"))

    def test_sla_credit_request_window(self):
        self.assertTrue(refunds.sla_credit_request_open(date(2026, 10, 31), date(2026, 11, 30)))
        self.assertFalse(refunds.sla_credit_request_open(date(2026, 10, 31), date(2026, 12, 1)))


if __name__ == "__main__":
    unittest.main()
