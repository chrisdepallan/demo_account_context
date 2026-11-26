"""Tests for the install state machine, plan limits and sync rules."""

import unittest
from datetime import datetime, timedelta

from acme_integrations import FieldChange, Install, InstallError, InstallState, SyncCursor
from acme_integrations import installs, sync

T0 = datetime(2026, 11, 2, 9, 0, 0)


def make_install(n: int = 1, slug: str = "slack", state: InstallState = InstallState.ACTIVE) -> Install:
    return Install(
        integration_id=f"int_A{n:05d}", workspace_id="ws_4H8P2L", app_slug=slug, created_at=T0, state=state
    )


class InstallLimitTests(unittest.TestCase):
    def test_plan_limits(self):
        self.assertEqual(installs.install_limit("Free"), 2)
        self.assertEqual(installs.install_limit("starter"), 5)
        self.assertEqual(installs.install_limit("pro"), 20)
        self.assertEqual(installs.install_limit("business"), 50)
        self.assertIsNone(installs.install_limit("enterprise"))

    def test_unknown_plan_raises(self):
        with self.assertRaises(InstallError):
            installs.install_limit("platinum")

    def test_only_active_and_suspended_count(self):
        existing = [
            make_install(1, "slack", InstallState.ACTIVE),
            make_install(2, "github", InstallState.SUSPENDED),
            make_install(3, "jira", InstallState.PENDING),
            make_install(4, "google-workspace", InstallState.REVOKED),
        ]
        self.assertEqual(installs.counted_installs(existing), 2)

    def test_free_plan_blocks_third_install(self):
        existing = [make_install(1, "slack"), make_install(2, "github")]
        self.assertFalse(installs.can_install("free", existing, "jira"))
        self.assertTrue(installs.can_install("starter", existing, "jira"))

    def test_same_app_cannot_be_installed_twice(self):
        self.assertFalse(installs.can_install("pro", [make_install(1, "slack")], "slack"))
        revoked = [make_install(1, "slack", InstallState.REVOKED)]
        self.assertTrue(installs.can_install("pro", revoked, "slack"))

    def test_app_kinds_per_plan(self):
        self.assertFalse(installs.can_install("free", [], "partner-app", "partner"))
        self.assertTrue(installs.can_install("starter", [], "partner-app", "partner"))
        self.assertFalse(installs.can_install("pro", [], "internal-tool", "private"))
        self.assertTrue(installs.can_install("business", [], "internal-tool", "private"))

    def test_downgrade_needs_installs_removed(self):
        existing = [make_install(n, f"app-{n}") for n in range(8)]
        self.assertEqual(installs.installs_to_remove_for_plan("starter", existing), 3)
        self.assertEqual(installs.installs_to_remove_for_plan("enterprise", existing), 0)

    def test_only_owner_and_admin_manage_installs(self):
        self.assertTrue(installs.can_manage_installs("Owner"))
        self.assertTrue(installs.can_manage_installs("admin"))
        for role in ("billing admin", "member", "guest"):
            self.assertFalse(installs.can_manage_installs(role))


class InstallStateTests(unittest.TestCase):
    def test_pending_to_active(self):
        install = make_install(state=InstallState.PENDING)
        installs.transition(install, InstallState.ACTIVE, T0 + timedelta(minutes=2))
        self.assertIs(install.state, InstallState.ACTIVE)
        self.assertEqual(install.state_changed_at, T0 + timedelta(minutes=2))

    def test_revoked_is_final(self):
        install = make_install(state=InstallState.REVOKED)
        for target in InstallState:
            with self.assertRaises(InstallError):
                installs.transition(install, target, T0)

    def test_pending_cannot_be_suspended(self):
        with self.assertRaises(InstallError):
            installs.transition(make_install(state=InstallState.PENDING), InstallState.SUSPENDED, T0)

    def test_pending_expires_after_30_minutes(self):
        install = make_install(state=InstallState.PENDING)
        self.assertFalse(installs.is_pending_expired(install, T0 + timedelta(minutes=30)))
        self.assertTrue(installs.is_pending_expired(install, T0 + timedelta(minutes=31)))
        installs.expire_stale(install, T0 + timedelta(minutes=31))
        self.assertIs(install.state, InstallState.REVOKED)

    def test_five_failures_suspend(self):
        install = make_install()
        for _ in range(4):
            installs.record_failure(install, T0)
        self.assertIs(install.state, InstallState.ACTIVE)
        installs.record_failure(install, T0)
        self.assertIs(install.state, InstallState.SUSPENDED)
        self.assertEqual(install.suspended_reason, "sync_failures")

    def test_success_resets_failures_and_resume_clears_reason(self):
        install = make_install()
        installs.record_failure(install, T0)
        installs.record_success(install)
        self.assertEqual(install.consecutive_failures, 0)
        installs.transition(install, InstallState.SUSPENDED, T0, reason="paused_by_admin")
        installs.transition(install, InstallState.ACTIVE, T0)
        self.assertIsNone(install.suspended_reason)

    def test_suspended_auto_revoked_after_60_days_and_links_purged_30_days_later(self):
        install = make_install()
        installs.transition(install, InstallState.SUSPENDED, T0, reason="paused_by_admin")
        installs.expire_stale(install, T0 + timedelta(days=59))
        self.assertIs(install.state, InstallState.SUSPENDED)
        self.assertIsNone(installs.links_purge_at(install))
        revoked_at = T0 + timedelta(days=60)
        installs.expire_stale(install, revoked_at)
        self.assertIs(install.state, InstallState.REVOKED)
        self.assertEqual(installs.links_purge_at(install), revoked_at + timedelta(days=30))


