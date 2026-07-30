"""Sentinel and Stalwart Defender Resolve mechanics."""

from __future__ import annotations

from typing import Any

from .meters import _class_ring_data
from .state import class_name, combat_state


RESOLVE_SPEND_ABILITIES: tuple[dict[str, Any], ...] = (
    {
        "name": "Shield Check",
        "role": "Control",
        "cost": 10,
        "description": "Batter the enemy with your shield, lowering Attack and Speed.",
    },
    {
        "name": "Brace Wall",
        "role": "Stance",
        "cost": 15,
        "description": "Refresh Hold the Line and raise Defense for the next exchange.",
    },
    {
        "name": "Shield Riposte",
        "role": "Counter",
        "cost": 20,
        "description": "Answer pressure with an immediate weapon counter.",
    },
    {
        "name": "Covering Guard",
        "role": "Protection",
        "cost": 20,
        "description": "Prepare a shield ward against the next dangerous hit.",
    },
    {
        "name": "Deflect Spell",
        "role": "Anti-magic",
        "cost": 20,
        "description": "Raise Magic Defense and brace against hostile spell pressure.",
    },
    {
        "name": "Bulwark",
        "role": "Barrier",
        "cost": 25,
        "description": "Convert stored Resolve into a short-lived damage barrier.",
    },
)

RESOLVE_SURGES: tuple[dict[str, Any], ...] = (
    {
        "name": "Citadel Aegis",
        "role": "Barrier Surge",
        "mastery": 0,
        "description": "Empty full Resolve into a fortress barrier and defensive stance.",
    },
    {
        "name": "Ironwall Reprisal",
        "role": "Counter Surge",
        "mastery": 4,
        "description": "Empty full Resolve into a crushing counterattack.",
    },
    {
        "name": "Last Bastion",
        "role": "Survival Surge",
        "mastery": 8,
        "description": "Empty full Resolve to recover and rebuild your guard.",
    },
)


def resolve_cap(character: Any) -> int:
    return 100 if class_name(character) == "Stalwart Defender" else 50


def _normalize_resolve_data(data: dict[str, Any]) -> None:
    data["guard_meter"] = max(0, int(data.get("guard_meter", 0) or 0))
    data["resolve_mastery"] = max(0, int(data.get("resolve_mastery", 0) or 0))


def _has_shield(character: Any) -> bool:
    return getattr(character.equipment.get("OffHand"), "subtyp", None) == "Shield"


def _require_resolve_training(character: Any, ability_name: str) -> str:
    if class_name(character) not in {"Sentinel", "Stalwart Defender"}:
        return f"{ability_name} belongs to the shield defender track.\n"
    return ""


def _require_shield(character: Any, ability_name: str) -> str:
    if not _has_shield(character):
        return f"{ability_name} requires a shield.\n"
    return ""


def _resolve_data(character: Any) -> dict[str, Any]:
    data = _class_ring_data(character, "Stalwart Defender")
    _normalize_resolve_data(data)
    data["guard_meter"] = min(resolve_cap(character), int(data.get("guard_meter", 0) or 0))
    return data


def gain_resolve_mastery(character: Any, amount: int = 1, reason: str = "") -> str:
    if class_name(character) != "Stalwart Defender":
        return ""
    data = _resolve_data(character)
    before = int(data.get("resolve_mastery", 0) or 0)
    cap = max(entry["mastery"] for entry in RESOLVE_SURGES)
    data["resolve_mastery"] = min(cap, before + max(0, int(amount)))
    if data["resolve_mastery"] == before:
        return ""
    reason_text = f" through {reason}" if reason else ""
    return f"{character.name}'s Resolve mastery deepens{reason_text}.\n"


def resolve_surge_unlocked(character: Any, surge_name: str) -> bool:
    if class_name(character) != "Stalwart Defender":
        return False
    data = _resolve_data(character)
    mastery = int(data.get("resolve_mastery", 0) or 0)
    for entry in RESOLVE_SURGES:
        if entry["name"] == surge_name:
            return mastery >= int(entry["mastery"])
    return False


def current_resolve(character: Any) -> int:
    data = _resolve_data(character)
    return int(data.get("guard_meter", 0) or 0)


def resolve_is_full(character: Any) -> bool:
    return current_resolve(character) >= resolve_cap(character)


def resolve_surge_available(character: Any, surge_name: str) -> bool:
    return resolve_surge_unlocked(character, surge_name) and resolve_is_full(character)


