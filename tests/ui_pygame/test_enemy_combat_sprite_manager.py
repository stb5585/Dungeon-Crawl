#!/usr/bin/env python3
"""Focused coverage for transparent enemy combat sprite loading."""

from __future__ import annotations

import json
from pathlib import Path
import re
from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.assets.enemy_combat_sprite_manager import EnemyCombatSpriteManager
from src.ui_pygame.assets.enemy_render_manager import EnemyRenderManager


PROJECT_ROOT = Path(__file__).resolve().parents[2]


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


def _write_sprite(path: Path, color: tuple[int, int, int, int], size: tuple[int, int] = (32, 48)) -> None:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surface, color, pygame.Rect(4, 2, size[0] - 8, size[1] - 4))
    pygame.image.save(surface, path)


def test_enemy_combat_sprite_manager_loads_mapping_and_exact_sprite(tmp_path):
    _write_render_fixture(tmp_path)
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "goblin.png", (220, 30, 20, 255))
    _write_sprite(sprite_root / "boss.png", (20, 220, 30, 255))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255))

    render_manager = EnemyRenderManager(render_root=tmp_path)
    manager = EnemyCombatSpriteManager(render_manager, sprite_root=sprite_root)

    assert manager.get_sprite_key_for_enemy(SimpleNamespace(name="Goblin Raider")) == "goblin"
    assert manager.get_sprite_by_name("Goblin Raider").get_at((5, 5)) == pygame.Color(220, 30, 20, 255)
    assert manager.get_sprite_by_key("goblin") is manager.get_sprite_by_key("goblin")


def test_enemy_combat_sprite_manager_scaled_cache_fallbacks_and_aspect_ratio(tmp_path):
    _write_render_fixture(tmp_path)
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "boss.png", (20, 220, 30, 255), size=(20, 40))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255), size=(20, 40))

    render_manager = EnemyRenderManager(render_root=tmp_path)
    manager = EnemyCombatSpriteManager(render_manager, sprite_root=sprite_root)

    assert manager.get_sprite_key_for_enemy(SimpleNamespace(name="Goblin Raider")) == "generic_enemy"
    assert manager.get_sprite_key_for_enemy(SimpleNamespace(name="Goblin Raider", boss=True)) == "boss"

    scaled = manager.get_scaled_sprite_by_name("Named Boss", (40, 40))
    scaled_again = manager.get_scaled_sprite_by_name("Named Boss", (40, 40))
    assert scaled.get_size() == (40, 40)
    assert scaled_again is scaled
    assert scaled.get_at((0, 20)).a == 0
    assert scaled.get_at((20, 20)).a > 0

    manager.clear_cache()
    assert manager.get_scaled_sprite_by_name("Named Boss", (40, 40)) is not scaled


def test_enemy_combat_sprite_manager_strict_map_avoids_broad_render_reuse(tmp_path):
    _write_render_fixture(tmp_path)
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "battle_toad.png", (220, 30, 20, 255))
    _write_sprite(sprite_root / "bear.png", (20, 220, 30, 255))
    _write_sprite(sprite_root / "evil_crusader.png", (220, 220, 30, 255))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255))
    (sprite_root / "enemy_combat_sprite_map.json").write_text(
        json.dumps({"Battle Toad": "battle_toad", "Direbear": "bear", "Evil Crusader": "evil_crusader"}),
        encoding="utf-8",
    )
    (tmp_path / "enemy_render_map.json").write_text(
        json.dumps({"Alligator": "bear", "Battle Toad": "boar", "Evil Crusader": "skeleton_warrior"}),
        encoding="utf-8",
    )

    render_manager = EnemyRenderManager(render_root=tmp_path)
    manager = EnemyCombatSpriteManager(render_manager, sprite_root=sprite_root)

    assert manager.get_sprite_key_for_enemy("Battle Toad") == "battle_toad"
    assert manager.get_sprite_key_for_enemy("Direbear") == "bear"
    assert manager.get_sprite_key_for_enemy("Evil Crusader") == "evil_crusader"
    assert manager.get_sprite_key_for_enemy("Alligator") == "generic_enemy"


def test_enemy_combat_sprite_manager_missing_sprite_uses_runtime_fallback(tmp_path):
    _write_render_fixture(tmp_path)
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()

    render_manager = EnemyRenderManager(render_root=tmp_path)
    manager = EnemyCombatSpriteManager(render_manager, sprite_root=sprite_root)

    fallback = manager.get_sprite_by_key("goblin")

    assert fallback.get_size() == (384, 384)
    assert fallback.get_at((0, 0)).a == 0
    assert manager.get_sprite_by_name("Unknown Thing").get_size() == (384, 384)


def test_default_enemy_combat_sprite_assets_cover_render_archetypes():
    manager = EnemyCombatSpriteManager()
    expected_keys = set(manager.render_manager.frames)

    assert expected_keys
    assert expected_keys <= manager.available_keys
    assert manager.get_sprite_key_for_enemy("Evil Crusader") == "evil_crusader"
    assert manager.get_sprite_key_for_enemy("Battle Toad") == "battle_toad"
    assert manager.get_sprite_key_for_enemy("Alligator") == "alligator"
    assert manager.get_sprite_key_for_enemy("Water Myrmidon") == "water_myrmidon"
    for enemy_name in (
        "Goblin",
        "Skeleton",
        "Giant Rat",
        "Battle Toad",
        "Evil Crusader",
        "Satyr",
        "Gnoll",
        "Alligator",
        "Werewolf",
        "Troll",
        "Conjurer",
        "Water Myrmidon",
        "Dragonkin",
        "Warforged",
    ):
        sprite = manager.get_sprite_by_name(enemy_name)
        assert sprite.get_width() > 0
        assert sprite.get_height() > 0
        assert sprite.get_at((0, 0)).a == 0


def test_default_enemy_combat_sprite_map_covers_concrete_enemy_names():
    manager = EnemyCombatSpriteManager()
    enemy_names = _concrete_enemy_names()
    ignored = {"Test", "Myrmidon"}
    missing = sorted(name for name in enemy_names if name not in manager.sprite_map and name not in ignored)

    assert missing == []


def _concrete_enemy_names() -> set[str]:
    enemies_source = (PROJECT_ROOT / "src" / "core" / "enemies.py").read_text(encoding="utf-8")
    class_pattern = re.compile(r"^class\s+\w+\([^)]*\):", re.MULTILINE)
    starts = [match.start() for match in class_pattern.finditer(enemies_source)]
    names: set[str] = set()

    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(enemies_source)
        block = enemies_source[start:end]
        super_name = re.search(r"super\(\)\.__init__\(\s*name\s*=\s*(['\"])(.*?)\1", block)
        if super_name:
            names.add(super_name.group(2))
        for assigned_name in re.finditer(r"self\.name\s*=\s*(['\"])(.*?)\1", block):
            names.add(assigned_name.group(2))

    return names
