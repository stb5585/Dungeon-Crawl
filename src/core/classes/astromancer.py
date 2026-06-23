"""Astromancer class definition and rune-state helpers."""

from __future__ import annotations

import random
from typing import Any

from .base import Job
from .. import items


CONSTELLATIONS = ("Ember", "Tide", "Gale", "Stone")
RUNE_CAP = 3
BASE_RUNE_DROP_CHANCE = 0.25
ASTROMANCER_ACTIVE_SIGN_DROP_BONUS = 0.25
RUNIC_BOOST_FLOOR = 0.75
RING_ACTIVE_SIGN_BOOST_FLOOR = 1.0

SIGN_TO_ELEMENT = {
    "Ember": "Fire",
    "Tide": "Water",
    "Gale": "Wind",
    "Stone": "Earth",
}
ELEMENT_TO_SIGN = {element: sign for sign, element in SIGN_TO_ELEMENT.items()}
NATURAL_ELEMENTS = set(ELEMENT_TO_SIGN)


def default_state() -> dict[str, Any]:
    return {
        "active_constellation_index": 0,
        "runes": {sign: 0 for sign in CONSTELLATIONS},
    }


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if not isinstance(state, dict):
        return normalized

    try:
        normalized["active_constellation_index"] = int(
            state.get("active_constellation_index", 0) or 0
        ) % len(CONSTELLATIONS)
    except (TypeError, ValueError):
        normalized["active_constellation_index"] = 0

    incoming_runes = state.get("runes", {})
    if isinstance(incoming_runes, dict):
        for sign in CONSTELLATIONS:
            try:
                count = int(incoming_runes.get(sign, 0) or 0)
            except (TypeError, ValueError):
                count = 0
            normalized["runes"][sign] = max(0, min(RUNE_CAP, count))
    return normalized


def ensure_state(character: Any) -> dict[str, Any]:
    state = normalize_state(getattr(character, "astromancer_state", None))
    setattr(character, "astromancer_state", state)
    return state


def class_name(character: Any) -> str:
    return str(getattr(getattr(character, "cls", None), "name", "") or "")


def has_rune_system(character: Any) -> bool:
    return class_name(character) in {"Diviner", "Astromancer"}


def is_astromancer(character: Any) -> bool:
    return class_name(character) == "Astromancer"


def active_constellation(character: Any) -> str:
    state = ensure_state(character)
    index = int(state.get("active_constellation_index", 0) or 0)
    return CONSTELLATIONS[index % len(CONSTELLATIONS)]


def advance_constellation(character: Any) -> str:
    state = ensure_state(character)
    index = int(state.get("active_constellation_index", 0) or 0) + 1
    state["active_constellation_index"] = index % len(CONSTELLATIONS)
    return active_constellation(character)


def spin_constellation(character: Any, rng: Any = random) -> str:
    state = ensure_state(character)
    current = int(state.get("active_constellation_index", 0) or 0)
    choices = [idx for idx in range(len(CONSTELLATIONS)) if idx != current]
    state["active_constellation_index"] = int(rng.choice(choices))
    return active_constellation(character)


def rune_grid_lines(character: Any) -> list[str]:
    state = ensure_state(character)
    runes = state["runes"]
    lines = []
    for sign in CONSTELLATIONS:
        filled = int(runes.get(sign, 0) or 0)
        cells = "".join("*" if idx < filled else "." for idx in range(RUNE_CAP))
        lines.append(f"{sign}: {cells}")
    return lines


def rune_status_summary(character: Any) -> str:
    return " | ".join(rune_grid_lines(character))


def sign_for_spell(spell: Any) -> str | None:
    return ELEMENT_TO_SIGN.get(str(getattr(spell, "subtyp", "") or ""))


