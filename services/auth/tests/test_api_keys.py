"""Tests for API key rules. Key values here are obviously fake placeholders."""

import unittest
from datetime import datetime, timedelta

from acme_auth import api_keys

T0 = datetime(2026, 11, 1, 12, 0, 0)
FAKE_TEST_KEY = "acme_test_EXAMPLEKEY000"
FAKE_LIVE_KEY = "acme_live_EXAMPLEKEY000"


class KeyFormatTests(unittest.TestCase):
    def test_known_prefixes_are_valid(self):
        self.assertTrue(api_keys.is_valid_key_format(FAKE_TEST_KEY))
        self.assertTrue(api_keys.is_valid_key_format(FAKE_LIVE_KEY))

    def test_unknown_prefix_or_bad_body_is_invalid(self):
        self.assertFalse(api_keys.is_valid_key_format("acme_prod_EXAMPLEKEY000"))
        self.assertFalse(api_keys.is_valid_key_format("acme_test_"))
        self.assertFalse(api_keys.is_valid_key_format("acme_test_EXAMPLE KEY 000"))

    def test_environment_from_prefix(self):
        self.assertEqual(api_keys.environment_for(FAKE_LIVE_KEY), "production")
        self.assertEqual(api_keys.environment_for(FAKE_TEST_KEY), "sandbox")
        with self.assertRaises(ValueError):
            api_keys.environment_for("EXAMPLEKEY000")

    def test_mask_hides_everything_after_prefix(self):
        self.assertEqual(api_keys.mask_key(FAKE_TEST_KEY), "acme_test_****")


class KeyLimitTests(unittest.TestCase):
    def test_free_plan_cannot_use_api(self):
        self.assertEqual(api_keys.max_keys_for_plan("free"), 0)
        self.assertFalse(api_keys.can_create_key("free", "owner", 0))

    def test_25_active_keys_per_workspace(self):
        for plan in ("starter", "pro", "business", "enterprise"):
            self.assertEqual(api_keys.max_keys_for_plan(plan), 25)
        self.assertTrue(api_keys.can_create_key("pro", "admin", 24))
        self.assertFalse(api_keys.can_create_key("pro", "admin", 25))

    def test_only_owner_and_admin_create_keys(self):
        self.assertTrue(api_keys.can_create_key("starter", "owner", 0))
        for role in ("billing_admin", "member", "guest"):
            self.assertFalse(api_keys.can_create_key("starter", role, 0))


class ScopeTests(unittest.TestCase):
    def test_scopes_are_sorted_and_deduplicated(self):
        scopes = api_keys.validate_scopes(["files:read", "projects:read", "files:read"], "admin")
        self.assertEqual(scopes, ["files:read", "projects:read"])

    def test_unknown_or_empty_scopes_rejected(self):
        with self.assertRaises(ValueError):
            api_keys.validate_scopes(["projects:delete"], "owner")
        with self.assertRaises(ValueError):
            api_keys.validate_scopes([], "owner")

    def test_billing_read_is_restricted(self):
        self.assertEqual(api_keys.validate_scopes(["billing:read"], "owner"), ["billing:read"])
        with self.assertRaises(ValueError):
            api_keys.validate_scopes(["billing:read"], "admin")

    def test_scopes_match_exactly(self):
        self.assertTrue(api_keys.has_scope(["files:read", "files:write"], "files:write"))
        self.assertFalse(api_keys.has_scope(["files:write"], "files:read"))
        self.assertFalse(api_keys.has_scope(["files:read"], "projects:read"))


class ExpiryTests(unittest.TestCase):
    def test_allowed_expiry_choices(self):
        for days in (30, 90, 180, 365, None):
            self.assertEqual(api_keys.validate_expiry(days), days)
        with self.assertRaises(ValueError):
            api_keys.validate_expiry(60)

    def test_never_refused_when_expiry_required(self):
        with self.assertRaises(ValueError):
            api_keys.validate_expiry(None, require_expiry=True)
        self.assertEqual(api_keys.validate_expiry(90, require_expiry=True), 90)

    def test_expiry_time(self):
        expiry = api_keys.expires_at(T0, 90)
        self.assertEqual(expiry, T0 + timedelta(days=90))
        self.assertFalse(api_keys.is_expired(expiry, T0 + timedelta(days=89)))
        self.assertTrue(api_keys.is_expired(expiry, T0 + timedelta(days=90)))
        self.assertFalse(api_keys.is_expired(api_keys.expires_at(T0, None), T0 + timedelta(days=9999)))

    def test_owner_warned_14_days_before_expiry(self):
        expiry = api_keys.expires_at(T0, 30)
        self.assertFalse(api_keys.expiry_warning_due(expiry, T0 + timedelta(days=15)))
        self.assertTrue(api_keys.expiry_warning_due(expiry, T0 + timedelta(days=16)))
        self.assertFalse(api_keys.expiry_warning_due(expiry, T0 + timedelta(days=30)))

    def test_rotated_key_works_for_24_hours(self):
        self.assertTrue(api_keys.old_key_usable_after_rotation(T0, T0 + timedelta(hours=23)))
        self.assertFalse(api_keys.old_key_usable_after_rotation(T0, T0 + timedelta(hours=24)))


if __name__ == "__main__":
    unittest.main()
