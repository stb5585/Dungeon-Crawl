"""Berserker class definition and Battle Scars helpers."""

from __future__ import annotations

import random
from typing import Any

from .base import Job

SCAR_CAP = 20
SCAR_CHANCE = 0.10
LOW_HP_THRESHOLD = 0.10
BLOODIED_DAMAGE_THRESHOLD = 0.25


class Berserker(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Additional Pros: Can dual wield 2-handed weapons; additional charisma gain
    Additional Cons: Can only equip light armor
    Special Mechanic: Battle Scars - surviving combat with less than 10% health gives
        a chance of earning a permanent scar.
    """

    def __init__(self):
        super().__init__(
            name="Berserker",
            description="Berserkers are combat masters, driven by pure rage and "
            "vengeance. Their strength is so great, they gain the "
            "ability to dual wield two-handed weapons. Their further "
            "reliance on maneuverability limits the type of armor to light "
            "armor.",
            str_plus=3,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=5,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Longsword", "Battle Axe", "Polearm", "Hammer"],
                "OffHand": ["Longsword", "Battle Axe", "Polearm", "Hammer"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )


def data(character: Any) -> dict[str, Any]:
    from . import class_rings

    state = class_rings.ensure_state(character)
    berserker = state["data"].setdefault("Berserker", {})
    berserker.setdefault("no_healing_duel_complete", False)
    berserker["battle_scars"] = max(
        0,
        min(SCAR_CAP, int(berserker.get("battle_scars", 0) or 0)),
    )
    berserker["battle_scar_hp_bonus"] = max(
        0,
        int(berserker.get("battle_scar_hp_bonus", 0) or 0),
    )
    return berserker


def scar_count(character: Any) -> int:
    return int(data(character).get("battle_scars", 0) or 0)


def bloodied_weapon_bonus(character: Any) -> float:
    if getattr(getattr(character, "cls", None), "name", "") != "Berserker":
        return 0.0
    hp_max = max(1, int(getattr(getattr(character, "health", None), "max", 1) or 1))
    if getattr(character.health, "current", hp_max) / hp_max >= BLOODIED_DAMAGE_THRESHOLD:
        return 0.0
    return scar_count(character) * 0.005


def record_battle_scar(character: Any, *, rng: Any = random) -> tuple[bool, str]:
    """Roll for a Battle Scar after a qualifying non-trial victory."""
    if getattr(getattr(character, "cls", None), "name", "") != "Berserker":
        return False, ""
    hp = getattr(character, "health", None)
    hp_max = max(1, int(getattr(hp, "max", 1) or 1))
    if getattr(hp, "current", hp_max) / hp_max > LOW_HP_THRESHOLD:
        return False, ""

    berserker = data(character)
    if int(berserker.get("battle_scars", 0) or 0) >= SCAR_CAP:
        return False, ""
    if rng.random() >= SCAR_CHANCE:
        return False, ""

    berserker["battle_scars"] = int(berserker.get("battle_scars", 0) or 0) + 1
    hp_bonus = max(1, int(hp_max * 0.01))
    berserker["battle_scar_hp_bonus"] = int(berserker.get("battle_scar_hp_bonus", 0) or 0) + hp_bonus
    character.health.max += hp_bonus
    character.health.current = min(character.health.max, character.health.current + hp_bonus)
    return True, f"{character.name} earns a Battle Scar. Max HP rises by {hp_bonus}.\n"
