"""Compact enemy token generation derived from combat sprites."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any

import pygame

from src.ui_pygame.assets.enemy_combat_sprite_manager import (
    ENEMY_COMBAT_SPRITE_ROOT,
    EnemyCombatSpriteManager,
    get_enemy_combat_sprite_manager,
)

logger = logging.getLogger(__name__)

DEFAULT_TOKEN_SIZE = (96, 96)
DEFAULT_CROP_RATIO = 0.72
_SHARED_ENEMY_TOKEN_MANAGER: EnemyTokenManager | None = None


@dataclass(frozen=True)
class EnemyTokenCrop:
    """Head-and-shoulders crop rectangle for one sprite archetype."""

    rect: pygame.Rect


class EnemyTokenManager:
    """Build and cache compact enemy tokens from combat sprites."""

    def __init__(
        self,
        sprite_manager: EnemyCombatSpriteManager | None = None,
        *,
        crop_path: Path | None = None,
        token_size: tuple[int, int] = DEFAULT_TOKEN_SIZE,
    ) -> None:
        self.sprite_manager = sprite_manager or get_enemy_combat_sprite_manager()
        self.crop_path = Path(crop_path or ENEMY_COMBAT_SPRITE_ROOT / "enemy_token_crop.json")
        self.token_size = (max(1, int(token_size[0])), max(1, int(token_size[1])))
        self.crop_overrides: dict[str, EnemyTokenCrop] = {}
        self._token_cache: dict[str, pygame.Surface] = {}
        self._framed_cache: dict[str, pygame.Surface] = {}
        self._scaled_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self.load_crop_overrides()

    def load_crop_overrides(self) -> None:
        if not self.crop_path.exists():
            return
        try:
            data = json.loads(self.crop_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load enemy token crops %s: %s", self.crop_path, exc)
            return

        for key, entry in data.items():
            try:
                rect = pygame.Rect(
                    int(entry["crop_x"]),
                    int(entry["crop_y"]),
                    int(entry["crop_w"]),
                    int(entry["crop_h"]),
                )
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Skipping invalid enemy token crop %s: %s", key, exc)
                continue
            self.crop_overrides[str(key)] = EnemyTokenCrop(rect=rect)

    def get_token(self, enemy: Any) -> pygame.Surface:
        return self.get_token_by_key(self.sprite_manager.get_sprite_key_for_enemy(enemy))

    def get_token_by_name(self, enemy_name: str) -> pygame.Surface:
        return self.get_token_by_key(self.sprite_manager.get_sprite_key_for_enemy(enemy_name))

    def get_token_by_key(self, sprite_key: str) -> pygame.Surface:
        key = self.sprite_manager._valid_key(sprite_key)
        cached = self._framed_cache.get(key)
        if cached is not None:
            return cached

        cropped = self._cropped_token_by_key(key)
        framed = self._frame_token(cropped)
        self._framed_cache[key] = framed
        return framed

    def get_scaled_token(self, enemy: Any, target_size: tuple[int, int]) -> pygame.Surface:
        return self.get_scaled_token_by_key(
            self.sprite_manager.get_sprite_key_for_enemy(enemy), target_size
        )

    def get_scaled_token_by_name(
        self, enemy_name: str, target_size: tuple[int, int]
    ) -> pygame.Surface:
        return self.get_scaled_token_by_key(
            self.sprite_manager.get_sprite_key_for_enemy(enemy_name), target_size
        )

    def get_scaled_token_by_key(
        self, sprite_key: str, target_size: tuple[int, int]
    ) -> pygame.Surface:
        key = self.sprite_manager._valid_key(sprite_key)
        target = (max(1, int(target_size[0])), max(1, int(target_size[1])))
        cache_key = (key, target)
        cached = self._scaled_cache.get(cache_key)
        if cached is not None:
            return cached

        token = self.get_token_by_key(key)
        scaled = pygame.transform.smoothscale(token, target)
        self._scaled_cache[cache_key] = scaled
        return scaled

    def _cropped_token_by_key(self, key: str) -> pygame.Surface:
        cached = self._token_cache.get(key)
        if cached is not None:
            return cached

        sprite = self.sprite_manager.get_sprite_by_key(key)
        crop = self._crop_rect_for_key(key, sprite.get_size())
        try:
            cropped = sprite.subsurface(crop).copy()
        except ValueError:
            logger.warning("Enemy token crop out of bounds for %s: %s", key, crop)
            cropped = sprite.subsurface(self._default_crop_rect(sprite.get_size())).copy()
        token = pygame.transform.smoothscale(cropped, self.token_size)
        self._token_cache[key] = token
        return token

    def _crop_rect_for_key(self, key: str, render_size: tuple[int, int]) -> pygame.Rect:
        override = self.crop_overrides.get(key)
        if override is None:
            return self._default_crop_rect(render_size)
        render_rect = pygame.Rect((0, 0), render_size)
        return override.rect.clip(render_rect)

    @staticmethod
    def _default_crop_rect(render_size: tuple[int, int]) -> pygame.Rect:
        width, height = render_size
        crop_size = max(1, int(min(width, height) * DEFAULT_CROP_RATIO))
        x = max(0, (width - crop_size) // 2)
        y = max(0, int(height * 0.12))
        if y + crop_size > height:
            y = max(0, height - crop_size)
        return pygame.Rect(x, y, crop_size, crop_size)

    def _frame_token(self, token: pygame.Surface) -> pygame.Surface:
        size = token.get_size()
        framed = pygame.Surface(size, pygame.SRCALPHA)

        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect().inflate(-4, -4))

        clipped = token.copy()
        clipped.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        framed.blit(clipped, (0, 0))

        outer = framed.get_rect().inflate(-2, -2)
        inner = framed.get_rect().inflate(-8, -8)
        pygame.draw.ellipse(framed, (34, 28, 20, 255), outer, 3)
        pygame.draw.ellipse(framed, (174, 128, 65, 255), outer, 1)
        pygame.draw.ellipse(framed, (236, 211, 145, 185), inner, 1)
        return framed

    def clear_cache(self) -> None:
        self._token_cache.clear()
        self._framed_cache.clear()
        self._scaled_cache.clear()


def get_enemy_token_manager() -> EnemyTokenManager:
    """Return the shared runtime enemy token manager."""
    global _SHARED_ENEMY_TOKEN_MANAGER
    if _SHARED_ENEMY_TOKEN_MANAGER is None:
        _SHARED_ENEMY_TOKEN_MANAGER = EnemyTokenManager()
    return _SHARED_ENEMY_TOKEN_MANAGER
