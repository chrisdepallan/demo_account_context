"""Acme Cloud Billing service rules.

Implements the rules documented in ``services/billing/docs/``:

- ``pricing`` – list prices per plan, billing cycle and currency, discounts
  and invoice subtotals.
- ``proration`` – prorated charges and credits for mid-cycle changes.
- ``dunning`` – the failed-payment schedule (Day 0/1/3/7/14/44).
- ``refunds`` – refund eligibility, approval thresholds and SLA credits.

All money values are ``decimal.Decimal``. The package uses the standard
library only.
"""

from . import dunning, pricing, proration, refunds

__all__ = ["dunning", "pricing", "proration", "refunds"]
__version__ = "2.4.0"
