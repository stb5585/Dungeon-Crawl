"""Totem, summon, companion, song, and transformation progression."""

from __future__ import annotations

import math
import random
from typing import Any

from .meters import _spend_mp, cap_for, gain_meter
from .state import (
    ADVANCED_SONGS,
    SUMMON_NAMES,
    _clamp_int,
    _ring_awakened_equipped,
    class_name,
    combat_state,
    ensure_state,
)
from .tracks import _preserve_spent_meter


XENID_CASTER_EFFECTS = {
    "Hodag": {"strength": 4, "melee": 0.10},
    "Caladrius": {"wisdom": 4, "healing": 0.12},
    "Patagon": {"strength": 3, "melee": 0.10},
    "Kobalos": {"dexterity": 3, "melee": 0.06},
    "Dilong": {"constitution": 3, "armor": 0.08},
    "Cacus": {"strength": 5, "melee": 0.15},
    "Agloolik": {"wisdom": 2, "magic_defense": 0.08},
    "Izulu": {"dexterity": 3, "magic": 0.06},
    "Hala": {"dexterity": 3, "melee": 0.06},
    "Lamashtu": {"charisma": 3, "magic": 0.10},
    "Seraphim": {"wisdom": 4, "healing": 0.12},
    "Bardi": {"intelligence": 4, "magic": 0.10},
    "Tiamat": {"constitution": 4, "armor": 0.08, "magic_defense": 0.08},
    "Zahhak": {"intelligence": 5, "magic": 0.12},
}
XENID_DEATH_CONDUIT_LOSS = 25
XENID_RAISE_CONDUIT_REFUND = 10


def xenid_caster_effects(character: Any) -> dict[str, float]:
    """Return cumulative caster bonuses produced by all chosen Xenid conduits."""
    if class_name(character) != "Thaumaturgist":
        return {}
    state = ensure_state(character)
    choices = getattr(character, "xenid_choices", {})
    if not isinstance(choices, dict):
        return {}
    mastery = False
    progression = getattr(character, "progression", None)
    if progression is not None:
        mastery = (
            "thaumaturgist.talent.conduit-mastery"
            in getattr(progression, "purchased_node_ids", set())
        )
    mastery_scale = 1.5 if mastery else 1.0
    totals: dict[str, float] = {}
    for name in choices.values():
        conduit = int(state["summon_bonds"].get(name, 0) or 0)
        scale = conduit / 100 * mastery_scale
        for effect, maximum in XENID_CASTER_EFFECTS.get(name, {}).items():
            totals[effect] = totals.get(effect, 0.0) + float(maximum) * scale
    return totals


def xenid_caster_attribute_bonus(character: Any, stat_name: str) -> int:
    """Return the conduit-derived virtual primary-attribute bonus."""
    aliases = {
        "strength": "strength",
        "intel": "intelligence",
        "wisdom": "wisdom",
        "con": "constitution",
        "charisma": "charisma",
        "dex": "dexterity",
    }
    return int(xenid_caster_effects(character).get(aliases[stat_name], 0.0))


def xenid_caster_multiplier(character: Any, effect: str) -> float:
    """Return a conduit-derived multiplier for one combat result."""
    return 1.0 + xenid_caster_effects(character).get(effect, 0.0)


def add_aspect(character: Any, aspect: str) -> str:
    if class_name(character) != "Archdruid":
        return ""
    cap = cap_for(character, "aspect_harmony")
    aspects = combat_state(character).setdefault("aspect_harmony", set())
    if not isinstance(aspects, set):
        aspects = set(aspects)
        combat_state(character)["aspect_harmony"] = aspects
    if aspect in aspects:
        return ""
    if len(aspects) >= cap:
        return "Aspect Harmony is capped.\n"
    aspects.add(aspect)
    return f"{character.name} represents {aspect} Aspect Harmony.\n"


