"""Wizard class definition and six-school affinity helpers."""

from __future__ import annotations

import random
from typing import Any

from .base import Job

AFFINITY_SCHOOLS = ("Fire", "Ice", "Water", "Electric", "Earth", "Wind", "Arcane")
OPPOSITES = {
    "Fire": "Ice",
    "Ice": "Fire",
    "Water": "Electric",
    "Electric": "Water",
    "Earth": "Wind",
    "Wind": "Earth",
}
DEFAULT_AFFINITY = 0.0
SORCERER_CAP = 50.0
WIZARD_CAP = 100.0
AFFINITY_STEP = 2.0
RING_AFFINITY_STEP = 3.0
OPPOSITE_DRIFT = 1.0
OTHER_DRIFT = 0.2
AFFINITY_MIN = 0
AFFINITY_MAX = 100.0
SORCERER_UNLOCK_THRESHOLD = 30.0
SORCERER_MASTERY_THRESHOLD = 50.0
WIZARD_UNLOCK_THRESHOLD = 80.0
WIZARD_MASTERY_THRESHOLD = 100.0

SPELL_UPGRADES: dict[str, tuple[str, str, str]] = {
    "Fire": ("Firebolt", "Fireball", "Firestorm"),
    "Ice": ("Ice Lance", "Icicle", "Blizzard"),
    "Electric": ("Shock", "Lightning", "Electrocution"),
    "Water": ("Water Jet", "Aqualung", "Tsunami"),
    "Earth": ("Tremor", "Mudslide", "Earthquake"),
    "Wind": ("Gust", "Hurricane", "Tornado"),
    "Arcane": ("Magic Missile", "Magic Missile 2", "Magic Missile 3"),
}


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
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


def default_affinity() -> dict[str, float]:
    return {school: DEFAULT_AFFINITY for school in AFFINITY_SCHOOLS}


def cap_for(character: Any | None) -> float:
    class_name = getattr(getattr(character, "cls", None), "name", None)
    return WIZARD_CAP if class_name == "Wizard" else SORCERER_CAP


def normalize_affinity(state: Any, *, cap: float = WIZARD_CAP, migrate_legacy: bool = False) -> dict[str, float]:
    affinity = default_affinity()
    if isinstance(state, dict):
        for school in AFFINITY_SCHOOLS:
            try:
                value = float(state.get(school, DEFAULT_AFFINITY) or DEFAULT_AFFINITY)
            except (TypeError, ValueError):
                value = DEFAULT_AFFINITY
            if migrate_legacy:
                value = max(0.0, value - 50.0)
            affinity[school] = max(float(AFFINITY_MIN), min(float(cap), value))
    return affinity


def ensure_affinity(character: Any) -> dict[str, float]:
    version = int(getattr(character, "wizard_affinity_version", 1) or 1)
    affinity = normalize_affinity(
        getattr(character, "wizard_affinity", None),
        cap=cap_for(character),
        migrate_legacy=version < 2,
    )
    setattr(character, "wizard_affinity", affinity)
    setattr(character, "wizard_affinity_version", 2)
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


def record_cast(character: Any, school: str | None) -> dict[str, float]:
    if school not in AFFINITY_SCHOOLS:
        return ensure_affinity(character)
    affinity = ensure_affinity(character)
    cap = cap_for(character)
    step = RING_AFFINITY_STEP if _wizard_ring_accelerates(character) else AFFINITY_STEP
    affinity[school] = min(cap, affinity[school] + step)
    if school == "Arcane":
        return affinity
    opposite = OPPOSITES[school]
    affinity[opposite] = max(float(AFFINITY_MIN), affinity[opposite] - OPPOSITE_DRIFT)
    for other in AFFINITY_SCHOOLS:
        if other not in {school, opposite}:
            affinity[other] = max(float(AFFINITY_MIN), affinity[other] - OTHER_DRIFT)
    return affinity