class SyncTests(unittest.TestCase):
    def test_cursor_expires_after_7_days(self):
        cursor = SyncCursor("c1", T0)
        self.assertFalse(cursor.is_expired(T0 + timedelta(days=6, hours=23)))
        self.assertTrue(cursor.is_expired(T0 + timedelta(days=7)))

    def test_next_sync_mode(self):
        cursor = SyncCursor("c1", T0)
        now = T0 + timedelta(hours=1)
        self.assertEqual(sync.next_sync_mode(None, T0, now), "full")
        self.assertEqual(sync.next_sync_mode(cursor, T0, now), "incremental")
        self.assertEqual(sync.next_sync_mode(cursor, T0, T0 + timedelta(hours=24)), "full")
        self.assertEqual(sync.next_sync_mode(cursor, T0 + timedelta(days=7), T0 + timedelta(days=8)), "full")

    def test_incremental_runs_every_5_minutes(self):
        self.assertEqual(sync.next_scheduled_run(T0), T0 + timedelta(minutes=5))

    def test_manual_sync_cooldown(self):
        self.assertTrue(sync.can_manual_sync(None, T0))
        self.assertFalse(sync.can_manual_sync(T0, T0 + timedelta(minutes=6)))
        self.assertEqual(sync.manual_sync_retry_after(T0, T0 + timedelta(minutes=6)), 540)
        self.assertTrue(sync.can_manual_sync(T0, T0 + timedelta(minutes=15)))
        self.assertEqual(sync.manual_sync_retry_after(T0, T0 + timedelta(minutes=15)), 0)

    def test_retry_delays(self):
        minutes = [sync.retry_delay(a).total_seconds() / 60 for a in range(1, 6)]
        self.assertEqual(minutes, [1, 2, 4, 8, 16])
        self.assertIsNone(sync.retry_delay(6))
        with self.assertRaises(ValueError):
            sync.retry_delay(0)

    def test_page_count(self):
        self.assertEqual(sync.page_count(0), 0)
        self.assertEqual(sync.page_count(200), 1)
        self.assertEqual(sync.page_count(201), 2)

    def test_later_change_wins_outside_window(self):
        local = FieldChange("title", "Local", T0, "acme")
        remote = FieldChange("title", "Remote", T0 + timedelta(seconds=61), "remote")
        self.assertEqual(sync.resolve_conflict(local, remote).value, "Remote")

    def test_source_of_truth_wins_inside_window(self):
        local = FieldChange("title", "Local", T0, "acme")
        remote = FieldChange("title", "Remote", T0 + timedelta(seconds=60), "remote")
        self.assertEqual(sync.resolve_conflict(local, remote).value, "Local")
        self.assertEqual(sync.resolve_conflict(local, remote, "remote").value, "Remote")

    def test_merge_keeps_changes_to_different_fields(self):
        local = {"title": FieldChange("title", "New title", T0, "acme")}
        remote = {
            "status": FieldChange("status", "Done", T0, "remote"),
            "title": FieldChange("title", "Old", T0 - timedelta(hours=1), "remote"),
        }
        merged = sync.merge_changes(local, remote)
        self.assertEqual(merged["title"].value, "New title")
        self.assertEqual(merged["status"].value, "Done")

    def test_deletes_unlink_and_bad_origin_rejected(self):
        self.assertEqual(sync.resolve_delete("remote"), "unlink")
        self.assertEqual(sync.resolve_delete("acme"), "unlink")
        with self.assertRaises(ValueError):
            FieldChange("title", "x", T0, "elsewhere")


if __name__ == "__main__":
    unittest.main()
