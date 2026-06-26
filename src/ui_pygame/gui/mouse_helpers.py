"""Shared mouse-hit helpers for pygame selector screens."""

from __future__ import annotations

import pygame


def mouse_position(event) -> tuple[int, int] | None:
    """Return an event position for mouse events, if one is available."""
    pos = getattr(event, "pos", None)
    if pos is None:
        return None
    try:
        return int(pos[0]), int(pos[1])
    except (TypeError, ValueError, IndexError):
        return None


def hit_index(rects: list[pygame.Rect], pos: tuple[int, int] | None) -> int | None:
    """Return the first rect index containing a mouse position."""
    if pos is None:
        return None
    for index, rect in enumerate(rects):
        if rect.collidepoint(pos):
            return index
    return None


def is_left_click(event) -> bool:
    """Return True for a left mouse-button press."""
    return event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 1
