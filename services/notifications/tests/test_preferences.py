"""Tests for channel preference resolution and role eligibility."""

import unittest

from acme_notifications import (
    CHANNELS,
    MANDATORY_TYPES,
    NOTIFICATION_TYPES,
    SYSTEM_DEFAULTS,
    is_eligible,
    is_mandatory,
    resolve_channels,
    validate_preferences,
)
from acme_notifications.preferences import resolve_setting


class CatalogTests(unittest.TestCase):
    def test_there_are_eleven_types_and_three_channels(self):
        self.assertEqual(len(NOTIFICATION_TYPES), 11)
        self.assertEqual(CHANNELS, ("email", "in_app", "push"))

    def test_mandatory_types(self):
        self.assertEqual(
            MANDATORY_TYPES, {"security_alert", "billing_alert", "account_notice"}
        )
        self.assertTrue(is_mandatory("security_alert"))
        self.assertFalse(is_mandatory("mention"))

    def test_in_app_is_on_by_default_for_every_type(self):
        for name in NOTIFICATION_TYPES:
            self.assertTrue(SYSTEM_DEFAULTS[name]["in_app"], name)


class ResolutionTests(unittest.TestCase):
    def test_system_defaults_apply_without_overrides(self):
        self.assertEqual(resolve_channels("mention"), {"email", "in_app", "push"})
        self.assertEqual(resolve_channels("task_completed"), {"in_app"})
        self.assertEqual(resolve_channels("file_shared"), {"email", "in_app"})

    def test_workspace_default_overrides_system_default(self):
        workspace = {"task_completed": {"email": True}}
        self.assertEqual(
            resolve_channels("task_completed", None, workspace), {"email", "in_app"}
        )

    def test_user_setting_overrides_workspace_default(self):
        workspace = {"mention": {"email": False, "push": False}}
        user = {"mention": {"email": True}}
        self.assertEqual(resolve_channels("mention", user, workspace), {"email", "in_app"})

    def test_user_can_turn_off_in_app_for_optional_type(self):
        user = {"comment_added": {"in_app": False}}
        self.assertEqual(resolve_channels("comment_added", user), set())

    def test_mandatory_email_and_in_app_cannot_be_disabled(self):
        user = {"security_alert": {"email": False, "in_app": False, "push": False}}
        self.assertEqual(resolve_channels("security_alert", user), {"email", "in_app"})
        self.assertTrue(resolve_setting("billing_alert", "email", user, user))

    def test_push_dropped_without_registered_device(self):
        self.assertEqual(
            resolve_channels("task_assigned", has_push_device=False), {"email", "in_app"}
        )

    def test_hard_bounce_suppresses_all_email(self):
        self.assertNotIn("email", resolve_channels("mention", email_suppression="hard_bounce"))
        self.assertNotIn(
            "email", resolve_channels("security_alert", email_suppression="hard_bounce")
        )

    def test_complaint_still_allows_mandatory_email(self):
        self.assertNotIn("email", resolve_channels("mention", email_suppression="complaint"))
        self.assertIn("email", resolve_channels("security_alert", email_suppression="complaint"))

    def test_unknown_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            resolve_channels("not_a_type")
        with self.assertRaises(ValueError):
            resolve_channels("mention", email_suppression="unknown")
        with self.assertRaises(ValueError):
            resolve_setting("mention", "sms")


class RoleTests(unittest.TestCase):
    def test_owner_receives_every_type(self):
        for name in NOTIFICATION_TYPES:
            self.assertTrue(is_eligible(name, "owner"), name)

    def test_billing_alert_goes_to_owner_and_billing_admin_only(self):
        allowed = {r for r in ("owner", "admin", "billing_admin", "member", "guest")
                   if is_eligible("billing_alert", r)}
        self.assertEqual(allowed, {"owner", "billing_admin"})

    def test_guest_types(self):
        guest = {name for name in NOTIFICATION_TYPES if is_eligible(name, "guest")}
        self.assertEqual(
            guest,
            {"mention", "comment_added", "file_shared", "security_alert", "account_notice"},
        )

    def test_ineligible_role_gets_no_channels(self):
        self.assertEqual(resolve_channels("storage_warning", role="member"), set())
        self.assertEqual(resolve_channels("storage_warning", role="admin"), {"email", "in_app"})

    def test_unknown_role_is_rejected(self):
        with self.assertRaises(ValueError):
            is_eligible("mention", "superuser")


class ValidationTests(unittest.TestCase):
    def test_valid_preferences_pass(self):
        validate_preferences({"mention": {"email": False}, "security_alert": {"push": False}})

    def test_invalid_preferences_are_rejected(self):
        bad = [
            {"not_a_type": {"email": True}},
            {"mention": {"sms": True}},
            {"mention": {"email": "yes"}},
            {"billing_alert": {"email": False}},
            {"account_notice": {"in_app": False}},
        ]
        for prefs in bad:
            with self.assertRaises(ValueError, msg=str(prefs)):
                validate_preferences(prefs)


if __name__ == "__main__":
    unittest.main()
