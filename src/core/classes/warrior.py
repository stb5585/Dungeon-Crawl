"""Warrior class definition."""

from __future__ import annotations

from .base import Job
from .. import items

COMMITMENT_ACCURACY_PER_STACK = 0.03
COMMITMENT_CRITICAL_BONUS_PER_STACK = 0.05
COMMITMENT_MAX_STACKS = 5


def has_skill(character, name: str) -> bool:
    """Return whether a character knows a Warrior-tree skill."""
    return name in getattr(character, "spellbook", {}).get("Skills", {})


def start_combat(character) -> None:
    """Reset Warrior passives with encounter-local state."""
    reset_commitment(character)


def reset_commitment(character) -> None:
    """Clear Commitment's target and accumulated focus."""
    character._commitment_target = None
    character._commitment_stacks = 0
    character._commitment_attacked_this_action = False


def begin_action(character) -> None:
    """Begin tracking whether the action contributes to Commitment."""
    character._commitment_attacked_this_action = False


def finish_action(character) -> None:
    """Break Commitment when the completed action made no weapon attack."""
    if has_skill(character, "Commitment") and not getattr(
        character,
        "_commitment_attacked_this_action",
        False,
    ):
        reset_commitment(character)


def record_attack(character, target) -> int:
    """Advance Commitment for an attack against the same target."""
    if not has_skill(character, "Commitment"):
        return 0
    target_key = id(target)
    if getattr(character, "_commitment_target", None) != target_key:
        character._commitment_target = target_key
        character._commitment_stacks = 0
    character._commitment_stacks = min(
        COMMITMENT_MAX_STACKS,
        int(getattr(character, "_commitment_stacks", 0) or 0) + 1,
    )
    character._commitment_attacked_this_action = True
    return character._commitment_stacks


def commitment_accuracy_bonus(character) -> float:
    """Return Commitment's current weapon accuracy bonus."""
    if not has_skill(character, "Commitment"):
        return 0.0
    return int(getattr(character, "_commitment_stacks", 0) or 0) * COMMITMENT_ACCURACY_PER_STACK


def commitment_critical_multiplier(character, multiplier: float) -> float:
    """Increase only the bonus portion of critical damage for Commitment."""
    if multiplier <= 1 or not has_skill(character, "Commitment"):
        return multiplier
    stacks = int(getattr(character, "_commitment_stacks", 0) or 0)
    return 1 + ((multiplier - 1) * (1 + stacks * COMMITMENT_CRITICAL_BONUS_PER_STACK))


class Warrior(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
                       |                |
                       |                -> Grandmaster of Arms
                       |
                       -> Paladin       -> Crusader
                       |
                       -> Lancer        -> Dragoon
                       |
                       -> Sentinel      -> Stalwart Defender
    """

    def __init__(self):
        super().__init__(
            name="Warrior",
            description="Warriors are weapon specialists that rely on strength and "
            "defense. While unable to cast spells, they have access to a wide"
            " variety of combat skills that make them deadly in combat. The "
            "most stout of the bass classes, this character is best for "
            "someone who wants to hack and slash their way through the game.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=0,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=1,
            equipment={
                "Weapon": items.Rapier(),
                "OffHand": items.Aspis(),
                "Armor": items.HideArmor(),
            },
            restrictions={
                "Weapon": [
                    "Dagger",
                    "Sword",
                    "Club",
                    "Longsword",
                    "Battle Axe",
                    "Hammer",
                ],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium", "Heavy"],
            },
            pro_level=1,
        )
