"""
Centralized path resolution for Wolfclaw data directories.

When running as a frozen PyInstaller executable (e.g. installed in Program Files),
we MUST NOT write to the executable's directory. Instead, we write to the user's
home directory under ~/.wolfclaw/data/.

When running from source (development), we use the relative 'data/' directory
as before.
"""
import os
import sys
from pathlib import Path


def get_data_dir() -> Path:
    """
    Returns the base data directory for Wolfclaw.
    - Frozen exe: ~/.wolfclaw/data
    - Development: ./data (relative to CWD)
    """
    if getattr(sys, 'frozen', False):
        base = Path(os.path.expanduser("~")) / ".wolfclaw" / "data"
    else:
        base = Path("data")
    base.mkdir(parents=True, exist_ok=True)
    return base
