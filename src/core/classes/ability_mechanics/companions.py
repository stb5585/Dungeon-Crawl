"""Tamed-companion state, growth, commands, and combat behavior."""

from __future__ import annotations

import random
from typing import Any

from .equipment import (
    BEAST_COMPANION_COMMANDS,
    TAMED_COMPANION_CLASS_ALIASES,
    TAMED_COMPANION_EVOLUTIONS,
    TAMED_COMPANION_ROSTER_LIMIT,
    TAMED_COMPANION_SPECIALS,
    TAMED_COMPANION_SPECIES,
)
from .exploration import favorite_enemy_type


def default_tamed_companion() -> dict[str, Any]:
    return {
        "active": False,
        "enemy_class": None,
        "name": None,
        "custom_name": None,
        "level": 1,
        "bond": 0,
        "species": None,
        "evolution": "Wild Form",
        "special_ability": "Keen Scent",
        "pending_command": None,
        "active_index": None,
        "companions": [],
        "base": {},
    }


def _tamed_enemy_class_key(enemy_class: Any) -> str | None:
    if not enemy_class:
        return None
    key = str(enemy_class)
    return TAMED_COMPANION_CLASS_ALIASES.get(key, key)


def _tamed_species_data(enemy_class: Any = None, species: Any = None, name: Any = None) -> dict[str, Any] | None:
    key = _tamed_enemy_class_key(enemy_class)
    if key and key in TAMED_COMPANION_SPECIES:
        return TAMED_COMPANION_SPECIES[key]
    token = str(species or name or "").lower()
    for data in TAMED_COMPANION_SPECIES.values():
        if str(data["species"]).lower() == token:
            return data
    return None


def tamed_companion_species(enemy: Any) -> str:
    data = _tamed_species_data(enemy.__class__.__name__, getattr(enemy, "name", None))
    return str(data["species"]) if data else str(getattr(enemy, "name", "Animal") or "Animal")


def tamed_companion_evolution_for_bond(bond: Any, enemy_class: Any = None, species: Any = None) -> str:
    try:
        value = max(0, min(100, int(bond or 0)))
    except (TypeError, ValueError):
        value = 0
    data = _tamed_species_data(enemy_class, species)
    if data:
        evolutions = data["evolutions"]
        for index, (threshold, _generic) in enumerate(TAMED_COMPANION_EVOLUTIONS):
            if value >= threshold:
                return str(evolutions[len(evolutions) - 1 - index])
    for threshold, generic_evolution in TAMED_COMPANION_EVOLUTIONS:
        if value >= threshold:
            return generic_evolution
    return "Wild Form"


def _infer_tamed_special_from_name(name: str | None) -> str:
    token = str(name or "").lower()
    if any(part in token for part in ("bat", "bird", "hawk", "eagle", "wasp", "bee")):
        return "Wingbeat"
    if any(part in token for part in ("bear", "boar", "turtle", "crab", "beetle")):
        return "Guard Hide"
    if any(part in token for part in ("fox", "wolf", "rat", "cat", "panther", "tiger")):
        return "Pounce"
    return "Keen Scent"


def tamed_special_from_enemy(enemy: Any) -> str:
    data = _tamed_species_data(enemy.__class__.__name__, getattr(enemy, "name", None))
    if data:
        return str(data["special_ability"])
    if getattr(enemy, "flying", False):
        return "Wingbeat"
    combat = getattr(enemy, "combat", None)
    stats = getattr(enemy, "stats", None)
    attack = int(getattr(combat, "attack", 0) or 0)
    defense = int(getattr(combat, "defense", 0) or 0)
    magic = int(getattr(combat, "magic", 0) or 0)
    dex = int(getattr(stats, "dex", 0) or 0)
    con = int(getattr(stats, "con", 0) or 0)
    if magic > max(attack, defense):
        return "Primal Spark"
    if dex >= con + 3 or attack > defense:
        return "Pounce"
    if defense >= attack + 2 or con >= dex + 3:
        return "Guard Hide"
    return _infer_tamed_special_from_name(getattr(enemy, "name", None) or enemy.__class__.__name__)


