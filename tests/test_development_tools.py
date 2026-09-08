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


def test_ci_pins_dependencies_and_checks_stable_type_contracts():
    """Keep CI's verified dependency resolution and strict boundary set explicit."""
    constraints = (PROJECT_ROOT / "constraints.txt").read_text(encoding="utf-8")
    workflow = (PROJECT_ROOT / ".github/workflows/main.yml").read_text(encoding="utf-8")

    for requirement in (
        "black==26.5.1",
        "mypy==2.3.1",
        "numpy==2.4.6",
        "pygame==2.6.1",
        "pyinstaller==6.22.2",
        "pytest==7.4.2",
        "ruff==0.16.6",
    ):
        assert requirement in constraints

    assert workflow.count("--constraint constraints.txt") == 4
    assert workflow.count("--build-constraint constraints.txt") == 2
    for strict_target in (
        "src/core/combat/encounter.py",
        "src/core/combat/targeting.py",
        "src/core/combat/battle_engine/models.py",
        "src/core/progression/models.py",
        "src/core/save_system/manager.py",
    ):
        assert strict_target in workflow
