#!/usr/bin/env python3
"""Focused coverage for reusable item icon atlases."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pygame

from src.ui_pygame.assets import icon_manager
from src.ui_pygame.assets.icon_manager import IconManager


def _surface(size=(64, 32), color=(0, 0, 0, 0)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface


def _write_icon_fixture(root: Path) -> None:
    root.mkdir(exist_ok=True)
    manifest = {
        "sword": {"x": 0, "y": 0, "w": 32, "h": 32},
        "generic_item": {"x": 32, "y": 0, "w": 32, "h": 32},
    }
    for atlas in ("equipment_icons", "consumable_icons", "utility_icons"):
        (root / f"{atlas}.json").write_text(json.dumps(manifest), encoding="utf-8")
        (root / f"{atlas}.png").touch()
    (root / "item_icon_map.json").write_text(json.dumps({"Iron Sword": "sword"}), encoding="utf-8")


def test_icon_manager_loads_manifests_and_item_mapping(tmp_path):
    _write_icon_fixture(tmp_path)

    manager = IconManager(icon_root=tmp_path)

    assert manager.frames["sword"].rect == pygame.Rect(0, 0, 32, 32)
    assert manager.item_map["Iron Sword"] == "sword"


def test_icon_manager_get_icon_by_item_name_and_cache_reuse(tmp_path):
    _write_icon_fixture(tmp_path)
    manager = IconManager(icon_root=tmp_path)
    atlas = _surface()
    atlas.fill((255, 0, 0, 255), pygame.Rect(0, 0, 32, 32))
    atlas.fill((0, 0, 255, 255), pygame.Rect(32, 0, 32, 32))
    manager.atlas_surface = lambda _atlas: atlas

    item = SimpleNamespace(name="Iron Sword", typ="Weapon", subtyp="Sword")
    icon = manager.get_icon(item)
    cached = manager.get_icon(item)

    assert icon.get_at((1, 1)) == pygame.Color(255, 0, 0, 255)
    assert cached is icon


def test_icon_manager_missing_mapping_infers_archetype_and_logs(tmp_path, caplog):
    _write_icon_fixture(tmp_path)
    manager = IconManager(icon_root=tmp_path)

    with caplog.at_level("WARNING"):
        key = manager.icon_key_for_item(SimpleNamespace(name="Mystery Blade", typ="Weapon", subtyp="Sword"))

    assert key == "sword"
    assert "Item icon mapping missing for Mystery Blade" in caplog.text


def test_icon_manager_does_not_warn_for_abilities(tmp_path, caplog):
    _write_icon_fixture(tmp_path)
    manager = IconManager(icon_root=tmp_path)

    with caplog.at_level("WARNING"):
        key = manager.icon_key_for_item(SimpleNamespace(name="Shield Slam", typ="Skill", subtyp=""))

    assert key == "generic_item"
    assert "Item icon mapping missing for Shield Slam" not in caplog.text


def test_icon_manager_infers_more_specific_weapon_archetypes(tmp_path):
    _write_icon_fixture(tmp_path)
    manager = IconManager(icon_root=tmp_path)

    assert manager.infer_icon_key(SimpleNamespace(name="War Hammer", typ="Weapon", subtyp="Hammer")) == "hammer"
    assert manager.infer_icon_key(SimpleNamespace(name="Bear Claw", typ="Weapon", subtyp="Natural")) == "claw"
    assert manager.infer_icon_key(SimpleNamespace(name="Brass Knuckles", typ="Weapon", subtyp="Fist")) == "fist_weapon"
    assert manager.infer_icon_key(SimpleNamespace(name="Claymore", typ="Weapon", subtyp="Longsword")) == "longsword"
    assert manager.infer_icon_key(SimpleNamespace(name="Rapier", typ="Weapon", subtyp="Sword")) == "sword"


def test_icon_manager_uses_default_icon_root():
    manager = IconManager()

    assert manager.icon_root == icon_manager.ICON_ROOT


def test_default_item_icon_map_resolves_gold_currency():
    manager = IconManager()

    assert manager.icon_key_for_item("Gold") == "gold"


def test_icon_manager_slot_and_generic_fallbacks(tmp_path):
    _write_icon_fixture(tmp_path)
    manager = IconManager(icon_root=tmp_path)

    assert manager.icon_key_for_item(SimpleNamespace(name="", typ="", subtyp=""), slot="Weapon") == "weapon"
    assert manager.icon_key_for_item(SimpleNamespace(name="", typ="", subtyp="")) == "generic_item"


def test_icon_manager_missing_frame_and_atlas_return_fallback(tmp_path):
    _write_icon_fixture(tmp_path)
    manager = IconManager(icon_root=tmp_path)

    icon = manager.get_icon_by_key("does_not_exist")

    assert icon.get_size() == (32, 32)