def _known_tamed_evolutions() -> set[str]:
    known = {name for _threshold, name in TAMED_COMPANION_EVOLUTIONS}
    for data in TAMED_COMPANION_SPECIES.values():
        known.update(str(name) for name in data["evolutions"])
    return known


def tamed_companion_display_name(state: Any) -> str:
    """Return the visible tamed companion name, preserving species identity."""
    entry = state if isinstance(state, dict) else {}
    base_name = str(entry.get("name") or entry.get("species") or entry.get("enemy_class") or "Companion")
    custom_name = str(entry.get("custom_name") or "").strip()
    if custom_name and custom_name != base_name:
        return f"{custom_name} ({base_name})"
    return base_name


def rename_tamed_companion(character: Any, custom_name: Any, roster_index: int | None = None) -> None:
    """Set a tamed companion nickname while keeping the original animal identity."""
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    roster = list(state.get("companions", []))
    if not roster:
        character.tamed_companion = state
        return
    if roster_index is None:
        roster_index = int(state.get("active_index", 0) or 0)
    if roster_index < 0 or roster_index >= len(roster):
        character.tamed_companion = state
        return
    nickname = str(custom_name or "").strip()[:20]
    entry = dict(roster[roster_index])
    entry["custom_name"] = nickname or None
    roster[roster_index] = entry
    character.tamed_companion = _with_active_tamed_companion(roster, int(state.get("active_index", roster_index) or 0))
    try:
        from ... import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass


def _tamed_entry_from_state(state: Any) -> dict[str, Any]:
    normalized = default_tamed_companion()
    if isinstance(state, dict):
        normalized["active"] = bool(state.get("active", False))
        normalized["enemy_class"] = _tamed_enemy_class_key(state.get("enemy_class")) if state.get("enemy_class") else None
        normalized["name"] = state.get("name") if state.get("name") else normalized["enemy_class"]
        custom_name = str(state.get("custom_name") or "").strip()
        normalized["custom_name"] = custom_name or None
        species_data = _tamed_species_data(normalized["enemy_class"], state.get("species"), normalized["name"])
        normalized["species"] = (
            str(species_data["species"])
            if species_data
            else state.get("species") if state.get("species") else normalized["name"]
        )
        try:
            normalized["level"] = max(1, int(state.get("level", 1) or 1))
        except (TypeError, ValueError):
            normalized["level"] = 1
        try:
            normalized["bond"] = max(0, min(100, int(state.get("bond", 0) or 0)))
        except (TypeError, ValueError):
            normalized["bond"] = 0
        special = str(state.get("special_ability") or "")
        if special not in TAMED_COMPANION_SPECIALS:
            special = str(species_data["special_ability"]) if species_data else _infer_tamed_special_from_name(normalized["enemy_class"] or normalized["name"])
        normalized["special_ability"] = special
        evolution = str(state.get("evolution") or "")
        expected_evolution = tamed_companion_evolution_for_bond(
            normalized["bond"], normalized["enemy_class"], normalized["species"]
        )
        normalized["evolution"] = evolution if evolution in _known_tamed_evolutions() and evolution == expected_evolution else expected_evolution
        pending = state.get("pending_command")
        normalized["pending_command"] = str(pending) if pending else None
        base = state.get("base")
        normalized["base"] = base if isinstance(base, dict) else {}
    normalized.pop("companions", None)
    normalized.pop("active_index", None)
    return normalized


def tamed_companion_base_snapshot(enemy: Any) -> dict[str, Any]:
    return {
        "health_max": max(1, int(getattr(enemy.health, "max", 20) * 0.75)),
        "mana_max": max(0, int(getattr(enemy.mana, "max", 0) * 0.5)),
        "stats": {
            "strength": max(1, int(getattr(enemy.stats, "strength", 5) * 0.75)),
            "intel": max(1, int(getattr(enemy.stats, "intel", 5) * 0.5)),
            "wisdom": max(1, int(getattr(enemy.stats, "wisdom", 5) * 0.5)),
            "con": max(1, int(getattr(enemy.stats, "con", 5) * 0.75)),
            "charisma": max(1, int(getattr(enemy.stats, "charisma", 5) * 0.5)),
            "dex": max(1, int(getattr(enemy.stats, "dex", 5) * 0.75)),
        },
        "combat": {
            "attack": max(1, int(getattr(enemy.combat, "attack", 5) * 0.75)),
            "defense": max(1, int(getattr(enemy.combat, "defense", 5) * 0.75)),
            "magic": max(1, int(getattr(enemy.combat, "magic", 5) * 0.5)),
            "magic_def": max(1, int(getattr(enemy.combat, "magic_def", 5) * 0.5)),
        },
    }


