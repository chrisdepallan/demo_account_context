"""Tests for the account state machine and retention windows."""

import unittest
from datetime import datetime, timedelta

from acme_accounts import AccountState, InvalidTransition, lifecycle

T0 = datetime(2026, 11, 1, 12, 0, 0)


class TransitionTests(unittest.TestCase):
    def test_trial_can_become_active_or_closed(self):
        self.assertTrue(lifecycle.can_transition(AccountState.TRIALING, AccountState.ACTIVE))
        self.assertTrue(lifecycle.can_transition(AccountState.TRIALING, AccountState.CLOSED))

    def test_active_cannot_skip_to_read_only(self):
        self.assertFalse(lifecycle.can_transition(AccountState.ACTIVE, AccountState.READ_ONLY))

    def test_past_due_paths(self):
        for target in (AccountState.ACTIVE, AccountState.READ_ONLY, AccountState.CLOSED):
            self.assertEqual(lifecycle.transition(AccountState.PAST_DUE, target), target)

    def test_deleted_is_terminal(self):
        for target in AccountState:
            self.assertFalse(lifecycle.can_transition(AccountState.DELETED, target))

    def test_illegal_transition_raises(self):
        with self.assertRaises(InvalidTransition):
            lifecycle.transition(AccountState.ACTIVE, AccountState.DELETED)

    def test_nothing_returns_to_trialing(self):
        for state in AccountState:
            self.assertFalse(lifecycle.can_transition(state, AccountState.TRIALING))


class AccessTests(unittest.TestCase):
    def test_login_allowed_until_closed(self):
        allowed = {s for s in AccountState if lifecycle.can_log_in(s)}
        self.assertEqual(
            allowed,
            {AccountState.TRIALING, AccountState.ACTIVE, AccountState.PAST_DUE, AccountState.READ_ONLY},
        )

    def test_read_only_cannot_edit(self):
        self.assertFalse(lifecycle.can_edit(AccountState.READ_ONLY))
        self.assertTrue(lifecycle.can_edit(AccountState.PAST_DUE))


class WindowTests(unittest.TestCase):
    def test_trial_lasts_14_days(self):
        self.assertEqual(lifecycle.trial_end(T0), T0 + timedelta(days=14))

    def test_plan_after_trial(self):
        self.assertEqual(lifecycle.plan_after_trial(True), "pro")
        self.assertEqual(lifecycle.plan_after_trial(False), "free")

    def test_grace_period_then_read_only(self):
        self.assertEqual(lifecycle.state_while_unpaid(T0, T0 + timedelta(days=13)), AccountState.PAST_DUE)
        self.assertEqual(lifecycle.state_while_unpaid(T0, T0 + timedelta(days=14)), AccountState.READ_ONLY)

    def test_deleted_after_30_days(self):
        self.assertEqual(lifecycle.state_after_closing(T0, T0 + timedelta(days=29)), AccountState.CLOSED)
        self.assertEqual(lifecycle.state_after_closing(T0, T0 + timedelta(days=30)), AccountState.DELETED)

    def test_backups_purged_within_65_days_of_closing(self):
        self.assertEqual(lifecycle.backup_purge_deadline(T0), T0 + timedelta(days=65))

    def test_restore_inside_window(self):
        restored = lifecycle.restore(AccountState.CLOSED, T0, T0 + timedelta(days=10))
        self.assertEqual(restored, AccountState.ACTIVE)

    def test_restore_after_window_fails(self):
        with self.assertRaises(InvalidTransition):
            lifecycle.restore(AccountState.CLOSED, T0, T0 + timedelta(days=31))

    def test_only_closed_accounts_can_be_restored(self):
        self.assertFalse(lifecycle.can_restore(AccountState.READ_ONLY, T0, T0 + timedelta(days=1)))


if __name__ == "__main__":
    unittest.main()
