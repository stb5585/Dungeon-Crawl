"""Exploration effects and favored-enemy progression."""

from __future__ import annotations

from typing import Any


def default_exploration_effects() -> dict[str, int]:
    return {"invisibility": 0, "volitation": 0, "enter_wall": 0}


def normalize_exploration_effects(state: Any) -> dict[str, int]:
    normalized = default_exploration_effects()
    if isinstance(state, dict):
        for key in normalized:
            try:
                normalized[key] = max(0, int(state.get(key, 0) or 0))
            except (TypeError, ValueError):
                normalized[key] = 0
    return normalized


def ensure_exploration_effects(character: Any) -> dict[str, int]:
    state = normalize_exploration_effects(getattr(character, "temporary_exploration_effects", None))
    setattr(character, "temporary_exploration_effects", state)
    sync_exploration_flags(character)
    return state


def sync_exploration_flags(character: Any) -> None:
    state = normalize_exploration_effects(getattr(character, "temporary_exploration_effects", None))
    if state["invisibility"] > 0:
        character.invisible = True
    if state["volitation"] > 0:
        character.flying = True
    if state["enter_wall"] > 0:
        character.enter_wall = True


def apply_exploration_effect(character: Any, key: str, turns: int) -> None:
    state = ensure_exploration_effects(character)
    state[key] = max(state.get(key, 0), int(turns))
    setattr(character, "temporary_exploration_effects", state)
    sync_exploration_flags(character)


def tick_exploration_effects(character: Any, steps: int) -> None:
    state = normalize_exploration_effects(getattr(character, "temporary_exploration_effects", None))
    step_count = max(0, int(steps or 0))
    if step_count <= 0:
        return
    changed = False
    for key in state:
        if state[key] > 0:
            state[key] = max(0, state[key] - step_count)
            changed = True
    if changed:
        character.temporary_exploration_effects = state
        if state["invisibility"] <= 0:
            character.invisible = False
        if state["volitation"] <= 0:
            character.flying = False
        if state["enter_wall"] <= 0:
            character.enter_wall = False


def favorite_enemy_type(character: Any) -> str | None:
    try:
        from .. import promotion_kits

        state = promotion_kits.ensure_state(character).get("favored_enemy", {})
        marked = state.get("type") if isinstance(state, dict) else None
        if marked:
            return str(marked)
    except Exception:
        pass
    return None


def favored_enemy_state(character: Any) -> dict[str, Any]:
    try:
        from .. import promotion_kits

        state = promotion_kits.ensure_state(character)["favored_enemy"]
        return {
            "type": state.get("type"),
            "practice": max(0, int(state.get("practice", 0) or 0)),
            "switches": max(0, int(state.get("switches", 0) or 0)),
        }
    except Exception:
        return {"type": None, "practice": 0, "switches": 0}


def favored_enemy_rank(practice: Any) -> str:
    try:
        value = max(0, int(practice or 0))
    except (TypeError, ValueError):
        value = 0
    if value >= 30:
        return "Mastered Trail"
    if value >= 15:
        return "Known Trail"
    if value >= 5:
        return "Fresh Trail"
    return "New Trail"


def favored_enemy_practice_bonus(character: Any) -> int:
    state = favored_enemy_state(character)
    practice = max(0, int(state.get("practice", 0) or 0))
    if not state.get("type"):
        return 0
    return min(8, 1 + practice // 5)


def favored_enemy_label(character: Any) -> str:
    state = favored_enemy_state(character)
    marked = state.get("type")
    if marked:
        return str(marked)
    return "None"


def mark_favored_enemy(character: Any, target: Any | None) -> str:
    if target is None:
        return "There is no quarry to mark.\n"
    enemy_type = getattr(target, "enemy_typ", None)
    if not enemy_type:
        return f"{getattr(target, 'name', 'The target')} leaves no usable trail.\n"
    try:
        from .. import promotion_kits

        state = promotion_kits.ensure_state(character)["favored_enemy"]
    except Exception:
        return "The trail slips away.\n"

    current = state.get("type")
    before = int(state.get("practice", 0) or 0)
    if current == enemy_type:
        state["practice"] = min(999, before + 2)
        return f"{character.name} studies the {enemy_type} trail more deeply.\n"

    carryover = before // 3 if current else 0
    state["type"] = str(enemy_type)
    state["practice"] = carryover
    state["switches"] = int(state.get("switches", 0) or 0) + int(bool(current))
    if current:
        return f"{character.name} changes quarry from {current} to {enemy_type}.\n"
    return f"{character.name} marks {enemy_type} as their favored enemy.\n"


def gain_favored_enemy_practice(character: Any, enemy: Any | None, amount: int, reason: str) -> str:
    enemy_type = getattr(enemy, "enemy_typ", None)
    state = favored_enemy_state(character)
    if not enemy_type or enemy_type != state.get("type"):
        return ""
    try:
        from .. import promotion_kits

        favored = promotion_kits.ensure_state(character)["favored_enemy"]
    except Exception:
        return ""
    before = int(favored.get("practice", 0) or 0)
    favored["practice"] = min(999, before + max(0, int(amount or 0)))
    after = int(favored.get("practice", 0) or 0)
    if after <= before:
        return ""
    return ""


def favored_enemy_bonus(character: Any, enemy: Any | None) -> int:
    if enemy is None:
        return 0
    if "Favored Enemy" not in getattr(character, "spellbook", {}).get("Skills", {}):
        return 0
    enemy_type = getattr(enemy, "enemy_typ", None)
    if not enemy_type or enemy_type != favorite_enemy_type(character):
        return 0
    state = favored_enemy_state(character)
    if state.get("type"):
        bonus = favored_enemy_practice_bonus(character)
    else:
        total = sum(int(value or 0) for value in (getattr(character, "kill_dict", {}) or {}).get(enemy_type, {}).values())
        bonus = max(1, total // 10)
    if bonus > 0:
        try:
            from .. import promotion_kits

            combat = promotion_kits.combat_state(character)
            if not combat.get("favored_enemy_bonus_logged"):
                combat["favored_enemy_bonus_logged"] = True
        except Exception:
            pass
    return bonus


def consume_favored_enemy_bonus_message(character: Any) -> str:
    try:
        from .. import promotion_kits

        combat = promotion_kits.combat_state(character)
        if combat.pop("favored_enemy_bonus_logged", False):
            return "Favored Enemy pressure guides the strike.\n"
    except Exception:
        pass
    return ""
