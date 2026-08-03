"""Compatibility coverage for the split frontend modules."""

from pathlib import Path

from src.ui_pygame.gui import (
    combat_manager,
    combat_view,
    dungeon_manager,
    modern_character_screen,
    popup_menus,
)
from src.ui_pygame.gui.dungeon import renderer


FRONTEND_PACKAGES = (
    combat_manager,
    combat_view,
    dungeon_manager,
    modern_character_screen,
    popup_menus,
    renderer,
)


def test_refactored_frontend_facades_are_packages():
    for module in FRONTEND_PACKAGES:
        assert Path(module.__file__).name == "__init__.py"


def test_refactored_frontend_facades_preserve_primary_exports():
    assert combat_manager.GUICombatManager.__name__ == "GUICombatManager"
    assert combat_view.CombatView.__name__ == "CombatView"
    assert dungeon_manager.DungeonManager.__name__ == "DungeonManager"
    assert modern_character_screen.ModernCharacterScreen.__name__ == (
        "ModernCharacterScreen"
    )
    assert popup_menus.BasePopupMenu.__name__ == "BasePopupMenu"
    assert renderer.SceneRenderer.__name__ == "SceneRenderer"


def test_composed_frontend_classes_keep_methods_on_behavior_modules():
    assert combat_manager.GUICombatManager.start_combat.__module__.endswith(
        ".lifecycle"
    )
    assert combat_view.CombatView.render_combat.__module__.endswith(".sprites")
    assert dungeon_manager.DungeonManager.explore_dungeon.__module__.endswith(
        ".exploration"
    )
    assert modern_character_screen.ModernCharacterScreen.navigate.__module__.endswith(
        ".equipment"
    )
    assert renderer.SceneRenderer._build_render_commands.__module__.endswith(".core")
