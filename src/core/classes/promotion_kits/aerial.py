"""Lancer and Dragoon Aerial Tempo combat mechanics."""

from __future__ import annotations

from typing import Any

from .state import _ring_awakened_equipped, class_name, combat_state


LEGAL_AERIAL_WEAPONS = {"Sword", "Polearm"}
AUTOMATIC_FOLLOW_THROUGH_EXCLUSIONS = {"Jump", "Dragon Dive"}


def current_aerial_tempo(character: Any) -> int:
    """Return the character's current combat-only Aerial Tempo."""
    return max(0, int(combat_state(character).get("aerial_tempo", 0) or 0))


def spend_aerial_tempo(character: Any) -> int:
    """Consume and return all current Aerial Tempo."""
    state = combat_state(character)
    stacks = max(0, int(state.get("aerial_tempo", 0) or 0))
    state["aerial_tempo"] = 0
    return stacks


def _jump_skill(character: Any) -> Any | None:
    skills = getattr(character, "spellbook", {}).get("Skills", {})
    jump = skills.get("Jump")
    if jump is not None:
        return jump
    return next(
        (
            skill
            for skill in skills.values()
            if getattr(skill, "name", "") == "Jump"
        ),
        None,
    )


def record_clean_jump_landing(
    character: Any,
    jump_damage: int,
    modifications: dict[str, bool] | None = None,
) -> str:
    """Grant Tempo and the equipped Aerial Supremacy landing shield."""
    if class_name(character) not in {"Lancer", "Dragoon"}:
        return ""
    from ...progression import has_talent
    from .. import class_rings
    from .meters import gain_meter

    modifications = modifications or {}
    amount = 1
    if (
        modifications.get("Soaring Strike")
        and has_talent(character, "dragoon.dragons-ascent")
    ):
        amount = 2
    message = gain_meter(character, "aerial_tempo", amount, "clean Jump landing")
    shield = class_rings.apply_aerial_supremacy_shield(
        character,
        max(0, int(jump_damage or 0)),
    )
    if shield:
        message += (
            f"Aerial Supremacy forms a {shield}-point Landing Shield around "
            f"{character.name}.\n"
        )
    return message


def _eligible_aerial_action(
    character: Any,
    action: str,
    choice: str | None,
) -> bool:
    if class_name(character) not in {"Lancer", "Dragoon"}:
        return False
    weapon = getattr(character, "equipment", {}).get("Weapon")
    if getattr(weapon, "subtyp", None) not in LEGAL_AERIAL_WEAPONS:
        return False
    if action == "Attack":
        return True
    if action != "Use Skill" or not choice:
        return False
    if choice in AUTOMATIC_FOLLOW_THROUGH_EXCLUSIONS:
        return False
    skill = getattr(character, "spellbook", {}).get("Skills", {}).get(choice)
    return bool(skill is not None and getattr(skill, "weapon", False))


def arm_aerial_follow_through(
    character: Any,
    action: str,
    choice: str | None = None,
) -> int:
    """Consume Tempo and arm one action-level follow-through."""
    state = combat_state(character)
    state["pending_aerial_follow_through"] = None
    stacks = current_aerial_tempo(character)
    if stacks <= 0 or not _eligible_aerial_action(character, action, choice):
        return 0
    state["aerial_tempo"] = 0
    state["pending_aerial_follow_through"] = {
        "token": int(state.get("action_token", 0) or 0),
        "stacks": stacks,
        "damage": 0,
        "target": None,
    }
    return stacks


def aerial_accuracy_bonus(character: Any) -> float:
    """Return the accuracy bonus for the currently armed action."""
    state = combat_state(character)
    pending = state.get("pending_aerial_follow_through")
    if not isinstance(pending, dict):
        return 0.0
    if int(pending.get("token", -1)) != int(state.get("action_token", 0) or 0):
        return 0.0
    stacks = max(0, int(pending.get("stacks", 0) or 0))
    per_stack = 0.04 if _ring_awakened_equipped(character, "Dragoon") else 0.03
    return per_stack * stacks


def record_aerial_weapon_damage(
    character: Any,
    target: Any,
    amount: int,
    metadata: dict[str, Any] | None,
) -> None:
    """Accumulate weapon damage for one armed follow-through action."""
    state = combat_state(character)
    pending = state.get("pending_aerial_follow_through")
    if not isinstance(pending, dict) or not isinstance(metadata, dict):
        return
    if metadata.get("attack_source") not in {"weapon", "special_attack"}:
        return
    if metadata.get("weapon_type") not in LEGAL_AERIAL_WEAPONS:
        return
    if int(pending.get("token", -1)) != int(state.get("action_token", 0) or 0):
        return
    pending["damage"] = int(pending.get("damage", 0) or 0) + max(0, int(amount or 0))
    pending["target"] = target


def finish_aerial_follow_through(character: Any) -> str:
    """Resolve one armed follow-through after every strike in the action."""
    state = combat_state(character)
    pending = state.get("pending_aerial_follow_through")
    state["pending_aerial_follow_through"] = None
    if not isinstance(pending, dict):
        return ""
    stacks = max(0, int(pending.get("stacks", 0) or 0))
    damage = max(0, int(pending.get("damage", 0) or 0))
    target = pending.get("target")
    if stacks <= 0:
        return ""
    if damage <= 0 or target is None:
        return (
            f"{character.name} spends {stacks} Aerial Tempo, but the "
            "follow-through misses.\n"
        )

    per_stack = 0.08 if _ring_awakened_equipped(character, "Dragoon") else 0.06
    bonus = max(1, int(damage * per_stack * stacks))
    target.health.current = max(0, int(target.health.current) - bonus)
    message = (
        f"{character.name} spends {stacks} Aerial Tempo; the follow-through "
        f"deals {bonus} damage.\n"
    )
    if class_name(character) == "Dragoon":
        speed = target.stat_effects["Speed"]
        speed.active = True
        speed.duration = max(2, int(speed.duration or 0))
        speed.extra = min(int(speed.extra or 0), -stacks)
        message += (
            f"Dragoon pressure reduces {target.name}'s Speed by {stacks} "
            "for two turns.\n"
        )
    return message


def grounded_landing_reduction(
    character: Any,
    damage: int,
) -> tuple[int, str]:
    """Reduce final incoming damage while a trained Jump is charging."""
    damage = max(0, int(damage or 0))
    if damage <= 0:
        return damage, ""
    from ...progression import has_talent

    jump = _jump_skill(character)
    if (
        jump is None
        or not getattr(jump, "charging", False)
        or not has_talent(character, "lancer.grounded-landing")
    ):
        return damage, ""
    reduction = max(1, int(damage * 0.10))
    return (
        max(0, damage - reduction),
        f"{character.name}'s Grounded Landing training reduces damage by "
        f"{reduction}.\n",
    )