def resolve_surge_rows(character: Any) -> list[dict[str, Any]]:
    data = _resolve_data(character)
    mastery = int(data.get("resolve_mastery", 0) or 0)
    rows: list[dict[str, Any]] = []
    for entry in RESOLVE_SURGES:
        unlocked = class_name(character) == "Stalwart Defender" and mastery >= int(entry["mastery"])
        rows.append({**entry, "unlocked": unlocked})
    return rows


def resolve_spend_rows(character: Any) -> list[dict[str, Any]]:
    learned = set(getattr(character, "spellbook", {}).get("Skills", {}) or {})
    return [
        {**entry, "unlocked": entry["name"] in learned}
        for entry in RESOLVE_SPEND_ABILITIES
    ]


def _spend_resolve(character: Any, cost: int, ability_name: str) -> tuple[bool, str, dict[str, Any]]:
    data = _resolve_data(character)
    resolve = int(data.get("guard_meter", 0) or 0)
    if resolve < cost:
        return False, f"{ability_name} requires {cost} Resolve.\n", data
    data["guard_meter"] = resolve - cost
    gain_resolve_mastery(character, 1, ability_name)
    return True, "", data


def build_resolve(character: Any, amount: int, reason: str = "") -> str:
    if class_name(character) not in {"Sentinel", "Stalwart Defender"}:
        return ""
    cap = resolve_cap(character)
    data = _resolve_data(character)
    before = int(data.get("guard_meter", 0) or 0)
    data["guard_meter"] = min(cap, before + max(0, int(amount)))
    if data["guard_meter"] == before:
        return "Resolve is capped.\n"
    msg = f"{character.name} gains {data['guard_meter'] - before} Resolve from {reason} ({data['guard_meter']}/{cap}).\n"
    msg += gain_resolve_mastery(character, 1, reason)
    return msg


def hold_the_line(character: Any) -> str:
    training = _require_resolve_training(character, "Hold the Line")
    if training:
        return training
    shield = _require_shield(character, "Hold the Line")
    if shield:
        return shield
    combat_state(character)["hold_the_line"] = 3
    character.enter_defensive_stance(duration=3)
    return f"{character.name} holds the line behind their shield.\n" + gain_resolve_mastery(character, 1, "Hold the Line")


def shield_check(character: Any, target: Any | None) -> str:
    training = _require_resolve_training(character, "Shield Check")
    if training:
        return training
    shield = _require_shield(character, "Shield Check")
    if shield:
        return shield
    if target is None:
        return "There is no target to check.\n"
    ok, msg, _data = _spend_resolve(character, 10, "Shield Check")
    if not ok:
        return msg
    attack = getattr(target, "stat_effects", {}).get("Attack")
    if attack is not None:
        attack.active = True
        attack.duration = max(int(attack.duration or 0), 2)
        attack.extra = min(int(attack.extra or 0), -2)
    speed = getattr(target, "stat_effects", {}).get("Speed")
    if speed is not None:
        speed.active = True
        speed.duration = max(int(speed.duration or 0), 2)
        speed.extra = min(int(speed.extra or 0), -2)
    return f"{character.name} spends 10 Resolve on Shield Check, lowering the enemy's Attack and Speed.\n"


def shield_bash(character: Any, target: Any | None) -> str:
    return shield_check(character, target)


def brace_wall(character: Any) -> str:
    training = _require_resolve_training(character, "Brace Wall")
    if training:
        return training
    shield = _require_shield(character, "Brace Wall")
    if shield:
        return shield
    ok, msg, _data = _spend_resolve(character, 15, "Brace Wall")
    if not ok:
        return msg
    state = combat_state(character)
    state["hold_the_line"] = max(int(state.get("hold_the_line", 0) or 0), 3)
    character.enter_defensive_stance(duration=3)
    defense = character.stat_effects["Defense"]
    defense.active = True
    defense.duration = max(int(defense.duration or 0), 2)
    defense.extra = max(int(defense.extra or 0), 3)
    return f"{character.name} spends 15 Resolve to brace the wall.\n"


def covering_guard(character: Any) -> str:
    training = _require_resolve_training(character, "Covering Guard")
    if training:
        return training
    shield = _require_shield(character, "Covering Guard")
    if shield:
        return shield
    ok, msg, _data = _spend_resolve(character, 20, "Covering Guard")
    if not ok:
        return msg
    effect = character.magic_effects["Nature Shield"]
    effect.active = True
    effect.duration = max(int(effect.duration or 0), 1)
    effect.extra = max(int(effect.extra or 0), 20)
    combat_state(character)["covering_guard"] = 2
    return f"{character.name} spends 20 Resolve on Covering Guard.\n"


