"""Regression coverage for shell launcher behavior."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCH_SCRIPTS = (
    "launch_debug.sh",
    "launch_gui.sh",
    "launch_gui_character_menu.sh",
    "launch_gui_debug.sh",
)


@pytest.mark.parametrize("script_name", LAUNCH_SCRIPTS)
def test_launcher_returns_to_calling_shell_when_sourced(tmp_path, script_name):
    script_path = tmp_path / script_name
    shutil.copy2(PROJECT_ROOT / script_name, script_path)

    fake_python = tmp_path / ".venv" / "bin" / "python"
    fake_python.parent.mkdir(parents=True)
    fake_python.write_text("#!/bin/bash\nexit 0\n", encoding="utf-8")
    fake_python.chmod(0o755)

    result = subprocess.run(
        [
            "bash",
            "-c",
            (
                'caller_directory=$PWD; source "$1"; '
                'test "$PWD" = "$caller_directory"; printf "caller-survived\\n"'
            ),
            "bash",
            str(script_path),
        ],
        cwd=tmp_path.parent,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "caller-survived" in result.stdout
