"""Promotion combat meters and shared payoff mechanics."""

from __future__ import annotations

from typing import Any

from ...progression_manifest import TALENT_KIT_EFFECTS as _TALENT_KIT_EFFECTS
from .state import (
    _has_skill,
    _hierophant_overchannel_active,
    _is_weapon_hit,
    _message,
    _ring_awakened_equipped,
    class_name,
    combat_state,
)


def _talent_cap_bonus(character: Any, key: str) -> int:
    from ...progression import has_talent

    effect_key = "fortune" if key == "misfortune" else key
    return sum(
        int(effect[2])
        for talent_key, effect in _TALENT_KIT_EFFECTS.items()
        if effect[:2] == ("meter_cap", effect_key)
        and has_talent(character, talent_key)
    )


def cap_for(character: Any, key: str) -> int:
    cls = class_name(character)
    base = 0
    if key == "foresight_threads":
        base = 3 if cls == "Astromancer" else 0
    elif key == "bloodied_momentum":
        scars = _class_ring_data(character, "Berserker").get("battle_scars", 0)
        base = 5 if scars >= 20 else 4 if scars >= 10 else 3
    elif key == "oath_conviction":
        base = 3 if cls == "Crusader" else 2 if cls == "Paladin" else 0
    elif key == "aerial_tempo":
        base = 3 if cls == "Dragoon" else 2 if cls == "Lancer" else 0
    elif key in {"fortune", "misfortune"}:
        base = 3 if cls == "Rogue" else 2 if cls == "Thief" else 0
    elif key == "revelation":
        base = 3 if cls == "Seeker" else 2 if cls == "Inquisitor" else 0
    elif key == "death_marks":
        base = 3 if cls == "Ninja" else 1 if cls == "Assassin" else 0
    elif key == "stolen_charge":
        base = 3 if cls == "Arcane Trickster" else 2 if cls == "Spell Stealer" else 0
    elif key == "devotion":
        base = 5 if cls in {"Templar", "Hierophant"} else 3 if cls == "Cleric" else 0
    elif key == "prayer":
        base = 7 if cls == "Archbishop" else 4 if cls == "Priest" else 0
    elif key == "ki":
        base = 5 if cls == "Master Monk" else 3 if cls == "Monk" else 0
    elif key == "crescendo":
        base = 3 if cls in {"Bard", "Troubadour"} else 0
    elif key == "aspect_harmony":
        base = 5 if _ring_awakened_equipped(character, "Archdruid") else 4
    elif key == "totem_resonance":
        base = 4 if _ring_awakened_equipped(character, "Soulcatcher") else 3
    return base + _talent_cap_bonus(character, key) if base else 0


def _class_ring_data(character: Any, class_value: str) -> dict[str, Any]:
    try:
        from .. import class_rings

        return class_rings.ensure_state(character)["data"][class_value]
    except Exception:
        return {}


def gain_meter(character: Any, key: str, amount: int = 1, reason: str = "") -> str:
    cap = cap_for(character, key)
    if cap <= 0:
        return ""
    state = combat_state(character)
    before = int(state.get(key, 0) or 0)
    after = min(cap, before + max(0, int(amount)))
    state[key] = after
    if after <= before:
        return f"{key.replace('_', ' ').title()} is capped at {cap}.\n"
    label = key.replace("_", " ").title()
    suffix = f" from {reason}" if reason else ""
    return f"{character.name} gains {after - before} {label}{suffix} ({after}/{cap}).\n"


def _gain_or_queue_devotion(character: Any, amount: int, reason: str) -> str:
    state = combat_state(character)
    if not state.get("defer_devotion_until_survival"):
        return gain_meter(character, "devotion", amount, reason)
    pending = state.get("pending_devotion_gains")
    if not isinstance(pending, list):
        pending = []
        state["pending_devotion_gains"] = pending
    pending.append({"amount": max(0, int(amount or 0)), "reason": reason})
    return ""


def finish_action(character: Any, *, defender_survived: bool) -> str:
    from .aerial import finish_aerial_follow_through

    state = combat_state(character)
    pending = state.get("pending_devotion_gains")
    state["defer_devotion_until_survival"] = False
    state["pending_devotion_gains"] = []
    state["pending_hierophant_devotion_token"] = None
    msg = finish_aerial_follow_through(character)
    if defender_survived and isinstance(pending, list):
        for entry in pending:
            msg += gain_meter(
                character,
                "devotion",
                int(entry.get("amount", 0) or 0),
                str(entry.get("reason") or ""),
            )
    return msg


