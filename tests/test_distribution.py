"""Distribution configuration and clean-location startup smoke tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_resources_live_in_packaged_trees():
    assert (PROJECT_ROOT / "src/core/data/maps/map_level_1.json").is_file()
    assert (PROJECT_ROOT / "src/core/data/maps/dungeon_tiles.tsx").is_file()
    assert (PROJECT_ROOT / "src/ui_pygame/assets/backgrounds/main_menu.png").is_file()
    spec = (PROJECT_ROOT / "packaging/forsaken_tenet.spec").read_text(encoding="utf-8")
    assert 'collect_data_files("src.core.data"' in spec
    assert 'collect_data_files(\n        "src.ui_pygame.assets"' in spec
    assert "review_sheet.png" in spec


def test_headless_startup_from_clean_working_directory(tmp_path):
    environment = os.environ.copy()
    environment.update(
        {
            "SDL_AUDIODRIVER": "dummy",
            "SDL_VIDEODRIVER": "dummy",
            "FORSAKEN_TENET_DATA_DIR": str(tmp_path / "user-data"),
        }
    )

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "game_pygame.py"), "--smoke-test"],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "Startup smoke test passed." in result.stdout
    assert (tmp_path / "user-data" / "saves").is_dir()
