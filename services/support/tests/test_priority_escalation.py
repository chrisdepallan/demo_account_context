"""Tests for acme_support.priority and acme_support.escalation."""

import unittest
from datetime import datetime

from acme_support import escalation, priority
from acme_support.priority import TicketSignals

MON_9 = datetime(2026, 11, 23, 9, 0)


class PriorityTests(unittest.TestCase):
    def test_p1_outage_many_users_no_workaround(self):
        signals = TicketSignals(service_down=True, users_affected="many", workaround="none")
        self.assertEqual(priority.classify(signals), "P1")

    def test_p1_data_loss_many_users(self):
        signals = TicketSignals(data_loss=True, users_affected="many")
        self.assertEqual(priority.classify(signals), "P1")

    def test_outage_with_workaround_is_p2(self):
        signals = TicketSignals(service_down=True, users_affected="many", workaround="easy")
        self.assertEqual(priority.classify(signals), "P2")

    def test_p2_major_feature_many_users(self):
        signals = TicketSignals(major_feature=True, users_affected="many", workaround="easy")
        self.assertEqual(priority.classify(signals), "P2")

    def test_p2_hard_workaround(self):
        signals = TicketSignals(users_affected="some", workaround="hard")
        self.assertEqual(priority.classify(signals), "P2")

    def test_data_loss_single_user_is_at_least_p2(self):
        signals = TicketSignals(data_loss=True, users_affected="one", workaround="easy")
        self.assertEqual(priority.classify(signals), "P2")

    def test_p3_some_users_or_workaround(self):
        self.assertEqual(priority.classify(TicketSignals(users_affected="some")), "P3")
        self.assertEqual(
            priority.classify(TicketSignals(major_feature=True, users_affected="one",
                                            workaround="easy")), "P3")

    def test_p4_questions_and_requests(self):
        for kind in ("question", "how_to", "feature_request"):
            self.assertEqual(priority.classify(TicketSignals(kind=kind, service_down=True)), "P4")

    def test_invalid_signals(self):
        with self.assertRaises(ValueError):
            TicketSignals(kind="rant")
        with self.assertRaises(ValueError):
            TicketSignals(users_affected="everyone")

    def test_labels_and_ordering(self):
        self.assertEqual(priority.label("p1"), "P1 – Critical")
        self.assertTrue(priority.is_higher("P1", "P3"))
        self.assertFalse(priority.is_higher("P4", "P4"))
        self.assertTrue(priority.pages_on_call("P1"))
        self.assertFalse(priority.pages_on_call("P2"))

    def test_priority_change_permissions(self):
        self.assertTrue(priority.can_change_priority("support_agent", "P3", "P1"))
        self.assertTrue(priority.can_change_priority("support_agent", "P2", "P4"))
        self.assertFalse(priority.can_change_priority("support_agent", "P1", "P2"))
        self.assertTrue(priority.can_change_priority("support_team_lead", "P1", "P2"))
        self.assertFalse(priority.can_change_priority("support_team_lead", "P2", "P2"))


class EscalationTests(unittest.TestCase):
    def test_p1_pages_on_call(self):
        decision = escalation.route("P1", MON_9, MON_9)
        self.assertEqual(decision.target, escalation.ON_CALL)
        self.assertIn("open_status_page_incident", decision.actions)
        self.assertEqual(escalation.incident_deadline(MON_9), datetime(2026, 11, 23, 9, 15))

    def test_p2_moves_to_tier_2_after_four_business_hours(self):
        self.assertEqual(escalation.route("P2", MON_9, datetime(2026, 11, 23, 12, 59)).target,
                         escalation.TIER_1)
        self.assertEqual(escalation.route("P2", MON_9, datetime(2026, 11, 23, 13, 0)).target,
                         escalation.TIER_2)

    def test_p3_moves_to_tier_2_after_one_business_day(self):
        self.assertEqual(escalation.route("P3", MON_9, datetime(2026, 11, 23, 17, 59)).target,
                         escalation.TIER_1)
        self.assertEqual(escalation.route("P3", MON_9, datetime(2026, 11, 24, 9, 0)).target,
                         escalation.TIER_2)
        self.assertEqual(escalation.tier_2_due("P3", MON_9), datetime(2026, 11, 24, 9, 0))

    def test_weekend_does_not_count(self):
        friday_16 = datetime(2026, 11, 27, 16, 0)
        self.assertEqual(escalation.route("P2", friday_16, datetime(2026, 11, 29, 16, 0)).target,
                         escalation.TIER_1)
        self.assertEqual(escalation.tier_2_due("P2", friday_16), datetime(2026, 11, 30, 10, 0))

    def test_p4_stays_in_tier_1(self):
        self.assertEqual(escalation.route("P4", MON_9, datetime(2026, 12, 23, 9, 0)).target,
                         escalation.TIER_1)
        self.assertIsNone(escalation.tier_2_due("P4", MON_9))

    def test_confirmed_bug_goes_to_owning_team(self):
        decision = escalation.route("P3", MON_9, MON_9, confirmed_bug=True, service="files")
        self.assertEqual(decision.target, escalation.ENGINEERING)
        self.assertIn("Storage Platform", decision.reason)
        self.assertIn("notify #team-storage", decision.actions)
        with self.assertRaises(ValueError):
            escalation.route("P3", MON_9, MON_9, confirmed_bug=True)

    def test_owning_team_table(self):
        self.assertEqual(escalation.owning_team("billing"),
                         ("Revenue Engineering", "#team-billing"))
        self.assertEqual(escalation.owning_team("audit-log"),
                         ("Trust and Compliance", "#team-trust"))
        self.assertEqual(len(escalation.OWNING_TEAMS), 12)
        with self.assertRaises(ValueError):
            escalation.owning_team("payroll")

    def test_escalation_paths(self):
        self.assertEqual(escalation.escalation_path("P1"), ["on_call_engineer", "engineering"])
        self.assertEqual(escalation.escalation_path("P2"), ["tier_1", "tier_2", "engineering"])
        self.assertEqual(escalation.escalation_path("P4"), ["tier_1"])

    def test_customer_requested_escalation(self):
        self.assertTrue(escalation.is_escalation_request(" Escalate. "))
        self.assertFalse(escalation.is_escalation_request("please do not escalate"))
        self.assertEqual(escalation.customer_escalation_review_due(datetime(2026, 11, 27, 17, 0)),
                         datetime(2026, 11, 30, 17, 0))

    def test_customer_escalation_channels_by_plan(self):
        self.assertEqual(escalation.customer_escalation_channels("pro"), ["ticket_reply"])
        self.assertEqual(escalation.customer_escalation_channels("business"),
                         ["ticket_reply", "phone"])
        self.assertEqual(escalation.customer_escalation_channels("enterprise"),
                         ["ticket_reply", "phone", "customer_success_manager"])


if __name__ == "__main__":
    unittest.main()
