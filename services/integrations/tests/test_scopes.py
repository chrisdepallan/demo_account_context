"""Tests for the scope catalog and least-privilege checks."""

import unittest

from acme_integrations import ScopeError, scopes


class ValidateScopesTests(unittest.TestCase):
    def test_valid_scopes_are_sorted_and_deduplicated(self):
        result = scopes.validate_scopes(["projects:write", "projects:read", "projects:read"])
        self.assertEqual(result, ["projects:read", "projects:write"])

    def test_scope_names_are_normalised(self):
        self.assertEqual(scopes.validate_scopes([" Files:Read "]), ["files:read"])

    def test_empty_request_is_rejected(self):
        with self.assertRaises(ScopeError):
            scopes.validate_scopes([])

    def test_unknown_scope_is_rejected(self):
        with self.assertRaises(ScopeError):
            scopes.validate_scopes(["tasks:delete"])

    def test_billing_read_is_never_grantable(self):
        with self.assertRaises(ScopeError):
            scopes.validate_scopes(["projects:read", "billing:read"])

    def test_all_six_grantable_scopes_are_accepted(self):
        grantable = [name for name, s in scopes.SCOPE_CATALOG.items() if s.grantable]
        self.assertEqual(len(grantable), scopes.MAX_SCOPES_PER_INSTALL)
        self.assertEqual(len(scopes.validate_scopes(grantable)), 6)

    def test_catalog_has_seven_scopes(self):
        self.assertEqual(len(scopes.SCOPE_CATALOG), 7)
        self.assertEqual(scopes.SCOPE_CATALOG["files:write"].resource, "files")
        self.assertEqual(scopes.SCOPE_CATALOG["files:write"].access, "write")


class LeastPrivilegeTests(unittest.TestCase):
    def test_write_implies_read(self):
        self.assertEqual(
            scopes.expand_implied(["files:write"]), {"files:read", "files:write"}
        )
        self.assertTrue(scopes.has_scope(["projects:write"], "projects:read"))

    def test_read_does_not_imply_write(self):
        self.assertFalse(scopes.has_scope(["projects:read"], "projects:write"))

    def test_excess_scopes_are_reported(self):
        excess = scopes.excess_scopes(
            ["projects:read", "members:read", "files:write"], ["projects:write"]
        )
        self.assertEqual(excess, ["files:write", "members:read"])

    def test_least_privilege_passes_for_first_party_defaults(self):
        for slug, needed in scopes.FIRST_PARTY_SCOPES.items():
            with self.subTest(app=slug):
                self.assertTrue(scopes.is_least_privilege(needed, needed))
                scopes.validate_scopes(needed)

    def test_github_asking_for_members_is_not_least_privilege(self):
        requested = set(scopes.FIRST_PARTY_SCOPES["github"]) | {"members:read"}
        self.assertFalse(scopes.is_least_privilege(requested, scopes.FIRST_PARTY_SCOPES["github"]))


class ApprovalTests(unittest.TestCase):
    def test_members_write_requires_owner(self):
        self.assertTrue(scopes.requires_owner_approval(["members:write"]))
        self.assertTrue(scopes.can_approve("Owner", ["members:write"]))
        self.assertFalse(scopes.can_approve("Admin", ["members:write"]))

    def test_admin_can_approve_unrestricted_scopes(self):
        self.assertTrue(scopes.can_approve("admin", ["projects:write", "members:read"]))

    def test_other_roles_cannot_approve(self):
        for role in ("billing admin", "member", "guest"):
            with self.subTest(role=role):
                self.assertFalse(scopes.can_approve(role, ["projects:read"]))

    def test_adding_a_scope_needs_reconsent(self):
        self.assertTrue(scopes.needs_reconsent(["projects:read"], ["projects:read", "files:read"]))

    def test_removing_or_implied_scopes_need_no_reconsent(self):
        self.assertFalse(scopes.needs_reconsent(["projects:read", "files:read"], ["projects:read"]))
        self.assertFalse(scopes.needs_reconsent(["projects:write"], ["projects:read"]))


if __name__ == "__main__":
    unittest.main()
