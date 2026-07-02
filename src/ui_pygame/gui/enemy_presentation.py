"""Pygame-only enemy readability presentation helpers."""

from __future__ import annotations

import re


BLEED_PRESENTATION_LABEL = "Oil Leak"
BLEED_PRESENTATION_ICON = "OIL"


def is_construct_like(character) -> bool:
    """Return whether an enemy should receive construct-flavored status wording."""
    enemy_type = str(getattr(character, "enemy_typ", "") or "").strip().lower()
    if enemy_type == "construct":
        return True

    for cls in type(character).__mro__:
        if cls.__name__ == "Construct":
            return True

    name = str(getattr(character, "name", "") or "").strip().lower()
    return name in {"cyborg", "golem", "iron golem", "warforged", "steel predator"}


def is_invisible_target(enemy) -> bool:
    """Return whether the enemy should receive an invisibility readability note."""
    return bool(getattr(enemy, "invisible", False))


def invisible_target_note(enemy, has_sight: bool) -> str | None:
    """Return the combat-panel note for invisible enemy visibility rules."""
    if not is_invisible_target(enemy):
        return None
    if has_sight:
        return "Sight reveals this invisible target."
    return "Invisible: details hidden without Sight."


def effect_display_name(effect_name: str, target=None) -> str:
    """Return a pygame-facing effect name without changing canonical mechanics."""
    if effect_name == "Bleed" and target is not None and is_construct_like(target):
        return BLEED_PRESENTATION_LABEL
    return effect_name


def effect_icon_label(effect_name: str, default_label: str, target=None) -> str:
    """Return a pygame-facing compact effect label."""
    if effect_name == "Bleed" and target is not None and is_construct_like(target):
        return BLEED_PRESENTATION_ICON
    return default_label


def present_status_log_line(line: str, enemy=None) -> str:
    """Swap visible bleed wording for constructs while preserving stored effects."""
    if enemy is None or not is_construct_like(enemy):
        return line

    text = re.sub(r"\bbleeds\b", "leaks oil", line, flags=re.IGNORECASE)
    text = re.sub(r"\bbleeding\b", "oil leak", text, flags=re.IGNORECASE)
    text = re.sub(r"\bbleed\b", BLEED_PRESENTATION_LABEL, text, flags=re.IGNORECASE)
    return text
