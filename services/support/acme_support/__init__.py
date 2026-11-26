"""Acme Cloud Support service rules.

Implements the rules documented in ``services/support/docs/``:

- ``priority`` – classifying a ticket as P1–P4 by impact.
- ``sla`` – first-response targets per plan and priority, business-hours
  arithmetic and breach checks.
- ``escalation`` – tier routing, escalation thresholds and the owning
  engineering team for confirmed bugs.

All datetimes are naive and expressed in support local time (US Central).
The package uses the standard library only.
"""

from . import escalation, priority, sla

__all__ = ["escalation", "priority", "sla"]
__version__ = "2.1.0"