def affinity_damage_bonus(character: Any, damage_type: str | None) -> float:
    if getattr(getattr(character, "cls", None), "name", None) not in {"Sorcerer", "Wizard"}:
        return 0.0
    if damage_type not in AFFINITY_SCHOOLS:
        return 0.0
    affinity = ensure_affinity(character)
    return max(0.0, int(affinity[damage_type] // 10) * 0.01)


def frozen_armor_reduction(character: Any, damage: int) -> tuple[int, str]:
    """Retain the legacy hook; Frozen Armor now reduces only incoming Ice."""
    return damage, ""


def process_cast(character: Any, spell: Any, target: Any | None = None) -> str:
    from . import mage_mechanics

    message = mage_mechanics.process_cast(character, spell, target)
    if getattr(getattr(character, "cls", None), "name", None) not in {"Sorcerer", "Wizard"}:
        return message
    school = mage_mechanics.school_from_ability(spell)
    if school not in AFFINITY_SCHOOLS:
        return message
    chosen = mage_mechanics.specialization(character)
    if chosen == "Arcane" and school != "Arcane":
        return message
    if chosen == "Elemental" and school == "Arcane":
        return message
    record_cast(character, school)
    message += _upgrade_spellbook(character, school)
    message += _apply_mastery_proc(character, school, target)
    return message


def _wizard_ring_accelerates(character: Any) -> bool:
    if getattr(getattr(character, "cls", None), "name", None) != "Wizard":
        return False
    try:
        from . import class_rings

        return class_rings.is_awakened(character, "Wizard") and class_rings.has_equipped_class_ring(character)
    except Exception:
        return False


def _spell_class_by_name(spell_name: str):
    from .. import abilities

    class_names = {
        "Ice Lance": "IceLance",
        "Ball Lightning": "BallLightning",
        "Water Jet": "WaterJet",
        "Molten Rock": "MoltenRock",
        "Firebolt": "Firebolt",
        "Fireball": "Fireball",
        "Firestorm": "Firestorm",
        "Icicle": "Icicle",
        "Blizzard": "IceBlizzard",
        "Shock": "Shock",
        "Lightning": "Lightning",
        "Electrocution": "Electrocution",
        "Aqualung": "Aqualung",
        "Tsunami": "Tsunami",
        "Tremor": "Tremor",
        "Mudslide": "Mudslide",
        "Earthquake": "Earthquake",
        "Gust": "Gust",
        "Hurricane": "Hurricane",
        "Tornado": "Tornado",
        "Magic Missile": "MagicMissile",
        "Magic Missile 2": "MagicMissile2",
        "Magic Missile 3": "MagicMissile3",
    }
    return getattr(abilities, class_names.get(spell_name, spell_name.replace(" ", "")), None)


def _upgrade_spellbook(character: Any, school: str) -> str:
    spells = getattr(character, "spellbook", {}).get("Spells", {})
    if not isinstance(spells, dict):
        return ""
    affinity = ensure_affinity(character)[school]
    chain = SPELL_UPGRADES.get(school)
    if not chain:
        return ""
    class_name = getattr(getattr(character, "cls", None), "name", None)
    target_index = None
    if affinity >= WIZARD_UNLOCK_THRESHOLD and class_name == "Wizard":
        target_index = 2
    elif affinity >= SORCERER_UNLOCK_THRESHOLD and class_name in {"Sorcerer", "Wizard"}:
        target_index = 1
    if target_index is None:
        return ""
    for lower_name in chain[:target_index]:
        if lower_name in spells:
            new_name = chain[target_index]
            spell_cls = _spell_class_by_name(new_name)
            if spell_cls is None or new_name in spells:
                return ""
            del spells[lower_name]
            spells[new_name] = spell_cls()
            return f"{lower_name} resonates with {school} affinity and upgrades to {new_name}.\n"
    return ""


def _buff_state(character: Any) -> dict[str, int]:
    state = getattr(character, "wizard_school_buffs", None)
    if not isinstance(state, dict):
        state = {}
        setattr(character, "wizard_school_buffs", state)
    return state


def _apply_mastery_proc(character: Any, school: str, target: Any | None) -> str:
    if school == "Arcane":
        return ""
    affinity = ensure_affinity(character)[school]
    class_name = getattr(getattr(character, "cls", None), "name", None)
    if class_name not in {"Sorcerer", "Wizard"}:
        return ""
    if affinity < SORCERER_MASTERY_THRESHOLD:
        return ""
    mastery = affinity >= WIZARD_MASTERY_THRESHOLD and _wizard_ring_accelerates(character)
    chance = 0.12 + (0.08 if mastery else 0.0)
    if random.random() >= chance:
        return ""
    stacks = _buff_state(character)
    stacks[school] = min(3, int(stacks.get(school, 0) or 0) + 1)
    stack = stacks[school]
    if school == "Fire":
        character.stat_effects["Magic"].active = True
        character.stat_effects["Magic"].duration = max(character.stat_effects["Magic"].duration, 2)
        character.stat_effects["Magic"].extra = max(character.stat_effects["Magic"].extra, stack)
        return f"{character.name}'s fire affinity burns brighter ({stack}).\n"
    if school == "Ice":
        character.stat_effects["Defense"].active = True
        character.stat_effects["Defense"].duration = max(character.stat_effects["Defense"].duration, 2)
        character.stat_effects["Defense"].extra = max(character.stat_effects["Defense"].extra, stack)
        return f"{character.name}'s ice affinity hardens their guard ({stack}).\n"
    if school == "Water":
        heal = min(character.health.max - character.health.current, stack)
        mana = min(character.mana.max - character.mana.current, stack)
        character.health.current += max(0, heal)
        character.mana.current += max(0, mana)
        return f"{character.name}'s water affinity restores {max(0, heal)} HP and {max(0, mana)} MP.\n"
    if school == "Electric" and target is not None:
        damage = max(1, stack * (2 if mastery else 1))
        target.health.current -= damage
        return f"{character.name}'s electric affinity arcs for {damage} extra damage.\n"
    if school == "Earth":
        character.stat_effects["Defense"].active = True
        character.stat_effects["Defense"].duration = max(character.stat_effects["Defense"].duration, 2)
        character.stat_effects["Defense"].extra = max(character.stat_effects["Defense"].extra, stack)
        character.stat_effects["Magic Defense"].active = True
        character.stat_effects["Magic Defense"].duration = max(character.stat_effects["Magic Defense"].duration, 2)
        character.stat_effects["Magic Defense"].extra = max(character.stat_effects["Magic Defense"].extra, stack)
        return f"{character.name}'s earth affinity settles into a ward ({stack}).\n"
    if school == "Wind":
        character.stat_effects["Speed"].active = True
        character.stat_effects["Speed"].duration = max(character.stat_effects["Speed"].duration, 2)
        character.stat_effects["Speed"].extra = max(character.stat_effects["Speed"].extra, stack)
        return f"{character.name}'s wind affinity quickens them ({stack}).\n"
    return ""
