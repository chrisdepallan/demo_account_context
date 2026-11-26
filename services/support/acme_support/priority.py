"""Priority classification (P1–P4).

Source: ``services/support/docs/sla-and-escalation.md`` and
``services/support/docs/ticket-lifecycle.md``. Priority is set by impact,
never by the plan of the customer.

- P1 – Critical: service down or data loss for many users, no workaround.
- P2 – High: a major feature is broken for many users, or a workaround is
  very hard.
- P3 – Normal: a feature is broken for some users, or a workaround exists.
- P4 – Low: questions, how-to requests and feature requests.
"""

from __future__ import annotations

from dataclasses import dataclass

P1, P2, P3, P4 = "P1", "P2", "P3", "P4"
ORDER = (P1, P2, P3, P4)

LABELS = {P1: "Critical", P2: "High", P3: "Normal", P4: "Low"}

KINDS = ("incident", "question", "how_to", "feature_request")
SCOPES = ("one", "some", "many")
WORKAROUNDS = ("none", "hard", "easy")

ROLE_AGENT = "support_agent"
ROLE_TEAM_LEAD = "support_team_lead"


@dataclass(frozen=True)
class TicketSignals:
    """Impact facts collected during triage.

    ``kind`` – one of ``KINDS``. ``users_affected`` – one of ``SCOPES``.
    ``workaround`` – ``none``, ``hard`` (very hard to apply) or ``easy``.
    """

    kind: str = "incident"
    service_down: bool = False
    data_loss: bool = False
    major_feature: bool = False
    users_affected: str = "some"
    workaround: str = "none"

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"unknown ticket kind: {self.kind}")
        if self.users_affected not in SCOPES:
            raise ValueError(f"unknown scope: {self.users_affected}")
        if self.workaround not in WORKAROUNDS:
            raise ValueError(f"unknown workaround value: {self.workaround}")


def classify(signals: TicketSignals) -> str:
    """Return the priority for the given impact.

    Rules are checked from most to least severe. Data loss is never
    classified lower than P2, even for a single user.
    """
    if signals.kind != "incident":
        return P4
    many = signals.users_affected == "many"
    severe = signals.service_down or signals.data_loss
    if severe and many and signals.workaround == "none":
        return P1
    if (severe or signals.major_feature) and many:
        return P2
    if signals.workaround == "hard" or signals.data_loss:
        return P2
    return P3


def label(priority: str) -> str:
    """Return the display label, for example ``P1 – Critical``."""
    priority = priority.upper()
    if priority not in LABELS:
        raise ValueError(f"unknown priority: {priority}")
    return f"{priority} – {LABELS[priority]}"


def is_higher(a: str, b: str) -> bool:
    """Return True if priority ``a`` is more urgent than ``b``."""
    return ORDER.index(a.upper()) < ORDER.index(b.upper())


def pages_on_call(priority: str) -> bool:
    """Only P1 tickets page the on-call engineer immediately."""
    return priority.upper() == P1


def opens_status_incident(priority: str) -> bool:
    """P1 tickets open an incident on the status page within 15 minutes."""
    return priority.upper() == P1


def can_change_priority(role: str, old: str, new: str) -> bool:
    """Return True if ``role`` may change a ticket from ``old`` to ``new``.

    Any agent may raise a priority or change between P2, P3 and P4. Lowering
    a ticket from P1 needs a support team lead.
    """
    old, new = old.upper(), new.upper()
    if old not in ORDER or new not in ORDER:
        raise ValueError("unknown priority")
    if role not in (ROLE_AGENT, ROLE_TEAM_LEAD):
        raise ValueError(f"unknown role: {role}")
    if old == new:
        return False
    if old == P1:
        return role == ROLE_TEAM_LEAD
    return True
