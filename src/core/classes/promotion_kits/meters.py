"""Promotion combat meters and shared payoff mechanics."""

from __future__ import annotations

import random
from typing import Any

from ...progression_manifest import TALENT_KIT_EFFECTS as _TALENT_KIT_EFFECTS
from .state import (
    _claim_action,
    _class_ring_data,
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
        if effect[:2] == ("meter_cap", effect_key) and has_talent(character, talent_key)
    )


def cap_for(character: Any, key: str) -> int:
    cls = class_name(character)
    base = 0
    if key == "foresight_threads":
        base = 3 if cls == "Astromancer" else 0
    elif key == "bloodied_momentum":
        if cls != "Berserker":
            return 0
        scars = int(_class_ring_data(character, "Berserker").get("battle_scars", 0) or 0)
        return 5 if scars >= 20 else 4 if scars >= 10 else 3
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
    if key in {"death_marks", "fortune", "misfortune", "revelation"}:
        return base
    return base + _talent_cap_bonus(character, key) if base else 0


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


def gain_bloodied_momentum(
    character: Any,
    reason: str,
    *,
    incoming: bool = False,
) -> str:
    """Grant one action-deduplicated Momentum gain and its round bonus."""
    if class_name(character) != "Berserker" or _hp_ratio(character) >= 0.50:
        return ""
    if not _claim_action(character, "bloodied_momentum", incoming=incoming):
        return ""
    state = combat_state(character)
    amount = 1
    current_round = int(state.get("action_round", 0) or 0)
    if _hp_ratio(character) < 0.25 and state.get("bloodied_bonus_round") != current_round:
        amount += 1
        state["bloodied_bonus_round"] = current_round
    return gain_meter(character, "bloodied_momentum", amount, reason)


def _power_up_active(character: Any, skill_name: str) -> bool:
    effect = getattr(character, "class_effects", {}).get("Power Up")
    return bool(
        getattr(character, "power_up", False)
        and _has_skill(character, skill_name)
        and effect is not None
        and getattr(effect, "active", False)
    )


def _devotion_amount(character: Any, *, holy_or_shield: bool) -> int:
    amount = (
        2
        if class_name(character) == "Hierophant" and _hierophant_overchannel_active(character)
        else 1
    )
    from ..cleric import has_cleric_talent

    if (
        class_name(character) == "Hierophant"
        and not holy_or_shield
        and has_cleric_talent(character, "hierophant.gentle-grace")
    ):
        amount += 1
    state = combat_state(character)
    current_round = int(state.get("action_round", 0) or 0)
    if (
        class_name(character) == "Templar"
        and holy_or_shield
        and _power_up_active(character, "Holy Retribution")
        and state.get("holy_retribution_gain_round") != current_round
    ):
        amount += 1
        state["holy_retribution_gain_round"] = current_round
    return amount


def record_devotion_source(
    character: Any,
    reason: str,
    *,
    hostile: bool = False,
    holy_or_shield: bool = False,
) -> str:
    """Record one successful authored Devotion source for this action."""
    if class_name(character) not in {"Cleric", "Templar", "Hierophant"}:
        return ""
    if not _claim_action(character, "devotion"):
        return ""
    amount = _devotion_amount(character, holy_or_shield=holy_or_shield)
    from ..cleric import has_cleric_talent

    if reason == "Holy pressure" and has_cleric_talent(character, "cleric.consecrated-blows"):
        amount += 1
    if reason == "Holy pressure" and has_cleric_talent(character, "hierophant.luminous-doctrine"):
        amount += 1
    return _gain_or_queue_devotion(
        character,
        amount,
        reason,
        require_survivor=hostile,
    )


def record_prayer_source(character: Any, reason: str, *, divine_support: bool = False) -> str:
    """Record one successful authored Prayer source for this action."""
    if class_name(character) not in {"Priest", "Archbishop"}:
        return ""
    choice = str(combat_state(character).get("action_choice") or "")
    if choice in {"Supplication", "Great Benediction", "Great Gospel"}:
        return ""
    if not _claim_action(character, "prayer"):
        return ""
    amount = 1
    from ...progression import has_talent

    if divine_support and has_talent(character, "priest.deliberate-prayer"):
        amount += 1
    if int(combat_state(character).get("prayer", 0) or 0) == 0 and has_talent(
        character, "archbishop.first-words"
    ):
        amount += 1
    state = combat_state(character)
    current_round = int(state.get("action_round", 0) or 0)
    if (
        divine_support
        and _power_up_active(character, "Great Gospel")
        and state.get("great_gospel_gain_round") != current_round
    ):
        amount += 1
        state["great_gospel_gain_round"] = current_round
    return gain_meter(character, "prayer", amount, reason)


