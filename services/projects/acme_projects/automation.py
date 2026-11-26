"""Automation rule engine.

Implements ``docs/templates-and-automation.md``: a rule is one trigger, up
to 5 conditions (all must pass) and up to 5 actions. Tasks are plain dicts
with the keys ``status``, ``priority``, ``assignees`` and ``labels``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .tasks import PRIORITIES, STATUSES, can_transition

TRIGGERS = (
    "task.created",
    "task.status_changed",
    "task.assigned",
    "task.due_date_passed",
    "comment.added",
)
OPERATORS = ("equals", "not_equals", "contains", "in", "is_empty")
ACTION_TYPES = ("set_status", "set_priority", "assign", "add_label", "notify")

MAX_CONDITIONS = 5
MAX_ACTIONS = 5
MAX_CHAIN_DEPTH = 5
DISABLE_AFTER_FAILURES = 10

#: Rules per project by plan. 0 means automation is not available.
RULE_LIMITS: Dict[str, int] = {
    "free": 0, "starter": 5, "pro": 25, "business": 100, "enterprise": 250,
}
#: Rule runs per workspace per calendar month.
MONTHLY_RUN_LIMITS: Dict[str, int] = {
    "free": 0, "starter": 1_000, "pro": 10_000, "business": 50_000,
    "enterprise": 250_000,
}


class RuleValidationError(ValueError):
    """Raised when a rule definition is not valid."""


class ActionError(RuntimeError):
    """Raised when an action cannot be applied to a task."""


@dataclass(frozen=True)
class Condition:
    """A check on one task field, for example ``priority equals urgent``."""

    field: str
    operator: str
    value: Any = None


@dataclass(frozen=True)
class Action:
    """Something a rule does, for example ``set_status`` to ``in_review``."""

    type: str
    value: Any = None


@dataclass
class Rule:
    """One automation rule. ``consecutive_failures`` drives auto-disable."""

    name: str
    trigger: str
    actions: List[Action]
    conditions: List[Condition] = field(default_factory=list)
    enabled: bool = True
    consecutive_failures: int = 0


def validate_rule(rule: Rule) -> None:
    """Raise RuleValidationError if ``rule`` breaks the documented limits."""
    if rule.trigger not in TRIGGERS:
        raise RuleValidationError(f"unknown trigger: {rule.trigger!r}")
    if not 1 <= len(rule.actions) <= MAX_ACTIONS:
        raise RuleValidationError(f"a rule needs 1 to {MAX_ACTIONS} actions")
    if len(rule.conditions) > MAX_CONDITIONS:
        raise RuleValidationError(f"a rule can have at most {MAX_CONDITIONS} conditions")
    for condition in rule.conditions:
        if condition.operator not in OPERATORS:
            raise RuleValidationError(f"unknown operator: {condition.operator!r}")
    for action in rule.actions:
        if action.type not in ACTION_TYPES:
            raise RuleValidationError(f"unknown action: {action.type!r}")
        if action.type == "set_status" and action.value not in STATUSES:
            raise RuleValidationError(f"unknown status: {action.value!r}")
        if action.type == "set_priority" and action.value not in PRIORITIES:
            raise RuleValidationError(f"unknown priority: {action.value!r}")


def can_add_rule(plan: str, current_rules: int) -> bool:
    """Return True if a project on ``plan`` may have one more rule."""
    if plan not in RULE_LIMITS:
        raise ValueError(f"unknown plan: {plan!r}")
    return current_rules < RULE_LIMITS[plan]


def runs_remaining(plan: str, runs_this_month: int) -> int:
    """Return how many rule runs the workspace has left this month."""
    if plan not in MONTHLY_RUN_LIMITS:
        raise ValueError(f"unknown plan: {plan!r}")
    return max(0, MONTHLY_RUN_LIMITS[plan] - runs_this_month)


def evaluate_condition(condition: Condition, task: Dict[str, Any]) -> bool:
    """Return True if ``task`` satisfies ``condition``."""
    actual = task.get(condition.field)
    op = condition.operator
    if op == "equals":
        return actual == condition.value
    if op == "not_equals":
        return actual != condition.value
    if op == "contains":
        return actual is not None and condition.value in actual
    if op == "in":
        return actual in condition.value
    if op == "is_empty":
        return actual is None or actual == "" or actual == []
    raise RuleValidationError(f"unknown operator: {op!r}")


def matches(rule: Rule, trigger: str, task: Dict[str, Any]) -> bool:
    """Return True if an enabled rule should run for this trigger and task."""
    if not rule.enabled or rule.trigger != trigger:
        return False
    return all(evaluate_condition(c, task) for c in rule.conditions)


def apply_action(action: Action, task: Dict[str, Any]) -> Optional[str]:
    """Apply ``action`` to ``task`` in place.

    Returns the name of the event the action raises (so other rules can
    react to it), or None. Raises ActionError if a ``set_status`` action is
    not allowed by the status workflow.
    """
    if action.type == "set_status":
        current = task.get("status", "backlog")
        if current == action.value:
            return None
        if not can_transition(current, action.value):
            raise ActionError(f"cannot move from {current} to {action.value}")
        task["status"] = action.value
        return "task.status_changed"
    if action.type == "set_priority":
        task["priority"] = action.value
        return None
    if action.type == "assign":
        assignees = task.setdefault("assignees", [])
        if action.value in assignees:
            return None
        if len(assignees) >= 10:
            raise ActionError("a task can have at most 10 assignees")
        assignees.append(action.value)
        return "task.assigned"
    if action.type == "add_label":
        labels = task.setdefault("labels", [])
        if action.value not in labels:
            labels.append(action.value)
        return None
    if action.type == "notify":
        task.setdefault("notifications", []).append(action.value)
        return None
    raise ActionError(f"unknown action: {action.type!r}")


def run_rules(
    rules: List[Rule], trigger: str, task: Dict[str, Any]
) -> List[Tuple[str, str]]:
    """Run every matching rule for ``trigger`` and follow the events they raise.

    A chain stops after MAX_CHAIN_DEPTH rule steps and a rule never runs twice
    in one chain. A failed action skips the rest of that rule and counts as a
    failure; after DISABLE_AFTER_FAILURES failures in a row the rule is
    disabled. Returns a run history of ``(rule name, "ok" | "failed")``.
    """
    history: List[Tuple[str, str]] = []
    queue: List[str] = [trigger]
    ran: set = set()
    while queue and len(history) < MAX_CHAIN_DEPTH:
        event = queue.pop(0)
        for rule in rules:
            if len(history) >= MAX_CHAIN_DEPTH:
                break
            if id(rule) in ran or not matches(rule, event, task):
                continue
            ran.add(id(rule))
            try:
                raised = [apply_action(action, task) for action in rule.actions]
            except ActionError:
                rule.consecutive_failures += 1
                if rule.consecutive_failures >= DISABLE_AFTER_FAILURES:
                    rule.enabled = False
                history.append((rule.name, "failed"))
                continue
            rule.consecutive_failures = 0
            history.append((rule.name, "ok"))
            queue.extend(e for e in raised if e is not None)
    return history
