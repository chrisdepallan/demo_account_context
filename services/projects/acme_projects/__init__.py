"""Business rules of the Acme Cloud Projects service (fictional).

Modules:
    tasks        -- task status workflow, transitions and validation
    permissions  -- project access levels by workspace role, project limits
    automation   -- automation rule engine (trigger + conditions + actions)
"""

from . import automation, permissions, tasks

__all__ = ["automation", "permissions", "tasks"]
__version__ = "2.0.0"
