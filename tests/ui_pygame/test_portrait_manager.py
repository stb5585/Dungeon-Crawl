#!/usr/bin/env python3
"""Focused coverage for portrait atlas loading and composition."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pygame

from src.ui_pygame.assets.portrait_manager import PortraitManager


def _write_atlas_json(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "image": "atlas.png",
                "entries": {
                    "human_male": {"x": 0, "y": 0, "w": 10, "h": 10, "race": "human", "gender": "male"},
                    "half_orc_female": {
                        "x": 10,
                        "y": 0,
                        "w": 10,
                        "h": 10,
                        "race": "half_orc",
                        "gender": "female",
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def _surface(size=(10, 10), color=(0, 0, 0, 255)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface


def test_portrait_atlas_json_loading(tmp_path):
    atlas_json = tmp_path / "base_portrait_atlas.json"
    _write_atlas_json(atlas_json)

    manager = PortraitManager(portrait_root=tmp_path, atlas_json=atlas_json)

    assert manager.atlas_image_path == tmp_path / "atlas.png"
    assert manager.frames["human_male"].rect == pygame.Rect(0, 0, 10, 10)
    assert manager.frames["half_orc_female"].race == "half_orc"


def test_portrait_key_normalization_variants():
    assert PortraitManager.normalize_key("Half Orc") == "half_orc"
    assert PortraitManager.normalize_key("half_orc") == "half_orc"
    assert PortraitManager.normalize_key("Half Giant") == "half_giant"
    assert PortraitManager.normalize_key("Male") == "male"
    assert PortraitManager.normalize_key("female") == "female"
    assert PortraitManager.entry_key(SimpleNamespace(name="Half Orc"), "Female") == "half_orc_female"


def test_successful_base_portrait_lookup_from_atlas(tmp_path):
    atlas_json = tmp_path / "base_portrait_atlas.json"
    _write_atlas_json(atlas_json)
    (tmp_path / "atlas.png").touch()
    manager = PortraitManager(portrait_root=tmp_path, atlas_json=atlas_json)
    atlas = _surface((20, 10), (0, 0, 0, 0))
    atlas.fill((255, 0, 0, 255), pygame.Rect(0, 0, 10, 10))
    atlas.fill((0, 0, 255, 255), pygame.Rect(10, 0, 10, 10))
    manager.load_image = lambda _path: atlas

    portrait = manager.base_portrait("Human", "Male")
    half_orc = manager.base_portrait("Half Orc", "Female")

    assert portrait.get_size() == (10, 10)
    assert portrait.get_at((1, 1)) == pygame.Color(255, 0, 0, 255)
    assert half_orc.get_at((1, 1)) == pygame.Color(0, 0, 255, 255)


def test_missing_portrait_returns_placeholder_and_logs_warning(tmp_path, caplog):
    manager = PortraitManager(portrait_root=tmp_path, atlas_json=tmp_path / "missing.json")

    with caplog.at_level("WARNING"):
        portrait = manager.get_portrait("Unknown Race", "Unknown Gender")

    assert portrait.get_size() == (225, 400)
    assert "Portrait missing" in caplog.text


def test_missing_overlay_is_recorded_and_skipped(tmp_path):
    atlas_json = tmp_path / "base_portrait_atlas.json"
    _write_atlas_json(atlas_json)
    (tmp_path / "atlas.png").touch()
    manager = PortraitManager(portrait_root=tmp_path, atlas_json=atlas_json)
    manager.load_image = lambda _path: _surface((20, 10), (10, 20, 30, 255))

    portrait = manager.get_portrait("Human", "Male", class_name="Warrior")

    assert portrait.get_size() == (10, 10)
    assert manager.missing_overlays
    assert manager.missing_overlays[-1].name == "warrior.png"


def test_portrait_composition_order_and_cache_reuse(tmp_path):
    atlas_json = tmp_path / "base_portrait_atlas.json"
    _write_atlas_json(atlas_json)
    (tmp_path / "atlas.png").touch()
    manager = PortraitManager(portrait_root=tmp_path, atlas_json=atlas_json)
    manager.load_image = lambda _path: _surface((20, 10), (10, 10, 10, 255))
    order = []
    colors = {
        "warrior.png": (20, 20, 20, 255),
        "paladin.png": (30, 30, 30, 255),
        "crusader.png": (40, 40, 40, 255),
        "blessed.png": (50, 50, 50, 255),
    }

    def load_overlay(path):
        order.append(path.name)
        return _surface((10, 10), colors[path.name])

    manager.load_overlay = load_overlay

    portrait = manager.get_portrait(
        "Human",
        "Male",
        class_name="Warrior",
        first_promotion="Paladin",
        second_promotion="Crusader",
        effects=("Blessed",),
    )
    cached = manager.get_portrait(
        "Human",
        "Male",
        class_name="Warrior",
        first_promotion="Paladin",
        second_promotion="Crusader",
        effects=("Blessed",),
    )

    assert order == ["warrior.png", "paladin.png", "crusader.png", "blessed.png"]
    assert portrait.get_at((1, 1)) == pygame.Color(50, 50, 50, 255)
    assert cached is portrait


def test_portrait_cache_distinguishes_promotion_and_effects(tmp_path):
    atlas_json = tmp_path / "base_portrait_atlas.json"
    _write_atlas_json(atlas_json)
    (tmp_path / "atlas.png").touch()
    manager = PortraitManager(portrait_root=tmp_path, atlas_json=atlas_json)
    manager.load_image = lambda _path: _surface((20, 10), (10, 10, 10, 255))
    manager.load_overlay = lambda _path: None

    base = manager.get_portrait("Human", "Male", first_promotion="Paladin")
    promoted = manager.get_portrait("Human", "Male", first_promotion="Crusader")
    affected = manager.get_portrait("Human", "Male", first_promotion="Paladin", effects=("Blessed",))

    assert promoted is not base
    assert affected is not base
