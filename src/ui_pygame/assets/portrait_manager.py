"""Portrait atlas loading and composition helpers for the Pygame UI."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any, Iterable

import pygame


logger = logging.getLogger(__name__)

PORTRAIT_ROOT = Path(__file__).resolve().parent / "portraits"


@dataclass(frozen=True)
class PortraitFrame:
    """Atlas frame metadata for one race/gender portrait."""

    key: str
    race: str
    gender: str
    rect: pygame.Rect


class PortraitManager:
    """Load base portrait atlas entries and compose optional overlay layers."""

    def __init__(
        self,
        portrait_root: Path | None = None,
        *,
        atlas_json: Path | None = None,
        atlas_image: Path | None = None,
        overlay_root: Path | None = None,
    ) -> None:
        self.portrait_root = Path(portrait_root or PORTRAIT_ROOT)
        self.base_root = self.portrait_root / "base"
        self.fallback_root = self.base_root / "fallback_individuals"
        self.overlay_root = Path(overlay_root or self.portrait_root / "overlays")
        self.atlas_json_path = Path(atlas_json or self._first_existing(
            self.base_root / "base_portrait_atlas.json",
            self.portrait_root / "base_portrait_atlas.json",
        ))
        self.atlas_image_path = Path(atlas_image) if atlas_image else None
        self.frames: dict[str, PortraitFrame] = {}
        self._atlas_surface: pygame.Surface | None = None
        self._base_cache: dict[tuple[str, str], pygame.Surface] = {}
        self._portrait_cache: dict[tuple[Any, ...], pygame.Surface] = {}
        self.missing_overlays: list[Path] = []
        self.load_atlas()

    @staticmethod
    def normalize_key(value: Any, default: str = "unknown") -> str:
        if hasattr(value, "name"):
            value = getattr(value, "name", default)
        text = str(value or default).strip().lower()
        normalized = "_".join("".join(ch if ch.isalnum() else " " for ch in text).split())
        return normalized or default

    @staticmethod
    def _first_existing(*paths: Path) -> Path:
        for path in paths:
            if path.exists():
                return path
        return paths[0]

    def load_atlas(self) -> None:
        if not self.atlas_json_path.exists():
            logger.warning("Portrait atlas JSON missing: %s", self.atlas_json_path)
            return

        try:
            data = json.loads(self.atlas_json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load portrait atlas JSON %s: %s", self.atlas_json_path, exc)
            return

        image_name = str(data.get("image", "base_portrait_atlas.png"))
        self.atlas_image_path = self.atlas_image_path or self.atlas_json_path.parent / image_name
        for entry_key, entry in (data.get("entries") or {}).items():
            try:
                race = self.normalize_key(entry.get("race", entry_key.rsplit("_", 1)[0]))
                gender = self.normalize_key(entry.get("gender", entry_key.rsplit("_", 1)[-1]))
                rect = pygame.Rect(int(entry["x"]), int(entry["y"]), int(entry["w"]), int(entry["h"]))
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Skipping invalid portrait atlas entry %s: %s", entry_key, exc)
                continue
            key = self.entry_key(race, gender)
            self.frames[key] = PortraitFrame(key=key, race=race, gender=gender, rect=rect)

    @staticmethod
    def entry_key(race: Any, gender: Any) -> str:
        return f"{PortraitManager.normalize_key(race)}_{PortraitManager.normalize_key(gender, 'male')}"

    def cache_key(
        self,
        race: Any,
        gender: Any,
        class_name: Any = None,
        first_promotion: Any = None,
        second_promotion: Any = None,
        effects: Iterable[Any] | None = None,
    ) -> tuple[Any, ...]:
        return (
            self.normalize_key(race, "human"),
            self.normalize_key(gender, "male"),
            self.normalize_key(class_name, "") if class_name else "",
            self.normalize_key(first_promotion, "") if first_promotion else "",
            self.normalize_key(second_promotion, "") if second_promotion else "",
            tuple(self.normalize_key(effect, "") for effect in effects or ()),
        )

    def get_portrait(
        self,
        race: Any,
        gender: Any,
        class_name: Any = None,
        first_promotion: Any = None,
        second_promotion: Any = None,
        effects: Iterable[Any] | None = None,
    ) -> pygame.Surface:
        key = self.cache_key(race, gender, class_name, first_promotion, second_promotion, effects)
        cached = self._portrait_cache.get(key)
        if cached is not None:
            return cached

        portrait = self.base_portrait(key[0], key[1]).copy()
        for overlay_path in self.overlay_paths(key[2], key[3], key[4], key[5]):
            overlay = self.load_overlay(overlay_path)
            if overlay is None:
                continue
            portrait.blit(overlay, (0, 0))

        self._portrait_cache[key] = portrait
        return portrait

    def base_portrait(self, race: Any, gender: Any) -> pygame.Surface:
        race_key = self.normalize_key(race, "human")
        gender_key = self.normalize_key(gender, "male")
        cache_key = (race_key, gender_key)
        cached = self._base_cache.get(cache_key)
        if cached is not None:
            return cached

        surface = self.atlas_portrait(race_key, gender_key)
        if surface is None:
            surface = self.fallback_portrait(race_key, gender_key)
        if surface is None:
            logger.warning("Portrait missing for race=%s gender=%s", race_key, gender_key)
            surface = self.placeholder_surface()

        self._base_cache[cache_key] = surface
        return surface

    def atlas_portrait(self, race: str, gender: str) -> pygame.Surface | None:
        frame = self.frames.get(self.entry_key(race, gender))
        atlas = self.atlas_surface()
        if frame is None or atlas is None:
            return None
        try:
            return atlas.subsurface(frame.rect).copy()
        except ValueError as exc:
            logger.warning("Portrait atlas frame out of bounds for %s: %s", frame.key, exc)
            return None

    def atlas_surface(self) -> pygame.Surface | None:
        if self._atlas_surface is not None:
            return self._atlas_surface
        if self.atlas_image_path is None or not self.atlas_image_path.exists():
            logger.warning("Portrait atlas image missing: %s", self.atlas_image_path)
            return None
        self._atlas_surface = self.load_image(self.atlas_image_path)
        return self._atlas_surface

    def fallback_portrait(self, race: str, gender: str) -> pygame.Surface | None:
        filename = f"{self.entry_key(race, gender)}.png"
        paths = (
            self.fallback_root / filename,
            self.portrait_root / filename,
            self.portrait_root / filename.replace("_", ""),
        )
        for path in paths:
            if path.exists():
                return self.load_image(path)
        return None

    def overlay_paths(
        self,
        class_name: str,
        first_promotion: str,
        second_promotion: str,
        effects: Iterable[str],
    ) -> list[Path]:
        paths: list[Path] = []
        if class_name:
            paths.append(self.overlay_root / "class" / f"{class_name}.png")
        if first_promotion:
            paths.append(self.overlay_root / "promotion" / f"{first_promotion}.png")
        if second_promotion:
            paths.append(self.overlay_root / "promotion" / f"{second_promotion}.png")
        for effect in effects:
            if effect:
                paths.append(self.overlay_root / "effects" / f"{effect}.png")
        return paths

    def load_overlay(self, path: Path) -> pygame.Surface | None:
        if not path.exists():
            self.missing_overlays.append(path)
            logger.debug("Portrait overlay missing: %s", path)
            return None
        return self.load_image(path)

    def load_image(self, path: Path) -> pygame.Surface | None:
        try:
            surface = pygame.image.load(str(path))
        except (pygame.error, OSError) as exc:
            logger.warning("Could not load portrait image %s: %s", path, exc)
            return None
        try:
            return surface.convert_alpha()
        except pygame.error:
            return surface.copy()

    def placeholder_surface(self, size: tuple[int, int] = (225, 400)) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((28, 28, 34, 255))
        pygame.draw.rect(surface, (90, 90, 104), surface.get_rect(), 3)
        return surface

    def clear_cache(self) -> None:
        self._base_cache.clear()
        self._portrait_cache.clear()
