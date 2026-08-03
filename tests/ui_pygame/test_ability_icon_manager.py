"""Regression coverage for semantic progression icon assets."""

import pygame

from src.core.progression_manifest import ABILITY_ICON_KEYS
from src.ui_pygame.assets.ability_icon_manager import AbilityIconManager


def test_ability_icon_manifest_covers_every_semantic_key():
    manager = AbilityIconManager()

    assert set(manager.frames) == set(ABILITY_ICON_KEYS)


def test_ability_icon_frames_fit_inside_atlas():
    manager = AbilityIconManager()
    atlas = pygame.image.load(str(manager.atlas_path))
    atlas_rect = atlas.get_rect()

    assert all(atlas_rect.contains(frame.rect) for frame in manager.frames.values())


def test_ability_icon_manager_returns_native_icon_and_fallback():
    manager = AbilityIconManager()

    assert manager.get_icon("skill_offense").get_size() == (32, 32)
    assert manager.get_icon("missing_semantic_type").get_size() == (32, 32)
