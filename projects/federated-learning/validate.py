#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent
shipped = json.loads((root / "results.json").read_text())
with tempfile.TemporaryDirectory() as tmp:
    generated = Path(tmp) / "results.json"
    subprocess.run([sys.executable, str(root / "demo.py"), "--check", "--output", str(generated)], check=True, cwd=root)
    fresh = json.loads(generated.read_text())
if shipped["headline"] != fresh["headline"]:
    raise SystemExit("Determinism check failed: fresh headline differs from shipped results")
print("Validation passed: executable, deterministic headline metrics, and sanity checks are consistent.")
