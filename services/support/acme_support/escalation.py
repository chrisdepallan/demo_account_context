"""Tier routing and escalation paths.

Source: ``services/support/docs/sla-and-escalation.md``.

1. Tier 1 (frontline) handles the ticket first.
2. Unsolved after 4 business hours (P2) or 1 business day (P3), the ticket
   goes to Tier 2 (product specialists).
3. Confirmed bugs go to the owning engineering team through a linked Jira
   issue.
4. P1 tickets page the on-call engineer immediately and open an incident on
   the status page within 15 minutes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .sla import BUSINESS_DAY_MINUTES, add_business_minutes, business_minutes_between

TIER_1 = "tier_1"
TIER_2 = "tier_2"
ENGINEERING = "engineering"
ON_CALL = "on_call_engineer"

#: Business minutes a ticket may stay unsolved in Tier 1 before Tier 2.
TIER_2_AFTER_MINUTES: Dict[str, int] = {"P2": 240, "P3": BUSINESS_DAY_MINUTES}
STATUS_INCIDENT_WITHIN_MINUTES = 15
CUSTOMER_ESCALATION_REVIEW_MINUTES = BUSINESS_DAY_MINUTES
SUPPORT_CHANNEL = "#support-escalations"

#: Service -> (owning team, Slack channel) for confirmed bugs.
OWNING_TEAMS: Dict[str, Tuple[str, str]] = {
    "accounts": ("Accounts Platform", "#team-accounts"),
    "auth": ("Identity", "#team-identity"),
    "billing": ("Revenue Engineering", "#team-billing"),
    "support": ("Customer Support", "#support-escalations"),
    "projects": ("Work Management", "#team-projects"),
    "files": ("Storage Platform", "#team-storage"),
    "notifications": ("Messaging", "#team-notifications"),
    "webhooks": ("Developer Platform", "#team-developer-platform"),
    "search": ("Search and Discovery", "#team-search"),
    "audit-log": ("Trust and Compliance", "#team-trust"),
    "integrations": ("Ecosystem", "#team-ecosystem"),
    "analytics": ("Data Platform", "#team-data"),
}


@dataclass(frozen=True)
class Decision:
    """Where a ticket should be now, why, and what must be done."""

    target: str
    reason: str
    actions: Tuple[str, ...] = ()


def owning_team(service: str) -> Tuple[str, str]:
    """Return ``(team, slack_channel)`` for the service that owns a bug."""
    try:
        return OWNING_TEAMS[service.lower()]
    except KeyError:
        raise ValueError(f"unknown service: {service}") from None


def incident_deadline(created_at: datetime) -> datetime:
    """Return when the status page incident for a P1 must be open."""
    return created_at + timedelta(minutes=STATUS_INCIDENT_WITHIN_MINUTES)


def tier_2_due(priority: str, created_at: datetime) -> Optional[datetime]:
    """Return when an unsolved ticket moves to Tier 2, or ``None``.

    Only P2 and P3 have a time-based threshold. P1 skips the tiers and P4
    stays in Tier 1 unless an agent escalates it by hand.
    """
    minutes = TIER_2_AFTER_MINUTES.get(priority.upper())
    return None if minutes is None else add_business_minutes(created_at, minutes)


def route(priority: str, created_at: datetime, now: datetime,
          confirmed_bug: bool = False, service: Optional[str] = None) -> Decision:
    """Return the routing decision for an unsolved ticket at ``now``."""
    priority = priority.upper()
    if priority not in ("P1", "P2", "P3", "P4"):
        raise ValueError(f"unknown priority: {priority}")
    if priority == "P1":
        return Decision(ON_CALL, "P1 pages the on-call engineer immediately",
                        ("page_on_call", "open_status_page_incident"))
    if confirmed_bug:
        if service is None:
            raise ValueError("service is required for a confirmed bug")
        team, channel = owning_team(service)
        return Decision(ENGINEERING, f"confirmed bug owned by {team}",
                        ("create_linked_jira_issue", f"notify {channel}"))
    limit = TIER_2_AFTER_MINUTES.get(priority)
    if limit is not None and business_minutes_between(created_at, now) >= limit:
        return Decision(TIER_2, f"{priority} unsolved past the Tier 1 threshold",
                        ("assign_tier_2",))
    return Decision(TIER_1, "within the Tier 1 window")


def escalation_path(priority: str) -> List[str]:
    """Return the ordered escalation path for a priority."""
    priority = priority.upper()
    if priority == "P1":
        return [ON_CALL, ENGINEERING]
    if priority in ("P2", "P3"):
        return [TIER_1, TIER_2, ENGINEERING]
    if priority == "P4":
        return [TIER_1]
    raise ValueError(f"unknown priority: {priority}")


def customer_escalation_review_due(requested_at: datetime) -> datetime:
    """A team lead reviews a customer-requested escalation within 1 business day."""
    return add_business_minutes(requested_at, CUSTOMER_ESCALATION_REVIEW_MINUTES)


def is_escalation_request(reply_text: str) -> bool:
    """Return True if the customer replied "escalate" on the ticket."""
    return reply_text.strip().strip('."!').lower() == "escalate"


def customer_escalation_channels(plan: str) -> List[str]:
    """Return the ways a customer on ``plan`` can ask for an escalation."""
    plan = plan.lower()
    channels = ["ticket_reply"]
    if plan in ("business", "enterprise"):
        channels.append("phone")
    if plan == "enterprise":
        channels.append("customer_success_manager")
    return channels
