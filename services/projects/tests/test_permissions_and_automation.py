"""Tests for project permissions and the automation rule engine."""

import unittest

from acme_projects import automation, permissions
from acme_projects.automation import Action, Condition, Rule
from acme_projects.permissions import Access, can, effective_access


class PermissionTests(unittest.TestCase):
    def test_owner_and_admin_manage_private_projects(self):
        for role in ("owner", "admin"):
            self.assertEqual(effective_access(role, "private"), Access.MANAGER)

    def test_member_access(self):
        self.assertEqual(effective_access("member", "workspace"), Access.EDITOR)
        self.assertEqual(effective_access("member", "private"), Access.NONE)
        self.assertEqual(effective_access("member", "private", is_creator=True),
                         Access.MANAGER)

    def test_grant_raises_but_never_lowers_member_access(self):
        self.assertEqual(
            effective_access("member", "workspace", grant=Access.VIEWER), Access.EDITOR)
        self.assertEqual(
            effective_access("member", "private", grant=Access.MANAGER), Access.MANAGER)

    def test_guest_is_capped_at_commenter(self):
        self.assertEqual(effective_access("guest", "workspace"), Access.NONE)
        self.assertEqual(
            effective_access("guest", "workspace", grant=Access.EDITOR), Access.COMMENTER)
        self.assertFalse(permissions.can_grant("guest", Access.EDITOR))
        self.assertTrue(permissions.can_grant("guest", Access.COMMENTER))

    def test_billing_admin_has_no_project_access(self):
        self.assertEqual(
            effective_access("billing_admin", "workspace", grant=Access.EDITOR),
            Access.NONE)
        self.assertFalse(permissions.can_grant("billing_admin", Access.VIEWER))

    def test_action_matrix(self):
        self.assertTrue(can("view", Access.VIEWER))
        self.assertFalse(can("comment", Access.VIEWER))
        self.assertTrue(can("comment", Access.COMMENTER))
        self.assertFalse(can("edit_task", Access.COMMENTER))
        self.assertTrue(can("edit_task", Access.EDITOR))
        self.assertFalse(can("delete_project", Access.EDITOR))
        self.assertTrue(can("delete_project", Access.MANAGER))
        with self.assertRaises(ValueError):
            can("fly", Access.MANAGER)

    def test_task_deletion(self):
        self.assertTrue(permissions.can_delete_task(Access.EDITOR, is_task_creator=True))
        self.assertFalse(permissions.can_delete_task(Access.EDITOR, is_task_creator=False))
        self.assertTrue(permissions.can_delete_task(Access.MANAGER, is_task_creator=False))
        self.assertFalse(permissions.can_delete_task(Access.COMMENTER, is_task_creator=True))

    def test_project_limits_per_plan(self):
        self.assertEqual(permissions.project_limit("free"), 5)
        self.assertEqual(permissions.project_limit("starter"), 50)
        self.assertEqual(permissions.project_limit("pro"), 500)
        self.assertIsNone(permissions.project_limit("enterprise"))
        self.assertTrue(permissions.can_create_project("member", "free", 4))
        self.assertFalse(permissions.can_create_project("member", "free", 5))
        self.assertTrue(permissions.can_create_project("admin", "business", 100_000))
        self.assertFalse(permissions.can_create_project("guest", "pro", 0))
        self.assertFalse(permissions.can_create_project("billing_admin", "pro", 0))