def fourfold_surge(character: Any, target: Any | None) -> str:
    if class_name(character) != "Archdruid":
        return "Fourfold Surge requires Archdruid training.\n"
    aspects = combat_state(character).setdefault("aspect_harmony", set())
    if not isinstance(aspects, set):
        aspects = set(aspects)
    if len(aspects) < 2:
        return "Fourfold Surge requires at least two represented aspects.\n"
    if not _spend_mp(character, 14):
        return "Not enough MP for Fourfold Surge.\n"
    spent = set(aspects)
    combat_state(character)["aspect_harmony"] = set()
    msg = f"{character.name} spends {', '.join(sorted(spent))} Aspect Harmony on Fourfold Surge.\n"
    if target is not None and {"Venom", "Storm"} & spent:
        damage = max(1, int(character.check_mod("magic", enemy=target) * (0.35 + 0.15 * len(spent))))
        target.health.current = max(0, target.health.current - damage)
        msg += f"Fourfold Surge deals {damage} nature damage.\n"
    if "Growth" in spent:
        heal = min(character.health.max - character.health.current, 10 + 5 * len(spent))
        character.health.current += heal
        msg += f"Growth restores {heal} HP.\n"
    if "Stone" in spent:
        character.stat_effects["Defense"].active = True
        character.stat_effects["Defense"].duration = 2
        character.stat_effects["Defense"].extra = max(int(character.stat_effects["Defense"].extra or 0), 5 * len(spent))
        msg += "Stone hardens the caster's defense.\n"
    if _ring_awakened_equipped(character, "Archdruid"):
        preserved = sorted(spent)[0]
        combat_state(character)["aspect_harmony"] = {preserved}
        msg += f"Harmony Bonus preserves {preserved} Aspect Harmony.\n"
    return msg


def totem_resonance(character: Any) -> int:
    effect = getattr(character, "magic_effects", {}).get("Totem")
    if not effect or not effect.active or not isinstance(effect.extra, dict):
        return 0
    return max(0, int(effect.extra.get("resonance", 0) or 0))


def gain_totem_resonance(character: Any, reason: str) -> str:
    effect = getattr(character, "magic_effects", {}).get("Totem")
    if not effect or not effect.active or not isinstance(effect.extra, dict):
        return ""
    cap = cap_for(character, "totem_resonance")
    before = totem_resonance(character)
    effect.extra["resonance"] = min(cap, before + 1)
    if effect.extra["resonance"] == before:
        return "Totem Resonance is capped.\n"
    return f"{character.name}'s Totem gains Resonance from {reason} ({effect.extra['resonance']}/{cap}).\n"


def totem_surge(character: Any, target: Any | None) -> str:
    from .. import nature_totems

    aspect = nature_totems.active_totem_aspect(character)
    stacks = totem_resonance(character)
    if not aspect:
        return "Totem Surge requires an active Totem.\n"
    if stacks <= 0:
        return "Totem Surge requires Totem Resonance.\n"
    spell_name = nature_totems.highest_unlocked_spell_name(character, aspect)
    if not spell_name:
        return "No known spell matches the active Totem.\n"
    if target is None:
        return "Totem Surge needs a target.\n"
    if not _spend_mp(character, 10):
        return "Not enough MP for Totem Surge.\n"
    spell = character.spellbook.get("Spells", {}).get(spell_name)
    if not spell:
        return "No known spell matches the active Totem.\n"
    effect = character.magic_effects["Totem"]
    effect.extra["resonance"] = 0
    sentinel, prior = nature_totems._set_temp_attr(character, "_totem_pulse_potency", nature_totems.TOTEM_PULSE_POTENCY)
    try:
        msg = f"{character.name} spends {stacks} Totem Resonance to force {spell_name}.\n"
        msg += str(spell.cast(character, target=target, special=True))
    finally:
        nature_totems._restore_temp_attr(character, "_totem_pulse_potency", sentinel, prior)
    return msg


def gain_summon_bond_for_active(character: Any, amount: int, reason: str) -> str:
    summon = getattr(character, "active_summon_name", None)
    if not summon:
        return ""
    return gain_summon_bond(character, str(summon), amount, reason)


def record_xenid_death(character: Any, summon_name: str) -> str:
    """Apply one conduit penalty and remember the fallen active Xenid."""
    if class_name(character) != "Thaumaturgist" or summon_name not in SUMMON_NAMES:
        return ""
    combat = combat_state(character)
    if combat.get("fallen_xenid") == summon_name:
        return ""
    state = ensure_state(character)
    before = int(state["summon_bonds"].get(summon_name, 0) or 0)
    after = max(0, before - XENID_DEATH_CONDUIT_LOSS)
    loss = before - after
    state["summon_bonds"][summon_name] = after
    combat["fallen_xenid"] = summon_name
    combat["fallen_xenid_conduit_loss"] = loss
    from ... import companions

    companions.sync_xenid_conduit(character, summon_name, after)
    return (
        f"{summon_name}'s death weakens its conduit by {loss} "
        f"({after}/100).\n"
        if loss
        else f"{summon_name}'s conduit cannot weaken any further.\n"
    )


