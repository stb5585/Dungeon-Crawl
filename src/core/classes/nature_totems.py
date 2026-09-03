"""Shaman and Soulcatcher nature Totem helpers."""

from __future__ import annotations

import random
from typing import Any


ELIGIBLE_CLASSES = {"Shaman", "Soulcatcher"}
ELEMENTAL_ASPECTS = ("Earth", "Water", "Fire", "Wind")
COMMUNION_SPELLS = {
    "Water": "Tsunami",
    "Earth": "Earthquake",
    "Fire": "Fireball",
    "Wind": "Tornado",
}
ASPECT_SPELL_ORDER = {
    "Earth": ("Tremor", "Mudslide", "Earthquake"),
    "Water": ("Water Jet", "Hydration", "Tsunami"),
    "Fire": ("Scorch", "Firebolt", "Fireball", "Firestorm"),
    "Wind": ("Gust", "Hurricane", "Tornado"),
    "Soul": ("Soul Drain",),
}
SPELL_TO_ASPECT = {
    "Tremor": "Earth",
    "Mudslide": "Earth",
    "Earthquake": "Earth",
    "Water Jet": "Water",
    "Hydration": "Water",
    "Tsunami": "Water",
    "Scorch": "Fire",
    "Firebolt": "Fire",
    "Fireball": "Fire",
    "Firestorm": "Fire",
    "Gust": "Wind",
    "Hurricane": "Wind",
    "Tornado": "Wind",
    "Soul Drain": "Soul",
}
BASE_PULSE_CHANCE = 0.35
STAFF_PULSE_BONUS = 0.15
TOTEM_PULSE_POTENCY = 0.50
STAFF_MATCHING_CAST_MULTIPLIER = 1.20
WATER_WARD_MAGIC_DEFENSE_BONUS = 0.20
WATER_WARD_ABSORB_FRACTION = 0.25
WIND_COMMUNION_POS = (5, 5, 3)


def is_nature_totem_class(character: Any) -> bool:
    return getattr(getattr(character, "cls", None), "name", None) in ELIGIBLE_CLASSES


def has_staff_equipped(character: Any) -> bool:
    weapon = getattr(character, "equipment", {}).get("Weapon")
    return getattr(weapon, "subtyp", None) == "Staff"


def active_totem_aspect(character: Any) -> str | None:
    effect = getattr(character, "magic_effects", {}).get("Totem")
    if not effect or not getattr(effect, "active", False):
        return None
    extra = getattr(effect, "extra", None)
    if not isinstance(extra, dict):
        return None
    aspect = extra.get("aspect")
    return str(aspect) if aspect else None


def spell_aspect(spell_or_name: Any) -> str | None:
    name = spell_or_name if isinstance(spell_or_name, str) else getattr(spell_or_name, "name", "")
    return SPELL_TO_ASPECT.get(str(name))


def spell_output_multiplier(character: Any, spell_or_name: Any) -> float:
    multiplier = 1.0
    if hasattr(character, "_totem_pulse_potency"):
        try:
            multiplier = max(0.0, float(getattr(character, "_totem_pulse_potency", 1.0)))
            multiplier *= max(0.0, float(getattr(character, "_totem_surge_output", 1.0)))
            if active_totem_aspect(character) == "Soul":
                from . import class_rings

                multiplier *= 1.0 + class_rings.soul_aspect_bonus(character)
            return multiplier
        except (TypeError, ValueError):
            return multiplier

    aspect = spell_aspect(spell_or_name)
    if (
        aspect
        and has_staff_equipped(character)
        and active_totem_aspect(character) == aspect
    ):
        multiplier *= STAFF_MATCHING_CAST_MULTIPLIER
    if aspect and active_totem_aspect(character) == aspect:
        try:
            from . import promotion_kits

            multiplier *= 1.0 + (promotion_kits.totem_resonance(character) * 0.03)
        except Exception:
            pass
    return multiplier


