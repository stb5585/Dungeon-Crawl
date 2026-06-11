#!/usr/bin/env python3
"""Focused coverage for compact enemy token generation."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.assets.enemy_combat_sprite_manager import EnemyCombatSpriteManager
from src.ui_pygame.assets.enemy_token_manager import EnemyTokenManager


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    yield


def _write_token_fixture(root: Path) -> None:
    root.mkdir(exist_ok=True)
    (root / "enemy_combat_sprite_map.json").write_text(json.dumps({"Goblin Raider": "goblin"}), encoding="utf-8")
    (root / "enemy_token_crop.json").write_text(
        json.dumps({"goblin": {"crop_x": 0, "crop_y": 0, "crop_w": 40, "crop_h": 40}}),
        encoding="utf-8",
    )

    goblin = pygame.Surface((80, 120), pygame.SRCALPHA)
    goblin.fill((0, 0, 0, 0))
    goblin.fill((220, 20, 20, 255), pygame.Rect(0, 0, 80, 40))
    goblin.fill((20, 180, 50, 255), pygame.Rect(0, 40, 80, 80))
    pygame.image.save(goblin, root / "goblin.png")

    generic = pygame.Surface((80, 120), pygame.SRCALPHA)
    generic.fill((90, 90, 120, 255), pygame.Rect(0, 0, 80, 120))
    pygame.image.save(generic, root / "generic_enemy.png")


def test_enemy_token_manager_generates_framed_token_with_crop_override(tmp_path):
    _write_token_fixture(tmp_path)
    sprite_manager = EnemyCombatSpriteManager(sprite_root=tmp_path)
    token_manager = EnemyTokenManager(sprite_manager, crop_path=tmp_path / "enemy_token_crop.json")

    token = token_manager.get_token(SimpleNamespace(name="Goblin Raider"))

    assert token.get_size() == (96, 96)
    assert token.get_at((48, 48)).r > token.get_at((48, 48)).g
    assert token.get_at((0, 0)).a == 0
    assert token_manager.get_token_by_name("Goblin Raider") is token
    assert token_manager.get_token_by_key("goblin") is token


def test_enemy_token_manager_default_crop_scaled_cache_and_missing_mapping(tmp_path):
    _write_token_fixture(tmp_path)
    sprite_manager = EnemyCombatSpriteManager(sprite_root=tmp_path)
    token_manager = EnemyTokenManager(sprite_manager, crop_path=tmp_path / "missing_crops.json")

    generic = token_manager.get_token(SimpleNamespace(name="Unknown Thing", enemy_typ=""))
    assert generic.get_size() == (96, 96)

    scaled = token_manager.get_scaled_token_by_key("goblin", (64, 64))
    scaled_again = token_manager.get_scaled_token_by_key("goblin", (64, 64))
    assert scaled.get_size() == (64, 64)
    assert scaled_again is scaled

    token_manager.clear_cache()
    assert token_manager.get_scaled_token_by_key("goblin", (64, 64)) is not scaled
