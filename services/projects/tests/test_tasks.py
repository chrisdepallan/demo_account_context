"""Tests for the task status workflow and validation."""

import unittest
from datetime import date, datetime, timezone

from acme_projects import tasks
from acme_projects.tasks import (
    InvalidTransitionError,
    Task,
    TaskValidationError,
    can_transition,
    is_overdue,
    transition,
    validate_task,
)


class TransitionTests(unittest.TestCase):
    def test_new_task_defaults(self):
        task = Task(id="tsk_3F9H2L6P", title="Draft the checklist")
        self.assertEqual(task.status, "backlog")
        self.assertEqual(task.priority, "medium")

    def test_happy_path_to_done(self):
        task = Task(id="tsk_3F9H2L6P", title="Draft the checklist")
        now = datetime(2026, 11, 26, 9, 0, tzinfo=timezone.utc)
        for status in ("todo", "in_progress", "in_review", "done"):
            transition(task, status, now=now)
        self.assertEqual(task.status, "done")
        self.assertEqual(task.completed_at, now)

    def test_backlog_cannot_jump_to_done(self):
        task = Task(id="tsk_3F9H2L6P", title="Draft the checklist")
        with self.assertRaises(InvalidTransitionError) as ctx:
            transition(task, "done")
        self.assertEqual(ctx.exception.code, "invalid_transition")
        self.assertEqual(task.status, "backlog")

    def test_done_can_only_be_reopened(self):
        self.assertEqual(tasks.allowed_transitions("done"), frozenset({"in_progress"}))
        self.assertFalse(can_transition("done", "cancelled"))

    def test_reopen_clears_completed_at(self):
        task = Task(id="tsk_3F9H2L6P", title="t", status="in_progress")
        transition(task, "done")
        self.assertIsNotNone(task.completed_at)
        transition(task, "in_progress")
        self.assertIsNone(task.completed_at)

    def test_cancelled_restores_to_backlog_only(self):
        self.assertTrue(can_transition("cancelled", "backlog"))
        self.assertFalse(can_transition("cancelled", "todo"))

    def test_every_open_status_can_be_cancelled(self):
        for status in ("backlog", "todo", "in_progress", "in_review"):
            self.assertTrue(can_transition(status, "cancelled"), status)

    def test_unknown_status_rejected(self):
        task = Task(id="tsk_3F9H2L6P", title="t")
        with self.assertRaises(InvalidTransitionError):
            transition(task, "blocked")
        with self.assertRaises(ValueError):
            can_transition("blocked", "todo")

    def test_open_subtasks_block_done(self):
        sub = Task(id="tsk_AAAA1111", title="sub", status="todo",
                   parent_task_id="tsk_3F9H2L6P")
        task = Task(id="tsk_3F9H2L6P", title="t", status="in_progress", subtasks=[sub])
        with self.assertRaises(InvalidTransitionError):
            transition(task, "done")
        sub.status = "cancelled"
        transition(task, "done")
        self.assertEqual(task.status, "done")


class ValidationTests(unittest.TestCase):
    def test_title_limits(self):
        validate_task(Task(id="tsk_3F9H2L6P", title="x" * 255))
        with self.assertRaises(TaskValidationError):
            validate_task(Task(id="tsk_3F9H2L6P", title="x" * 256))
        with self.assertRaises(TaskValidationError):
            validate_task(Task(id="tsk_3F9H2L6P", title="   "))

    def test_assignee_and_label_limits(self):
        with self.assertRaises(TaskValidationError):
            validate_task(Task(id="tsk_3F9H2L6P", title="t",
                               assignees=[f"m{i}@customer.example" for i in range(11)]))
        with self.assertRaises(TaskValidationError):
            validate_task(Task(id="tsk_3F9H2L6P", title="t",
                               labels=[str(i) for i in range(21)]))

    def test_subtask_limits(self):
        subs = [Task(id="tsk_AAAA1111", title="s") for _ in range(51)]
        with self.assertRaises(TaskValidationError):
            validate_task(Task(id="tsk_3F9H2L6P", title="t", subtasks=subs))
        nested = Task(id="tsk_AAAA1111", title="s", parent_task_id="tsk_3F9H2L6P",
                      subtasks=[Task(id="tsk_BBBB2222", title="deep")])
        with self.assertRaises(TaskValidationError):
            validate_task(nested)

    def test_overdue_rule(self):
        today = date(2026, 11, 26)
        late = Task(id="tsk_3F9H2L6P", title="t", due_date=date(2026, 11, 25))
        self.assertTrue(is_overdue(late, today))
        late.status = "cancelled"
        self.assertFalse(is_overdue(late, today))
        due_today = Task(id="tsk_3F9H2L6P", title="t", due_date=today)
        self.assertFalse(is_overdue(due_today, today))
        self.assertFalse(is_overdue(Task(id="tsk_3F9H2L6P", title="t"), today))

    def test_id_formats(self):
        self.assertTrue(tasks.is_valid_task_id("tsk_3F9H2L6P"))
        self.assertFalse(tasks.is_valid_task_id("tsk_3f9h2l6p"))
        self.assertTrue(tasks.is_valid_project_id("prj_8K2M4QX7"))
        self.assertFalse(tasks.is_valid_project_id("prj_8K2M4QX"))

    def test_project_task_limit(self):
        self.assertTrue(tasks.can_add_task(9_999))
        self.assertFalse(tasks.can_add_task(10_000))


if __name__ == "__main__":
    unittest.main()
