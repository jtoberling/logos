"""
Logos: The Architecture of Reason

A digital memory engine and personality framework built on the principles
of logic, transparency, and grounded knowledge.
"""

import os
from pathlib import Path

# Read version from VERSION file
_version_file = Path(__file__).parent.parent / "VERSION"
try:
    with open(_version_file, "r", encoding="utf-8") as f:
        __version__ = f.read().strip()
except (FileNotFoundError, IOError):
    # Fallback to hardcoded version if file not found
    __version__ = "1.0.0"

__author__ = "Janos Toberling"
__description__ = "Digital memory engine and personality framework"
__url__ = "https://github.com/janos/logos"