def _tamed_roster_key(entry: dict[str, Any]) -> str:
    return str(entry.get("enemy_class") or entry.get("species") or entry.get("name") or "")


def _with_active_tamed_companion(roster: list[dict[str, Any]], active_index: int | None) -> dict[str, Any]:
    normalized = default_tamed_companion()
    normalized["companions"] = roster[:TAMED_COMPANION_ROSTER_LIMIT]
    if active_index is None or active_index < 0 or active_index >= len(normalized["companions"]):
        normalized["active_index"] = None
        return normalized
    active = dict(normalized["companions"][active_index])
    active["active"] = True
    active["pending_command"] = active.get("pending_command")
    normalized.update(active)
    normalized["active_index"] = active_index
    normalized["companions"][active_index] = active
    return normalized


def normalize_tamed_companion(state: Any) -> dict[str, Any]:
    active_entry = _tamed_entry_from_state(state)
    raw_roster = state.get("companions") if isinstance(state, dict) else None
    roster: list[dict[str, Any]] = []
    seen: set[str] = set()
    if isinstance(raw_roster, list):
        for raw_entry in raw_roster:
            entry = _tamed_entry_from_state(raw_entry)
            if not entry.get("enemy_class"):
                continue
            key = _tamed_roster_key(entry)
            if key in seen:
                continue
            seen.add(key)
            roster.append(entry)
            if len(roster) >= TAMED_COMPANION_ROSTER_LIMIT:
                break
    if active_entry.get("active") and active_entry.get("enemy_class") and _tamed_roster_key(active_entry) not in seen:
        roster.insert(0, active_entry)
        roster = roster[:TAMED_COMPANION_ROSTER_LIMIT]

    active_index = None
    if roster:
        try:
            requested_index = int(state.get("active_index")) if isinstance(state, dict) and state.get("active_index") is not None else None
        except (TypeError, ValueError):
            requested_index = None
        if requested_index is not None and 0 <= requested_index < len(roster):
            active_index = requested_index
        elif active_entry.get("active"):
            active_key = _tamed_roster_key(active_entry)
            for index, entry in enumerate(roster):
                if _tamed_roster_key(entry) == active_key:
                    active_index = index
                    break
        if active_index is None:
            active_index = 0
    for index, entry in enumerate(roster):
        entry["active"] = index == active_index
        if index != active_index:
            entry["pending_command"] = None
    normalized = _with_active_tamed_companion(roster, active_index)
    if isinstance(state, dict) and state.get("pending_command") and normalized["active"]:
        normalized["pending_command"] = str(state["pending_command"])
        normalized["companions"][normalized["active_index"]]["pending_command"] = normalized["pending_command"]
    return normalized


def activate_tamed_companion(character: Any, roster_index: int) -> str:
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    roster = list(state.get("companions", []))
    if roster_index < 0 or roster_index >= len(roster):
        return "No tamed companion is waiting there.\n"
    character.tamed_companion = _with_active_tamed_companion(roster, roster_index)
    try:
        from ... import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass
    return f"{character.tamed_companion['name']} takes the lead.\n"


def release_tamed_companion(character: Any, roster_index: int | None = None) -> str:
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    roster = list(state.get("companions", []))
    if not roster:
        return "There is no tamed companion to release.\n"
    if roster_index is None:
        roster_index = state.get("active_index")
    if roster_index is None or roster_index < 0 or roster_index >= len(roster):
        return "No tamed companion is waiting there.\n"
    released = roster.pop(roster_index)
    active_index = None if not roster else min(roster_index, len(roster) - 1)
    character.tamed_companion = _with_active_tamed_companion(roster, active_index)
    try:
        from ... import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass
    return f"{released.get('name', 'The companion')} returns to the wild.\n"


