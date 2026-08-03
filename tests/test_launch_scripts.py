"""Regression coverage for shell launcher behavior."""

from __future__ import annotations

import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCH_SCRIPTS = (
    "launch.sh",
    "launch_character_menu.sh",
    "launch_debug.sh",
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


@pytest.mark.parametrize("script_name", ("launch.sh", "launch_debug.sh"))
def test_standard_launchers_target_supported_pygame_frontend(script_name):
    script = (PROJECT_ROOT / script_name).read_text(encoding="utf-8")

    assert "game_pygame.py" in script
    assert "game_curses.py" not in script


def test_packaged_entry_points_target_supported_pygame_frontend():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        scripts = tomllib.load(pyproject_file)["project"]["scripts"]

    assert scripts["forsaken-tenet"] == "src.ui_pygame.game:main"
    assert all("ui_curses" not in target for target in scripts.values())
