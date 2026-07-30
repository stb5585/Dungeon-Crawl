"""Regression coverage for project-root resource path resolution."""

import importlib
from pathlib import Path

from src import paths as project_paths
from src.ui_pygame.gui.dungeon_manager.core import DungeonCoreMixin
from src.ui_pygame.gui.modern_character_screen.models import PORTRAIT_DIR


def test_resource_paths_do_not_depend_on_working_directory(monkeypatch, tmp_path):
    """Resource roots remain stable when the game starts outside the repository."""
    repository_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(tmp_path)

    importlib.reload(project_paths)

    assert project_paths.PROJECT_ROOT == repository_root
    assert project_paths.PYGAME_ASSETS_DIR == repository_root / "src" / "ui_pygame" / "assets"
    assert (project_paths.PYGAME_ASSETS_DIR / "backgrounds" / "dungeon.png").is_file()
    assert (project_paths.PYGAME_ASSETS_DIR / "sprites" / "npcs" / "nimue.png").is_file()
    assert PORTRAIT_DIR == project_paths.PYGAME_ASSETS_DIR / "portraits"


def test_dungeon_manager_image_helpers_return_root_anchored_paths():
    """Dungeon dialogue helpers return absolute asset paths after package splits."""
    manager = object.__new__(DungeonCoreMixin)

    assert Path(manager._npc_image_path("nimue.png")) == (
        project_paths.PYGAME_ASSETS_DIR / "sprites" / "npcs" / "nimue.png"
    )
    assert Path(manager._enemy_combat_sprite_image_path("jester.png")) == (
        project_paths.PYGAME_ASSETS_DIR / "enemy_combat_sprites" / "jester.png"
    )