def deflect_spell(character: Any) -> str:
    training = _require_resolve_training(character, "Deflect Spell")
    if training:
        return training
    shield = _require_shield(character, "Deflect Spell")
    if shield:
        return shield
    ok, msg, _data = _spend_resolve(character, 20, "Deflect Spell")
    if not ok:
        return msg
    effect = character.stat_effects["Magic Defense"]
    effect.active = True
    effect.duration = max(int(effect.duration or 0), 3)
    effect.extra = max(int(effect.extra or 0), 6)
    combat_state(character)["deflect_spell"] = 2
    return f"{character.name} spends 20 Resolve to deflect hostile magic.\n"


def bulwark(character: Any) -> str:
    training = _require_resolve_training(character, "Bulwark")
    if training:
        return training
    shield = _require_shield(character, "Bulwark")
    if shield:
        return shield
    data = _resolve_data(character)
    resolve = int(data.get("guard_meter", 0) or 0)
    if resolve < 25:
        return "Bulwark requires 25 Resolve.\n"
    spent = min(resolve, 50)
    data["guard_meter"] = resolve - spent
    gain_resolve_mastery(character, 1, "Bulwark")
    effect = character.magic_effects["Nature Shield"]
    effect.active = True
    effect.duration = 2
    effect.extra = max(int(effect.extra or 0), spent)
    return f"{character.name} spends {spent} Resolve on Bulwark.\n"


def shield_riposte(character: Any, target: Any | None) -> str:
    training = _require_resolve_training(character, "Shield Riposte")
    if training:
        return training
    shield = _require_shield(character, "Shield Riposte")
    if shield:
        return shield
    if target is None:
        return "There is no target to riposte.\n"
    ok, msg, _data = _spend_resolve(character, 20, "Shield Riposte")
    if not ok:
        return msg
    msg, _hit, _crit = character.weapon_damage(target, dmg_mod=0.75, use_offhand=False)
    return f"{character.name} spends 20 Resolve on Shield Riposte.\n{msg}"


def _use_resolve_surge(character: Any, surge_name: str, target: Any | None = None) -> str:
    if class_name(character) != "Stalwart Defender":
        return f"{surge_name} requires Stalwart Defender training.\n"
    shield = _require_shield(character, surge_name)
    if shield:
        return shield
    if not resolve_surge_unlocked(character, surge_name):
        return f"{surge_name} is still locked behind Resolve mastery.\n"
    if surge_name == "Ironwall Reprisal" and target is None:
        return "There is no target for Ironwall Reprisal.\n"
    data = _resolve_data(character)
    cap = resolve_cap(character)
    if int(data.get("guard_meter", 0) or 0) < cap:
        return f"{surge_name} requires a full Resolve bar.\n"
    data["guard_meter"] = 0
    gain_resolve_mastery(character, 1, surge_name)

    if surge_name == "Citadel Aegis":
        effect = character.magic_effects["Nature Shield"]
        effect.active = True
        effect.duration = 3
        effect.extra = max(int(effect.extra or 0), cap)
        character.enter_defensive_stance(duration=3)
        return f"{character.name} unleashes Citadel Aegis, emptying Resolve into a fortress barrier.\n"

    if surge_name == "Ironwall Reprisal":
        msg, _hit, _crit = character.weapon_damage(target, dmg_mod=1.35, use_offhand=False)
        return f"{character.name} unleashes Ironwall Reprisal, emptying Resolve into a crushing counter.\n{msg}"

    if surge_name == "Last Bastion":
        heal = max(1, int(character.health.max * 0.30))
        character.health.current = min(character.health.max, character.health.current + heal)
        effect = character.magic_effects["Nature Shield"]
        effect.active = True
        effect.duration = max(int(effect.duration or 0), 2)
        effect.extra = max(int(effect.extra or 0), cap // 2)
        character.enter_defensive_stance(duration=2)
        return f"{character.name} unleashes Last Bastion, emptying Resolve to recover {heal} health and reset their guard.\n"

    return f"{surge_name} is not a recognized Resolve Surge.\n"


def citadel_aegis(character: Any) -> str:
    return _use_resolve_surge(character, "Citadel Aegis")


def ironwall_reprisal(character: Any, target: Any | None) -> str:
    return _use_resolve_surge(character, "Ironwall Reprisal", target)


def last_bastion(character: Any) -> str:
    return _use_resolve_surge(character, "Last Bastion")
