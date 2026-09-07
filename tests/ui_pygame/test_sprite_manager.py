#!/usr/bin/env python3
"""Focused coverage for shared pygame sprite loading."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.assets import sprite_manager
from src.ui_pygame.assets.sprite_manager import SpriteManager


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    yield


def test_enemy_character_sprite_uses_combat_sprite_manager(monkeypatch):
    calls = []
    combat_surface = pygame.Surface((128, 128), pygame.SRCALPHA)

    class DummyCombatSpriteManager:
        def get_scaled_sprite(self, character, size):
            calls.append((character.name, size))
            return combat_surface

    manager = SpriteManager()
    monkeypatch.setattr(
        sprite_manager,
        "get_enemy_combat_sprite_manager",
        lambda: DummyCombatSpriteManager(),
    )
    monkeypatch.setattr(
        manager,
        "load_sprite",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("enemy sprites must not load from sprites/enemies")
        ),
    )

    result = manager.get_character_sprite(SimpleNamespace(name="Goblin"))

    assert result is combat_surface
    assert calls == [("Goblin", (128, 128))]


def test_preload_common_sprites_does_not_load_retired_enemy_directory(monkeypatch):
    loaded = []
    manager = SpriteManager()
    monkeypatch.setattr(
        manager,
        "load_sprite",
        lambda name, category="sprites": loaded.append((name, category)) or None,
    )

    manager.preload_common_sprites()

    assert loaded
    assert all(category != "sprites/enemies" for _name, category in loaded)
