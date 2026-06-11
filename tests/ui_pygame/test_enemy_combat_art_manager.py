#!/usr/bin/env python3
"""Focused coverage for dedicated enemy combat artwork loading."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.assets.enemy_combat_art_manager import EnemyCombatArtManager
from src.ui_pygame.assets.enemy_render_manager import EnemyRenderManager


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    yield


def _write_render_fixture(root: Path) -> None:
    root.mkdir(exist_ok=True)
    manifest = {
        "goblin": {"x": 0, "y": 0, "w": 16, "h": 16},
        "boss": {"x": 16, "y": 0, "w": 16, "h": 16},
        "dragon": {"x": 32, "y": 0, "w": 16, "h": 16},
        "generic_enemy": {"x": 48, "y": 0, "w": 16, "h": 16},
    }
    (root / "enemy_render_atlas.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "enemy_render_map.json").write_text(
        json.dumps({"Goblin Raider": "goblin", "Named Boss": "boss"}),
        encoding="utf-8",
    )
    surface = pygame.Surface((64, 16), pygame.SRCALPHA)
    pygame.image.save(surface, root / "enemy_render_atlas.png")


def _write_art(path: Path, color: tuple[int, int, int, int], size: tuple[int, int] = (32, 48)) -> None:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    pygame.image.save(surface, path)


def test_enemy_combat_art_manager_loads_mapping_and_exact_art(tmp_path):
    _write_render_fixture(tmp_path)
    art_root = tmp_path / "enemy_combat_art"
    art_root.mkdir()
    _write_art(art_root / "goblin.png", (220, 30, 20, 255))
    _write_art(art_root / "boss.png", (20, 220, 30, 255))
    _write_art(art_root / "generic_enemy.png", (20, 30, 220, 255))

    render_manager = EnemyRenderManager(render_root=tmp_path)
    manager = EnemyCombatArtManager(render_manager, art_root=art_root)

    assert manager.get_art_key_for_enemy(SimpleNamespace(name="Goblin Raider")) == "goblin"
    assert manager.get_art_by_name("Goblin Raider").get_at((1, 1)) == pygame.Color(220, 30, 20, 255)
    assert manager.get_art_by_key("goblin") is manager.get_art_by_key("goblin")


def test_enemy_combat_art_manager_scaled_cache_and_fallbacks(tmp_path):
    _write_render_fixture(tmp_path)
    art_root = tmp_path / "enemy_combat_art"
    art_root.mkdir()
    _write_art(art_root / "boss.png", (20, 220, 30, 255), size=(20, 30))
    _write_art(art_root / "generic_enemy.png", (20, 30, 220, 255), size=(20, 30))

    render_manager = EnemyRenderManager(render_root=tmp_path)
    manager = EnemyCombatArtManager(render_manager, art_root=art_root)

    assert manager.get_art_key_for_enemy(SimpleNamespace(name="Goblin Raider")) == "generic_enemy"
    assert manager.get_art_key_for_enemy(SimpleNamespace(name="Goblin Raider", boss=True)) == "boss"

    scaled = manager.get_scaled_art_by_name("Named Boss", (40, 40))
    scaled_again = manager.get_scaled_art_by_name("Named Boss", (40, 40))
    assert scaled.get_size() == (40, 40)
    assert scaled_again is scaled

    manager.clear_cache()
    assert manager.get_scaled_art_by_name("Named Boss", (40, 40)) is not scaled


def test_enemy_combat_art_manager_missing_art_uses_runtime_fallback(tmp_path):
    _write_render_fixture(tmp_path)
    art_root = tmp_path / "enemy_combat_art"
    art_root.mkdir()

    render_manager = EnemyRenderManager(render_root=tmp_path)
    manager = EnemyCombatArtManager(render_manager, art_root=art_root)

    fallback = manager.get_art_by_key("goblin")

    assert fallback.get_size() == (256, 320)
    assert manager.get_art_by_name("Unknown Thing").get_size() == (256, 320)


def test_default_enemy_combat_art_assets_cover_render_archetypes():
    manager = EnemyCombatArtManager()
    expected_keys = set(manager.render_manager.frames)

    assert expected_keys
    assert expected_keys <= manager.available_keys
    for enemy_name in ("Goblin", "Skeleton", "Wolf", "Dragon", "The Devil", "Red Dragon"):
        assert manager.get_art_by_name(enemy_name).get_width() > 0
