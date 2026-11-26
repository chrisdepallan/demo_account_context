"""List prices, discounts and invoice subtotals.

Source of truth: ``services/billing/docs/pricing.md``. Prices are per seat,
excluding tax, and are set per currency (they do not follow exchange rates).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Optional, Tuple

CENT = Decimal("0.01")

PLANS = ("free", "starter", "pro", "business", "enterprise")
CYCLES = ("monthly", "annual")
CURRENCIES = ("USD", "EUR", "GBP", "INR")

#: Monthly list price per seat, by plan and currency.
MONTHLY_PRICES: Dict[str, Dict[str, Decimal]] = {
    "free": {c: Decimal("0") for c in CURRENCIES},
    "starter": {"USD": Decimal("8"), "EUR": Decimal("8"), "GBP": Decimal("7"), "INR": Decimal("549")},
    "pro": {"USD": Decimal("15"), "EUR": Decimal("14"), "GBP": Decimal("12"), "INR": Decimal("999")},
    "business": {"USD": Decimal("29"), "EUR": Decimal("27"), "GBP": Decimal("24"), "INR": Decimal("1999")},
}

#: Annual billing charges 10 months for 12 months of service (2 months free).
ANNUAL_MONTHS_CHARGED = 10

#: Maximum members (seats) per plan. ``None`` means unlimited.
MAX_SEATS: Dict[str, Optional[int]] = {
    "free": 3, "starter": 10, "pro": 100, "business": 500, "enterprise": None,
}
ENTERPRISE_MIN_SEATS = 50

#: Discount code -> (fraction off, plans it applies to). Only one may apply.
DISCOUNTS: Dict[str, Tuple[Decimal, Tuple[str, ...]]] = {
    "nonprofit": (Decimal("0.50"), ("starter", "pro", "business")),
    "startup": (Decimal("0.30"), ("starter", "pro", "business")),
    "education": (Decimal("1.00"), ("pro",)),
}
EDUCATION_MAX_FREE_SEATS = 10
STARTUP_DISCOUNT_MONTHS = 12

_EU_COUNTRIES = frozenset({
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE",
    "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
})


class PricingError(ValueError):
    """Raised when a price cannot be computed for the given input."""


def quantize(amount: Decimal) -> Decimal:
    """Round a money amount to two decimal places, half up."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def currency_for_country(country_code: str) -> str:
    """Return the billing currency for an ISO 3166-1 alpha-2 country code.

    EU billing addresses are billed in EUR, the UK in GBP, India in INR and
    everywhere else in USD.
    """
    code = country_code.upper()
    if code in _EU_COUNTRIES:
        return "EUR"
    return {"GB": "GBP", "IN": "INR"}.get(code, "USD")


def seat_price(plan: str, cycle: str = "monthly", currency: str = "USD") -> Decimal:
    """Return the list price of one seat for one full billing cycle.

    For ``annual`` this is the annual total per seat (10 x the monthly price),
    for example 150.00 USD for Pro. Enterprise pricing is custom and raises
    ``PricingError``.
    """
    plan, cycle, currency = plan.lower(), cycle.lower(), currency.upper()
    if plan == "enterprise":
        raise PricingError("Enterprise pricing is custom; contact Sales")
    if plan not in MONTHLY_PRICES:
        raise PricingError(f"unknown plan: {plan}")
    if cycle not in CYCLES:
        raise PricingError(f"unknown billing cycle: {cycle}")
    if currency not in CURRENCIES:
        raise PricingError(f"unsupported currency: {currency}")
    monthly = MONTHLY_PRICES[plan][currency]
    return quantize(monthly * ANNUAL_MONTHS_CHARGED if cycle == "annual" else monthly)


def annual_monthly_equivalent(plan: str, currency: str = "USD") -> Decimal:
    """Return the per-month cost of a seat on annual billing (Pro USD: 12.50)."""
    return quantize(seat_price(plan, "annual", currency) / 12)


def validate_seats(plan: str, seats: int) -> None:
    """Raise ``PricingError`` if ``seats`` is outside the limits of the plan."""
    plan = plan.lower()
    if plan not in MAX_SEATS:
        raise PricingError(f"unknown plan: {plan}")
    if seats < 1:
        raise PricingError("seat count must be at least 1")
    limit = MAX_SEATS[plan]
    if limit is not None and seats > limit:
        raise PricingError(f"{plan} allows at most {limit} seats")
    if plan == "enterprise" and seats < ENTERPRISE_MIN_SEATS:
        raise PricingError(f"Enterprise needs at least {ENTERPRISE_MIN_SEATS} seats")


def discount_amount(plan: str, cycle: str, seats: int, currency: str,
                    discount: Optional[str]) -> Decimal:
    """Return the amount taken off the list subtotal by ``discount``.

    ``nonprofit`` is 50% off, ``startup`` is 30% off, and ``education`` makes
    up to 10 Pro seats free. A discount on a plan it does not cover raises
    ``PricingError``.
    """
    if discount is None:
        return Decimal("0.00")
    key = discount.lower()
    if key not in DISCOUNTS:
        raise PricingError(f"unknown discount: {discount}")
    fraction, plans = DISCOUNTS[key]
    if plan.lower() not in plans:
        raise PricingError(f"the {key} discount does not apply to {plan}")
    discounted_seats = min(seats, EDUCATION_MAX_FREE_SEATS) if key == "education" else seats
    return quantize(seat_price(plan, cycle, currency) * discounted_seats * fraction)


def invoice_subtotal(plan: str, cycle: str, seats: int, currency: str = "USD",
                     discount: Optional[str] = None) -> Decimal:
    """Return the pre-tax subtotal for one full cycle.

    >>> invoice_subtotal("pro", "monthly", 12)
    Decimal('180.00')
    >>> invoice_subtotal("business", "annual", 40, "EUR")
    Decimal('10800.00')
    """
    validate_seats(plan, seats)
    gross = seat_price(plan, cycle, currency) * seats
    return quantize(gross - discount_amount(plan, cycle, seats, currency, discount))