def spend_meter(character: Any, key: str) -> int:
    state = combat_state(character)
    value = int(state.get(key, 0) or 0)
    state[key] = 0
    return max(0, value)


def _gain_hierophant_devotion_once(actor: Any, reason: str) -> str:
    state = combat_state(actor)
    token = state.get("action_token")
    if token is not None and (
        state.get("hierophant_devotion_token") == token
        or state.get("pending_hierophant_devotion_token") == token
    ):
        return ""
    amount = 2 if _hierophant_overchannel_active(actor) else 1
    msg = _gain_or_queue_devotion(actor, amount, reason)
    if msg:
        state["hierophant_devotion_token"] = token
    elif state.get("defer_devotion_until_survival"):
        state["pending_hierophant_devotion_token"] = token
    return msg


def _is_hierophant_staff_hit(actor: Any, metadata: dict[str, Any] | None) -> bool:
    if not isinstance(metadata, dict):
        return False
    if metadata.get("attack_source") not in {"weapon", "special_attack"}:
        return False
    weapon_type = metadata.get("weapon_type")
    if weapon_type:
        return weapon_type == "Staff"
    slot = metadata.get("weapon_slot") or "Weapon"
    weapon = getattr(actor, "equipment", {}).get(slot)
    return getattr(weapon, "subtyp", None) == "Staff"


