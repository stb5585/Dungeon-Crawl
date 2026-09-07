"""Transparent companion and familiar artwork loading."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pygame

from src.paths import PYGAME_ASSETS_DIR

from .enemy_combat_sprite_manager import get_enemy_combat_sprite_manager

logger = logging.getLogger(__name__)

COMPANION_ART_ROOT = PYGAME_ASSETS_DIR / "companion_art"
_SHARED_COMPANION_ART_MANAGER: CompanionArtManager | None = None


class CompanionArtManager:
    """Resolve familiars, tamed companions, and summons to display artwork."""

    def __init__(
        self,
        *,
        art_root: Path | None = None,
        art_map_path: Path | None = None,
        enemy_sprite_manager: Any | None = None,
    ) -> None:
        self.art_root = Path(art_root or COMPANION_ART_ROOT)
        self.art_map_path = Path(art_map_path or self.art_root / "companion_art_map.json")
        self.enemy_sprite_manager = enemy_sprite_manager
        self.available_keys = {path.stem for path in self.art_root.glob("*.png") if path.is_file()}
        self.art_map: dict[str, str] = {}
        self._sprite_cache: dict[str, pygame.Surface] = {}
        self._scaled_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self._fallback_surface: pygame.Surface | None = None
        self.load_map()

    def load_map(self) -> None:
        if not self.art_map_path.exists():
            return
        try:
            data = json.loads(self.art_map_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load companion art map %s: %s", self.art_map_path, exc)
            return
        if not isinstance(data, dict):
            logger.warning("Companion art map must be an object: %s", self.art_map_path)
            return
        self.art_map = {str(name): str(key) for name, key in data.items()}

    @staticmethod
    def companion_name(companion: Any) -> str:
        if isinstance(companion, str):
            return companion
        for attr in ("enemy_class", "race", "name", "spec", "cls"):
            value = getattr(companion, attr, None)
            if value:
                return str(value)
        return ""

    @staticmethod
    def normalize_key(value: Any) -> str:
        text = str(value or "").strip().lower()
        return "_".join(part for part in text.replace("-", " ").split() if part)

    def _candidate_names(self, companion: Any) -> list[str]:
        if isinstance(companion, str):
            return [companion]
        candidates = []
        for attr in ("enemy_class", "race", "name", "spec", "cls"):
            value = getattr(companion, attr, None)
            if value:
                candidates.append(str(value))
        return candidates

    def get_art_key_for_companion(self, companion: Any) -> str | None:
        for name in self._candidate_names(companion):
            mapped = self.art_map.get(name)
            if mapped and mapped in self.available_keys:
                return mapped
            normalized = self.normalize_key(name)
            if normalized in self.available_keys:
                return normalized
        return None

    def get_mapped_fallback_key_for_companion(self, companion: Any) -> str | None:
        for name in self._candidate_names(companion):
            mapped = self.art_map.get(name)
            if mapped:
                return self.normalize_key(mapped)
        return None

    def get_sprite(self, companion: Any) -> pygame.Surface:
        key = self.get_art_key_for_companion(companion)
        if key is None:
            enemy_manager = self.enemy_sprite_manager or get_enemy_combat_sprite_manager()
            fallback_key = self.get_mapped_fallback_key_for_companion(companion)
            if fallback_key:
                try:
                    return enemy_manager.get_sprite_by_key(fallback_key)
                except Exception:
                    pass
            try:
                return enemy_manager.get_sprite(companion)
            except Exception:
                return self._runtime_fallback_surface()
        return self.get_sprite_by_key(key)

    def get_sprite_by_key(self, art_key: str) -> pygame.Surface:
        key = self.normalize_key(art_key)
        if key not in self.available_keys:
            return self._runtime_fallback_surface()
        cached = self._sprite_cache.get(key)
        if cached is not None:
            return cached
        path = self.art_root / f"{key}.png"
        try:
            loaded = pygame.image.load(str(path))
            try:
                surface = loaded.convert_alpha()
            except pygame.error:
                surface = loaded.copy()
        except pygame.error as exc:
            logger.warning("Could not load companion art %s: %s", path, exc)
            return self._runtime_fallback_surface()
        self._sprite_cache[key] = surface
        return surface

    def get_scaled_sprite(self, companion: Any, target_size: tuple[int, int]) -> pygame.Surface:
        key = self.get_art_key_for_companion(companion)
        if key is None:
            enemy_manager = self.enemy_sprite_manager or get_enemy_combat_sprite_manager()
            fallback_key = self.get_mapped_fallback_key_for_companion(companion)
            if fallback_key:
                try:
                    return enemy_manager.get_scaled_sprite_by_key(fallback_key, target_size)
                except Exception:
                    pass
            try:
                return enemy_manager.get_scaled_sprite(companion, target_size)
            except Exception:
                return self._scale_surface(self._runtime_fallback_surface(), target_size)
        cache_key = (key, target_size)
        cached = self._scaled_cache.get(cache_key)
        if cached is not None:
            return cached
        scaled = self._scale_surface(self.get_sprite_by_key(key), target_size)
        self._scaled_cache[cache_key] = scaled
        return scaled

    @staticmethod
    def _scale_surface(surface: pygame.Surface, target_size: tuple[int, int]) -> pygame.Surface:
        source_w, source_h = surface.get_size()
        target_w, target_h = target_size
        scale = min(target_w / max(1, source_w), target_h / max(1, source_h))
        fitted_size = (max(1, int(source_w * scale)), max(1, int(source_h * scale)))
        fitted = pygame.transform.smoothscale(surface, fitted_size)
        canvas = pygame.Surface(target_size, pygame.SRCALPHA)
        canvas.blit(fitted, ((target_w - fitted_size[0]) // 2, (target_h - fitted_size[1]) // 2))
        return canvas

    def _runtime_fallback_surface(self) -> pygame.Surface:
        if self._fallback_surface is None:
            surface = pygame.Surface((384, 384), pygame.SRCALPHA)
            pygame.draw.circle(surface, (86, 76, 104, 220), (192, 192), 132)
            pygame.draw.circle(surface, (210, 180, 110, 255), (192, 192), 132, 4)
            self._fallback_surface = surface
        return self._fallback_surface

    def clear_cache(self) -> None:
        self._sprite_cache.clear()
        self._scaled_cache.clear()


def get_companion_art_manager() -> CompanionArtManager:
    """Return the shared runtime companion art manager."""
    global _SHARED_COMPANION_ART_MANAGER
    if _SHARED_COMPANION_ART_MANAGER is None:
        _SHARED_COMPANION_ART_MANAGER = CompanionArtManager()
    return _SHARED_COMPANION_ART_MANAGER