def record_defensive_regen(character: Any, amount: int) -> str:
    """Resolve the one Prayer gain attached to a Defend activation."""
    state = combat_state(character)
    if not state.get("defensive_regen_prayer_armed"):
        return ""
    state["defensive_regen_prayer_armed"] = False
    threshold = max(5, int((max(1, character.health.max) * 0.05) + 0.999))
    if amount < threshold:
        return ""
    state.setdefault("action_claims", set()).discard("prayer")
    return record_prayer_source(
        character,
        "Defensive Regen",
        divine_support=True,
    )


def _gain_or_queue_devotion(
    character: Any,
    amount: int,
    reason: str,
    *,
    require_survivor: bool = False,
) -> str:
    state = combat_state(character)
    if not state.get("defer_devotion_until_survival"):
        return gain_meter(character, "devotion", amount, reason)
    pending = state.get("pending_devotion_gains")
    if not isinstance(pending, list):
        pending = []
        state["pending_devotion_gains"] = pending
    pending.append(
        {
            "amount": max(0, int(amount or 0)),
            "reason": reason,
            "require_survivor": bool(require_survivor),
        }
    )
    return ""


def finish_action(character: Any, *, defender_survived: bool) -> str:
    from .aerial import finish_aerial_follow_through

    state = combat_state(character)
    pending = state.get("pending_devotion_gains")
    choice = str(state.get("action_choice") or state.get("action_name") or "")
    state["defer_devotion_until_survival"] = False
    state["pending_devotion_gains"] = []
    state["pending_hierophant_devotion_token"] = None
    msg = finish_aerial_follow_through(character)
    msg += finish_stolen_charge_payoff(character)
    if (
        choice == "Defend"
        and getattr(
            getattr(character, "equipment", {}).get("OffHand"),
            "subtyp",
            None,
        )
        == "Shield"
    ):
        msg += record_devotion_source(
            character,
            "shielded Defend",
            holy_or_shield=True,
        )
    if choice == "Great Gospel" and _power_up_active(character, "Great Gospel"):
        from .tracks import great_gospel_prayer

        msg += great_gospel_prayer(character)
    if (
        choice == "Defend"
        and class_name(character) in {"Priest", "Archbishop"}
        and _has_skill(character, "Defensive Regen")
    ):
        state["defensive_regen_prayer_armed"] = True
    if isinstance(pending, list):
        for entry in pending:
            if entry.get("require_survivor") and not defender_survived:
                continue
            msg += gain_meter(
                character,
                "devotion",
                int(entry.get("amount", 0) or 0),
                str(entry.get("reason") or ""),
            )
    state["consecrated_conduit_action"] = None
    return msg


def spend_meter(character: Any, key: str) -> int:
    state = combat_state(character)
    value = int(state.get(key, 0) or 0)
    state[key] = 0
    return max(0, value)


def _stolen_charge_action_is_eligible(action: str, ability: Any | None) -> bool:
    """Return whether an action can release stored stolen magic."""
    if action == "Attack":
        return True
    if action == "Use Skill":
        return bool(getattr(ability, "weapon", False))
    if action not in {"Cast Spell", "Steal As Well"} or ability is None:
        return False
    try:
        return float(getattr(ability, "dmg_mod", 0) or 0) > 0
    except (TypeError, ValueError):
        return False


def prepare_stolen_charge_payoff(
    character: Any,
    action: str,
    ability: Any | None = None,
) -> str:
    """Spend Charge after validation and arm one action-level Arcane payoff."""
    if class_name(character) not in {"Spell Stealer", "Arcane Trickster"}:
        return ""
    if not _stolen_charge_action_is_eligible(action, ability):
        return ""
    state = combat_state(character)
    if state.get("pending_stolen_charge_payoff") is not None:
        return ""
    charge = max(0, int(state.get("stolen_charge", 0) or 0))
    if charge <= 0:
        return ""
    state["stolen_charge"] = 0
    state["pending_stolen_charge_payoff"] = {"stacks": charge, "action": action}
    return f"{character.name} commits {charge} Stolen Charge to the attack.\n"


