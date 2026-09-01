"""Footpad class definition and shared Footpad-tree mechanics."""

from __future__ import annotations

import random
from typing import Any

from .base import Job
from .. import items


OBSCURATION_STEPS = 50


def has_skill(character: Any, name: str) -> bool:
    """Return whether a character knows a named Footpad-tree skill."""
    return name in getattr(character, "spellbook", {}).get("Skills", {})


def start_combat(character: Any) -> None:
    """Reset Footpad passives that can trigger once per battle."""
    character._do_over_used = False


def try_do_over(character: Any, *, rng: Any | None = None) -> bool:
    """Attempt the once-per-battle Do-over reroll after a missed attack."""
    if not has_skill(character, "Do-over") or getattr(character, "_do_over_used", False):
        return False
    generator = rng or random
    if generator.random() >= 0.25:
        return False
    character._do_over_used = True
    return True


def drain_basic_attack_mana(character: Any, target: Any, damage: int) -> int:
    """Apply Mana Depletion to damage dealt by the basic Attack action."""
    if not has_skill(character, "Mana Depletion") or damage <= 0:
        return 0
    mana = getattr(target, "mana", None)
    if mana is None:
        return 0
    drained = min(int(mana.current), max(1, int(damage * 0.10)))
    mana.current -= drained
    return drained


def loot_drop_multiplier(character: Any) -> float:
    """Return Serendipity's ordinary item-drop multiplier."""
    return 1.25 if has_skill(character, "Serendipity") else 1.0


def trap_damage(character: Any, damage: int, *, rng: Any | None = None) -> tuple[int, str]:
    """Resolve Avoid Traps against a triggered trap's negative effect."""
    damage = max(0, int(damage))
    severity, message = trap_severity_multiplier(character, rng=rng)
    return int(damage * severity), message


def trap_severity_multiplier(
    character: Any,
    *,
    rng: Any | None = None,
) -> tuple[float, str]:
    """Return 0, 0.5, or 1 for a trap effect after Avoid Traps."""
    if not has_skill(character, "Avoid Traps"):
        return 1.0, ""
    generator = rng or random
    dexterity = int(getattr(getattr(character, "stats", None), "dex", 10))
    avoid_chance = max(0.25, min(0.75, 0.35 + (dexterity - 10) * 0.02))
    if generator.random() < avoid_chance:
        return 0.0, f"{character.name} avoids the trap's effect."
    return 0.5, "Avoid Traps halves the trap's effect."


def tick_exploration(character: Any, steps: int) -> None:
    """Reduce Obscuration's exploration duration."""
    character.obscuration_steps = max(
        0,
        int(getattr(character, "obscuration_steps", 0) or 0) - max(0, int(steps)),
    )


def encounter_rate_multiplier(character: Any) -> float:
    """Reduce random encounters while Obscuration remains active."""
    return 0.5 if int(getattr(character, "obscuration_steps", 0) or 0) > 0 else 1.0


def obscuration_accuracy_penalty(defender: Any) -> float:
    """Return the attack accuracy penalty imposed by active Obscuration."""
    return 0.15 if int(getattr(defender, "obscuration_steps", 0) or 0) > 0 else 0.0


def scroll_effectiveness_multiplier(character: Any) -> float:
    """Return Incantation Comprehension's scroll potency multiplier."""
    return 1.25 if has_skill(character, "Incantation Comprehension") else 1.0


def spell_dodge_bonus(character: Any) -> float:
    """Return Mystical Evasion's bonus against spells."""
    return 0.15 if has_skill(character, "Mystical Evasion") else 0.0


def aggressive_pursuit(
    character: Any,
    target: Any,
    *,
    rng: Any | None = None,
) -> tuple[bool, str]:
    """Resolve the advantaged attack granted when an enemy attempts to flee.

    Returns whether the target escaped and the resulting combat message.
    """
    if not has_skill(character, "Aggressive Pursuit"):
        return True, f"{target.name} flees from battle.\n"
    generator = rng or random
    first = generator.random()
    second = generator.random()
    message, _hit, _crit = character.weapon_damage(
        target,
        use_offhand=False,
        hit=character.hit_chance(target, typ="weapon") > min(first, second),
    )
    if not target.is_alive():
        return False, message + f"{character.name}'s pursuit stops {target.name} from fleeing.\n"
    return True, message + f"{target.name} survives the pursuit and flees.\n"


class Footpad(Job):
    """
    Promotion: Footpad -> Thief         -> Rogue
                       |
                       -> Inquisitor    -> Seeker
                       |
                       -> Assassin      -> Ninja
                       |
                       -> Spell Stealer -> Arcane Trickster
    """

    def __init__(self):
        super().__init__(
            name="Footpad",
            description="Footpads are agile and perceptive, with an natural ability of "
            "deftness. While more than capable of holding their own in hand-"
            "to-hand combat, they truly excel at subterfuge. Footpads are the"
            " only base class that can dual wield, albeit the offhand weapon "
            "must be a dagger.",
            str_plus=0,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=2,
            att_plus=2,
            def_plus=1,
            magic_plus=1,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Dirk(),
                "OffHand": items.Dirk(),
                "Armor": items.PaddedArmor(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Sword", "Club"],
                "OffHand": ["Fist", "Dagger"],
                "Armor": ["Light"],
            },
            pro_level=1,
        )