def _consume_consecrated_conduit(
    actor: Any,
    target: Any,
    amount: int,
    damage_type: str,
    metadata: dict[str, Any] | None,
) -> None:
    state = combat_state(actor)
    conduit = state.get("consecrated_conduit")
    if class_name(actor) != "Hierophant" or not isinstance(conduit, dict):
        return
    staff_hit = _is_hierophant_staff_hit(actor, metadata)
    ability_name = str((metadata or {}).get("ability_name") or "")
    holy_action = damage_type == "Holy" or ability_name.lower().startswith(("smite", "holy"))
    if not (staff_hit or holy_action):
        return
    stacks = max(1, int(conduit.get("stacks", 1) or 1))
    multiplier = 0.12 + (0.03 * stacks)
    if _hierophant_overchannel_active(actor):
        multiplier += 0.08
    if _ring_awakened_equipped(actor, "Hierophant") and staff_hit:
        multiplier += 0.05
    bonus = max(2 * stacks, int(amount * multiplier))
    if target is not None:
        target.health.current = max(0, target.health.current - bonus)
    state["consecrated_conduit"] = None
    ward = getattr(actor, "magic_effects", {}).get("Nature Shield")
    if ward is not None:
        ward.active = True
        ward.duration = max(int(getattr(ward, "duration", 0) or 0), 2)
        ward.extra = max(int(getattr(ward, "extra", 0) or 0), max(8, stacks * 6))
    mana = getattr(actor, "mana", None)
    if mana is not None:
        return_floor = stacks if _hierophant_overchannel_active(actor) else max(1, stacks // 2)
        returned = min(int(getattr(mana, "max", 0) or 0) - int(getattr(mana, "current", 0) or 0), max(1, return_floor))
        if returned > 0:
            mana.current += returned
    lines = [
        f"Consecrated Conduit releases for {bonus} holy damage.\n",
        "A modest ward settles around the Hierophant.\n",
    ]
    _maybe_preserve(actor, "devotion", "Hierophant", "Sacred Conduit", lines)
    for line in lines:
        _message(actor, line)


def record_damage_event(
    actor: Any,
    target: Any,
    amount: int,
    damage_type: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> None:
    from .companions import add_aspect

    if not amount or amount <= 0:
        return
    cls = class_name(actor)
    damage_type = str(damage_type or "Physical")
    weapon_hit = _is_weapon_hit(metadata)
    from .aerial import record_aerial_weapon_damage

    record_aerial_weapon_damage(actor, target, amount, metadata)
    if isinstance(metadata, dict):
        critical_hit = bool(metadata.get("is_critical"))
        if not critical_hit:
            try:
                critical_hit = float(metadata.get("crit", 1) or 1) > 1
            except (TypeError, ValueError):
                critical_hit = False
    else:
        critical_hit = False
    if critical_hit and _is_weapon_hit(metadata):
        from .aerial import critical_vigor

        _message(actor, critical_vigor(actor))

    if cls == "Astromancer" and not weapon_hit:
        _message(actor, gain_meter(actor, "foresight_threads", 1, "successful spell thread"))

    spell_hit = bool(
        not weapon_hit
        and isinstance(metadata, dict)
        and (metadata.get("ability_name") or metadata.get("source") == "spell")
    )
    if cls in {"Spellblade", "Knight Enchanter"} and spell_hit:
        if cls == "Knight Enchanter":
            from .weaves import resolve_spellbind

            _message(actor, resolve_spellbind(actor, target, amount))
        _store_blade_charge(
            actor,
            charge_type=_blade_charge_type(damage_type),
        )
    if (
        spell_hit
        and target is not None
        and class_name(target) in {"Spellblade", "Knight Enchanter"}
        and _has_skill(target, "Counter Charge")
    ):
        source_state = combat_state(actor)
        source_token = int(source_state.get("action_token", 0) or 0)
        marker = (id(actor), source_token) if source_token > 0 else None
        target_state = combat_state(target)
        if marker is None or target_state.get("counter_charge_action_token") != marker:
            _store_blade_charge(
                target,
                charge_type=_blade_charge_type(damage_type),
                deduplicate=False,
            )
            target_state["counter_charge_action_token"] = marker
            _message(target, f"{target.name}'s Counter Charge answers the spell.\n")

    if cls == "Berserker" and weapon_hit and _hp_ratio(actor) < 0.50:
        bonus = 2 if _hp_ratio(actor) < 0.25 else 1
        _message(actor, gain_meter(actor, "bloodied_momentum", bonus, "bloodied weapon hit"))

    if cls in {"Thief", "Rogue"} and critical_hit:
        _message(actor, gain_meter(actor, "fortune", 1, "critical risky hit"))

    if cls in {"Cleric", "Templar"} and (damage_type == "Holy" or weapon_hit):
        _message(actor, _gain_or_queue_devotion(actor, 1, "holy or shield pressure"))
    if cls == "Hierophant":
        staff_hit = _is_hierophant_staff_hit(actor, metadata)
        turn_undead = str((metadata or {}).get("ability_name") or "").lower().startswith("turn undead")
        if damage_type == "Holy" or staff_hit or turn_undead:
            reason = "staff conduit" if staff_hit else "holy action"
            _message(actor, _gain_hierophant_devotion_once(actor, reason))
        _consume_consecrated_conduit(actor, target, amount, damage_type, metadata)

    if cls in {"Priest", "Archbishop"} and damage_type == "Holy":
        _message(actor, gain_meter(actor, "prayer", 1, "Holy spell"))

    if cls in {"Monk", "Master Monk"} and weapon_hit:
        _message(actor, gain_meter(actor, "ki", 1, "martial hit"))

    if cls == "Archdruid":
        if damage_type in {"Poison"}:
            _message(actor, add_aspect(actor, "Venom"))
        if damage_type in {"Electric", "Wind"}:
            _message(actor, add_aspect(actor, "Storm"))
        if damage_type in {"Earth", "Physical"} and not weapon_hit:
            _message(actor, add_aspect(actor, "Stone"))

    if weapon_hit:
        _apply_breakdown_stack(actor, target)
        _consume_weapon_payoffs(actor, target, amount, damage_type)
    elif spell_hit:
        _clear_breakdown_stacks(actor, target)


def record_damage_taken(defender: Any, amount: int, damage_type: str) -> None:
    from .companions import add_aspect
    from .resolve import build_resolve
    from .tracks import cheat_death

    if not amount or amount <= 0:
        return
    cls = class_name(defender)
    if cls == "Berserker" and _hp_ratio(defender) < 0.50:
        bonus = 2 if _hp_ratio(defender) < 0.25 else 1
        _message(defender, gain_meter(defender, "bloodied_momentum", bonus, "bloodied incoming damage"))
    if (
        cls in {"Sentinel", "Stalwart Defender"}
        and damage_type in {"Physical", "Melee"}
    ):
        _message(
            defender,
            build_resolve(
                defender,
                max(1, amount // 5),
                "mitigated pressure",
            ),
        )
    if cls == "Archdruid" and damage_type == "Physical":
        _message(defender, add_aspect(defender, "Stone"))
    if cls == "Rogue" and int(getattr(getattr(defender, "health", None), "current", 1) or 0) <= 0:
        _message(defender, cheat_death(defender))
    if (
        cls in {"Lancer", "Dragoon"}
        and int(getattr(getattr(defender, "health", None), "current", 1) or 0) <= 0
    ):
        from .aerial import try_dragon_soul

        _message(defender, try_dragon_soul(defender))
    if (
        cls in {"Lancer", "Dragoon"}
        and int(getattr(getattr(defender, "health", None), "current", 1) or 0) <= 0
    ):
        state = combat_state(defender)
        state["aerial_tempo"] = 0
        state["pending_aerial_follow_through"] = None
        from .. import class_rings

        class_rings.reset_combat_flags(defender)
    if (
        cls in {"Paladin", "Crusader"}
        and int(getattr(getattr(defender, "health", None), "current", 1) or 0) <= 0
    ):
        state = combat_state(defender)
        state["oath_conviction"] = 0
        state["oath_judgment_counter"] = None
        state["oath_protection_guard"] = None
        state["oath_retribution_shelter"] = None


def record_healing_done(actor: Any, amount: int) -> str:
    from .companions import add_aspect

    if not amount or amount <= 0:
        return ""
    cls = class_name(actor)
    msg = ""
    if cls in {"Cleric", "Templar"}:
        msg += _gain_or_queue_devotion(actor, 1, "meaningful healing")
    if cls == "Hierophant":
        msg += _gain_hierophant_devotion_once(actor, "meaningful healing")
    if cls in {"Priest", "Archbishop"}:
        msg += gain_meter(actor, "prayer", 1, "meaningful healing")
    if cls in {"Monk", "Master Monk"} and _has_skill(actor, "Chi Heal"):
        msg += gain_meter(actor, "ki", 1, "Chi Heal")
    if cls == "Archdruid":
        msg += add_aspect(actor, "Growth")
    return msg


def _consume_weapon_payoffs(actor: Any, target: Any, amount: int, damage_type: str) -> None:
    state = combat_state(actor)
    cls = class_name(actor)
    extra = 0
    lines: list[str] = []

    charge = _normalized_blade_charge(state.get("blade_charge"))
    quick_recharge = ""
    if cls == "Knight Enchanter":
        from .weaves import resolve_quick_recharge_hit

        quick_recharge = resolve_quick_recharge_hit(actor, target, amount)
        lines.append(quick_recharge)
    if not quick_recharge and cls in {"Spellblade", "Knight Enchanter"} and charge:
        lines.append(_release_blade_charge_damage(actor, target, amount, charge))
        state["blade_charge"] = None
        if cls == "Knight Enchanter":
            from .weaves import resolve_enchanted_assault

            lines.append(resolve_enchanted_assault(actor, target, amount, charge))

    stolen = int(state.get("stolen_charge", 0) or 0)
    if cls in {"Spell Stealer", "Arcane Trickster"} and stolen:
        burst = max(5 * stolen, int(amount * (0.20 * stolen)))
        extra += burst
        state["stolen_charge"] = 0
        lines.append(f"Stolen Charge releases for {burst} arcane damage.\n")
        _maybe_preserve(actor, "stolen_charge", "Arcane Trickster", "Arcane Larceny", lines)

    marks = _target_stacks(state.get("death_marks"), target)
    if cls in {"Assassin", "Ninja"} and marks:
        burst = max(1, int(amount * (0.12 * marks)))
        extra += burst
        _set_target_stacks(state.setdefault("death_marks", {}), target, 0)
        lines.append(f"Death Mark pays off for {burst} execution pressure.\n")
        _maybe_preserve(actor, "death_marks", "Ninja", "No-Trace Opener", lines, target=target)

    if extra > 0 and target is not None:
        target.health.current = max(0, target.health.current - extra)
    for line in lines:
        _message(actor, line)


_ELEMENTAL_CHARGE_TYPES = frozenset({
    "Earth",
    "Electric",
    "Fire",
    "Ice",
    "Lightning",
    "Water",
    "Wind",
})
_ELEMENTAL_RESISTANCE_TYPES = (
    "Earth",
    "Electric",
    "Fire",
    "Ice",
    "Water",
    "Wind",
)


def _normalized_blade_charge(value: Any) -> dict[str, Any] | None:
    """Return canonical Arcane and Elemental blade-charge pools."""
    if not isinstance(value, dict):
        return None
    arcane = max(0, int(value.get("Arcane", 0) or 0))
    elemental = max(0, int(value.get("Elemental", 0) or 0))
    count = arcane + elemental
    if not count:
        return None
    return {"Arcane": arcane, "Elemental": elemental, "count": count}


def _blade_charge_type(damage_type: str) -> str:
    """Collapse damaging spell types into Arcane or Elemental charges."""
    return (
        "Elemental"
        if str(damage_type or "") in _ELEMENTAL_CHARGE_TYPES
        else "Arcane"
    )


def _blade_charge_capacity(actor: Any) -> int:
    """Return each typed pool's capacity."""
    capacity = 1
    if _has_skill(actor, "Storage Capacity"):
        capacity += 1
    if _has_skill(actor, "Storage Capacity II"):
        capacity += 2
    return capacity


def _blade_charge_resistance(
    target: Any,
    actor: Any,
    charge_type: str,
) -> float:
    """Return resistance for one broad charge category."""
    if target is None:
        return 0.0
    if charge_type == "Arcane":
        return float(target.check_mod("resist", enemy=actor, typ="Arcane"))
    values = [
        float(target.check_mod("resist", enemy=actor, typ=element))
        for element in _ELEMENTAL_RESISTANCE_TYPES
    ]
    return sum(values) / len(values)


def _release_blade_charge_damage(
    actor: Any,
    target: Any,
    amount: int,
    charge: dict[str, Any],
) -> str:
    """Apply both typed charge pools to one release target."""
    lines = []
    for charge_type in ("Arcane", "Elemental"):
        count = int(charge.get(charge_type, 0) or 0)
        if count <= 0:
            continue
        amplified = _has_skill(actor, f"Amplify {charge_type}")
        percent = 0.24 if amplified else 0.12
        raw_damage = int(amount * percent) * count
        resistance = _blade_charge_resistance(target, actor, charge_type)
        charge_damage = int(raw_damage * (1.0 - resistance))
        if target is not None:
            if charge_damage >= 0:
                target.health.current = max(
                    0,
                    int(target.health.current) - charge_damage,
                )
            else:
                target.health.current = min(
                    int(target.health.max),
                    int(target.health.current) + abs(charge_damage),
                )
        qualifier = " amplified" if amplified else ""
        if charge_damage >= 0:
            lines.append(
                f"{actor.name}'s {count}{qualifier} {charge_type} blade "
                f"charge(s) release on {target.name} for {charge_damage} bonus damage.\n"
            )
        else:
            lines.append(
                f"{target.name} absorbs the {charge_type} blade charge and "
                f"recovers {abs(charge_damage)} health.\n"
            )
    return "".join(lines)


def _store_blade_charge(
    actor: Any,
    *,
    charge_type: str = "Arcane",
    deduplicate: bool = True,
) -> None:
    """Store one typed charge, normally at most once per combat action."""
    state = combat_state(actor)
    action_token = int(state.get("action_token", 0) or 0)
    if (
        deduplicate
        and action_token > 0
        and state.get("blade_charge_action_token") == action_token
    ):
        return
    current = _normalized_blade_charge(state.get("blade_charge"))
    capacity = _blade_charge_capacity(actor)
    normalized_type = "Elemental" if charge_type == "Elemental" else "Arcane"
    pools = {
        "Arcane": current["Arcane"] if current else 0,
        "Elemental": current["Elemental"] if current else 0,
    }
    pools[normalized_type] = min(capacity, pools[normalized_type] + 1)
    state["blade_charge"] = pools
    if deduplicate:
        state["blade_charge_action_token"] = (
            action_token if action_token > 0 else None
        )
    _message(
        actor,
        f"{actor.name}'s blade stores {normalized_type} "
        f"{pools[normalized_type]}/{capacity} "
        f"(Arcane {pools['Arcane']}, Elemental {pools['Elemental']}).\n",
    )


def _apply_breakdown_stack(actor: Any, target: Any) -> None:
    """Apply one per-target Breakdown stack after a damaging weapon hit."""
    if not _has_skill(actor, "Breakdown") or target is None:
        return
    stacks = combat_state(actor).setdefault("breakdown_stacks", {})
    current = _target_stacks(stacks, target)
    updated = min(5, current + 1)
    _set_target_stacks(stacks, target, updated)
    _message(
        actor,
        f"Breakdown lowers {target.name}'s Magic Defense ({updated}/5).\n",
    )


def breakdown_magic_defense_penalty(actor: Any, target: Any) -> int:
    """Return the Magic Defense penalty built by the actor on one target."""
    if actor is None or target is None or not _has_skill(actor, "Breakdown"):
        return 0
    stacks = combat_state(actor).get("breakdown_stacks", {})
    return 4 * min(5, _target_stacks(stacks, target))


def _clear_breakdown_stacks(actor: Any, target: Any) -> None:
    """Clear Breakdown after a spell deals positive damage to its target."""
    if target is None:
        return
    stacks = combat_state(actor).setdefault("breakdown_stacks", {})
    count = _target_stacks(stacks, target)
    if count <= 0:
        return
    _set_target_stacks(stacks, target, 0)
    _message(actor, f"{actor.name}'s spell consumes {count} Breakdown stack(s).\n")


def activate_novel_shield(character: Any, capacity: int) -> str:
    """Refresh a three-turn Novel Shielding absorption pool."""
    pool = max(0, int(capacity))
    combat_state(character)["novel_shield"] = {
        "remaining": pool,
        "maximum": pool,
        "turns": 3,
    }
    return f"{character.name} raises Novel Shielding with {pool} absorption.\n"


def absorb_novel_shield(
    defender: Any,
    damage: int,
    *,
    source: str,
) -> tuple[int, str, bool]:
    """Absorb post-mitigation direct damage with Novel Shielding."""
    if source not in {"spell", "weapon"}:
        return max(0, int(damage)), "", False
    state = combat_state(defender)
    shield = state.get("novel_shield")
    incoming = max(0, int(damage))
    if not isinstance(shield, dict) or incoming <= 0:
        return incoming, "", False
    remaining = max(0, int(shield.get("remaining", 0) or 0))
    turns = max(0, int(shield.get("turns", 0) or 0))
    if remaining <= 0 or turns <= 0:
        state["novel_shield"] = None
        return incoming, "", False
    absorbed = min(remaining, incoming)
    shield["remaining"] = remaining - absorbed
    resulting_damage = incoming - absorbed
    broken = shield["remaining"] <= 0
    if broken:
        state["novel_shield"] = None
    message = (
        f"{defender.name}'s Novel Shielding absorbs {absorbed} damage"
        + (
            " and shatters.\n"
            if broken
            else f" ({shield['remaining']} remains).\n"
        )
    )
    return resulting_damage, message, resulting_damage <= 0


def _maybe_preserve(
    actor: Any,
    key: str,
    ring_class: str,
    label: str,
    lines: list[str],
    *,
    target: Any | None = None,
) -> None:
    state = combat_state(actor)
    marker = f"{ring_class}:{key}"
    if marker in state.setdefault("ring_preserved", set()):
        return
    if not _ring_awakened_equipped(actor, ring_class):
        return
    state["ring_preserved"].add(marker)
    if target is None:
        state[key] = max(1, int(state.get(key, 0) or 0))
    else:
        _set_target_stacks(state.setdefault(key, {}), target, 1)
    lines.append(f"{label} preserves 1 spent {key.replace('_', ' ')}.\n")


def _target_key(target: Any) -> str:
    return str(id(target))


def _target_stacks(mapping: Any, target: Any) -> int:
    if not isinstance(mapping, dict) or target is None:
        return 0
    return int(mapping.get(_target_key(target), 0) or 0)


def _set_target_stacks(mapping: dict[str, int], target: Any, value: int) -> None:
    if target is None:
        return
    key = _target_key(target)
    if value <= 0:
        mapping.pop(key, None)
    else:
        mapping[key] = value


def _hp_ratio(character: Any) -> float:
    hp = getattr(character, "health", None)
    hp_max = max(1, int(getattr(hp, "max", 1) or 1))
    return max(0.0, min(1.0, int(getattr(hp, "current", hp_max) or 0) / hp_max))


def _spend_mp(character: Any, cost: int) -> bool:
    mana = getattr(character, "mana", None)
    if int(getattr(mana, "current", 0) or 0) < cost:
        return False
    mana.current -= cost
    return True


def threaded_cast(character: Any) -> str:
    if class_name(character) != "Astromancer":
        return "Only an Astromancer can thread a cast.\n"
    state = combat_state(character)
    threads = int(state.get("foresight_threads", 0) or 0)
    if threads <= 0:
        return "Threaded Cast requires at least 1 Foresight Thread.\n"
    if not _spend_mp(character, 8):
        return "Not enough MP for Threaded Cast.\n"
    state["threaded_cast_pending"] = True
    return f"{character.name} prepares Threaded Cast with {threads} Foresight Thread(s).\n"


def eclipse(character: Any) -> str:
    if class_name(character) != "Shadowcaster":
        return "Only a Shadowcaster can enter Eclipse.\n"
    data = _class_ring_data(character, "Shadowcaster")
    _normalize_shadowcaster_data(data)
    if int(data.get("debt", 0) or 0) < 20:
        return "Eclipse requires at least 20 Umbral Debt.\n"
    data["debt"] -= 20
    data["eclipse_turns"] = 3
    return f"{character.name} spends 20 Umbral Debt and enters Eclipse for 3 turns.\n"


def shadowcaster_debt_cap(character: Any) -> int:
    hp_max = max(1, int(getattr(getattr(character, "health", None), "max", 1) or 1))
    pct = 0.45 if _ring_awakened_equipped(character, "Shadowcaster") else 0.30
    return max(1, int(hp_max * pct))


def record_shadow_damage(character: Any, amount: int) -> None:
    if class_name(character) != "Shadowcaster" or amount <= 0:
        return
    data = _class_ring_data(character, "Shadowcaster")
    _normalize_shadowcaster_data(data)
    familiar = getattr(getattr(character, "familiar", None), "spec", "")
    rate = 0.25 if familiar == "Arcane" else 0.20
    gain = max(1, int(amount * rate))
    cap = shadowcaster_debt_cap(character)
    new_debt = int(data.get("debt", 0) or 0) + gain
    if new_debt > cap:
        over = new_debt - cap
        if _ring_awakened_equipped(character, "Shadowcaster"):
            over = int(over * 0.75)
        data["backlash"] = int(data.get("backlash", 0) or 0) + over
        new_debt = cap
    data["debt"] = new_debt
    _message(character, f"{character.name} stores {gain} Umbral Debt ({new_debt}/{cap}).\n")


def _normalize_shadowcaster_data(data: dict[str, Any]) -> None:
    data["debt"] = max(0, int(data.get("debt", 0) or 0))
    data["backlash"] = max(0, int(data.get("backlash", 0) or 0))
    data["eclipse_turns"] = max(0, int(data.get("eclipse_turns", 0) or 0))
    data["familiar_echo_used"] = bool(data.get("familiar_echo_used", False))


def _reset_shadowcaster_combat_fields(character: Any) -> None:
    data = _class_ring_data(character, "Shadowcaster")
    if data:
        data["eclipse_turns"] = 0
        data["familiar_echo_used"] = False


def convert_shadow_backlash(character: Any, *, fraction: float, reason: str) -> str:
    if class_name(character) != "Shadowcaster":
        return ""
    data = _class_ring_data(character, "Shadowcaster")
    _normalize_shadowcaster_data(data)
    backlash = int(data.get("backlash", 0) or 0)
    if backlash <= 0:
        return ""
    hp_max = max(1, int(character.health.max or 1))
    amount = min(backlash, max(1, int(hp_max * fraction)))
    if getattr(getattr(character, "familiar", None), "spec", "") == "Luck" and not data.get("familiar_echo_used"):
        amount = max(0, amount // 2)
        data["familiar_echo_used"] = True
    data["backlash"] = backlash - amount
    if amount:
        character.health.current = max(1, character.health.current - amount)
    return f"Umbral backlash converts {amount} stored pressure into nonlethal shadow damage at {reason}.\n"