def raise_fallen_xenid(
    character: Any,
    battle_engine: Any | None,
    *,
    health_fraction: float = 0.25,
) -> tuple[bool, str]:
    """Raise only the Xenid that fell while active in the current combat."""
    if class_name(character) != "Thaumaturgist":
        return False, "Raise Summon requires Thaumaturgist training.\n"
    if battle_engine is None or not bool(getattr(character, "_active_combat", False)):
        return False, "Raise Summon can only be used during combat.\n"
    combat = combat_state(character)
    summon_name = str(combat.get("fallen_xenid", "") or "")
    summons = getattr(character, "summons", {}) or {}
    summon = summons.get(summon_name)
    if summon is None or summon.health.current > 0:
        return False, "No fallen active Xenid can be raised.\n"

    state = ensure_state(character)
    loss = max(0, int(combat.get("fallen_xenid_conduit_loss", 0) or 0))
    refund = min(XENID_RAISE_CONDUIT_REFUND, loss)
    conduit = int(state["summon_bonds"].get(summon_name, 0) or 0)
    conduit = min(100, conduit + refund)
    state["summon_bonds"][summon_name] = conduit
    from ... import companions

    companions.sync_xenid_conduit(character, summon_name, conduit)
    summon.health.current = max(
        1,
        int(summon.health.max * max(0.01, float(health_fraction))),
    )
    battle_engine.summon = summon
    battle_engine.summon_active = True
    character.active_summon_name = summon_name
    combat["fallen_xenid"] = None
    combat["fallen_xenid_conduit_loss"] = 0
    battle_engine.available_actions = battle_engine._available_actions()
    return True, (
        f"{summon_name} returns with {summon.health.current} HP. The rite "
        f"restores {refund} of the lost conduit ({conduit}/100).\n"
    )


def summon_level_span_xp(summon: Any) -> int:
    level = getattr(summon, "level", None)
    try:
        creature_level = max(1, int(getattr(level, "level", 1) or 1))
    except (TypeError, ValueError):
        creature_level = 1
    try:
        pro_level = max(1, int(getattr(level, "pro_level", 1) or 1))
    except (TypeError, ValueError):
        pro_level = 1
    try:
        exp_scale = max(1, int(getattr(summon, "exp_scale", 1000) or 1000))
    except (TypeError, ValueError):
        exp_scale = 1000
    return max(1, pro_level * exp_scale * creature_level)


def summon_bond_gain_for_victory(
    character: Any,
    exp_gain: int,
    *,
    guaranteed: bool = False,
    multiplier: int = 1,
) -> int:
    summon_name = getattr(character, "active_summon_name", None)
    try:
        exp_gain = max(0, int(exp_gain))
    except (TypeError, ValueError):
        exp_gain = 0
    if exp_gain <= 0:
        setattr(character, "_active_summon_bond_note", f"{summon_name or 'Summon'} bond sees no eligible XP.")
        return 0
    global_level = getattr(
        getattr(character, "progression", None),
        "level",
        getattr(getattr(character, "level", None), "level", 1),
    )
    level_span = max(50, int(global_level or 1) * 20)
    ratio = max(0.0, float(exp_gain) / float(level_span))
    chance = min(1.0, ratio)
    if chance < 1.0 and not guaranteed and random.random() >= chance:
        setattr(
            character,
            "_active_summon_bond_note",
            f"{summon_name or 'Summon'} conduit holds steady after a low-XP victory.",
        )
        return 0
    gain = max(1, min(5, int(math.ceil(ratio * 5))))
    try:
        multiplier = max(1, int(multiplier))
    except (TypeError, ValueError):
        multiplier = 1
    setattr(character, "_active_summon_bond_note", "")
    return min(10, gain * multiplier)


