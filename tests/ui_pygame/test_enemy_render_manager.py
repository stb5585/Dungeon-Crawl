#!/usr/bin/env python3
"""Focused coverage for large enemy render atlas loading."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import pygame

from src.core import enemies
from src.core.character import Character
from src.ui_pygame.assets.enemy_render_manager import EnemyRenderManager


def _write_render_fixture(root: Path) -> None:
    root.mkdir(exist_ok=True)
    manifest = {
        "goblin": {"x": 0, "y": 0, "w": 80, "h": 120},
        "boss": {"x": 80, "y": 0, "w": 80, "h": 120},
        "bandit": {"x": 160, "y": 0, "w": 80, "h": 120},
        "dragon": {"x": 0, "y": 120, "w": 80, "h": 120},
        "generic_enemy": {"x": 80, "y": 120, "w": 80, "h": 120},
    }
    (root / "enemy_render_atlas.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "enemy_render_map.json").write_text(
        json.dumps({"Goblin Raider": "goblin", "Named Boss": "boss"}),
        encoding="utf-8",
    )
    surface = pygame.Surface((240, 240), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    surface.fill((255, 0, 0, 255), pygame.Rect(0, 0, 80, 120))
    surface.fill((0, 255, 0, 255), pygame.Rect(80, 0, 80, 120))
    surface.fill((0, 0, 255, 255), pygame.Rect(160, 0, 80, 120))
    surface.fill((255, 255, 0, 255), pygame.Rect(0, 120, 80, 120))
    surface.fill((255, 0, 255, 255), pygame.Rect(80, 120, 80, 120))
    pygame.image.save(surface, root / "enemy_render_atlas.png")


def test_enemy_render_manager_loads_manifest_mapping_and_exact_render(tmp_path):
    _write_render_fixture(tmp_path)

    manager = EnemyRenderManager(render_root=tmp_path)

    assert manager.frames["goblin"].rect == pygame.Rect(0, 0, 80, 120)
    assert manager.render_map["Goblin Raider"] == "goblin"
    assert manager.get_render_key_for_enemy(SimpleNamespace(name="Goblin Raider")) == "goblin"
    assert manager.get_render_by_name("Goblin Raider").get_at((1, 1)) == pygame.Color(255, 0, 0, 255)


def test_enemy_render_manager_lookup_order_and_missing_mapping(tmp_path, caplog):
    _write_render_fixture(tmp_path)
    manager = EnemyRenderManager(render_root=tmp_path)

    assert manager.get_render_key_for_enemy(SimpleNamespace(name="Village Bandit", render_archetype="bandit")) == "bandit"
    assert manager.get_render_key_for_enemy(SimpleNamespace(name="Young Dragon", enemy_typ="Dragon")) == "dragon"
    assert manager.get_render_key_for_enemy(SimpleNamespace(name="Unknown Boss", boss=True)) == "boss"

    with caplog.at_level("WARNING"):
        assert manager.get_render_key_for_enemy(SimpleNamespace(name="Unmapped Thing", enemy_typ="")) == "generic_enemy"
    assert "Enemy render mapping missing for Unmapped Thing" in caplog.text
    assert "Unmapped Thing" in manager.missing_mappings


def test_enemy_render_manager_cache_scaled_render_and_missing_assets(tmp_path):
    _write_render_fixture(tmp_path)
    manager = EnemyRenderManager(render_root=tmp_path)

    render = manager.get_render_by_key("goblin")
    cached = manager.get_render_by_key("goblin")
    assert cached is render

    scaled = manager.get_scaled_render_by_key("goblin", (40, 40))
    scaled_again = manager.get_scaled_render_by_key("goblin", (40, 40))
    assert scaled.get_size() == (40, 40)
    assert scaled_again is scaled

    missing = EnemyRenderManager(
        render_root=tmp_path,
        atlas_image=tmp_path / "missing.png",
    )
    assert missing.get_render_by_key("goblin").get_size() == (256, 320)


def test_default_enemy_render_map_covers_discovered_enemy_names():
    manager = EnemyRenderManager()
    discovered_names = set()
    for _class_name, obj in vars(enemies).items():
        if not inspect.isclass(obj) or not issubclass(obj, Character) or obj is Character:
            continue
        required = [
            param
            for param in inspect.signature(obj).parameters.values()
            if param.default is param.empty
            and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
        ]
        if required:
            continue
        try:
            discovered_names.add(obj().name)
        except Exception:
            continue

    assert discovered_names
    assert discovered_names <= set(manager.render_map)
    for enemy_name in ("Goblin", "Skeleton", "Direwolf", "Green Slime", "The Devil", "Red Dragon"):
        assert manager.get_render_key_for_enemy(enemy_name) != "generic_enemy"
