"""Temporary feature flag helpers for the parallel character menu."""

from __future__ import annotations

import os
from typing import Any


TRUTHY_FLAG_VALUES = {"1", "true", "yes", "on", "modern", "new"}
MODERN_CHARACTER_MENU_ENV = "DUNGEON_CRAWL_MODERN_CHARACTER_MENU"


def modern_character_menu_enabled(*sources: Any) -> bool:
    """Return whether the modern character menu should be used.

    The legacy character menu remains the default. During acceptance testing,
    callers can opt in by setting ``use_modern_character_menu`` on the game or
    presenter, or by exporting ``DUNGEON_CRAWL_MODERN_CHARACTER_MENU=1``.
    """
    for source in sources:
        if bool(getattr(source, "use_modern_character_menu", False)):
            return True
    return os.getenv(MODERN_CHARACTER_MENU_ENV, "").strip().lower() in TRUTHY_FLAG_VALUES
