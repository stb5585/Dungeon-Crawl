#!/usr/bin/env python3
"""Focused coverage for companion art loading."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.assets.companion_art_manager import CompanionArtManager


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    yield


def _write_sprite(path, color, size=(32, 48)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surface, color, pygame.Rect(4, 2, size[0] - 8, size[1] - 4))
    pygame.image.save(surface, path)


def test_companion_art_manager_loads_mapped_familiar_art(tmp_path):
    art_root = tmp_path / "companion_art"
    art_root.mkdir()
    _write_sprite(art_root / "fairy.png", (20, 220, 90, 255))
    (art_root / "companion_art_map.json").write_text(
        json.dumps({"Support": "fairy", "Fairy": "fairy"}),
        encoding="utf-8",
    )

    manager = CompanionArtManager(art_root=art_root)
    companion = SimpleNamespace(race="Fairy", spec="Support", name="Aster")

    assert manager.get_art_key_for_companion(companion) == "fairy"
    assert manager.get_sprite(companion).get_at((5, 5)) == pygame.Color(20, 220, 90, 255)
    assert manager.get_sprite_by_key("fairy") is manager.get_sprite_by_key("fairy")


def test_companion_art_manager_scales_and_clears_cache(tmp_path):
    art_root = tmp_path / "companion_art"
    art_root.mkdir()
    _write_sprite(art_root / "homunculus.png", (220, 120, 40, 255), size=(20, 40))

    manager = CompanionArtManager(art_root=art_root)
    companion = SimpleNamespace(race="Homunculus")

    scaled = manager.get_scaled_sprite(companion, (40, 40))
    scaled_again = manager.get_scaled_sprite(companion, (40, 40))

    assert scaled.get_size() == (40, 40)
    assert scaled_again is scaled
    assert scaled.get_at((0, 20)).a == 0
    assert scaled.get_at((20, 20)).a > 0

    manager.clear_cache()
    assert manager.get_scaled_sprite(companion, (40, 40)) is not scaled


def test_companion_art_manager_falls_back_to_enemy_sprite_manager(tmp_path):
    art_root = tmp_path / "companion_art"
    art_root.mkdir()
    fallback = pygame.Surface((24, 24), pygame.SRCALPHA)
    fallback.fill((30, 40, 220, 255))
    scaled = pygame.Surface((16, 16), pygame.SRCALPHA)
    scaled.fill((220, 40, 30, 255))

    class FakeEnemyManager:
        def __init__(self):
            self.sprite_calls = []
            self.scaled_calls = []

        def get_sprite(self, companion):
            self.sprite_calls.append(companion)
            return fallback

        def get_scaled_sprite(self, companion, target_size):
            self.scaled_calls.append((companion, target_size))
            return scaled

    enemy_manager = FakeEnemyManager()
    manager = CompanionArtManager(art_root=art_root, enemy_sprite_manager=enemy_manager)
    companion = SimpleNamespace(race="Dire Wolf", enemy_typ="Animal")

    assert manager.get_sprite(companion) is fallback
    assert manager.get_scaled_sprite(companion, (16, 16)) is scaled
    assert enemy_manager.sprite_calls == [companion]
    assert enemy_manager.scaled_calls == [(companion, (16, 16))]


def test_companion_art_manager_uses_mapped_enemy_sprite_fallback(tmp_path):
    art_root = tmp_path / "companion_art"
    art_root.mkdir()
    (art_root / "companion_art_map.json").write_text(
        json.dumps({"Patagon": "giant"}),
        encoding="utf-8",
    )
    fallback = pygame.Surface((24, 24), pygame.SRCALPHA)
    fallback.fill((80, 90, 100, 255))
    scaled = pygame.Surface((16, 16), pygame.SRCALPHA)
    scaled.fill((100, 90, 80, 255))

    class FakeEnemyManager:
        def __init__(self):
            self.sprite_key_calls = []
            self.scaled_key_calls = []

        def get_sprite_by_key(self, key):
            self.sprite_key_calls.append(key)
            return fallback

        def get_scaled_sprite_by_key(self, key, target_size):
            self.scaled_key_calls.append((key, target_size))
            return scaled

    enemy_manager = FakeEnemyManager()
    manager = CompanionArtManager(art_root=art_root, enemy_sprite_manager=enemy_manager)
    companion = SimpleNamespace(name="Patagon")

    assert manager.get_sprite(companion) is fallback
    assert manager.get_scaled_sprite(companion, (16, 16)) is scaled
    assert enemy_manager.sprite_key_calls == ["giant"]
    assert enemy_manager.scaled_key_calls == [("giant", (16, 16))]


def test_default_companion_art_assets_cover_core_familiars():
    manager = CompanionArtManager()

    for race in ("Homunculus", "Fairy", "Mephit", "Jinkin"):
        sprite = manager.get_sprite(SimpleNamespace(race=race))
        assert sprite.get_width() > 0
        assert sprite.get_height() > 0
        assert sprite.get_flags() & pygame.SRCALPHA
