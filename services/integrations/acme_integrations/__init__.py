"""Rules for the Acme Cloud Integrations service.

The package implements the rules described in ``services/integrations/docs``:
the scope catalog, the install state machine with per-plan limits, and the
sync cursor and conflict resolution rules.
"""

from . import installs, scopes, sync
from .installs import Install, InstallError, InstallState
from .scopes import ScopeError
from .sync import FieldChange, SyncCursor

__all__ = [
    "installs",
    "scopes",
    "sync",
    "Install",
    "InstallError",
    "InstallState",
    "ScopeError",
    "FieldChange",
    "SyncCursor",
]