def highest_unlocked_spell_name(character: Any, aspect: str) -> str | None:
    spells = getattr(character, "spellbook", {}).get("Spells", {})
    for name in reversed(ASPECT_SPELL_ORDER.get(aspect, ())):
        if name in spells:
            return name
    return None


def totem_pulse_chance(character: Any) -> float:
    chance = BASE_PULSE_CHANCE
    if has_staff_equipped(character):
        chance += STAFF_PULSE_BONUS
    try:
        from . import promotion_kits

        chance += promotion_kits.totem_resonance(character) * 0.05
    except Exception:
        pass
    return min(1.0, chance)


def _set_temp_attr(character: Any, attr: str, value: Any):
    sentinel = object()
    prior = getattr(character, attr, sentinel)
    setattr(character, attr, value)
    return sentinel, prior


def _restore_temp_attr(character: Any, attr: str, sentinel: object, prior: Any) -> None:
    if prior is sentinel:
        try:
            delattr(character, attr)
        except AttributeError:
            pass
    else:
        setattr(character, attr, prior)


def resolve_totem_pulse(character: Any, target: Any, rng: Any = random) -> str:
    if not (is_nature_totem_class(character) and target and getattr(target, "is_alive", lambda: False)()):
        return ""
    aspect = active_totem_aspect(character)
    if not aspect:
        return ""
    spell_name = highest_unlocked_spell_name(character, aspect)
    if not spell_name:
        return ""
    if rng.random() >= totem_pulse_chance(character):
        return ""

    spell = character.spellbook.get("Spells", {}).get(spell_name)
    if not spell:
        return ""

    sentinel, prior = _set_temp_attr(character, "_totem_pulse_potency", TOTEM_PULSE_POTENCY)
    try:
        message = f"{character.name}'s {aspect} Totem pulses with {spell_name}.\n"
        resolved = spell.cast(character, target=target, special=True)
        message += str(resolved)
        result = resolved if hasattr(resolved, "damage") else getattr(spell, "result", None)
        successful = bool(
            max(0, int(getattr(result, "damage", 0) or 0))
            or max(0, int(getattr(result, "healing", 0) or 0))
            or getattr(result, "hit", False)
            or any(
                bool(values)
                for values in (getattr(result, "effects_applied", {}) or {}).values()
            )
        )
        try:
            from . import promotion_kits

            if successful:
                message += promotion_kits.gain_totem_resonance(character, "successful pulse")
        except Exception:
            pass
    finally:
        _restore_temp_attr(character, "_totem_pulse_potency", sentinel, prior)
    return message


def communion_spell_name(aspect: str) -> str | None:
    return COMMUNION_SPELLS.get(aspect)


def unlock_communion(character: Any, aspect: str) -> tuple[bool, str]:
    spell_name = communion_spell_name(aspect)
    if not spell_name:
        return False, ""
    if not is_nature_totem_class(character):
        return False, f"A {aspect.lower()} presence stirs here, but it does not answer your path.\n"

    spells = character.spellbook.setdefault("Spells", {})
    if spell_name in spells:
        return False, f"The {aspect.lower()} presence is already bound to your Totem.\n"

    from src.core import abilities

    spell_cls = getattr(abilities, spell_name.replace(" ", ""), None)
    if spell_cls is None:
        return False, ""
    spells[spell_name] = spell_cls()
    return True, f"{character.name} communes with {aspect.lower()} and learns {spell_name}.\n"


def water_ward_absorb(defender: Any, damage: int) -> tuple[int, str]:
    if damage <= 0 or active_totem_aspect(defender) != "Water":
        return damage, ""
    absorbed = int(damage * WATER_WARD_ABSORB_FRACTION)
    if absorbed <= 0:
        return damage, ""
    defender.health.current = min(defender.health.max, defender.health.current + absorbed)
    try:
        defender._emit_healing_event(absorbed, source="Water Totem")
    except Exception:
        pass
    return damage - absorbed, (
        f"{defender.name}'s water totem absorbs {absorbed} spell damage "
        f"and restores {absorbed} health.\n"
    )
