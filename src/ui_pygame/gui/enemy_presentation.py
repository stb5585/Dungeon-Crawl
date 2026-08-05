"""Pygame-only enemy readability presentation helpers."""

from __future__ import annotations

import re


BLEED_PRESENTATION_LABEL = "Oil Leak"
BLEED_PRESENTATION_ICON = "OIL"
UNSEEN_FORCE_LABEL = "Unseen force"


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
    return bool(
        getattr(enemy, "invisible", False)
        or getattr(enemy, "name", "") == "Invisible Stalker"
    )


def player_has_sight(player_char) -> bool:
    """Return whether the player can identify invisible combatants."""
    if getattr(getattr(player_char, "cls", None), "name", None) in {
        "Inquisitor",
        "Seeker",
    }:
        return True
    equipment = getattr(player_char, "equipment", {})
    pendant = equipment.get("Pendant") if isinstance(equipment, dict) else None
    if getattr(pendant, "mod", None) == "Vision":
        return True
    return bool(getattr(player_char, "sight", False))


def invisible_target_note(enemy, has_sight: bool) -> str | None:
    """Return the combat-panel note for invisible enemy visibility rules."""
    if not is_invisible_target(enemy):
        return None
    if has_sight:
        return "Sight reveals this invisible target."
    return "Invisible: details hidden without Sight."


def presented_enemy_name(enemy, has_sight: bool) -> str:
    """Return an enemy identity appropriate for the player's current vision."""
    if is_invisible_target(enemy) and not has_sight:
        return UNSEEN_FORCE_LABEL
    return str(getattr(enemy, "name", enemy) or "")


def redact_hidden_enemy_identities(
    text: str,
    hidden_enemy_names,
) -> str:
    """Replace canonical invisible-enemy names in player-facing combat text."""
    redacted = str(text)
    for enemy_name in sorted(
        {str(name) for name in hidden_enemy_names if str(name)},
        key=len,
        reverse=True,
    ):
        redacted = re.sub(
            rf"\b{re.escape(enemy_name)}\b",
            UNSEEN_FORCE_LABEL,
            redacted,
            flags=re.IGNORECASE,
        )
    return redacted


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
