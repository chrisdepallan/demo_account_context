"""Tests for version retention, trash expiry and share link rules."""

import unittest
from datetime import datetime, timedelta, timezone

from acme_files import share_links, versioning
from acme_files.share_links import ShareLinkError, create_link
from acme_files.versioning import FileVersion

NOW = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)


def days_ago(days: float) -> datetime:
    return NOW - timedelta(days=days)


class VersioningTests(unittest.TestCase):
    def test_retention_days_per_plan(self):
        self.assertEqual(versioning.retention_days("free"), 7)
        self.assertEqual(versioning.retention_days("starter"), 30)
        self.assertEqual(versioning.retention_days("pro"), 180)
        self.assertEqual(versioning.retention_days("business"), 365)
        self.assertIsNone(versioning.retention_days("enterprise"))
        with self.assertRaises(ValueError):
            versioning.retention_days("platinum")

    def test_old_version_expires_by_plan(self):
        old = FileVersion(1, 100, days_ago(60), replaced_at=days_ago(31))
        self.assertTrue(versioning.is_version_expired(old, "starter", NOW))
        self.assertFalse(versioning.is_version_expired(old, "pro", NOW))
        self.assertFalse(versioning.is_version_expired(old, "enterprise", NOW))

    def test_current_version_never_expires(self):
        current = FileVersion(1, 100, days_ago(4000))
        self.assertTrue(current.is_current)
        self.assertFalse(versioning.is_version_expired(current, "free", NOW))

    def test_prune_by_age(self):
        versions = [
            FileVersion(1, 10, days_ago(20), replaced_at=days_ago(10)),
            FileVersion(2, 10, days_ago(10), replaced_at=days_ago(3)),
            FileVersion(3, 10, days_ago(3)),
        ]
        pruned = versioning.versions_to_prune(versions, "free", NOW)
        self.assertEqual([v.number for v in pruned], [1])

    def test_prune_over_100_versions(self):
        versions = [FileVersion(n, 1, days_ago(1), replaced_at=days_ago(1))
                    for n in range(1, 103)]
        versions.append(FileVersion(103, 1, NOW))
        pruned = versioning.versions_to_prune(versions, "enterprise", NOW)
        self.assertEqual([v.number for v in pruned], [1, 2, 3])

    def test_add_version_and_stored_bytes(self):
        versions = versioning.add_version([], 100, days_ago(2))
        versions = versioning.add_version(versions, 100, days_ago(1))
        versions = versioning.add_version(versions, 100, NOW)
        self.assertEqual([v.number for v in versions], [1, 2, 3])
        self.assertEqual([v.is_current for v in versions], [False, False, True])
        self.assertEqual(versions[0].replaced_at, days_ago(1))
        self.assertEqual(versioning.stored_bytes(versions), 300)

    def test_trash_is_30_days(self):
        trashed = days_ago(29)
        self.assertTrue(versioning.is_restorable(trashed, NOW))
        self.assertEqual(versioning.days_left_in_trash(trashed, NOW), 1)
        self.assertFalse(versioning.is_restorable(days_ago(30), NOW))
        self.assertEqual(versioning.days_left_in_trash(days_ago(45), NOW), 0)
        self.assertEqual(versioning.trash_purge_at(NOW), NOW + timedelta(days=30))

    def test_who_can_restore_from_trash(self):
        self.assertTrue(versioning.can_restore_from_trash("admin", False))
        self.assertTrue(versioning.can_restore_from_trash("member", True))
        self.assertFalse(versioning.can_restore_from_trash("member", False))
        self.assertFalse(versioning.can_restore_from_trash("guest", True))


