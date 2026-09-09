"""Semantic presentation metadata shared by ability consumers."""

from __future__ import annotations

from typing import Any

from ..progression_manifest import ABILITY_ICON_OVERRIDES


def ability_icon_key(book: str, ability: Any) -> str:
    """Return the authored semantic icon key for an ability."""
    override = ABILITY_ICON_OVERRIDES.get(getattr(ability, "name", ""))
    if override:
        return override
    normalized_name = str(getattr(ability, "name", "")).lower()
    if "transform" in normalized_name or "shapeshift" in normalized_name:
        return "spell_transform"
    if any(token in normalized_name for token in ("summon", "familiar", "invoke", "tame")):
        return "spell_summon"
    subtype = str(getattr(ability, "subtyp", "") or "").strip().lower()
    if book == "Spells":
        spell_icons = {
            "death": "spell_shadow",
            "earth": "spell_earth",
            "electric": "spell_lightning",
            "fire": "spell_fire",
            "heal": "spell_heal",
            "holy": "spell_holy",
            "ice": "spell_ice",
            "illusion": "spell_illusion",
            "nature": "spell_earth",
            "movement": "spell_movement",
            "non-elemental": "spell_arcane",
            "offensive": "spell_arcane",
            "poison": "spell_poison",
            "shadow": "spell_shadow",
            "soul": "spell_shadow",
            "status": "spell_status",
            "support": "spell_support",
            "time": "spell_time",
            "water": "spell_water",
            "wind": "spell_wind",
        }
        return spell_icons.get(subtype, "spell_arcane")
    skill_icons = {
        "chi strike": "skill_martial_arts",
        "class": "skill_passive" if getattr(ability, "passive", False) else "skill_support",
        "defensive": "skill_defense",
        "drain": "skill_drain",
        "enhance": "skill_support",
        "luck": "skill_luck",
        "martial arts": "skill_martial_arts",
        "offensive": "skill_offense",
        "power up": "skill_passive",
        "stealth": "skill_stealth",
        "truth": "skill_truth",
    }
    return skill_icons.get(
        subtype,
        "skill_passive" if getattr(ability, "passive", False) else "skill_offense",
    )
