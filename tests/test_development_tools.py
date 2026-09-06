"""Regression coverage for standalone development tools."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_balance_suite_help_starts_without_import_errors():
    """The balance-suite CLI resolves its runtime imports before showing help."""
    result = subprocess.run(
        [sys.executable, "tools/run_balance_suite.py", "--help"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--encounters" in result.stdout
