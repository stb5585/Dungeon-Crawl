"""Compact player token generation derived from player portrait artwork."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pygame

from src.ui_pygame.assets.portrait_manager import PortraitManager


DEFAULT_PLAYER_TOKEN_SIZE = (96, 96)
FACE_INSET_RATIO = 0.16


class PlayerTokenManager:
    """Build and cache circular face tokens from player portrait artwork."""

    def __init__(
        self,
        portrait_manager: PortraitManager | None = None,
        *,
        token_size: tuple[int, int] = DEFAULT_PLAYER_TOKEN_SIZE,
    ) -> None:
        self.portrait_manager = portrait_manager or PortraitManager()
        self.token_size = (max(1, int(token_size[0])), max(1, int(token_size[1])))
        self._token_cache: dict[tuple[Any, ...], pygame.Surface] = {}
        self._scaled_cache: dict[tuple[tuple[Any, ...], tuple[int, int]], pygame.Surface] = {}

    def get_token(self, player: Any) -> pygame.Surface:
        key = self._cache_key(player)
        cached = self._token_cache.get(key)
        if cached is not None:
            return cached

        portrait = self.portrait_manager.get_portrait(
            race=key[0],
            gender=key[1],
            class_name=key[2],
            first_promotion=key[3],
            second_promotion=key[4],
            effects=key[5],
        )
        crop = self._face_crop_rect(portrait.get_size())
        try:
            face = portrait.subsurface(crop).copy()
        except ValueError:
            face = portrait.subsurface(portrait.get_rect()).copy()
        token = self._compose_face_token(face)
        framed = self._frame_token(token)
        self._token_cache[key] = framed
        return framed

    def get_scaled_token(self, player: Any, target_size: tuple[int, int]) -> pygame.Surface:
        key = self._cache_key(player)
        target = (max(1, int(target_size[0])), max(1, int(target_size[1])))
        cache_key = (key, target)
        cached = self._scaled_cache.get(cache_key)
        if cached is not None:
            return cached

        token = self.get_token(player)
        scaled = pygame.transform.smoothscale(token, target)
        self._scaled_cache[cache_key] = scaled
        return scaled

    def _cache_key(self, player: Any) -> tuple[Any, ...]:
        race = getattr(player, "race", "Human")
        gender = getattr(player, "gender", getattr(player, "sex", "Male"))
        cls = getattr(player, "cls", getattr(player, "class_name", ""))
        class_name = getattr(cls, "name", cls)
        first_promotion = getattr(player, "first_promotion", getattr(player, "promotion", ""))
        second_promotion = getattr(player, "second_promotion", "")
        effects = self._portrait_effects(player)
        return self.portrait_manager.cache_key(
            race=race,
            gender=gender,
            class_name=class_name,
            first_promotion=first_promotion,
            second_promotion=second_promotion,
            effects=effects,
        )

    @staticmethod
    def _portrait_effects(player: Any) -> tuple[str, ...]:
        effects: list[str] = []
        for attr in ("portrait_effects", "visual_effects"):
            value = getattr(player, attr, ())
            if isinstance(value, str):
                effects.append(value)
            elif isinstance(value, Iterable):
                effects.extend(str(effect) for effect in value if effect)
        return tuple(effects)

    @staticmethod
    def _face_crop_rect(portrait_size: tuple[int, int]) -> pygame.Rect:
        width, height = portrait_size
        crop_size = max(1, int(min(width * 0.74, height * 0.42)))
        x = max(0, (width - crop_size) // 2)
        y = max(0, int(height * 0.06))
        if y + crop_size > height:
            y = max(0, height - crop_size)
        return pygame.Rect(x, y, crop_size, crop_size)

    def _compose_face_token(self, face: pygame.Surface) -> pygame.Surface:
        token = pygame.Surface(self.token_size, pygame.SRCALPHA)
        inset = max(2, int(min(self.token_size) * FACE_INSET_RATIO))
        inner_size = (max(1, self.token_size[0] - inset * 2), max(1, self.token_size[1] - inset * 2))
        scaled_face = pygame.transform.smoothscale(face, inner_size)
        token.blit(scaled_face, (inset, inset))
        return token

    @staticmethod
    def _frame_token(token: pygame.Surface) -> pygame.Surface:
        size = token.get_size()
        framed = pygame.Surface(size, pygame.SRCALPHA)
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect().inflate(-4, -4))

        clipped = token.copy()
        clipped.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        framed.blit(clipped, (0, 0))

        outer = framed.get_rect().inflate(-2, -2)
        inner = framed.get_rect().inflate(-8, -8)
        pygame.draw.ellipse(framed, (18, 26, 38, 255), outer, 3)
        pygame.draw.ellipse(framed, (88, 142, 204, 255), outer, 1)
        pygame.draw.ellipse(framed, (210, 230, 255, 175), inner, 1)
        return framed

    def clear_cache(self) -> None:
        self._token_cache.clear()
        self._scaled_cache.clear()


_SHARED_PLAYER_TOKEN_MANAGER: PlayerTokenManager | None = None


def get_player_token_manager() -> PlayerTokenManager:
    """Return the shared runtime player token manager."""
    global _SHARED_PLAYER_TOKEN_MANAGER
    if _SHARED_PLAYER_TOKEN_MANAGER is None:
        _SHARED_PLAYER_TOKEN_MANAGER = PlayerTokenManager()
    return _SHARED_PLAYER_TOKEN_MANAGER
