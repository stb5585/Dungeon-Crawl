"""Lycan class definition and Moon Cycle helpers."""

from __future__ import annotations

import random
from typing import Any

from .base import Job

MOON_PHASES = ("New", "Waxing", "Full", "Waning")
STEPS_PER_PHASE = 120


class Lycan(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Additional Pros: Can unlock Dragon Essence; increased constitution gain
    Additional Cons: Lower intel gain
    Special Mechanic: Can shapeshift into alternative forms
    """

    def __init__(self):
        super().__init__(
            name="Lycan",
            description="Unlike the lycans of mythology who have little choice in morphing "
            "into their animal form, these lycans have gained mastery over their"
            " powers to become something truly terrifying.",
            str_plus=1,
            int_plus=0,
            wis_plus=1,
            con_plus=2,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Club", "Polearm", "Hammer", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )


def default_state() -> dict[str, Any]:
    return {"moon_phase": "New", "moon_steps": 0, "frenzy_turns": 0, "dragon_essence": False}


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if isinstance(state, dict):
        phase = state.get("moon_phase", "New")
        normalized["moon_phase"] = phase if phase in MOON_PHASES else "New"
        for key in ("moon_steps", "frenzy_turns"):
            try:
                normalized[key] = max(0, int(state.get(key, 0) or 0))
            except (TypeError, ValueError):
                normalized[key] = 0
        normalized["dragon_essence"] = bool(state.get("dragon_essence", False))
    return normalized


def ensure_state(character: Any) -> dict[str, Any]:
    state = normalize_state(getattr(character, "lycan_state", None))
    setattr(character, "lycan_state", state)
    return state


def record_steps(character: Any, steps: int = 1) -> dict[str, Any]:
    state = ensure_state(character)
    state["moon_steps"] += max(0, int(steps))
    while state["moon_steps"] >= STEPS_PER_PHASE:
        state["moon_steps"] -= STEPS_PER_PHASE
        index = (MOON_PHASES.index(state["moon_phase"]) + 1) % len(MOON_PHASES)
        state["moon_phase"] = MOON_PHASES[index]
    return state


def is_transformed(character: Any) -> bool:
    if hasattr(character, "_transformed"):
        return bool(character._transformed)
    transform_type = getattr(character, "transform_type", None)
    current_cls = getattr(getattr(character, "cls", None), "name", None)
    original_cls = getattr(transform_type, "name", None)
    return bool(original_cls and current_cls != original_cls)


def phase_damage_bonus(character: Any) -> float:
    if not _is_lycan(character):
        return 0.0
    if not is_transformed(character):
        return 0.0
    phase = ensure_state(character)["moon_phase"]
    return {"New": 0.00, "Waxing": 0.05, "Full": 0.15, "Waning": 0.08}[phase]


def frenzy_damage_bonus(character: Any) -> float:
    state = ensure_state(character)
    if state["frenzy_turns"] <= 0:
        return 0.0
    return 0.20


def healing_multiplier(character: Any) -> float:
    state = ensure_state(character)
    if state["frenzy_turns"] <= 0:
        return 1.0
    from . import class_rings

    return class_rings.controlled_frenzy_healing_multiplier(character)


def maybe_trigger_frenzy(
    character: Any,
    *,
    reason: str,
    rng: Any = random,
    ) -> tuple[bool, str]:
    if not _is_lycan(character):
        return False, ""
    if not is_transformed(character):
        return False, ""
    state = ensure_state(character)
    if state["frenzy_turns"] > 0:
        return False, ""
    phase = state["moon_phase"]
    base_chance = {"New": 0.05, "Waxing": 0.12, "Full": 0.25, "Waning": 0.16}[phase]
    if reason == "low_hp":
        base_chance += 0.10
    if rng.random() >= base_chance:
        return False, ""
    duration = {"New": 1, "Waxing": 2, "Full": 4, "Waning": 3}[phase]
    state["frenzy_turns"] = duration
    return True, f"The {phase} Moon locks {character.name} into a frenzy for {duration} turns.\n"


def tick_frenzy(character: Any) -> str:
    state = ensure_state(character)
    if state["frenzy_turns"] <= 0:
        return ""
    state["frenzy_turns"] -= 1
    if state["frenzy_turns"] <= 0:
        return f"{character.name}'s frenzy loosens.\n"
    return ""


def _is_lycan(character: Any) -> bool:
    current = getattr(getattr(character, "cls", None), "name", "")
    original = getattr(getattr(character, "transform_type", None), "name", "")
    return current == "Lycan" or original == "Lycan"
