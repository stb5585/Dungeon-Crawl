"""Transparent enemy combat sprite loading for battlefield presentation."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pygame

from src.ui_pygame.assets.enemy_render_manager import (
    EnemyRenderManager,
    get_enemy_render_manager,
)


logger = logging.getLogger(__name__)

ENEMY_COMBAT_SPRITE_ROOT = Path(__file__).resolve().parent / "enemy_combat_sprites"
_SHARED_ENEMY_COMBAT_SPRITE_MANAGER: EnemyCombatSpriteManager | None = None


class EnemyCombatSpriteManager:
    """Resolve enemies to transparent full-body combat sprites."""

    def __init__(
        self,
        render_manager: EnemyRenderManager | None = None,
        *,
        sprite_root: Path | None = None,
        sprite_map_path: Path | None = None,
    ) -> None:
        self.render_manager = render_manager or get_enemy_render_manager()
        self.sprite_root = Path(sprite_root or ENEMY_COMBAT_SPRITE_ROOT)
        self.sprite_map_path = Path(sprite_map_path or self.sprite_root / "enemy_combat_sprite_map.json")
        self.available_keys: set[str] = {
            path.stem
            for path in self.sprite_root.glob("*.png")
            if path.is_file() and not path.stem.endswith("_review_sheet")
        }
        self.sprite_map: dict[str, str] = {}
        self._sprite_cache: dict[str, pygame.Surface] = {}
        self._scaled_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self._fallback_surface: pygame.Surface | None = None
        self.load_map()

    def load_map(self) -> None:
        if not self.sprite_map_path.exists():
            return
        try:
            data = json.loads(self.sprite_map_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load enemy combat sprite map %s: %s", self.sprite_map_path, exc)
            return
        self.sprite_map = {str(name): str(key) for name, key in data.items()}

    def get_sprite(self, enemy: Any) -> pygame.Surface:
        return self.get_sprite_by_key(self.get_sprite_key_for_enemy(enemy))

    def get_sprite_by_name(self, enemy_name: str) -> pygame.Surface:
        return self.get_sprite_by_key(self.get_sprite_key_for_enemy(enemy_name))

    def get_sprite_by_key(self, sprite_key: str) -> pygame.Surface:
        key = self._valid_key(sprite_key)
        cached = self._sprite_cache.get(key)
        if cached is not None:
            return cached

        path = self.sprite_root / f"{key}.png"
        if not path.exists():
            logger.warning("Enemy combat sprite missing for %s: %s", key, path)
            return self.fallback_surface()

        try:
            surface = pygame.image.load(str(path))
        except (pygame.error, OSError) as exc:
            logger.warning("Could not load enemy combat sprite %s: %s", path, exc)
            return self.fallback_surface()

        try:
            surface = surface.convert_alpha()
        except pygame.error:
            surface = surface.copy()

        self._sprite_cache[key] = surface
        return surface

    def get_scaled_sprite(self, enemy: Any, target_size: tuple[int, int]) -> pygame.Surface:
        return self.get_scaled_sprite_by_key(self.get_sprite_key_for_enemy(enemy), target_size)

    def get_scaled_sprite_by_name(self, enemy_name: str, target_size: tuple[int, int]) -> pygame.Surface:
        return self.get_scaled_sprite_by_key(self.get_sprite_key_for_enemy(enemy_name), target_size)

    def get_scaled_sprite_by_key(self, sprite_key: str, target_size: tuple[int, int]) -> pygame.Surface:
        key = self._valid_key(sprite_key)
        target = (max(1, int(target_size[0])), max(1, int(target_size[1])))
        cache_key = (key, target)
        cached = self._scaled_cache.get(cache_key)
        if cached is not None:
            return cached

        sprite = self.get_sprite_by_key(key)
        source_w, source_h = sprite.get_size()
        scale = min(target[0] / source_w, target[1] / source_h)
        fitted_size = (max(1, int(source_w * scale)), max(1, int(source_h * scale)))
        fitted = pygame.transform.smoothscale(sprite, fitted_size)
        surface = pygame.Surface(target, pygame.SRCALPHA)
        surface.blit(fitted, ((target[0] - fitted_size[0]) // 2, (target[1] - fitted_size[1]) // 2))
        self._scaled_cache[cache_key] = surface
        return surface

    def get_sprite_key_for_enemy(self, enemy: Any) -> str:
        name = self.render_manager.enemy_name(enemy)
        if name in self.sprite_map:
            return self._valid_key(self.sprite_map[name], prefer_boss=self.render_manager._is_boss(enemy))

        if self.sprite_map:
            normalized_name = self.render_manager.normalize_key(name)
            if normalized_name in self.available_keys:
                return normalized_name

            class_name = enemy.__name__ if isinstance(enemy, type) else type(enemy).__name__
            class_key = self.render_manager.normalize_key(class_name)
            if class_key in self.available_keys:
                return class_key

            archetype = self.render_manager._attribute_key(enemy, "combat_sprite_archetype", "render_archetype", "archetype")
            if archetype:
                return self._valid_key(archetype, prefer_boss=self.render_manager._is_boss(enemy))

            if self.render_manager._is_boss(enemy):
                return self._valid_key("boss")
            return self._valid_key("generic_enemy")

        render_key = self.render_manager.get_render_key_for_enemy(enemy)
        return self._valid_key(render_key, prefer_boss=self.render_manager._is_boss(enemy))

    def _valid_key(self, key: str, *, prefer_boss: bool = False) -> str:
        if key in self.available_keys:
            return key
        if prefer_boss and "boss" in self.available_keys:
            return "boss"
        if "generic_enemy" in self.available_keys:
            return "generic_enemy"
        return str(key or "generic_enemy")

    def fallback_surface(self) -> pygame.Surface:
        if self._fallback_surface is not None:
            return self._fallback_surface
        surface = pygame.Surface((384, 384), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (34, 31, 36, 235), pygame.Rect(128, 84, 128, 216))
        pygame.draw.polygon(surface, (74, 63, 50, 245), [(152, 138), (232, 138), (250, 270), (134, 270)])
        pygame.draw.circle(surface, (210, 172, 88, 255), (168, 154), 7)
        pygame.draw.circle(surface, (210, 172, 88, 255), (216, 154), 7)
        self._fallback_surface = surface
        return surface

    def clear_cache(self) -> None:
        self._sprite_cache.clear()
        self._scaled_cache.clear()
        self._fallback_surface = None


def get_enemy_combat_sprite_manager() -> EnemyCombatSpriteManager:
    """Return the shared runtime enemy combat sprite manager."""
    global _SHARED_ENEMY_COMBAT_SPRITE_MANAGER
    if _SHARED_ENEMY_COMBAT_SPRITE_MANAGER is None:
        _SHARED_ENEMY_COMBAT_SPRITE_MANAGER = EnemyCombatSpriteManager()
    return _SHARED_ENEMY_COMBAT_SPRITE_MANAGER
