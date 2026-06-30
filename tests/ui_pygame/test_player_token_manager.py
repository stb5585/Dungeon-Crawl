#!/usr/bin/env python3
"""Focused coverage for compact player portrait tokens."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.assets.player_token_manager import PlayerTokenManager
from src.ui_pygame.assets.portrait_manager import PortraitManager


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    yield


def _write_portrait_fixture(root: Path) -> Path:
    mapping_json = root / "portrait_atlas_mapping.json"
    mapping_json.write_text(
        json.dumps(
            {
                "universal_frames": {
                    "male_1": {"x": 0, "y": 0, "w": 100, "h": 160},
                    "female_1": {"x": 0, "y": 160, "w": 100, "h": 160},
                },
                "sheets": {
                    "human": {"image": "human_base_portraits.png", "uses": "universal_frames"},
                },
            }
        ),
        encoding="utf-8",
    )
    surface = pygame.Surface((100, 320), pygame.SRCALPHA)
    surface.fill((20, 20, 30, 255))
    surface.fill((210, 170, 130, 255), pygame.Rect(24, 14, 52, 52))
    surface.fill((70, 40, 28, 255), pygame.Rect(24, 66, 52, 80))
    pygame.image.save(surface, root / "human_base_portraits.png")
    return mapping_json


def test_player_token_manager_crops_face_and_caches_scaled_token(tmp_path):
    atlas_json = _write_portrait_fixture(tmp_path)
    portrait_manager = PortraitManager(portrait_root=tmp_path, atlas_json=atlas_json)
    token_manager = PlayerTokenManager(portrait_manager)
    player = SimpleNamespace(
        name="Hero",
        race=SimpleNamespace(name="Human"),
        sex="Male",
        cls=SimpleNamespace(name="Warrior"),
    )

    token = token_manager.get_token(player)
    cached = token_manager.get_token(player)
    scaled = token_manager.get_scaled_token(player, (46, 46))
    scaled_again = token_manager.get_scaled_token(player, (46, 46))

    assert token.get_size() == (96, 96)
    assert cached is token
    assert scaled.get_size() == (46, 46)
    assert scaled_again is scaled
    assert token.get_at((48, 48)).r > token.get_at((48, 48)).b
    assert token.get_at((0, 0)).a == 0
    assert token.get_at((8, 48)).a == 0
