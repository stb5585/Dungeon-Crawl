"""Grandmaster of Arms weapon discipline helpers."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Any

from .base import Job
from .. import items


WEAPON_TYPES = (
    "Fist",
    "Dagger",
    "Sword",
    "Club",
    "Longsword",
    "Battle Axe",
    "Polearm",
    "Hammer",
)
ONE_HANDED_WEAPONS = {"Fist", "Dagger", "Sword", "Club"}
TWO_HANDED_WEAPONS = {"Longsword", "Battle Axe", "Polearm", "Hammer"}

MAX_RANK = 10
XP_THRESHOLDS = (8, 20, 38, 62, 95, 138, 192, 258, 336, 430)
HIT_XP = 1
VICTORY_XP = 3

BASE_ACCURACY_PER_RANK = 0.005
BASE_PROC_PER_RANK = 0.01


class GrandmasterOfArms(Job):
    """
    Promotion: Warrior -> Weapon Master -> GrandMaster of Arms
    Additional Pros: Higher dexterity and constitution gain
    Additional Cons: Lower strength gain
    Special Mechanic: Weapon Specialty - weapon types that gain max level now trigger certain
        abilities/buffs  TODO
    """

    def __init__(self):
        super().__init__(
            name="Grandmaster of Arms",
            description="Grandmasters of Arms are the pinnacle of weapon expertise, "
            "mastering the art of dual-wielding and wielding powerful "
            "blades with unmatched skill.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=0,
            dex_plus=3,
            att_plus=5,
            def_plus=3,
            magic_plus=0,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Shamshir(),
                "OffHand": items.Pernach(),
                "Armor": items.Breastplate(),
            },
            restrictions={
                "Weapon": [
                    "Fist",
                    "Dagger",
                    "Sword",
                    "Club",
                    "Longsword",
                    "Battle Axe",
                    "Polearm",
                    "Hammer",
                ],
                "OffHand": ["Fist", "Dagger", "Sword", "Club"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=3,
        )


def default_state() -> dict[str, Any]:
    return {
        "activated": False,
        "bound_weapon": None,
        "disciplines": {
            weapon_type: {"xp": 0, "rank": 0}
            for weapon_type in WEAPON_TYPES
        },
    }


def rank_for_xp(xp: int) -> int:
    xp = max(0, int(xp or 0))
    rank = 0
    for threshold in XP_THRESHOLDS:
        if xp >= threshold:
            rank += 1
    return min(MAX_RANK, rank)


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if not isinstance(state, dict):
        return normalized

    normalized["activated"] = bool(state.get("activated", False))
    bound_weapon = state.get("bound_weapon")
    normalized["bound_weapon"] = bound_weapon if bound_weapon in WEAPON_TYPES else None

    disciplines = state.get("disciplines", {})
    if isinstance(disciplines, dict):
        for weapon_type in WEAPON_TYPES:
            entry = disciplines.get(weapon_type, {})
            xp = int(entry.get("xp", 0) or 0) if isinstance(entry, dict) else 0
            normalized["disciplines"][weapon_type] = {
                "xp": max(0, xp),
                "rank": rank_for_xp(xp),
            }
    return normalized


def copy_state(state: Any) -> dict[str, Any]:
    return deepcopy(normalize_state(state))


def get_weapon_type(character: Any, slot: str = "Weapon") -> str | None:
    equipment = getattr(character, "equipment", {})
    item = equipment.get(slot) if isinstance(equipment, dict) else None
    weapon_type = getattr(item, "subtyp", None)
    return weapon_type if weapon_type in WEAPON_TYPES else None


def is_grandmaster(character: Any) -> bool:
    return getattr(getattr(character, "cls", None), "name", None) == "Grandmaster of Arms"


def has_equipped_class_ring(character: Any) -> bool:
    equipment = getattr(character, "equipment", {})
    ring = equipment.get("Ring") if isinstance(equipment, dict) else None
    return getattr(ring, "name", None) == "Class Ring"


def has_stored_class_ring(character: Any) -> bool:
    storage = getattr(character, "storage", {})
    if not isinstance(storage, dict):
        return False
    return any(getattr(item, "name", None) == "Class Ring" for item in storage.get("Class Ring", []))


def ring_visible_for_sergeant(character: Any) -> bool:
    return has_equipped_class_ring(character) or has_stored_class_ring(character)


def discipline_rank(character: Any, weapon_type: str | None) -> int:
    if weapon_type not in WEAPON_TYPES:
        return 0
    state = normalize_state(getattr(character, "grandmaster_discipline", None))
    return int(state["disciplines"][weapon_type]["rank"])


def add_discipline_xp(character: Any, weapon_type: str | None, amount: int) -> tuple[int, int]:
    if weapon_type not in WEAPON_TYPES or amount <= 0 or not is_grandmaster(character):
        return 0, 0
    state = normalize_state(getattr(character, "grandmaster_discipline", None))
    entry = state["disciplines"][weapon_type]
    before = int(entry["rank"])
    entry["xp"] = max(0, int(entry["xp"]) + int(amount))
    entry["rank"] = rank_for_xp(entry["xp"])
    setattr(character, "grandmaster_discipline", state)
    return before, int(entry["rank"])


def bind_weapon(character: Any, weapon_type: str) -> bool:
    if weapon_type not in WEAPON_TYPES:
        return False
    state = normalize_state(getattr(character, "grandmaster_discipline", None))
    state["activated"] = True
    state["bound_weapon"] = weapon_type
    setattr(character, "grandmaster_discipline", state)
    return True


def bound_multiplier(character: Any, weapon_type: str | None) -> int:
    state = normalize_state(getattr(character, "grandmaster_discipline", None))
    if (
        weapon_type in WEAPON_TYPES
        and state["activated"]
        and state["bound_weapon"] == weapon_type
        and has_equipped_class_ring(character)
    ):
        return 2
    return 1


def accuracy_bonus(character: Any, weapon_type: str | None) -> float:
    if not is_grandmaster(character):
        return 0.0
    rank = discipline_rank(character, weapon_type)
    return rank * BASE_ACCURACY_PER_RANK * bound_multiplier(character, weapon_type)


def proc_chance(character: Any, weapon_type: str | None) -> float:
    if not is_grandmaster(character):
        return 0.0
    rank = discipline_rank(character, weapon_type)
    return rank * BASE_PROC_PER_RANK * bound_multiplier(character, weapon_type)


def should_proc(character: Any, weapon_type: str | None) -> bool:
    chance = proc_chance(character, weapon_type)
    return chance > 0 and random.random() < chance


def _stack_entry(target: Any, key: str) -> dict[str, int]:
    stacks = getattr(target, "grandmaster_technique_stacks", None)
    if not isinstance(stacks, dict):
        stacks = {}
        setattr(target, "grandmaster_technique_stacks", stacks)
    entry = stacks.setdefault(key, {"stacks": 0, "duration": 0})
    entry["stacks"] = min(3, int(entry.get("stacks", 0) or 0) + 1)
    entry["duration"] = 3
    return entry


def apply_weapon_technique(attacker: Any, defender: Any, weapon_type: str | None) -> str:
    if weapon_type not in WEAPON_TYPES or not should_proc(attacker, weapon_type):
        return ""

    if weapon_type == "Fist":
        entry = _stack_entry(defender, "Fist Stagger")
        effect = defender.stat_effects["Attack"]
        effect.active = True
        effect.duration = 3
        effect.extra = -2 * entry["stacks"]
        return f"{attacker.name}'s fist technique staggers {defender.name}.\n"

    if weapon_type == "Dagger":
        entry = _stack_entry(defender, "Dagger Expose")
        effect = defender.physical_effects["Bleed"]
        effect.active = True
        effect.duration = 3
        effect.extra = max(int(effect.extra or 0), max(1, attacker.stats.dex // 4) * entry["stacks"])
        return f"{attacker.name}'s dagger exposes {defender.name}'s guard.\n"

    if weapon_type == "Sword":
        entry = _stack_entry(attacker, "Sword Precision")
        return f"{attacker.name}'s sword form sharpens into precision ({entry['stacks']}).\n"

    if weapon_type == "Club":
        entry = _stack_entry(defender, "Club Daze")
        effect = defender.stat_effects["Speed"]
        effect.active = True
        effect.duration = 3
        effect.extra = -2 * entry["stacks"]
        return f"{attacker.name}'s club strike dazes {defender.name}.\n"

    if weapon_type == "Longsword":
        effect = defender.stat_effects["Defense"]
        effect.active = True
        effect.duration = 3
        effect.extra = min(int(effect.extra or 0), -5)
        return f"{attacker.name}'s longsword breaks {defender.name}'s guard.\n"

    if weapon_type == "Battle Axe":
        effect = defender.physical_effects["Bleed"]
        effect.active = True
        effect.duration = 3
        effect.extra = max(int(effect.extra or 0), max(2, attacker.stats.strength // 3))
        return f"{attacker.name}'s axe rends {defender.name}.\n"

    if weapon_type == "Polearm":
        if getattr(defender, "flying", False):
            return f"{defender.name} stays beyond the trip.\n"
        effect = defender.physical_effects["Prone"]
        effect.active = True
        effect.duration = max(2, int(effect.duration or 0))
        return f"{attacker.name}'s polearm trips {defender.name}.\n"

    if weapon_type == "Hammer":
        effect = defender.stat_effects["Defense"]
        effect.active = True
        effect.duration = 3
        effect.extra = min(int(effect.extra or 0), -8)
        return f"{attacker.name}'s hammer sunders {defender.name}'s defenses.\n"

    return ""


def tick_technique_stacks(character: Any) -> list[str]:
    stacks = getattr(character, "grandmaster_technique_stacks", None)
    if not isinstance(stacks, dict) or not stacks:
        return []
    expired = []
    for key, entry in list(stacks.items()):
        entry["duration"] = int(entry.get("duration", 0) or 0) - 1
        if entry["duration"] <= 0:
            expired.append(key)
            del stacks[key]
    return expired