def boostable_spells(character: Any) -> list[str]:
    if not has_rune_system(character):
        return []
    state = ensure_state(character)
    spells = getattr(character, "spellbook", {}).get("Spells", {})
    names = []
    for name, spell in spells.items():
        if getattr(spell, "passive", False):
            continue
        sign = sign_for_spell(spell)
        if not sign:
            continue
        if int(state["runes"].get(sign, 0) or 0) <= 0:
            continue
        if int(getattr(spell, "cost", 0) or 0) > int(getattr(character.mana, "current", 0) or 0):
            continue
        names.append(name)
    return names


def has_awakened_equipped_class_ring(character: Any) -> bool:
    try:
        from . import class_rings

        return bool(
            class_rings.is_awakened(character, "Astromancer")
            and class_rings.has_equipped_class_ring(character)
        )
    except Exception:
        return False


def runic_boost_floor(character: Any, sign: str | None) -> float:
    if (
        is_astromancer(character)
        and sign == active_constellation(character)
        and has_awakened_equipped_class_ring(character)
    ):
        return RING_ACTIVE_SIGN_BOOST_FLOOR
    return RUNIC_BOOST_FLOOR


def consume_rune(character: Any, sign: str) -> bool:
    state = ensure_state(character)
    count = int(state["runes"].get(sign, 0) or 0)
    if count <= 0:
        return False
    state["runes"][sign] = count - 1
    return True


def add_rune(character: Any, sign: str, amount: int = 1) -> bool:
    if sign not in CONSTELLATIONS:
        return False
    state = ensure_state(character)
    before = int(state["runes"].get(sign, 0) or 0)
    after = max(0, min(RUNE_CAP, before + int(amount)))
    state["runes"][sign] = after
    return after > before


def rune_drop_chance(character: Any, target: Any, spell: Any) -> tuple[str | None, float]:
    sign = sign_for_spell(spell)
    if not sign:
        return None, 0.0
    chance = BASE_RUNE_DROP_CHANCE
    if is_astromancer(character) and sign == active_constellation(character):
        chance += ASTROMANCER_ACTIVE_SIGN_DROP_BONUS
    element = SIGN_TO_ELEMENT[sign]
    resistance = 0.0
    try:
        resistance = float(getattr(target, "resistance", {}).get(element, 0.0) or 0.0)
    except (TypeError, ValueError):
        resistance = 0.0
    if resistance >= 0:
        chance *= max(0.0, 1.0 - resistance)
    else:
        chance *= 1.0 + abs(resistance)
    return sign, max(0.0, min(1.0, chance))


def maybe_award_rune(character: Any, target: Any, spell: Any, rng: Any = random) -> tuple[bool, str | None, float]:
    if not has_rune_system(character):
        return False, None, 0.0
    sign, chance = rune_drop_chance(character, target, spell)
    if not sign or chance <= 0:
        return False, sign, chance
    if rng.random() < chance:
        return add_rune(character, sign), sign, chance
    return False, sign, chance


def constellation_bonus(character: Any, damage_type: str | None = None) -> float:
    if not has_awakened_equipped_class_ring(character):
        return 0.0
    current = active_constellation(character)
    element = SIGN_TO_ELEMENT.get(current)
    if damage_type is None or damage_type == element:
        return 0.15
    return 0.05


class Astromancer(Job):
    """
    Promotion: Pathfinder -> Diviner -> Astromancer
    Additional Pros: can learn rank 2 enemy specials when cast against; increased intel gain
    Additional Cons: None
    Special Mechanic: Runic Alterations - defeating enemies with elemental spells gives chance
        to drop runes
    """

    def __init__(self):
        super().__init__(
            name="Astromancer",
            description="Classified among the forbidden arts, astromancers study the celestial "
            "forces that govern magic, destiny, and the hidden threads of fate. Through careful "
            "observation they can learn spells cast by friend and foe alike, gradually unraveling"
            " the mysteries of the arcane. Those who master the stars gain the power to bend "
            "probability itself, turning fortune against their enemies and ensuring destiny "
            "unfolds according to their design.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=4,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.DragonRouge(),
                "Armor": items.CloakEnchantment(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome", "Rod"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )
