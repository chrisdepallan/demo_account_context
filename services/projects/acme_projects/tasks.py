"""Task status workflow and validation.

Implements the rules in ``docs/projects-and-tasks.md``: six statuses with a
fixed set of allowed transitions, per-task limits, and the overdue rule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Dict, FrozenSet, List, Optional

STATUSES = ("backlog", "todo", "in_progress", "in_review", "done", "cancelled")
PRIORITIES = ("low", "medium", "high", "urgent")
DEFAULT_STATUS = "backlog"
DEFAULT_PRIORITY = "medium"

#: Statuses that count as finished: such tasks are never overdue or "open".
CLOSED_STATUSES: FrozenSet[str] = frozenset({"done", "cancelled"})

#: Allowed moves. Anything else is an ``invalid_transition`` (HTTP 409).
TRANSITIONS: Dict[str, FrozenSet[str]] = {
    "backlog": frozenset({"todo", "cancelled"}),
    "todo": frozenset({"backlog", "in_progress", "cancelled"}),
    "in_progress": frozenset({"todo", "in_review", "done", "cancelled"}),
    "in_review": frozenset({"in_progress", "done", "cancelled"}),
    "done": frozenset({"in_progress"}),
    "cancelled": frozenset({"backlog"}),
}

MAX_TASKS_PER_PROJECT = 10_000
MAX_SUBTASKS_PER_TASK = 50
MAX_ASSIGNEES = 10
MAX_LABELS = 20
MAX_TITLE_CHARS = 255
MAX_DESCRIPTION_CHARS = 50_000

TASK_ID_PATTERN = re.compile(r"^tsk_[A-Z0-9]{8}$")
PROJECT_ID_PATTERN = re.compile(r"^prj_[A-Z0-9]{8}$")


class InvalidTransitionError(ValueError):
    """Raised when a status change is not allowed by the workflow."""

    code = "invalid_transition"


class TaskValidationError(ValueError):
    """Raised when a task breaks one of the per-task limits."""


@dataclass
class Task:
    """A task or subtask. Subtasks set ``parent_task_id``."""

    id: str
    title: str
    status: str = DEFAULT_STATUS
    priority: str = DEFAULT_PRIORITY
    description: str = ""
    assignees: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    due_date: Optional[date] = None
    parent_task_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    subtasks: List["Task"] = field(default_factory=list)


def is_valid_task_id(value: str) -> bool:
    """Return True for IDs such as ``tsk_3F9H2L6P``."""
    return bool(TASK_ID_PATTERN.match(value))


def is_valid_project_id(value: str) -> bool:
    """Return True for IDs such as ``prj_8K2M4QX7``."""
    return bool(PROJECT_ID_PATTERN.match(value))


def allowed_transitions(status: str) -> FrozenSet[str]:
    """Return the statuses a task in ``status`` may move to."""
    if status not in TRANSITIONS:
        raise ValueError(f"unknown status: {status!r}")
    return TRANSITIONS[status]


def can_transition(current: str, new: str) -> bool:
    """Return True if the workflow allows moving from ``current`` to ``new``."""
    return new in allowed_transitions(current)


def has_open_subtasks(task: Task) -> bool:
    """Return True if any subtask is not ``done`` or ``cancelled``."""
    return any(sub.status not in CLOSED_STATUSES for sub in task.subtasks)


def transition(task: Task, new_status: str, now: Optional[datetime] = None) -> Task:
    """Move ``task`` to ``new_status`` in place and return it.

    Raises InvalidTransitionError if the move is not in the workflow, or if
    the task would become ``done`` while it still has open subtasks.
    ``completed_at`` is set on ``done`` and cleared when a task is reopened.
    """
    if new_status not in STATUSES:
        raise InvalidTransitionError(f"unknown status: {new_status!r}")
    if not can_transition(task.status, new_status):
        raise InvalidTransitionError(
            f"a task cannot move from {task.status} to {new_status}"
        )
    if new_status == "done" and has_open_subtasks(task):
        raise InvalidTransitionError("a task with open subtasks cannot be done")
    task.status = new_status
    if new_status == "done":
        task.completed_at = now or datetime.now(timezone.utc)
    else:
        task.completed_at = None
    return task


def is_overdue(task: Task, today: Optional[date] = None) -> bool:
    """A task is overdue if its due date has passed and it is still open."""
    if task.due_date is None or task.status in CLOSED_STATUSES:
        return False
    today = today or datetime.now(timezone.utc).date()
    return task.due_date < today


def validate_task(task: Task) -> None:
    """Check the per-task limits; raise TaskValidationError on the first breach."""
    title = task.title.strip()
    if not title:
        raise TaskValidationError("title must not be empty")
    if len(title) > MAX_TITLE_CHARS:
        raise TaskValidationError(f"title is longer than {MAX_TITLE_CHARS} characters")
    if len(task.description) > MAX_DESCRIPTION_CHARS:
        raise TaskValidationError(
            f"description is longer than {MAX_DESCRIPTION_CHARS} characters"
        )
    if task.status not in STATUSES:
        raise TaskValidationError(f"unknown status: {task.status!r}")
    if task.priority not in PRIORITIES:
        raise TaskValidationError(f"unknown priority: {task.priority!r}")
    if len(task.assignees) > MAX_ASSIGNEES:
        raise TaskValidationError(f"a task can have at most {MAX_ASSIGNEES} assignees")
    if len(task.labels) > MAX_LABELS:
        raise TaskValidationError(f"a task can have at most {MAX_LABELS} labels")
    if len(task.subtasks) > MAX_SUBTASKS_PER_TASK:
        raise TaskValidationError(
            f"a task can have at most {MAX_SUBTASKS_PER_TASK} subtasks"
        )
    if task.parent_task_id is not None and task.subtasks:
        raise TaskValidationError("subtasks cannot have their own subtasks")


def can_add_task(current_task_count: int) -> bool:
    """Return True if a project with this many tasks can take one more."""
    return current_task_count < MAX_TASKS_PER_PROJECT