def tamed_special_description(special_ability: str | None) -> str:
    return TAMED_COMPANION_SPECIALS.get(str(special_ability or ""), TAMED_COMPANION_SPECIALS["Keen Scent"])


def apply_tamed_companion_growth(companion: Any, state: dict[str, Any]) -> None:
    bond = max(0, min(100, int(state.get("bond", 0) or 0)))
    multiplier = 1.0 + (0.20 * (bond / 100))
    companion.bond = bond
    companion.species = state.get("species") or getattr(companion, "race", None)
    companion.evolution = tamed_companion_evolution_for_bond(
        bond, state.get("enemy_class"), companion.species
    )
    companion.special_ability = state.get("special_ability") or "Keen Scent"
    for resource_name in ("health", "mana"):
        resource = getattr(companion, resource_name, None)
        if resource is None:
            continue
        resource.max = max(0, int(resource.max * multiplier))
        resource.current = resource.max
    for attr in ("strength", "con", "dex"):
        setattr(companion.stats, attr, max(1, int(getattr(companion.stats, attr, 1) * multiplier)))
    for attr in ("attack", "defense"):
        setattr(companion.combat, attr, max(1, int(getattr(companion.combat, attr, 1) * multiplier)))


def tamed_companion_special_turn(owner: Any, target: Any, *, hit: bool = False, crit: bool = False) -> str:
    companion = getattr(owner, "familiar", None)
    if companion is None or getattr(companion, "spec", "") != "Tamed":
        return ""
    bond = max(0, min(100, int(getattr(companion, "bond", 0) or 0)))
    if bond < 25 or target is None:
        return ""
    special = str(getattr(companion, "special_ability", "") or "Keen Scent")
    if special == "Pounce" and hit:
        damage = max(1, int(getattr(companion.combat, "attack", 1) * (0.12 + (0.08 if crit else 0.0))))
        target.health.current = max(0, target.health.current - damage)
        return f"{companion.name}'s Pounce follows through for {damage} damage.\n"
    if special == "Wingbeat" and hit:
        effect = target.stat_effects["Speed"]
        effect.active = True
        effect.duration = max(effect.duration, 2)
        effect.extra = min(int(effect.extra or 0), -max(1, bond // 25))
        return f"{companion.name}'s Wingbeat throws {target.name} off balance.\n"
    if special == "Guard Hide":
        effect = owner.magic_effects["Nature Shield"]
        effect.active = True
        effect.duration = max(effect.duration, 1)
        effect.extra = max(int(effect.extra or 0), max(4, bond // 5))
        effect.source = "Guard Hide"
        return f"{companion.name}'s Guard Hide braces {owner.name}.\n"
    if special == "Primal Spark" and hit:
        damage = max(1, int(getattr(companion.combat, "magic", 1) * 0.20))
        target.health.current = max(0, target.health.current - damage)
        return f"{companion.name}'s Primal Spark flashes for {damage} damage.\n"
    if special == "Keen Scent" and hit:
        effect = target.stat_effects["Defense"]
        effect.active = True
        effect.duration = max(effect.duration, 2)
        effect.extra = min(int(effect.extra or 0), -max(1, bond // 30))
        return f"{companion.name}'s Keen Scent finds a weak point.\n"
    return ""


def tamed_companion_bond(character: Any) -> int:
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    bond = max(0, min(100, int(state.get("bond", 0) or 0)))
    companion = getattr(character, "familiar", None)
    if getattr(companion, "spec", "") == "Tamed":
        try:
            bond = max(bond, max(0, min(100, int(getattr(companion, "bond", 0) or 0))))
        except (TypeError, ValueError):
            pass
    return bond


def has_living_tamed_companion(character: Any) -> bool:
    companion = getattr(character, "familiar", None)
    if companion is None or getattr(companion, "spec", "") != "Tamed":
        return False
    is_alive = getattr(companion, "is_alive", None)
    return bool(is_alive()) if callable(is_alive) else True


def _class_name(character: Any) -> str:
    return str(getattr(getattr(character, "cls", None), "name", "") or "")


def available_beast_companion_commands(character: Any) -> list[str]:
    if _class_name(character) != "Beast Master" or not has_living_tamed_companion(character):
        return []
    skills = getattr(character, "spellbook", {}).get("Skills", {})
    return [name for name in BEAST_COMPANION_COMMANDS if name in skills]


def _companion_command_state(character: Any) -> dict[str, Any]:
    state = getattr(character, "_promotion_kit_combat", None)
    if not isinstance(state, dict):
        state = {}
        setattr(character, "_promotion_kit_combat", state)
    return state


def pending_companion_command(character: Any) -> str | None:
    command = _companion_command_state(character).get("pending_companion_command")
    return str(command) if command else None


def set_pending_companion_command(character: Any, command: str | None) -> None:
    state = _companion_command_state(character)
    if command:
        state["pending_companion_command"] = str(command)
    else:
        state.pop("pending_companion_command", None)


def tamed_auto_action_chance(character: Any) -> float:
    bond = tamed_companion_bond(character)
    return min(0.40, 0.12 + (bond * 0.0028))


def tamed_companion_should_auto_act(character: Any, *, rng: Any = random) -> bool:
    if not has_living_tamed_companion(character) or pending_companion_command(character):
        return False
    class_name = _class_name(character)
    if class_name not in {"Ranger", "Beast Master"}:
        return False
    return rng.random() < tamed_auto_action_chance(character)


def _favored_enemy_pressure(character: Any, target: Any | None) -> bool:
    return bool(target is not None and getattr(target, "enemy_typ", None) == favorite_enemy_type(character))


def resolve_tamed_companion_command(character: Any, target: Any | None) -> str:
    command = pending_companion_command(character)
    if not command:
        return ""
    set_pending_companion_command(character, None)
    companion = getattr(character, "familiar", None)
    if target is None or not has_living_tamed_companion(character):
        return f"{command} fades without a living companion to follow it.\n"

    bond = tamed_companion_bond(character)
    rank = max(0, bond // 25)
    favored = _favored_enemy_pressure(character, target)

    if command == "Pack Strike":
        dmg_mod = 0.55 + (bond / 250.0) + (0.10 if favored else 0.0)
        msg = f"{companion.name} follows Pack Strike.\n"
        attack_str, hit, crit = companion.weapon_damage(target, dmg_mod=dmg_mod)
        msg += attack_str
        msg += tamed_companion_special_turn(character, target, hit=hit, crit=crit)
        return msg

    if command == "Guard Partner":
        effect = character.magic_effects["Nature Shield"]
        amount = 4 + rank * 4 + (bond // 20)
        effect.active = True
        effect.duration = max(effect.duration, 1 + (1 if rank >= 3 else 0))
        effect.extra = max(int(effect.extra or 0), amount)
        effect.source = "Guard Partner"
        return f"{companion.name} guards {character.name}, bracing the next hit.\n"

    if command == "Harry Prey":
        defense = target.stat_effects["Defense"]
        defense.active = True
        defense.duration = max(defense.duration, 1 + min(2, rank))
        defense.extra = min(int(defense.extra or 0), -(1 + rank))
        msg = f"{companion.name} harries {target.name}'s footing.\n"
        if rank >= 2:
            speed = target.stat_effects["Speed"]
            speed.active = True
            speed.duration = max(speed.duration, 2)
            speed.extra = min(int(speed.extra or 0), -max(1, rank))
        return msg

    if command == "Mend Wounds":
        owner_missing = max(0, character.health.max - character.health.current)
        companion_missing = max(0, companion.health.max - companion.health.current)
        heal_target = companion if companion_missing > owner_missing else character
        amount = min(max(owner_missing, companion_missing), 5 + rank * 5 + bond // 10)
        if amount <= 0:
            return f"{companion.name} stays close, ready to mend wounds.\n"
        heal_target.health.current = min(heal_target.health.max, heal_target.health.current + amount)
        return f"{companion.name} mends {heal_target.name}'s wounds for {amount} HP.\n"

    return f"{companion.name} cannot follow {command} yet.\n"
