#!/usr/bin/env python3
"""Run from a source checkout without requiring package installation."""

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from softflight_control_lab.benchmark import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