class ShareLinkTests(unittest.TestCase):
    def test_default_expiry_for_public_links(self):
        free = create_link("free", "member", "anyone", "view", NOW)
        self.assertEqual(free.expires_at, NOW + timedelta(days=7))
        pro = create_link("pro", "member", "anyone", "view", NOW)
        self.assertEqual(pro.expires_at, NOW + timedelta(days=30))

    def test_workspace_links_do_not_expire_by_default(self):
        link = create_link("free", "member", "workspace", "edit", NOW)
        self.assertIsNone(link.expires_at)
        self.assertTrue(share_links.is_active(link, NOW + timedelta(days=1000)))

    def test_longest_expiry_per_plan(self):
        with self.assertRaises(ShareLinkError):
            create_link("free", "member", "anyone", "view", NOW, expires_in_days=8)
        with self.assertRaises(ShareLinkError):
            create_link("starter", "member", "anyone", "view", NOW, expires_in_days=31)
        create_link("pro", "member", "anyone", "view", NOW, expires_in_days=365)
        with self.assertRaises(ShareLinkError):
            create_link("pro", "member", "anyone", "view", NOW, expires_in_days=None)
        never = create_link("business", "member", "anyone", "view", NOW,
                            expires_in_days=None)
        self.assertIsNone(never.expires_at)

    def test_public_access_levels_per_plan(self):
        with self.assertRaises(ShareLinkError):
            create_link("free", "member", "anyone", "comment", NOW)
        create_link("starter", "member", "anyone", "comment", NOW)
        with self.assertRaises(ShareLinkError) as ctx:
            create_link("starter", "member", "anyone", "edit", NOW, password="longenough")
        self.assertEqual(ctx.exception.code, "share_link_not_allowed")

    def test_public_edit_link_needs_password(self):
        with self.assertRaises(ShareLinkError):
            create_link("pro", "member", "anyone", "edit", NOW)
        link = create_link("pro", "member", "anyone", "edit", NOW, password="longenough")
        self.assertTrue(link.password_protected)

    def test_password_policy_and_rules(self):
        with self.assertRaises(ShareLinkError):
            create_link("business", "admin", "anyone", "view", NOW,
                        require_password_policy=True)
        with self.assertRaises(ShareLinkError):
            create_link("pro", "member", "anyone", "view", NOW, password="short")
        with self.assertRaises(ShareLinkError):
            create_link("free", "member", "anyone", "view", NOW, password="longenough")
        self.assertFalse(share_links.password_required("workspace", "edit", True))

    def test_who_can_create_links(self):
        for role in ("guest", "billing_admin"):
            with self.assertRaises(ShareLinkError):
                create_link("pro", role, "workspace", "view", NOW)
        with self.assertRaises(ShareLinkError):
            create_link("pro", "member", "workspace", "view", NOW, existing_links=50)

    def test_public_links_can_be_turned_off(self):
        with self.assertRaises(ShareLinkError):
            create_link("pro", "owner", "anyone", "view", NOW, public_links_enabled=False)
        create_link("pro", "owner", "invited", "view", NOW, public_links_enabled=False)

    def test_link_stops_working(self):
        link = create_link("starter", "member", "anyone", "view", NOW)
        self.assertTrue(share_links.is_active(link, NOW + timedelta(days=29)))
        self.assertFalse(share_links.is_active(link, NOW + timedelta(days=30)))
        self.assertFalse(share_links.is_active(link, NOW, file_trashed=True))
        link.revoked = True
        self.assertFalse(share_links.is_active(link, NOW))

    def test_lock_after_five_wrong_passwords(self):
        link = create_link("pro", "member", "anyone", "view", NOW, password="longenough")
        for _ in range(4):
            self.assertFalse(share_links.record_password_attempt(link, False, NOW))
        self.assertFalse(share_links.is_locked(link, NOW))
        share_links.record_password_attempt(link, False, NOW)
        self.assertTrue(share_links.is_locked(link, NOW + timedelta(minutes=14)))
        self.assertFalse(share_links.record_password_attempt(
            link, True, NOW + timedelta(minutes=14)))
        self.assertTrue(share_links.record_password_attempt(
            link, True, NOW + timedelta(minutes=15)))

    def test_guests_capped_at_comment(self):
        self.assertEqual(share_links.effective_access("edit", "guest"), "comment")
        self.assertEqual(share_links.effective_access("edit", "member"), "edit")
        self.assertEqual(share_links.effective_access("view", "guest"), "view")


if __name__ == "__main__":
    unittest.main()
