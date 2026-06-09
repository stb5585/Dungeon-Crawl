#!/usr/bin/env python3
"""Focused coverage for large item render atlas loading."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pygame

from src.ui_pygame.assets.item_render_manager import ItemRenderManager


def _write_render_fixture(root: Path) -> None:
    root.mkdir(exist_ok=True)
    manifest = {
        "longsword": {"x": 0, "y": 0, "w": 80, "h": 140},
        "greatsword": {"x": 80, "y": 0, "w": 80, "h": 140},
        "warhammer": {"x": 160, "y": 0, "w": 80, "h": 140},
        "weapon": {"x": 0, "y": 140, "w": 80, "h": 140},
        "armor": {"x": 80, "y": 140, "w": 80, "h": 140},
        "helmet": {"x": 160, "y": 140, "w": 80, "h": 140},
        "generic_item": {"x": 160, "y": 140, "w": 80, "h": 140},
    }
    (root / "item_render_atlas.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "item_render_map.json").write_text(json.dumps({"Claymore": "greatsword"}), encoding="utf-8")
    (root / "item_icon_map.json").write_text(json.dumps({"Iron Sword": "sword", "War Hammer": "hammer"}), encoding="utf-8")
    surface = pygame.Surface((240, 280), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    surface.fill((255, 0, 0, 255), pygame.Rect(0, 0, 80, 140))
    surface.fill((0, 255, 0, 255), pygame.Rect(80, 0, 80, 140))
    surface.fill((0, 0, 255, 255), pygame.Rect(160, 0, 80, 140))
    surface.fill((255, 255, 0, 255), pygame.Rect(0, 140, 80, 140))
    surface.fill((255, 0, 255, 255), pygame.Rect(80, 140, 80, 140))
    surface.fill((0, 255, 255, 255), pygame.Rect(160, 140, 80, 140))
    pygame.image.save(surface, root / "item_render_atlas.png")


def test_item_render_manager_loads_manifest_and_exact_mapping(tmp_path):
    _write_render_fixture(tmp_path)

    manager = ItemRenderManager(
        render_root=tmp_path,
        icon_map_path=tmp_path / "item_icon_map.json",
        enhance_artwork=False,
    )

    assert manager.frames["longsword"].rect == pygame.Rect(0, 0, 80, 140)
    assert manager.get_render_key_for_item(SimpleNamespace(name="Claymore")) == "greatsword"
    assert manager.get_render_by_name("Claymore").get_at((1, 1)) == pygame.Color(0, 255, 0, 255)


def test_item_render_manager_uses_icon_map_conversion_and_category_fallbacks(tmp_path):
    _write_render_fixture(tmp_path)
    manager = ItemRenderManager(
        render_root=tmp_path,
        icon_map_path=tmp_path / "item_icon_map.json",
        enhance_artwork=False,
    )

    assert manager.get_render_key_for_item(SimpleNamespace(name="Iron Sword")) == "longsword"
    assert manager.get_render_key_for_item(SimpleNamespace(name="War Hammer")) == "warhammer"
    assert manager.get_render_key_for_item(SimpleNamespace(name="Mystery Axe", typ="Weapon", subtyp="Unknown")) == "weapon"
    assert manager.get_render_key_for_item(SimpleNamespace(name="Mystery Plate", typ="Armor", subtyp="Unknown")) == "armor"
    assert manager.get_render_key_for_item(SimpleNamespace(name="Mystery Helm", typ="Helmet", subtyp="Heavy")) == "helmet"
    assert manager.get_render_key_for_item(SimpleNamespace(name="Mystery Thing", typ="", subtyp="")) == "generic_item"
    assert "Mystery Thing" in manager.missing_mappings


def test_item_render_manager_missing_frame_and_cache_reuse(tmp_path):
    _write_render_fixture(tmp_path)
    manager = ItemRenderManager(
        render_root=tmp_path,
        icon_map_path=tmp_path / "item_icon_map.json",
        enhance_artwork=False,
    )

    generic = manager.get_render_by_key("does_not_exist")
    again = manager.get_render_by_key("does_not_exist")

    assert generic.get_at((1, 1)) == pygame.Color(0, 255, 255, 255)
    assert again is generic


def test_item_render_manager_scaled_render_preserves_aspect_and_caches(tmp_path):
    _write_render_fixture(tmp_path)
    manager = ItemRenderManager(
        render_root=tmp_path,
        icon_map_path=tmp_path / "item_icon_map.json",
        enhance_artwork=False,
    )

    scaled = manager.get_scaled_render_by_key("longsword", (100, 100))
    cached = manager.get_scaled_render_by_key("longsword", (100, 100))

    assert scaled is cached
    assert scaled.get_size() == (100, 100)
    assert scaled.get_at((1, 50)).a == 0
    assert scaled.get_at((50, 50)).a > 0


def test_item_render_manager_missing_atlas_returns_fallback(tmp_path):
    root = tmp_path / "missing"
    root.mkdir()
    (root / "item_render_atlas.json").write_text(
        json.dumps({"generic_item": {"x": 0, "y": 0, "w": 80, "h": 140}}),
        encoding="utf-8",
    )
    (root / "item_render_map.json").write_text("{}", encoding="utf-8")
    (root / "item_icon_map.json").write_text("{}", encoding="utf-8")
    manager = ItemRenderManager(
        render_root=root,
        icon_map_path=root / "item_icon_map.json",
        enhance_artwork=False,
    )

    assert manager.get_render_by_key("generic_item").get_size() == (160, 280)


def test_item_render_manager_enhances_cached_display_art(tmp_path):
    _write_render_fixture(tmp_path)
    manager = ItemRenderManager(render_root=tmp_path, icon_map_path=tmp_path / "item_icon_map.json")

    render = manager.get_render_by_key("longsword")
    cached = manager.get_render_by_key("longsword")

    assert cached is render
    assert render.get_at((1, 1)).r == 255
    assert render.get_at((1, 1)).a == 255


def test_item_render_manager_contrast_lift_preserves_alpha():
    source = pygame.Surface((2, 1), pygame.SRCALPHA)
    source.set_at((0, 0), pygame.Color(40, 35, 30, 255))
    source.set_at((1, 0), pygame.Color(20, 20, 20, 0))

    enhanced = ItemRenderManager.enhance_display_contrast(source)

    assert enhanced.get_at((0, 0)).r > source.get_at((0, 0)).r
    assert enhanced.get_at((1, 0)).a == 0
