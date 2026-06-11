"""Dedicated enemy combat artwork loading for combat presentation panels."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pygame

from src.ui_pygame.assets.enemy_render_manager import (
    EnemyRenderManager,
    get_enemy_render_manager,
)


logger = logging.getLogger(__name__)

ENEMY_COMBAT_ART_ROOT = Path(__file__).resolve().parent / "enemy_combat_art"
_SHARED_ENEMY_COMBAT_ART_MANAGER: EnemyCombatArtManager | None = None


class EnemyCombatArtManager:
    """Resolve enemies to full-body combat artwork without affecting sprites."""

    def __init__(
        self,
        render_manager: EnemyRenderManager | None = None,
        *,
        art_root: Path | None = None,
    ) -> None:
        self.render_manager = render_manager or get_enemy_render_manager()
        self.art_root = Path(art_root or ENEMY_COMBAT_ART_ROOT)
        self.available_keys: set[str] = {
            path.stem
            for path in self.art_root.glob("*.png")
            if path.is_file() and not path.stem.endswith("_review_sheet")
        }
        self._art_cache: dict[str, pygame.Surface] = {}
        self._scaled_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self._fallback_surface: pygame.Surface | None = None

    def get_art(self, enemy: Any) -> pygame.Surface:
        return self.get_art_by_key(self.get_art_key_for_enemy(enemy))

    def get_art_by_name(self, enemy_name: str) -> pygame.Surface:
        return self.get_art_by_key(self.get_art_key_for_enemy(enemy_name))

    def get_art_by_key(self, archetype: str) -> pygame.Surface:
        key = self._valid_key(archetype)
        cached = self._art_cache.get(key)
        if cached is not None:
            return cached

        path = self.art_root / f"{key}.png"
        if not path.exists():
            logger.warning("Enemy combat artwork missing for %s: %s", key, path)
            return self.fallback_surface()

        try:
            surface = pygame.image.load(str(path))
        except (pygame.error, OSError) as exc:
            logger.warning("Could not load enemy combat artwork %s: %s", path, exc)
            return self.fallback_surface()

        try:
            surface = surface.convert_alpha()
        except pygame.error:
            surface = surface.copy()

        self._art_cache[key] = surface
        return surface

    def get_scaled_art(self, enemy: Any, target_size: tuple[int, int]) -> pygame.Surface:
        return self.get_scaled_art_by_key(self.get_art_key_for_enemy(enemy), target_size)

    def get_scaled_art_by_name(self, enemy_name: str, target_size: tuple[int, int]) -> pygame.Surface:
        return self.get_scaled_art_by_key(self.get_art_key_for_enemy(enemy_name), target_size)

    def get_scaled_art_by_key(self, archetype: str, target_size: tuple[int, int]) -> pygame.Surface:
        key = self._valid_key(archetype)
        target = (max(1, int(target_size[0])), max(1, int(target_size[1])))
        cache_key = (key, target)
        cached = self._scaled_cache.get(cache_key)
        if cached is not None:
            return cached

        art = self.get_art_by_key(key)
        source_w, source_h = art.get_size()
        scale = min(target[0] / source_w, target[1] / source_h)
        fitted_size = (max(1, int(source_w * scale)), max(1, int(source_h * scale)))
        fitted = pygame.transform.smoothscale(art, fitted_size)
        surface = pygame.Surface(target, pygame.SRCALPHA)
        surface.blit(fitted, ((target[0] - fitted_size[0]) // 2, (target[1] - fitted_size[1]) // 2))
        self._scaled_cache[cache_key] = surface
        return surface

    def get_art_key_for_enemy(self, enemy: Any) -> str:
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
        surface = pygame.Surface((256, 320), pygame.SRCALPHA)
        surface.fill((10, 10, 14, 255))
        pygame.draw.rect(surface, (118, 88, 50), surface.get_rect(), 2)
        pygame.draw.ellipse(surface, (58, 52, 62), pygame.Rect(54, 52, 148, 220))
        pygame.draw.line(surface, (176, 148, 92), (86, 238), (170, 82), 4)
        pygame.draw.circle(surface, (215, 184, 112), (112, 128), 6)
        pygame.draw.circle(surface, (215, 184, 112), (148, 128), 6)
        self._fallback_surface = surface
        return surface

    def clear_cache(self) -> None:
        self._art_cache.clear()
        self._scaled_cache.clear()
        self._fallback_surface = None


def get_enemy_combat_art_manager() -> EnemyCombatArtManager:
    """Return the shared runtime enemy combat artwork manager."""
    global _SHARED_ENEMY_COMBAT_ART_MANAGER
    if _SHARED_ENEMY_COMBAT_ART_MANAGER is None:
        _SHARED_ENEMY_COMBAT_ART_MANAGER = EnemyCombatArtManager()
    return _SHARED_ENEMY_COMBAT_ART_MANAGER
