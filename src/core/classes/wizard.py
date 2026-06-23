"""Wizard class definition and six-school affinity helpers."""

from __future__ import annotations

from typing import Any

from .base import Job
from .. import items

AFFINITY_SCHOOLS = ("Fire", "Ice", "Water", "Electric", "Earth", "Wind")
OPPOSITES = {
    "Fire": "Ice",
    "Ice": "Fire",
    "Water": "Electric",
    "Electric": "Water",
    "Earth": "Wind",
    "Wind": "Earth",
}
DEFAULT_AFFINITY = 50
AFFINITY_STEP = 5
AFFINITY_MIN = 0
AFFINITY_MAX = 100


class Wizard(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Additional Pros: Increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Wizard",
            description="The Wizard is a master of arcane magic, unparalleled in their "
            "magical ability. Being able to cast the most powerful spells makes"
            " the wizard an ideal class for anyone who prefers to live fast "
            "and die hard if not properly prepared.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=0,
            cha_plus=1,
            dex_plus=1,
            att_plus=0,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=4,
            equipment={
                "Weapon": items.RuneStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.CloakEnchantment(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


def default_affinity() -> dict[str, int]:
    return {school: DEFAULT_AFFINITY for school in AFFINITY_SCHOOLS}


def normalize_affinity(state: Any) -> dict[str, int]:
    affinity = default_affinity()
    if isinstance(state, dict):
        for school in AFFINITY_SCHOOLS:
            try:
                value = int(state.get(school, DEFAULT_AFFINITY) or DEFAULT_AFFINITY)
            except (TypeError, ValueError):
                value = DEFAULT_AFFINITY
            affinity[school] = max(AFFINITY_MIN, min(AFFINITY_MAX, value))
    return affinity


def ensure_affinity(character: Any) -> dict[str, int]:
    affinity = normalize_affinity(getattr(character, "wizard_affinity", None))
    setattr(character, "wizard_affinity", affinity)
    return affinity


def school_from_ability(ability: Any) -> str | None:
    for candidate in (
        getattr(ability, "subtyp", None),
        getattr(ability, "school", None),
        getattr(ability, "damage_type", None),
    ):
        if str(candidate) in AFFINITY_SCHOOLS:
            return str(candidate)
    return None


def record_cast(character: Any, school: str | None) -> dict[str, int]:
    if school not in AFFINITY_SCHOOLS:
        return ensure_affinity(character)
    affinity = ensure_affinity(character)
    affinity[school] = min(AFFINITY_MAX, affinity[school] + AFFINITY_STEP)
    opposite = OPPOSITES[school]
    affinity[opposite] = max(AFFINITY_MIN, affinity[opposite] - AFFINITY_STEP)
    return affinity


def affinity_damage_bonus(character: Any, damage_type: str | None) -> float:
    if damage_type not in AFFINITY_SCHOOLS:
        return 0.0
    affinity = ensure_affinity(character)
    return max(0.0, (affinity[damage_type] - DEFAULT_AFFINITY) * 0.002)