class AutomationTests(unittest.TestCase):
    def test_rule_limits_per_plan(self):
        self.assertFalse(automation.can_add_rule("free", 0))
        self.assertTrue(automation.can_add_rule("starter", 4))
        self.assertFalse(automation.can_add_rule("starter", 5))
        self.assertTrue(automation.can_add_rule("enterprise", 249))
        self.assertEqual(automation.runs_remaining("pro", 9_000), 1_000)
        self.assertEqual(automation.runs_remaining("starter", 2_000), 0)

    def test_validate_rule(self):
        automation.validate_rule(
            Rule("ok", "task.created", [Action("add_label", "new")]))
        with self.assertRaises(automation.RuleValidationError):
            automation.validate_rule(Rule("bad", "task.deleted", [Action("notify", "x")]))
        with self.assertRaises(automation.RuleValidationError):
            automation.validate_rule(Rule("none", "task.created", []))
        with self.assertRaises(automation.RuleValidationError):
            automation.validate_rule(
                Rule("many", "task.created", [Action("notify", "x")] * 6))
        with self.assertRaises(automation.RuleValidationError):
            automation.validate_rule(
                Rule("status", "task.created", [Action("set_status", "blocked")]))

    def test_condition_operators(self):
        task = {"priority": "urgent", "labels": ["bug"], "assignees": []}
        self.assertTrue(automation.evaluate_condition(
            Condition("priority", "equals", "urgent"), task))
        self.assertTrue(automation.evaluate_condition(
            Condition("priority", "not_equals", "low"), task))
        self.assertTrue(automation.evaluate_condition(
            Condition("labels", "contains", "bug"), task))
        self.assertTrue(automation.evaluate_condition(
            Condition("priority", "in", ["high", "urgent"]), task))
        self.assertTrue(automation.evaluate_condition(
            Condition("assignees", "is_empty"), task))
        self.assertFalse(automation.evaluate_condition(
            Condition("due_date", "contains", "2026"), task))

    def test_rule_runs_when_conditions_pass(self):
        rule = Rule("escalate", "task.created",
                    [Action("assign", "lead@customer.example"),
                     Action("add_label", "escalated")],
                    [Condition("priority", "equals", "urgent")])
        urgent = {"status": "backlog", "priority": "urgent"}
        self.assertEqual(automation.run_rules([rule], "task.created", urgent),
                         [("escalate", "ok")])
        self.assertEqual(urgent["assignees"], ["lead@customer.example"])
        self.assertEqual(urgent["labels"], ["escalated"])
        low = {"status": "backlog", "priority": "low"}
        self.assertEqual(automation.run_rules([rule], "task.created", low), [])

    def test_rules_chain_through_raised_events(self):
        first = Rule("start", "task.assigned", [Action("set_status", "todo")])
        second = Rule("flag", "task.status_changed", [Action("set_priority", "high")])
        task = {"status": "backlog", "priority": "low"}
        history = automation.run_rules([first, second], "task.assigned", task)
        self.assertEqual(history, [("start", "ok"), ("flag", "ok")])
        self.assertEqual(task["status"], "todo")
        self.assertEqual(task["priority"], "high")

    def test_chain_stops_after_five_steps(self):
        rules = [Rule(f"r{i}", "task.created", [Action("add_label", f"l{i}")])
                 for i in range(8)]
        history = automation.run_rules(rules, "task.created", {"status": "backlog"})
        self.assertEqual(len(history), automation.MAX_CHAIN_DEPTH)

    def test_invalid_status_action_fails_and_skips_rest(self):
        rule = Rule("bad", "task.created",
                    [Action("set_status", "done"), Action("add_label", "never")])
        task = {"status": "backlog"}
        self.assertEqual(automation.run_rules([rule], "task.created", task),
                         [("bad", "failed")])
        self.assertEqual(task["status"], "backlog")
        self.assertNotIn("labels", task)
        self.assertEqual(rule.consecutive_failures, 1)

    def test_rule_disabled_after_ten_failures(self):
        rule = Rule("bad", "task.created", [Action("set_status", "done")])
        for _ in range(10):
            automation.run_rules([rule], "task.created", {"status": "backlog"})
        self.assertFalse(rule.enabled)
        self.assertEqual(
            automation.run_rules([rule], "task.created", {"status": "backlog"}), [])


if __name__ == "__main__":
    unittest.main()
