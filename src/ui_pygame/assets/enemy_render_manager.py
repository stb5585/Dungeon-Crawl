"""Large enemy artwork atlas loading for combat and inspection presentation."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any

import pygame


logger = logging.getLogger(__name__)

ENEMY_RENDER_ROOT = Path(__file__).resolve().parent / "enemy_renders"
_SHARED_ENEMY_RENDER_MANAGER: EnemyRenderManager | None = None


@dataclass(frozen=True)
class EnemyRenderFrame:
    """Atlas frame metadata for one broad enemy render archetype."""

    key: str
    rect: pygame.Rect


class EnemyRenderManager:
    """Resolve enemy objects or names to large painterly enemy artwork."""

    CATEGORY_FALLBACKS = {
        "Animal": "wolf",
        "Slime": "slime",
        "Humanoid": "bandit",
        "Fey": "wraith",
        "Fiend": "demon",
        "Undead": "zombie",
        "Elemental": "earth_elemental",
        "Dragon": "dragon",
        "Monster": "boss",
        "Aberration": "boss",
        "Construct": "dark_knight",
        "Misc": "generic_enemy",
    }

    BOSS_NAMES = {
        "Barghest",
        "Beholder",
        "Behemoth",
        "Cerberus",
        "Chimera",
        "Circe",
        "Cockatrice",
        "Domingo",
        "Fuath",
        "Golem",
        "Incubus",
        "Jester",
        "Merzhin",
        "Minotaur",
        "Nightmare",
        "Red Dragon",
        "The Devil",
        "Wendigo",
    }

    NAME_HINTS = (
        ("goblin", "goblin"),
        ("kobold", "kobold"),
        ("skeleton warrior", "skeleton_warrior"),
        ("skeleton", "skeleton"),
        ("zombie", "zombie"),
        ("lich", "lich"),
        ("wraith", "wraith"),
        ("ghost", "ghost"),
        ("dire wolf", "dire_wolf"),
        ("direwolf", "dire_wolf"),
        ("wolf", "wolf"),
        ("bear", "bear"),
        ("boar", "boar"),
        ("rat", "giant_rat"),
        ("giant spider", "giant_spider"),
        ("spider", "spider"),
        ("scorpion", "scorpion"),
        ("slime", "slime"),
        ("ooze", "ooze"),
        ("bat", "bat"),
        ("harpy", "harpy"),
        ("gargoyle", "gargoyle"),
        ("fire", "fire_elemental"),
        ("water", "water_elemental"),
        ("earth", "earth_elemental"),
        ("wind", "air_elemental"),
        ("storm", "air_elemental"),
        ("shadow", "shadow_elemental"),
        ("demon", "demon"),
        ("devil", "greater_demon"),
        ("dragon", "dragon"),
        ("wyrm", "wyrm"),
        ("wyvern", "dragon"),
        ("orc", "orc"),
        ("bandit", "bandit"),
        ("cultist", "cultist"),
        ("disciple", "cultist"),
        ("dark knight", "dark_knight"),
    )

    def __init__(
        self,
        render_root: Path | None = None,
        *,
        atlas_json: Path | None = None,
        atlas_image: Path | None = None,
        render_map_path: Path | None = None,
    ) -> None:
        self.render_root = Path(render_root or ENEMY_RENDER_ROOT)
        self.atlas_json_path = Path(atlas_json or self.render_root / "enemy_render_atlas.json")
        self.atlas_image_path = Path(atlas_image or self.render_root / "enemy_render_atlas.png")
        self.render_map_path = Path(render_map_path or self.render_root / "enemy_render_map.json")
        self.frames: dict[str, EnemyRenderFrame] = {}
        self.render_map: dict[str, str] = {}
        self.missing_mappings: set[str] = set()
        self._atlas_surface: pygame.Surface | None = None
        self._render_cache: dict[str, pygame.Surface] = {}
        self._scaled_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self._fallback_surface: pygame.Surface | None = None
        self.load_manifest()
        self.load_map()

    @staticmethod
    def enemy_name(enemy: Any) -> str:
        if isinstance(enemy, str):
            return enemy
        return str(getattr(enemy, "name", enemy) or "")

    @staticmethod
    def normalize_key(value: Any) -> str:
        text = str(value or "").strip().lower()
        return "_".join("".join(ch if ch.isalnum() else " " for ch in text).split())

    def load_manifest(self) -> None:
        if not self.atlas_json_path.exists():
            logger.warning("Enemy render atlas JSON missing: %s", self.atlas_json_path)
            return
        try:
            data = json.loads(self.atlas_json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load enemy render atlas JSON %s: %s", self.atlas_json_path, exc)
            return

        for key, entry in data.items():
            try:
                rect = pygame.Rect(int(entry["x"]), int(entry["y"]), int(entry["w"]), int(entry["h"]))
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Skipping invalid enemy render frame %s: %s", key, exc)
                continue
            self.frames[str(key)] = EnemyRenderFrame(key=str(key), rect=rect)

    def load_map(self) -> None:
        if not self.render_map_path.exists():
            logger.warning("Enemy render map missing: %s", self.render_map_path)
            return
        try:
            data = json.loads(self.render_map_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load enemy render map %s: %s", self.render_map_path, exc)
            return
        self.render_map = {str(name): str(key) for name, key in data.items()}

    def atlas_surface(self) -> pygame.Surface | None:
        if self._atlas_surface is not None:
            return self._atlas_surface
        if not self.atlas_image_path.exists():
            logger.warning("Enemy render atlas image missing: %s", self.atlas_image_path)
            return None
        try:
            surface = pygame.image.load(str(self.atlas_image_path))
        except (pygame.error, OSError) as exc:
            logger.warning("Could not load enemy render atlas %s: %s", self.atlas_image_path, exc)
            return None
        try:
            surface = surface.convert_alpha()
        except pygame.error:
            surface = surface.copy()
        self._atlas_surface = surface
        return surface

    def get_render(self, enemy: Any) -> pygame.Surface:
        return self.get_render_by_key(self.get_render_key_for_enemy(enemy))

    def get_render_by_name(self, enemy_name: str) -> pygame.Surface:
        return self.get_render_by_key(self.get_render_key_for_enemy(enemy_name))

    def get_render_by_key(self, render_key: str) -> pygame.Surface:
        key = self._valid_key(render_key)
        cached = self._render_cache.get(key)
        if cached is not None:
            return cached

        frame = self.frames.get(key) or self.frames.get("generic_enemy")
        if frame is None:
            logger.warning("Enemy render frame missing for %s and generic_enemy", key)
            return self.fallback_surface()

        atlas = self.atlas_surface()
        if atlas is None:
            return self.fallback_surface()

        try:
            render = atlas.subsurface(frame.rect).copy()
        except ValueError as exc:
            logger.warning("Enemy render frame out of bounds for %s: %s", key, exc)
            return self.fallback_surface()
        self._render_cache[key] = render
        return render

    def get_scaled_render_by_key(self, render_key: str, target_size: tuple[int, int]) -> pygame.Surface:
        key = self._valid_key(render_key)
        target = (max(1, int(target_size[0])), max(1, int(target_size[1])))
        cache_key = (key, target)
        cached = self._scaled_cache.get(cache_key)
        if cached is not None:
            return cached

        render = self.get_render_by_key(key)
        source_w, source_h = render.get_size()
        scale = min(target[0] / source_w, target[1] / source_h)
        fitted_size = (max(1, int(source_w * scale)), max(1, int(source_h * scale)))
        fitted = pygame.transform.smoothscale(render, fitted_size)
        surface = pygame.Surface(target, pygame.SRCALPHA)
        surface.blit(fitted, ((target[0] - fitted_size[0]) // 2, (target[1] - fitted_size[1]) // 2))
        self._scaled_cache[cache_key] = surface
        return surface

    def get_scaled_render(self, enemy: Any, target_size: tuple[int, int]) -> pygame.Surface:
        return self.get_scaled_render_by_key(self.get_render_key_for_enemy(enemy), target_size)

    def get_render_key_for_enemy(self, enemy: Any) -> str:
        name = self.enemy_name(enemy)
        if name in self.render_map:
            return self._valid_key(self.render_map[name])

        archetype = self._attribute_key(enemy, "render_archetype", "archetype")
        if archetype:
            return self._valid_key(archetype, prefer_boss=self._is_boss(enemy))

        class_name = enemy.__name__ if isinstance(enemy, type) else type(enemy).__name__
        class_key = self.normalize_key(class_name)
        if class_key in self.frames:
            return class_key

        hinted = self._hint_key(name) or self._hint_key(class_name)
        if hinted:
            return self._valid_key(hinted, prefer_boss=self._is_boss(enemy))

        category = self._attribute_key(enemy, "enemy_typ", "category", "typ")
        if category in self.CATEGORY_FALLBACKS:
            return self._valid_key(self.CATEGORY_FALLBACKS[category], prefer_boss=self._is_boss(enemy))

        if self._is_boss(enemy):
            return self._valid_key("boss")

        if name:
            logger.warning("Enemy render mapping missing for %s", name)
            self.missing_mappings.add(name)
        return "generic_enemy"

    def _valid_key(self, key: str, *, prefer_boss: bool = False) -> str:
        if key in self.frames:
            return key
        if prefer_boss and "boss" in self.frames:
            return "boss"
        return "generic_enemy"

    def _hint_key(self, value: str) -> str | None:
        normalized = value.replace("_", " ").lower()
        for needle, key in self.NAME_HINTS:
            if needle in normalized:
                return key
        return None

    @staticmethod
    def _attribute_key(enemy: Any, *names: str) -> str:
        if isinstance(enemy, str):
            return ""
        for name in names:
            value = getattr(enemy, name, "")
            if value:
                return str(value)
        return ""

    def _is_boss(self, enemy: Any) -> bool:
        name = self.enemy_name(enemy)
        if bool(getattr(enemy, "boss", False) or getattr(enemy, "is_boss", False)):
            return True
        return name in self.BOSS_NAMES

    def fallback_surface(self) -> pygame.Surface:
        if self._fallback_surface is not None:
            return self._fallback_surface
        surface = pygame.Surface((256, 320), pygame.SRCALPHA)
        surface.fill((12, 12, 16, 255))
        pygame.draw.rect(surface, (122, 90, 48), surface.get_rect(), 2)
        pygame.draw.ellipse(surface, (56, 52, 60), pygame.Rect(58, 76, 140, 180))
        pygame.draw.circle(surface, (202, 172, 108), (108, 136), 7)
        pygame.draw.circle(surface, (202, 172, 108), (148, 136), 7)
        self._fallback_surface = surface
        return surface

    def clear_cache(self) -> None:
        self._atlas_surface = None
        self._render_cache.clear()
        self._scaled_cache.clear()
        self._fallback_surface = None


def get_enemy_render_manager() -> EnemyRenderManager:
    """Return the shared runtime enemy render manager."""
    global _SHARED_ENEMY_RENDER_MANAGER
    if _SHARED_ENEMY_RENDER_MANAGER is None:
        _SHARED_ENEMY_RENDER_MANAGER = EnemyRenderManager()
    return _SHARED_ENEMY_RENDER_MANAGER
