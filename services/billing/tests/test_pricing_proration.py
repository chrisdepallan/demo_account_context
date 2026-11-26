"""Tests for acme_billing.pricing and acme_billing.proration."""

import unittest
from datetime import date
from decimal import Decimal

from acme_billing import pricing, proration

NOV_START, NOV_END = date(2026, 11, 1), date(2026, 12, 1)


class PricingTests(unittest.TestCase):
    def test_monthly_usd_prices(self):
        self.assertEqual(pricing.seat_price("starter"), Decimal("8.00"))
        self.assertEqual(pricing.seat_price("pro"), Decimal("15.00"))
        self.assertEqual(pricing.seat_price("business"), Decimal("29.00"))

    def test_annual_total_is_ten_months(self):
        self.assertEqual(pricing.seat_price("starter", "annual"), Decimal("80.00"))
        self.assertEqual(pricing.seat_price("pro", "annual"), Decimal("150.00"))
        self.assertEqual(pricing.seat_price("business", "annual"), Decimal("290.00"))

    def test_annual_monthly_equivalent(self):
        self.assertEqual(pricing.annual_monthly_equivalent("starter"), Decimal("6.67"))
        self.assertEqual(pricing.annual_monthly_equivalent("pro"), Decimal("12.50"))
        self.assertEqual(pricing.annual_monthly_equivalent("business"), Decimal("24.17"))

    def test_other_currencies(self):
        self.assertEqual(pricing.seat_price("pro", "monthly", "EUR"), Decimal("14.00"))
        self.assertEqual(pricing.seat_price("business", "monthly", "GBP"), Decimal("24.00"))
        self.assertEqual(pricing.seat_price("starter", "monthly", "INR"), Decimal("549.00"))

    def test_currency_for_country(self):
        self.assertEqual(pricing.currency_for_country("de"), "EUR")
        self.assertEqual(pricing.currency_for_country("GB"), "GBP")
        self.assertEqual(pricing.currency_for_country("IN"), "INR")
        self.assertEqual(pricing.currency_for_country("US"), "USD")

    def test_subtotals_match_sample_invoices(self):
        self.assertEqual(pricing.invoice_subtotal("pro", "monthly", 12), Decimal("180.00"))
        self.assertEqual(pricing.invoice_subtotal("business", "annual", 40, "EUR"),
                         Decimal("10800.00"))

    def test_enterprise_is_custom(self):
        with self.assertRaises(pricing.PricingError):
            pricing.seat_price("enterprise")

    def test_seat_limits(self):
        with self.assertRaises(pricing.PricingError):
            pricing.invoice_subtotal("starter", "monthly", 11)
        with self.assertRaises(pricing.PricingError):
            pricing.validate_seats("enterprise", 49)
        pricing.validate_seats("enterprise", 50)
        pricing.validate_seats("business", 500)

    def test_nonprofit_and_startup_discounts(self):
        self.assertEqual(pricing.invoice_subtotal("pro", "monthly", 10, discount="nonprofit"),
                         Decimal("75.00"))
        self.assertEqual(pricing.invoice_subtotal("business", "monthly", 10, discount="startup"),
                         Decimal("203.00"))

    def test_education_discount_covers_ten_pro_seats(self):
        self.assertEqual(pricing.invoice_subtotal("pro", "monthly", 10, discount="education"),
                         Decimal("0.00"))
        self.assertEqual(pricing.invoice_subtotal("pro", "monthly", 12, discount="education"),
                         Decimal("30.00"))
        with self.assertRaises(pricing.PricingError):
            pricing.invoice_subtotal("business", "monthly", 5, discount="education")


class ProrationTests(unittest.TestCase):
    def test_add_seats_monthly(self):
        result = proration.seat_change("pro", "monthly", "USD", 4, NOV_START, NOV_END,
                                       date(2026, 11, 16))
        self.assertEqual((result.kind, result.amount), ("charge", Decimal("30.00")))
        self.assertEqual((result.remaining_days, result.cycle_days), (15, 30))

    def test_remove_seats_is_credit(self):
        result = proration.seat_change("business", "monthly", "USD", -3, NOV_START, NOV_END,
                                       date(2026, 11, 21))
        self.assertEqual((result.kind, result.amount), ("credit", Decimal("29.00")))

    def test_add_seats_annual(self):
        result = proration.seat_change("pro", "annual", "USD", 2, date(2026, 1, 1),
                                       date(2027, 1, 1), date(2026, 10, 20))
        self.assertEqual(result.amount, Decimal("60.00"))

    def test_change_on_first_day_is_full_price(self):
        result = proration.seat_change("starter", "monthly", "EUR", 1, NOV_START, NOV_END,
                                       NOV_START)
        self.assertEqual(result.amount, Decimal("8.00"))

    def test_rounding_half_up(self):
        # 15.00 * 1 / 31 = 0.4838... -> 0.48 ; 8.00 * 5 / 31 = 1.2903... -> 1.29
        dec = (date(2026, 12, 1), date(2027, 1, 1))
        self.assertEqual(proration.prorate(Decimal("15"), *dec, date(2026, 12, 31)),
                         Decimal("0.48"))
        self.assertEqual(proration.prorate(Decimal("8"), *dec, date(2026, 12, 27)),
                         Decimal("1.29"))
        # 1.00 * 15 / 30 = 0.50 exactly; 0.01 * 15 / 30 = 0.005 -> 0.01
        self.assertEqual(proration.prorate(Decimal("0.01"), NOV_START, NOV_END,
                                           date(2026, 11, 16)), Decimal("0.01"))

    def test_change_outside_period_rejected(self):
        with self.assertRaises(proration.ProrationError):
            proration.seat_change("pro", "monthly", "USD", 1, NOV_START, NOV_END, NOV_END)

    def test_plan_upgrade(self):
        result = proration.plan_upgrade("starter", "pro", "monthly", "USD", 10, NOV_START,
                                        NOV_END, date(2026, 11, 16))
        self.assertEqual((result.kind, result.amount), ("charge", Decimal("35.00")))

    def test_downgrade_not_prorated(self):
        with self.assertRaises(proration.ProrationError):
            proration.plan_upgrade("business", "pro", "monthly", "USD", 10, NOV_START, NOV_END,
                                   date(2026, 11, 16))

    def test_apply_credit_partial_and_full(self):
        part = proration.apply_credit(Decimal("180.00"), Decimal("29.00"))
        self.assertEqual((part.credit_applied, part.amount_due, part.credit_remaining),
                         (Decimal("29.00"), Decimal("151.00"), Decimal("0.00")))
        full = proration.apply_credit(Decimal("80.00"), Decimal("100.00"))
        self.assertEqual((full.amount_due, full.credit_remaining),
                         (Decimal("0.00"), Decimal("20.00")))

    def test_next_monthly_charge_date(self):
        self.assertEqual(proration.next_monthly_charge_date(31, date(2027, 1, 31)),
                         date(2027, 2, 28))
        self.assertEqual(proration.next_monthly_charge_date(15, date(2026, 11, 15)),
                         date(2026, 12, 15))
        self.assertEqual(proration.next_monthly_charge_date(31, date(2026, 12, 31)),
                         date(2027, 1, 31))


if __name__ == "__main__":
    unittest.main()
