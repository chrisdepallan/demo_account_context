"""Business rules of the Acme Cloud Files service (fictional).

Modules:
    quotas       -- storage quota per plan, usage states and upload checks
    versioning   -- version retention and trash expiry
    share_links  -- share link expiry, password and access-level rules
"""

from . import quotas, share_links, versioning

__all__ = ["quotas", "share_links", "versioning"]
__version__ = "2.0.0"
