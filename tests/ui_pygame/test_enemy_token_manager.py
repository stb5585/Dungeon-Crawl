#!/usr/bin/env python3
"""Focused coverage for compact enemy token generation."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.assets.enemy_render_manager import EnemyRenderManager
from src.ui_pygame.assets.enemy_token_manager import EnemyTokenManager
from tools.validate_enemy_render_atlas import validate_enemy_render_atlas


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    yield


def _write_token_fixture(root: Path) -> None:
    root.mkdir(exist_ok=True)
    manifest = {
        "goblin": {"x": 0, "y": 0, "w": 80, "h": 120},
        "generic_enemy": {"x": 80, "y": 0, "w": 80, "h": 120},
    }
    (root / "enemy_render_atlas.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "enemy_render_map.json").write_text(json.dumps({"Goblin Raider": "goblin"}), encoding="utf-8")
    (root / "enemy_token_crop.json").write_text(
        json.dumps({"goblin": {"crop_x": 0, "crop_y": 0, "crop_w": 40, "crop_h": 40}}),
        encoding="utf-8",
    )

    surface = pygame.Surface((160, 120), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    surface.fill((220, 20, 20, 255), pygame.Rect(0, 0, 80, 40))
    surface.fill((20, 180, 50, 255), pygame.Rect(0, 40, 80, 80))
    surface.fill((90, 90, 120, 255), pygame.Rect(80, 0, 80, 120))
    pygame.image.save(surface, root / "enemy_render_atlas.png")


def test_enemy_token_manager_generates_framed_token_with_crop_override(tmp_path):
    _write_token_fixture(tmp_path)
    render_manager = EnemyRenderManager(render_root=tmp_path)
    token_manager = EnemyTokenManager(render_manager, crop_path=tmp_path / "enemy_token_crop.json")

    token = token_manager.get_token(SimpleNamespace(name="Goblin Raider"))

    assert token.get_size() == (96, 96)
    assert token.get_at((48, 48)).r > token.get_at((48, 48)).g
    assert token.get_at((0, 0)).a == 0
    assert token_manager.get_token_by_name("Goblin Raider") is token
    assert token_manager.get_token_by_key("goblin") is token


def test_enemy_token_manager_default_crop_scaled_cache_and_missing_mapping(tmp_path):
    _write_token_fixture(tmp_path)
    render_manager = EnemyRenderManager(render_root=tmp_path)
    token_manager = EnemyTokenManager(render_manager, crop_path=tmp_path / "missing_crops.json")

    generic = token_manager.get_token(SimpleNamespace(name="Unknown Thing", enemy_typ=""))
    assert generic.get_size() == (96, 96)

    scaled = token_manager.get_scaled_token_by_key("goblin", (64, 64))
    scaled_again = token_manager.get_scaled_token_by_key("goblin", (64, 64))
    assert scaled.get_size() == (64, 64)
    assert scaled_again is scaled

    token_manager.clear_cache()
    assert token_manager.get_scaled_token_by_key("goblin", (64, 64)) is not scaled


def test_default_enemy_render_atlas_validation_passes():
    issues = validate_enemy_render_atlas(Path("src/ui_pygame/assets/enemy_renders"))

    assert issues == []


def test_enemy_render_atlas_validation_reports_missing_and_overlap(tmp_path):
    (tmp_path / "enemy_render_atlas.json").write_text(
        json.dumps(
            {
                "goblin": {"x": 0, "y": 0, "w": 256, "h": 320},
                "kobold": {"x": 0, "y": 0, "w": 256, "h": 320},
            }
        ),
        encoding="utf-8",
    )
    surface = pygame.Surface((256, 320), pygame.SRCALPHA)
    pygame.image.save(surface, tmp_path / "enemy_render_atlas.png")
    (tmp_path / "enemy_token_crop.json").write_text(
        json.dumps({"goblin": {"crop_x": 0, "crop_y": 0, "crop_w": 999, "crop_h": 96}}),
        encoding="utf-8",
    )

    issues = validate_enemy_render_atlas(tmp_path)

    assert any("manifest missing keys" in issue for issue in issues)
    assert any("frames overlap" in issue for issue in issues)
    assert any("token crop" in issue for issue in issues)