def gain_summon_bond(character: Any, summon_name: str, amount: int, reason: str) -> str:
    if class_name(character) != "Thaumaturgist" or summon_name not in SUMMON_NAMES:
        return ""
    state = ensure_state(character)
    before = int(state["summon_bonds"].get(summon_name, 0) or 0)
    after = min(100, before + max(0, int(amount)))
    state["summon_bonds"][summon_name] = after
    from ... import companions

    companions.sync_xenid_conduit(character, summon_name, after)
    if after == before:
        note = str(getattr(character, "_active_summon_bond_note", "") or "")
        return f"Xenid Conduit: {note}\n" if note else ""
    return (
        f"{summon_name}'s conduit grows by {after - before} from {reason} "
        f"({after}/100).\n"
    )


def summon_bond_multiplier(character: Any, summon_name: str) -> float:
    bond = int(ensure_state(character)["summon_bonds"].get(summon_name, 0) or 0)
    return 1.0 + 0.25 * bond / 100


def invoke_summon(character: Any, target: Any | None, summon_name: str) -> str:
    if class_name(character) != "Thaumaturgist":
        return "Only a Thaumaturgist can borrow a Xenid invocation.\n"
    bond = int(ensure_state(character)["summon_bonds"].get(summon_name, 0) or 0)
    if bond < 50:
        return f"Invoke {summon_name} requires conduit 50.\n"
    if target is None:
        return "There is no invocation target.\n"
    if not _spend_mp(character, 12):
        return "Not enough MP for the invocation.\n"
    element = {
        "Patagon": "Earth", "Dilong": "Earth", "Agloolik": "Ice", "Cacus": "Fire",
        "Izulu": "Electric", "Hala": "Wind", "Lamashtu": "Shadow",
        "Seraphim": "Holy", "Bardi": "Shadow", "Kobalos": "Poison",
        "Tiamat": "Water", "Zahhak": "Arcane",
    }.get(summon_name, "Physical")
    damage = max(1, int(character.check_mod("magic", enemy=target) * 0.55))
    target.health.current = max(0, target.health.current - damage)
    return f"{character.name} invokes {summon_name}: {element} pressure deals {damage} damage.\n"


def conduit_command(character: Any) -> str:
    if class_name(character) != "Thaumaturgist":
        return "Conduit Command requires Thaumaturgist training.\n"
    if getattr(character, "familiar", None) is None and not getattr(character, "active_summon_name", None):
        return "Conduit Command requires an active living Xenid.\n"
    if not _spend_mp(character, 10):
        return "Not enough MP for Conduit Command.\n"
    combat_state(character)["conduit_command"] = True
    return f"{character.name} empowers the active Xenid's next action with Conduit Command.\n"


def companion_bond_rank(bond: int) -> str:
    if bond >= 100:
        return "True Bond"
    if bond >= 75:
        return "Packmate"
    if bond >= 50:
        return "Battle-Trained"
    if bond >= 25:
        return "Trusted"
    return "New Bond"


def companion_bond_gain_roll(current_bond: int, amount: int, *, rng: Any = random) -> int:
    """Return inverse-scaled tamed companion bond gain for this opportunity."""
    current = _clamp_int(current_bond, 0, 100)
    base = max(0, int(amount or 0))
    if base <= 0 or current >= 100:
        return 0
    chance = max(0.15, 1.0 - (current / 110.0))
    if rng.random() >= chance:
        return 0
    scale = max(0.25, 1.0 - (current / 125.0))
    return max(1, min(base, int(round(base * scale))))


def gain_companion_bond(character: Any, amount: int, reason: str, *, rng: Any = random, announce: bool = True) -> str:
    if class_name(character) not in {"Ranger", "Beast Master"}:
        return ""
    state = getattr(character, "tamed_companion", None)
    if not isinstance(state, dict) or not state.get("active"):
        return ""
    before = _clamp_int(state.get("bond", 0), 0, 100)
    gain = companion_bond_gain_roll(before, amount, rng=rng)
    if gain <= 0:
        return ""
    after = min(100, before + gain)
    state["bond"] = after
    if after == before:
        return ""
    evolution_msg = ""
    try:
        from .. import ability_mechanics

        enemy_class = state.get("enemy_class")
        species = state.get("species")
        before_evolution = ability_mechanics.tamed_companion_evolution_for_bond(before, enemy_class, species)
        after_evolution = ability_mechanics.tamed_companion_evolution_for_bond(after, enemy_class, species)
        state["evolution"] = after_evolution
        roster = state.get("companions", [])
        active_index = state.get("active_index")
        if isinstance(roster, list) and isinstance(active_index, int) and 0 <= active_index < len(roster):
            roster[active_index]["bond"] = after
            roster[active_index]["evolution"] = after_evolution
            roster[active_index]["active"] = True
        familiar = getattr(character, "familiar", None)
        if familiar is not None and getattr(familiar, "spec", "") == "Tamed":
            familiar.bond = after
            familiar.evolution = after_evolution
        if after_evolution != before_evolution:
            evolution_msg = f"{state.get('name') or 'Companion'} evolves into {after_evolution}.\n"
    except Exception:
        pass
    bond_msg = f"{state.get('name') or 'Companion'} bond increased.\n" if announce else ""
    return f"{bond_msg}{evolution_msg}"


