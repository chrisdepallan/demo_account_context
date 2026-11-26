"""Tests for storage quotas and upload checks."""

import unittest

from acme_files import quotas
from acme_files.quotas import GB, MB, TB, check_upload, quota_bytes, usage_state


class QuotaTests(unittest.TestCase):
    def test_free_is_two_gb_total(self):
        self.assertEqual(quota_bytes("free"), 2 * GB)
        self.assertEqual(quota_bytes("free", seats=3), 2 * GB)

    def test_paid_plans_are_per_seat(self):
        self.assertEqual(quota_bytes("starter", seats=10), 100 * GB)
        self.assertEqual(quota_bytes("pro", seats=8), 400 * GB)
        self.assertEqual(quota_bytes("business", seats=2), 400 * GB)
        self.assertEqual(quota_bytes("enterprise", seats=50), 50 * TB)

    def test_storage_packs_add_100_gb_each(self):
        self.assertEqual(quota_bytes("starter", seats=1, storage_packs=2), 210 * GB)
        with self.assertRaises(ValueError):
            quota_bytes("free", storage_packs=1)
        with self.assertRaises(ValueError):
            quota_bytes("pro", storage_packs=51)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            quota_bytes("platinum")
        with self.assertRaises(ValueError):
            quota_bytes("pro", seats=0)

    def test_usage_states(self):
        quota = 100 * GB
        self.assertEqual(usage_state(89 * GB, quota), "ok")
        self.assertEqual(usage_state(90 * GB, quota), "warning")
        self.assertEqual(usage_state(100 * GB - 1, quota), "warning")
        self.assertEqual(usage_state(100 * GB, quota), "blocked")
        self.assertEqual(quotas.percent_used(45 * GB, quota), 45.0)

    def test_max_file_size_per_plan(self):
        self.assertEqual(quotas.max_file_bytes("free"), 250 * MB)
        self.assertEqual(quotas.max_file_bytes("starter"), 250 * MB)
        for plan in ("pro", "business", "enterprise"):
            self.assertEqual(quotas.max_file_bytes(plan), 5 * GB)


class UploadCheckTests(unittest.TestCase):
    def test_small_upload_allowed_in_single_request(self):
        decision = check_upload("starter", "member", "notes.txt", 10 * MB, 0)
        self.assertTrue(decision.allowed)
        self.assertIsNone(decision.error)
        self.assertFalse(decision.resumable)

    def test_large_upload_is_resumable(self):
        at_limit = check_upload("pro", "member", "video.mp4", 100 * MB, 0)
        self.assertFalse(at_limit.resumable)
        over = check_upload("pro", "member", "video.mp4", 100 * MB + 1, 0)
        self.assertTrue(over.allowed)
        self.assertTrue(over.resumable)

    def test_file_too_large(self):
        self.assertTrue(check_upload("starter", "admin", "a.zip", 250 * MB, 0).allowed)
        decision = check_upload("starter", "admin", "a.zip", 250 * MB + 1, 0)
        self.assertEqual(decision.error, "file_too_large")
        self.assertEqual(
            check_upload("enterprise", "owner", "a.zip", 5 * GB + 1, 0).error,
            "file_too_large")

    def test_quota_exceeded(self):
        used = 2 * GB - 5 * MB
        self.assertTrue(check_upload("free", "member", "a.pdf", 5 * MB, used).allowed)
        decision = check_upload("free", "member", "a.pdf", 6 * MB, used)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.error, "quota_exceeded")

    def test_storage_pack_lifts_block(self):
        used = 10 * GB
        self.assertEqual(
            check_upload("starter", "member", "a.pdf", MB, used).error, "quota_exceeded")
        self.assertTrue(
            check_upload("starter", "member", "a.pdf", MB, used, storage_packs=1).allowed)

    def test_guests_and_billing_admins_cannot_upload(self):
        for role in ("guest", "billing_admin"):
            self.assertEqual(
                check_upload("pro", role, "a.pdf", MB, 0).error, "forbidden")

    def test_read_only_account_cannot_upload(self):
        decision = check_upload("pro", "owner", "a.pdf", MB, 0, account_state="read_only")
        self.assertEqual(decision.error, "forbidden")

    def test_blocked_file_types(self):
        self.assertEqual(
            check_upload("pro", "member", "Setup.EXE", MB, 0).error, "file_type_blocked")
        self.assertTrue(quotas.is_blocked_file_type("run.bat"))
        self.assertFalse(quotas.is_blocked_file_type("report.exe.pdf"))

    def test_downgrade_blocked_when_over_new_quota(self):
        self.assertFalse(quotas.can_downgrade(60 * GB, "starter", new_seats=5))
        self.assertTrue(quotas.can_downgrade(50 * GB, "starter", new_seats=5))
        self.assertFalse(quotas.can_downgrade(3 * GB, "free"))


if __name__ == "__main__":
    unittest.main()
