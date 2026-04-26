#!/usr/bin/env python3
"""Wrapper for the shared OCI preview audit."""

from __future__ import annotations

import sys
from pathlib import Path

SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from preview_audit import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