def companion_bond_multiplier(character: Any) -> float:
    state = getattr(character, "tamed_companion", {}) or {}
    bond = _clamp_int(state.get("bond", 0), 0, 100)
    return 1.0 + (0.15 * (bond / 100))


def record_song_turn(character: Any, song: str) -> str:
    if class_name(character) not in {"Bard", "Troubadour"}:
        return ""
    msg = gain_meter(character, "crescendo", 1, f"Song of {song}")
    if class_name(character) == "Troubadour":
        msg += gain_bard_practice(character, song, 1, "performed turn")
    return msg


def clear_crescendo(character: Any, reason: str = "") -> str:
    if class_name(character) not in {"Bard", "Troubadour"}:
        return ""
    state = combat_state(character)
    if int(state.get("crescendo", 0) or 0) <= 0:
        return ""
    state["crescendo"] = 0
    suffix = f" from {reason}" if reason else ""
    return f"Crescendo clears{suffix}.\n"


def gain_bard_practice(character: Any, song: str, amount: int, reason: str) -> str:
    if class_name(character) != "Troubadour" or song not in ADVANCED_SONGS:
        return ""
    entry = ensure_state(character)["bard_repertoire"][song]
    before_xp = int(entry.get("practice_xp", 0) or 0)
    before_known = bool(entry.get("known", False))
    entry["practice_xp"] = min(999, before_xp + max(0, int(amount)))
    msg = ""
    if entry["practice_xp"] > before_xp:
        msg += f"{song} gains {entry['practice_xp'] - before_xp} practice XP from {reason} ({entry['practice_xp']}/18).\n"
    if not before_known and entry["practice_xp"] >= 18 and int(entry.get("clean_finishes", 0) or 0) >= 3:
        entry["known"] = True
        msg += f"{character.name} masters {song} as permanent repertoire.\n"
    return msg


