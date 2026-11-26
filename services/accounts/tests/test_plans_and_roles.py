"""Tests for plan limits and the role permission matrix."""

import unittest
from datetime import datetime, timedelta

from acme_accounts import Action, Role, plans, roles

T0 = datetime(2026, 11, 1, 12, 0, 0)


class PlanLimitTests(unittest.TestCase):
    def test_member_limits(self):
        expected = {"free": 3, "starter": 10, "pro": 100, "business": 500, "enterprise": None}
        self.assertEqual({name: p.max_members for name, p in plans.PLANS.items()}, expected)

    def test_cannot_exceed_member_limit(self):
        starter = plans.get_plan("Starter")
        self.assertTrue(plans.can_add_members(starter, 9))
        self.assertFalse(plans.can_add_members(starter, 9, to_add=2))
        self.assertTrue(plans.can_add_members(plans.get_plan("enterprise"), 100000))

    def test_workspace_limits(self):
        self.assertFalse(plans.can_create_workspace(plans.get_plan("starter"), 1))
        self.assertTrue(plans.can_create_workspace(plans.get_plan("pro"), 2))
        self.assertFalse(plans.can_create_workspace(plans.get_plan("pro"), 3))
        self.assertTrue(plans.can_create_workspace(plans.get_plan("enterprise"), 250))

    def test_regions_per_plan(self):
        self.assertFalse(plans.region_allowed(plans.get_plan("pro"), "eu-central"))
        self.assertTrue(plans.region_allowed(plans.get_plan("business"), "eu-central"))
        self.assertFalse(plans.region_allowed(plans.get_plan("business"), "ap-south"))
        self.assertTrue(plans.region_allowed(plans.get_plan("enterprise"), "ap-south"))

    def test_guest_allowance(self):
        self.assertEqual(plans.max_guests(plans.get_plan("pro"), 10), 50)
        self.assertEqual(plans.max_guests(plans.get_plan("free"), 3), 0)

    def test_storage_limit(self):
        self.assertEqual(plans.storage_limit_gb(plans.get_plan("free"), 3), 2)
        self.assertEqual(plans.storage_limit_gb(plans.get_plan("pro"), 4), 200)
        self.assertEqual(plans.storage_limit_gb(plans.get_plan("starter"), 2, storage_packs=1), 120)

    def test_storage_status_thresholds(self):
        self.assertEqual(plans.storage_status(89.9, 100), "ok")
        self.assertEqual(plans.storage_status(90, 100), "warning")
        self.assertEqual(plans.storage_status(100, 100), "blocked")

    def test_upload_size(self):
        self.assertFalse(plans.upload_allowed(plans.get_plan("starter"), 251))
        self.assertTrue(plans.upload_allowed(plans.get_plan("pro"), 5120))

    def test_downgrade_blocked_by_usage(self):
        blockers = plans.downgrade_blockers(
            plans.get_plan("starter"), members=12, workspaces=3, used_storage_gb=50, seats=12
        )
        self.assertEqual(len(blockers), 2)
        self.assertEqual(
            plans.downgrade_blockers(plans.get_plan("starter"), 8, 1, 50, 8), []
        )

    def test_trial_end_converts_extra_members(self):
        self.assertEqual(plans.members_converted_to_guests(7), 4)
        self.assertEqual(plans.members_converted_to_guests(2), 0)

    def test_upgrade_direction(self):
        self.assertTrue(plans.is_upgrade(plans.get_plan("starter"), plans.get_plan("pro")))
        self.assertFalse(plans.is_upgrade(plans.get_plan("business"), plans.get_plan("pro")))


class RoleTests(unittest.TestCase):
    def test_only_owner_closes_account(self):
        allowed = [r for r in Role if roles.can(r, Action.CLOSE_ACCOUNT)]
        self.assertEqual(allowed, [Role.OWNER])

    def test_admin_cannot_touch_billing(self):
        self.assertFalse(roles.can(Role.ADMIN, Action.VIEW_AND_PAY_INVOICES))
        self.assertTrue(roles.can(Role.BILLING_ADMIN, Action.CHANGE_PLAN_OR_PAYMENT_METHOD))

    def test_guest_can_only_comment(self):
        self.assertEqual(roles.allowed_actions(Role.GUEST), frozenset({Action.COMMENT}))

    def test_billing_admin_cannot_edit_or_comment(self):
        self.assertFalse(roles.can(Role.BILLING_ADMIN, Action.EDIT_PROJECTS))
        self.assertFalse(roles.can(Role.BILLING_ADMIN, Action.COMMENT))

    def test_guests_do_not_use_seats(self):
        people = [Role.OWNER, Role.ADMIN, Role.MEMBER, Role.GUEST, Role.GUEST]
        self.assertEqual(roles.seats_needed(people), 3)

    def test_invite_batch_limit(self):
        batch = [f"user{i}@customer.example" for i in range(50)]
        self.assertEqual(len(roles.validate_invite_batch(batch)), 50)
        with self.assertRaises(ValueError):
            roles.validate_invite_batch(batch + ["extra@customer.example"])
        with self.assertRaises(ValueError):
            roles.validate_invite_batch(["not-an-email"])

    def test_invite_permissions(self):
        self.assertTrue(roles.can_invite_as(Role.ADMIN, Role.MEMBER))
        self.assertFalse(roles.can_invite_as(Role.MEMBER, Role.GUEST))
        self.assertFalse(roles.can_invite_as(Role.OWNER, Role.OWNER))

    def test_invitation_expires_after_7_days(self):
        self.assertFalse(roles.invitation_expired(T0, T0 + timedelta(days=6, hours=23)))
        self.assertTrue(roles.invitation_expired(T0, T0 + timedelta(days=7)))

    def test_ownership_transfer(self):
        result = roles.transfer_ownership(Role.OWNER, Role.ADMIN)
        self.assertEqual(result, {"previous_owner": Role.ADMIN, "new_owner": Role.OWNER})
        with self.assertRaises(PermissionError):
            roles.transfer_ownership(Role.ADMIN, Role.ADMIN)
        with self.assertRaises(ValueError):
            roles.transfer_ownership(Role.OWNER, Role.MEMBER)


if __name__ == "__main__":
    unittest.main()