def _resolve_stolen_charge_payoff(character: Any, portions: list[Any]) -> str:
    """Resolve one typed Arcane burst from an aggregate action result."""
    state = combat_state(character)
    pending = state.get("pending_stolen_charge_payoff")
    if not isinstance(pending, dict):
        return ""
    state["pending_stolen_charge_payoff"] = None
    stacks = max(1, int(pending.get("stacks", 1) or 1))
    total_damage = sum(max(0, int(getattr(portion, "damage", 0) or 0)) for portion in portions)
    target = next(
        (
            getattr(portion, "target", None)
            for portion in portions
            if int(getattr(portion, "damage", 0) or 0) > 0
            and getattr(portion, "target", None) is not None
            and getattr(portion.target, "is_alive", lambda: False)()
        ),
        None,
    )
    if total_damage <= 0 or target is None:
        return _failed_stolen_charge_message(character)
    multiplier = 0.20
    try:
        from ...progression import has_talent

        if has_talent(character, "spell-stealer.volatile-script"):
            multiplier = 0.25
    except (AttributeError, KeyError, TypeError, ValueError):
        pass
    raw_bonus = max(5 * stacks, int(total_damage * (multiplier * stacks)))
    hit, reduction_message, reduced = target.damage_reduction(
        raw_bonus,
        character,
        typ="Arcane",
    )
    bonus = max(0, min(int(reduced or 0), int(target.health.current))) if hit else 0
    if bonus <= 0:
        return reduction_message + _failed_stolen_charge_message(character)
    target.health.current -= bonus
    character._emit_damage_event(
        target,
        bonus,
        damage_type="Arcane",
        source="promotion_kit_payoff",
        ability_name="Stolen Charge",
    )
    lines = [reduction_message, f"Stolen Charge releases for {bonus} Arcane damage.\n"]
    try:
        from ...progression import has_talent

        misdirection = has_talent(character, "arcane-trickster.misdirection")
    except (AttributeError, KeyError, TypeError, ValueError):
        misdirection = False
    if misdirection:
        penalty = max(3, int(character.stats.intel) // 6)
        for stat_name in ("Attack", "Magic"):
            effect = target.stat_effects[stat_name]
            effect.active = True
            effect.duration = max(int(effect.duration or 0), 2)
            effect.extra = min(int(effect.extra or 0), -penalty)
            effect.source = "Misdirection"
        lines.append(f"Misdirection lowers {target.name}'s Attack and Magic by {penalty}.\n")
    _maybe_preserve(
        character,
        "stolen_charge",
        "Arcane Trickster",
        "Arcane Larceny",
        lines,
    )
    return "".join(lines)


def _failed_stolen_charge_message(character: Any) -> str:
    """Resolve a failed discharge, retaining one stack when trained."""
    try:
        from ...progression import has_talent

        controlled = has_talent(character, "spell-stealer.controlled-discharge")
    except (AttributeError, KeyError, TypeError, ValueError):
        controlled = False
    if controlled:
        state = combat_state(character)
        state["stolen_charge"] = min(
            cap_for(character, "stolen_charge"),
            int(state.get("stolen_charge", 0) or 0) + 1,
        )
        return "Controlled Discharge retains 1 Stolen Charge.\n"
    return "Stolen Charge dissipates without finding purchase.\n"


def finish_stolen_charge_payoff(character: Any) -> str:
    """Consume an unresolved payoff when an eligible action produced no result."""
    state = combat_state(character)
    if not isinstance(state.get("pending_stolen_charge_payoff"), dict):
        return ""
    state["pending_stolen_charge_payoff"] = None
    return _failed_stolen_charge_message(character)


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


def prepare_action_payoffs(character: Any, action: str | None, choice: str | None) -> None:
    """Consume pending action-scoped preparations after ordinary validation."""
    state = combat_state(character)
    state["consecrated_conduit_action"] = None
    conduit = state.get("consecrated_conduit")
    if class_name(character) != "Hierophant" or not isinstance(conduit, dict):
        return
    weapon = getattr(character, "equipment", {}).get("Weapon")
    staff_action = action == "Attack" and getattr(weapon, "subtyp", None) == "Staff"
    normalized = str(choice or "").lower()
    holy_action = normalized.startswith(("smite", "holy", "turn undead"))
    if staff_action or holy_action:
        state["consecrated_conduit_action"] = dict(conduit)
        state["consecrated_conduit"] = None


def _consume_consecrated_conduit(
    actor: Any,
    target: Any,
    amount: int,
    damage_type: str,
    metadata: dict[str, Any] | None,
) -> None:
    state = combat_state(actor)
    conduit = state.get("consecrated_conduit_action")
    if class_name(actor) != "Hierophant" or not isinstance(conduit, dict):
        return
    staff_hit = _is_hierophant_staff_hit(actor, metadata)
    ability_name = str((metadata or {}).get("ability_name") or "")
    holy_action = damage_type == "Holy" or ability_name.lower().startswith(("smite", "holy"))
    if not (staff_hit or holy_action):
        return
    stacks = max(1, int(conduit.get("stacks", 1) or 1))
    multiplier = 0.12 + (0.03 * stacks)
    from ..cleric import has_cleric_talent

    if has_cleric_talent(actor, "hierophant.deep-conduit"):
        multiplier += 0.08
    if _hierophant_overchannel_active(actor):
        multiplier += 0.08
    if _ring_awakened_equipped(actor, "Hierophant") and staff_hit:
        multiplier += 0.05
    raw_bonus = max(2 * stacks, int(amount * multiplier))
    bonus = 0
    reduction_message = ""
    if target is not None:
        hit, reduction_message, reduced = target.damage_reduction(
            raw_bonus,
            actor,
            typ="Holy",
        )
        bonus = max(0, min(int(reduced or 0), int(target.health.current))) if hit else 0
        target.health.current -= bonus
    state["consecrated_conduit_action"] = None
    if bonus <= 0:
        _message(actor, reduction_message or "Consecrated Conduit is fully resisted.\n")
        return
    actor._emit_damage_event(
        target,
        bonus,
        damage_type="Holy",
        source="promotion_kit_payoff",
        ability_name="Consecrated Conduit",
    )
    ward = getattr(actor, "magic_effects", {}).get("Nature Shield")
    if ward is not None:
        ward.active = True
        ward.duration = max(int(getattr(ward, "duration", 0) or 0), 2)
        ward_scale = 1.5 if has_cleric_talent(actor, "hierophant.staff-ward") else 1.0
        ward.extra = max(
            int(getattr(ward, "extra", 0) or 0),
            max(8, int(stacks * 6 * ward_scale)),
        )
    mana = getattr(actor, "mana", None)
    if mana is not None:
        return_floor = stacks if _hierophant_overchannel_active(actor) else max(1, stacks // 2)
        if has_cleric_talent(actor, "hierophant.radiant-return"):
            return_floor = stacks
        returned = min(
            int(getattr(mana, "max", 0) or 0) - int(getattr(mana, "current", 0) or 0),
            max(1, return_floor),
        )
        if returned > 0:
            mana.current += returned
    lines = [
        reduction_message,
        f"Consecrated Conduit releases for {bonus} holy damage.\n",
        "A modest ward settles around the Hierophant.\n",
    ]
    _maybe_preserve(actor, "devotion", "Hierophant", "Sacred Conduit", lines)
    for line in lines:
        _message(actor, line)


def record_devotion_block(character: Any) -> str:
    """Grant Devotion once for a successful shield block action."""
    if not _claim_action(character, "devotion_block", incoming=True):
        return ""
    if class_name(character) not in {"Cleric", "Templar", "Hierophant"}:
        return ""
    from ..cleric import has_cleric_talent

    amount = 2 if has_cleric_talent(character, "cleric.shield-litany") else 1
    return gain_meter(
        character,
        "devotion",
        amount,
        "a successful shield block",
    )


PRAYER_SUPPORT_ABILITIES = frozenset(
    {
        "Bless",
        "Cleanse",
        "Dispel",
        "Mana Shield",
        "Mana Shield 2",
        "Prayer of Faith",
        "Regen",
        "Regen2",
        "Regen3",
        "Resurrection",
        "Shell",
        "Silence",
    }
)
STORM_UTILITY_ABILITIES = frozenset({"Ball Lightning", "Windswept"})
STONE_UTILITY_ABILITIES = frozenset({"Nature Shield", "Stone Skin"})


def record_action_resolution(character: Any, result: Any | None) -> str:
    """Translate a structured action result into authored meter outcomes."""
    if result is None:
        return ""
    portions = getattr(result, "results", None)
    if not isinstance(portions, list):
        portions = [result]
    choice = str(combat_state(character).get("action_choice") or "")
    successful = False
    applied = False
    for portion in portions:
        damage = max(0, int(getattr(portion, "damage", 0) or 0))
        healing = max(0, int(getattr(portion, "healing", 0) or 0))
        effects = getattr(portion, "effects_applied", {}) or {}
        changed = (
            any(bool(values) for values in effects.values()) if isinstance(effects, dict) else False
        )
        successful = successful or damage > 0 or healing > 0 or bool(getattr(portion, "hit", False))
        applied = applied or changed
    msg = _resolve_stolen_charge_payoff(character, portions)
    if choice in PRAYER_SUPPORT_ABILITIES and (successful or applied):
        msg += record_prayer_source(character, choice, divine_support=True)
    if choice == "Turn Undead" and successful:
        msg += record_devotion_source(
            character,
            "Turn Undead",
            hostile=True,
            holy_or_shield=True,
        )
    if class_name(character) == "Archdruid" and (successful or applied):
        from .companions import add_aspect

        if choice in STORM_UTILITY_ABILITIES:
            msg += add_aspect(character, "Storm")
        if choice in STONE_UTILITY_ABILITIES:
            msg += add_aspect(character, "Stone")
        if choice == "Tree of Life":
            msg += add_aspect(character, "Growth")
    if class_name(character) in {"Shaman", "Soulcatcher"} and (successful or applied):
        from .. import nature_totems
        from .companions import gain_totem_resonance

        if (
            choice != "Totem Surge"
            and nature_totems.spell_aspect(choice) == nature_totems.active_totem_aspect(character)
            and _claim_action(character, "totem_resonance")
        ):
            msg += gain_totem_resonance(character, "matching cast")
            if (
                nature_totems.has_nature_talent(character, "soulcatcher.ancestral-current")
                and random.random() < 0.25
            ):
                msg += gain_totem_resonance(character, "Ancestral Current")
    return msg


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
    try:
        from .. import mage_mechanics

        spell_metadata = dict(metadata or {})
        spell_metadata["damage_type"] = damage_type
        mage_mechanics.record_spell_damage_hit(actor, target, spell_metadata)
    except Exception:
        pass
    cls = class_name(actor)
    damage_type = str(damage_type or "Physical")
    weapon_hit = _is_weapon_hit(metadata)
    resource_payoff = str((metadata or {}).get("source") or "") == "promotion_kit_payoff"
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
    if critical_hit and cls in {"Shaman", "Soulcatcher"} and target is not None:
        from .. import nature_totems

        if nature_totems.has_nature_talent(actor, "shaman.bad-omens"):
            _message(actor, nature_totems.add_dread(actor, target, "a critical hit"))
            if nature_totems.has_nature_talent(actor, "soulcatcher.haunting-blows"):
                _message(actor, nature_totems.add_dread(actor, target, "Haunting Blows"))
    if cls == "Soulcatcher" and str((metadata or {}).get("ability_name") or "") == "Soul Drain":
        from .. import nature_totems

        if nature_totems.has_nature_talent(actor, "soulcatcher.gentle-reaping"):
            healing = min(
                max(0, int(actor.health.max) - int(actor.health.current)),
                max(1, int(amount * 0.25)),
            )
            actor.health.current += healing
            if healing:
                _message(actor, f"Gentle Reaping restores {healing} health.\n")

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

    if (
        cls == "Berserker"
        and weapon_hit
        and not getattr(actor, "_final_assault_countering", False)
        and combat_state(actor).get("bloodied_payoff_action_token")
        != int(combat_state(actor).get("action_token", 0) or 0)
    ):
        _message(actor, gain_bloodied_momentum(actor, "bloodied weapon hit"))

    if not resource_payoff and cls in {"Thief", "Rogue"} and weapon_hit:
        from .tracks import RISKY_LUCK_ACTIONS, record_luck_roll

        choice = str(combat_state(actor).get("action_choice") or "")
        if choice not in RISKY_LUCK_ACTIONS:
            reason = "critical attack" if critical_hit else "attack"
            _message(actor, record_luck_roll(actor, True, reason))

    if not resource_payoff and cls in {"Cleric", "Templar"} and damage_type == "Holy":
        _message(
            actor,
            record_devotion_source(
                actor,
                "Holy pressure",
                hostile=True,
                holy_or_shield=True,
            ),
        )
    if (
        not resource_payoff
        and cls in {"Cleric", "Templar"}
        and str((metadata or {}).get("ability_name") or "") == "Shield Slam"
    ):
        _message(
            actor,
            record_devotion_source(
                actor,
                "Shield Slam",
                hostile=True,
                holy_or_shield=True,
            ),
        )
    if cls == "Hierophant" and not resource_payoff:
        staff_hit = _is_hierophant_staff_hit(actor, metadata)
        turn_undead = (
            str((metadata or {}).get("ability_name") or "").lower().startswith("turn undead")
        )
        if damage_type == "Holy" or staff_hit or turn_undead:
            reason = "staff conduit" if staff_hit else "holy action"
            _message(
                actor,
                record_devotion_source(
                    actor,
                    reason,
                    hostile=True,
                    holy_or_shield=True,
                ),
            )
        _consume_consecrated_conduit(actor, target, amount, damage_type, metadata)

    if not resource_payoff and cls in {"Priest", "Archbishop"} and damage_type == "Holy":
        _message(actor, record_prayer_source(actor, "Holy spell"))

    if cls in {"Monk", "Master Monk"} and weapon_hit:
        from .tracks import record_ki_martial_hit

        _message(actor, record_ki_martial_hit(actor, metadata))

    if cls == "Archdruid" and not resource_payoff:
        if damage_type in {"Poison"}:
            _message(actor, add_aspect(actor, "Venom"))
        if damage_type in {"Electric", "Wind"}:
            _message(actor, add_aspect(actor, "Storm"))
        if damage_type in {"Earth", "Physical"} and not weapon_hit:
            _message(actor, add_aspect(actor, "Stone"))

    if cls in {"Shaman", "Soulcatcher"} and not hasattr(actor, "_totem_pulse_potency"):
        from .. import nature_totems
        from .companions import gain_totem_resonance

        ability_name = str((metadata or {}).get("ability_name") or "")
        if nature_totems.spell_aspect(ability_name) == nature_totems.active_totem_aspect(
            actor
        ) and _claim_action(actor, "totem_resonance"):
            _message(actor, gain_totem_resonance(actor, "matching cast"))

    if weapon_hit:
        _apply_breakdown_stack(actor, target)
        _consume_weapon_payoffs(actor, target, amount, damage_type)
    elif spell_hit:
        _clear_breakdown_stacks(actor, target)
    if target is not None and not target.is_alive():
        from .tracks import clear_death_marks

        clear_death_marks(actor, target)


def record_damage_taken(defender: Any, amount: int, damage_type: str) -> None:
    from .companions import add_aspect
    from .resolve import build_resolve
    from .tracks import cheat_death

    if not amount or amount <= 0:
        return
    cls = class_name(defender)
    if cls == "Master Monk":
        from .tracks import break_rope_a_dope

        _message(defender, break_rope_a_dope(defender))
    if cls == "Berserker":
        state = combat_state(defender)
        if int(getattr(getattr(defender, "health", None), "current", 0) or 0) <= 0:
            state["bloodied_momentum"] = 0
            state["bloodied_bonus_round"] = None
            state["bloodied_payoff_action_token"] = None
            state["battle_scar_momentum_preserved"] = False
            state["bloodied_ring_miss_preserved"] = False
        else:
            _message(
                defender,
                gain_bloodied_momentum(
                    defender,
                    "bloodied incoming damage",
                    incoming=True,
                ),
            )
    if cls in {"Sentinel", "Stalwart Defender"} and damage_type in {"Physical", "Melee"}:
        _message(
            defender,
            build_resolve(
                defender,
                max(1, amount // 5),
                "mitigated pressure",
            ),
        )
    if (
        cls == "Archdruid"
        and damage_type == "Physical"
        and int(getattr(getattr(defender, "health", None), "current", 0) or 0) > 0
    ):
        _message(defender, add_aspect(defender, "Stone", incoming=True))
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


def record_healing_done(
    actor: Any,
    amount: int,
    *,
    source: str = "Unknown",
    target: Any | None = None,
) -> str:
    from ..cleric import has_cleric_talent
    from .companions import add_aspect

    if not amount or amount <= 0:
        return ""
    cls = class_name(actor)
    recipient = target or actor
    threshold = max(5, int((max(1, recipient.health.max) * 0.05) + 0.999))
    meaningful = amount >= threshold
    msg = ""
    passive = str(source).lower().startswith(("regen", "water totem"))
    if meaningful and cls in {"Cleric", "Templar", "Hierophant"}:
        msg += record_devotion_source(actor, "meaningful healing")
    if (
        meaningful
        and not passive
        and cls == "Hierophant"
        and has_cleric_talent(actor, "hierophant.merciful-ward")
    ):
        ward = recipient.magic_effects["Nature Shield"]
        ward.active = True
        ward.duration = max(int(ward.duration or 0), 2)
        ward.extra = max(
            int(ward.extra or 0),
            max(6, int(getattr(actor.stats, "wisdom", 0) or 0) // 4),
        )
        msg += f"Merciful Ward shelters {recipient.name}.\n"
    if meaningful and cls in {"Priest", "Archbishop"} and not passive:
        msg += record_prayer_source(actor, "meaningful healing", divine_support=True)
    if cls in {"Monk", "Master Monk"} and _has_skill(actor, "Chi Heal"):
        state = combat_state(actor)
        token = int(state.get("action_token", 0) or 0)
        if state.get("action_choice") == "Chi Heal" and state.get("ki_action_token") != token:
            state["ki_action_token"] = token
            msg += gain_meter(actor, "ki", 1, "Chi Heal")
    if cls == "Archdruid" and meaningful:
        msg += add_aspect(actor, "Growth")
    if cls in {"Shaman", "Soulcatcher"} and not hasattr(actor, "_totem_pulse_potency"):
        from .. import nature_totems
        from .companions import gain_totem_resonance

        if nature_totems.spell_aspect(source) == nature_totems.active_totem_aspect(
            actor
        ) and _claim_action(actor, "totem_resonance"):
            msg += gain_totem_resonance(actor, "matching cast")
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

    if extra > 0 and target is not None:
        target.health.current = max(0, target.health.current - extra)
    for line in lines:
        _message(actor, line)


_ELEMENTAL_CHARGE_TYPES = frozenset(
    {
        "Earth",
        "Electric",
        "Fire",
        "Ice",
        "Lightning",
        "Water",
        "Wind",
    }
)
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
    return "Elemental" if str(damage_type or "") in _ELEMENTAL_CHARGE_TYPES else "Arcane"


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
    if deduplicate and action_token > 0 and state.get("blade_charge_action_token") == action_token:
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
        state["blade_charge_action_token"] = action_token if action_token > 0 else None
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
    message = f"{defender.name}'s Novel Shielding absorbs {absorbed} damage" + (
        " and shatters.\n" if broken else f" ({shield['remaining']} remains).\n"
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
    marker = (
        "Rogue:luck"
        if ring_class == "Rogue" and key in {"fortune", "misfortune"}
        else f"{ring_class}:{key}"
    )
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
    if state.get("threaded_cast_pending"):
        return "Threaded Cast is already prepared.\n"
    if not _spend_mp(character, 8):
        return "Not enough MP for Threaded Cast.\n"
    state["threaded_cast_pending"] = True
    return f"{character.name} prepares Threaded Cast with {threads} Foresight Thread(s).\n"


def shade_of_ahool(character: Any) -> str:
    if class_name(character) != "Shadowcaster":
        return "Only a Shadowcaster can become the Shade of Ahool.\n"
    data = _class_ring_data(character, "Shadowcaster")
    _normalize_shadowcaster_data(data)
    if int(data.get("debt", 0) or 0) < 20:
        return "Shade of Ahool requires at least 20 Umbral Debt.\n"
    data["debt"] -= 20
    data["eclipse_turns"] = 3
    if hasattr(character, "shade_of_ahool_turns"):
        delattr(character, "shade_of_ahool_turns")
    character.flying = True
    return f"{character.name} spends 20 Umbral Debt and becomes the Shade of Ahool for 3 turns.\n"


def eclipse(character: Any) -> str:
    """Backward-compatible alias for old saves and integrations."""
    return shade_of_ahool(character)


def shadowcaster_debt_cap(character: Any) -> int:
    hp_max = max(1, int(getattr(getattr(character, "health", None), "max", 1) or 1))
    pct = 0.45 if _ring_awakened_equipped(character, "Shadowcaster") else 0.30
    return max(1, int(hp_max * pct))


def record_shadow_damage(character: Any, amount: int) -> None:
    if class_name(character) != "Shadowcaster" or amount <= 0:
        return
    cap = shadowcaster_debt_cap(character)
    data = _class_ring_data(character, "Shadowcaster")
    _normalize_shadowcaster_data(data)
    familiar = getattr(getattr(character, "familiar", None), "spec", "")
    rate = 0.25 if familiar == "Arcane" else 0.20
    gain = max(1, int(amount * rate))
    new_debt = int(data.get("debt", 0) or 0) + gain
    if new_debt > cap:
        over = new_debt - cap
        data["backlash"] = int(data.get("backlash", 0) or 0) + over
        new_debt = cap
    data["debt"] = new_debt
    _message(character, f"{character.name} stores {gain} Umbral Debt ({new_debt}/{cap}).\n")


def _normalize_shadowcaster_data(data: dict[str, Any]) -> None:
    for key in ("debt", "backlash", "eclipse_turns"):
        try:
            value = int(data.get(key, 0) or 0)
        except (TypeError, ValueError):
            value = 0
        data[key] = max(0, value)
    data["familiar_echo_used"] = bool(data.get("familiar_echo_used", False))


def _reset_shadowcaster_combat_fields(character: Any) -> None:
    data = _class_ring_data(character, "Shadowcaster")
    if data:
        was_active = int(data.get("eclipse_turns", 0) or 0) > 0
        data["eclipse_turns"] = 0
        data["familiar_echo_used"] = False
        if was_active:
            character.flying = False
    if hasattr(character, "shade_of_ahool_turns"):
        delattr(character, "shade_of_ahool_turns")


def _fairy_debt_echo(character: Any, debt_spent: int) -> str:
    familiar = getattr(character, "familiar", None)
    if getattr(familiar, "spec", "") != "Support" or debt_spent <= 0:
        return ""
    missing = max(0, int(character.health.max) - int(character.health.current))
    healing = min(missing, max(1, int(debt_spent * 0.05)))
    if healing <= 0:
        return ""
    character.health.current += healing
    return f"{getattr(familiar, 'name', 'Fairy')} restores {healing} extra HP from spent debt.\n"


def convert_shadow_backlash(
    character: Any,
    *,
    fraction: float,
    reason: str,
    ring_stability: bool = True,
) -> str:
    if class_name(character) != "Shadowcaster":
        return ""
    stable_ring = ring_stability and _ring_awakened_equipped(
        character,
        "Shadowcaster",
    )
    data = _class_ring_data(character, "Shadowcaster")
    _normalize_shadowcaster_data(data)
    backlash = int(data.get("backlash", 0) or 0)
    if backlash <= 0:
        return ""
    hp_max = max(1, int(character.health.max or 1))
    amount = min(backlash, max(1, int(hp_max * fraction)))
    if stable_ring:
        amount = max(1, int(amount * 0.75))
    if getattr(getattr(character, "familiar", None), "spec", "") == "Luck" and not data.get(
        "familiar_echo_used"
    ):
        data["familiar_echo_used"] = True
        if random.random() < 0.30:
            amount = max(1, amount // 2)
    data["backlash"] = backlash - amount
    if amount:
        character.health.current = max(1, character.health.current - amount)
    return f"Umbral backlash converts {amount} stored pressure into nonlethal shadow damage at {reason}.\n"