def complete_song(character: Any, song: str) -> str:
    if class_name(character) not in {"Bard", "Troubadour"}:
        return ""
    msg = ""
    if class_name(character) == "Troubadour" and song in ADVANCED_SONGS:
        entry = ensure_state(character)["bard_repertoire"][song]
        entry["clean_finishes"] = min(999, int(entry.get("clean_finishes", 0) or 0) + 1)
        msg += f"{song} records a clean finish ({entry['clean_finishes']}/3).\n"
        msg += gain_bard_practice(character, song, 3, "natural completion")

    state = combat_state(character)
    spent = int(state.get("crescendo", 0) or 0)
    if spent <= 0:
        return msg
    state["crescendo"] = 0
    msg += f"{character.name} spends {spent} Crescendo on a {song} coda.\n"
    if song == "Valor":
        for stat_name in ("Attack", "Magic"):
            effect = character.stat_effects[stat_name]
            effect.active = True
            effect.duration = max(effect.duration, 2)
            effect.extra = max(int(effect.extra or 0), spent * 2)
        msg += "The Valor coda primes the next offensive phrase.\n"
    elif song == "Shelter":
        effect = character.magic_effects["Nature Shield"]
        effect.active = True
        effect.duration = max(effect.duration, 2)
        effect.extra = max(int(effect.extra or 0), spent * 10)
        msg += "The Shelter coda leaves a brief ward.\n"
    elif song == "Renewal":
        hp = min(character.health.max - character.health.current, max(1, spent * 8))
        mp = min(character.mana.max - character.mana.current, max(1, spent * 4))
        character.health.current += hp
        character.mana.current += mp
        if spent >= 3 and character.status_effects["Poison"].active:
            character.status_effects["Poison"].active = False
            msg += "The Renewal coda cleanses poison.\n"
        msg += f"The Renewal coda restores {hp} HP and {mp} MP.\n"
    elif song == "Battle Hymn":
        berserk = character.status_effects["Berserk"]
        berserk.active = True
        berserk.duration = max(berserk.duration, 1 + spent // 2)
        msg += "The Battle Hymn coda keeps one controlled offensive beat.\n"
    elif song == "Ode to the Ramparts":
        effect = character.magic_effects["Nature Shield"]
        effect.active = True
        effect.duration = max(effect.duration, 2)
        effect.extra = max(int(effect.extra or 0), spent * 12)
        msg += "The Ramparts coda hardens into a small barrier.\n"
    elif song == "Chorus Time":
        msg += "The Chorus Time coda lands one final reduced tempo check.\n"
    else:
        msg += "The final refrain lingers as a conservative coda.\n"
    return _preserve_spent_meter(character, "crescendo", "Troubadour", "Encore", msg)


def beast_command(character: Any, command: str) -> str:
    from .. import ability_mechanics

    if class_name(character) != "Beast Master":
        return f"{command} requires Beast Master training.\n"
    if command not in ability_mechanics.BEAST_COMPANION_COMMANDS:
        return f"{command} is not a known companion command.\n"
    if not ability_mechanics.has_living_tamed_companion(character):
        return f"{command} requires a living tamed companion.\n"
    if command not in ability_mechanics.available_beast_companion_commands(character):
        return f"{character.name} has not learned {command}.\n"
    combat_state(character)["pending_companion_command"] = command
    return f"{character.name} orders their companion: {command}.\n"


def favorite_enemy_type(character: Any) -> str | None:
    try:
        from .. import ability_mechanics

        return ability_mechanics.favorite_enemy_type(character)
    except Exception:
        return None


def lycan_control_state(character: Any) -> dict[str, Any]:
    return ensure_state(character)["lycan_control"]


def record_lycan_stress(character: Any, reason: str, *, survived: bool = True) -> str:
    if class_name(character) != "Lycan":
        return ""
    control = lycan_control_state(character)
    control["stress_events"] += 1
    if survived:
        progress = control["rank_progress"]
        progress[reason] = int(progress.get(reason, 0) or 0) + 1
        _maybe_advance_lycan_rank(control)
    return f"Lycan control records {reason} stress at rank {control['rank']}.\n"


def _maybe_advance_lycan_rank(control: dict[str, Any]) -> None:
    rank = control["rank"]
    progress = control["rank_progress"]
    gates = {
        "Feral": ("survive", "Muzzled", 3),
        "Muzzled": ("dismiss", "Restive", 3),
        "Restive": ("resist", "Tethered", 3),
        "Tethered": ("full_moon", "Tame", 3),
    }
    gate = gates.get(rank)
    if gate and int(progress.get(gate[0], 0) or 0) >= gate[2]:
        control["rank"] = gate[1]


def unlock_dragon_essence(character: Any) -> str:
    if class_name(character) != "Lycan":
        return ""
    lycan_control_state(character)["dragon_essence"] = True
    return "Dragon Essence settles into the Werewolf form.\n"


def winged_pounce(character: Any, target: Any | None) -> str:
    if class_name(character) != "Lycan":
        return "Winged Pounce requires Lycan training.\n"
    if not lycan_control_state(character).get("dragon_essence"):
        return "Winged Pounce requires Dragon Essence.\n"
    if target is None:
        return "There is no target for Winged Pounce.\n"
    msg, _hit, _crit = character.weapon_damage(target, dmg_mod=1.35, use_offhand=False)
    character.flying = True
    return f"{character.name} launches a Winged Pounce.\n{msg}"


PRESERVATION_METERS = {
    "Crusader": ("oath_conviction",),
    "Rogue": ("fortune", "misfortune"),
    "Ninja": ("death_marks",),
    "Arcane Trickster": ("stolen_charge",),
    "Templar": ("devotion",),
    "Hierophant": ("devotion",),
    "Archbishop": ("prayer",),
    "Troubadour": ("crescendo",),
}
