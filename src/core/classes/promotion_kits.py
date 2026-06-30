"""Promotion class-kit state and combat helpers.

This module owns the V1 promotion-track mechanics from
``docs/CLASS_KIT_DESIGN_GATES.md``.  The mechanics are intentionally compact:
persistent progression is normalized here, while combat-only meters live on the
character as transient runtime state and are cleared by battle/save lifecycle
hooks.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


SUMMON_NAMES = (
    "Patagon", "Dilong", "Agloolik", "Cacus", "Fuath", "Izulu",
    "Hala", "Grigori", "Bardi", "Kobalos", "Zahhak",
)

ADVANCED_SONGS = (
    "Battle Hymn",
    "Ode to the Ramparts",
    "Symphony of Disfunction",
    "Low-defense-ian Rhapsody",
    "Slow Ride",
    "Bones, Thugs, and Harmony",
    "Scores and Scores Score",
    "Gold Trigger",
    "Chorus Time",
)

LYCAN_RANKS = ("Feral", "Muzzled", "Restive", "Tethered", "Tame")

CASE_MILESTONES = (
    (100, "Closed Case"),
    (75, "Pattern Lock"),
    (50, "Weakness Brief"),
    (25, "Known Tells"),
)


def class_name(character: Any) -> str:
    return str(getattr(getattr(character, "cls", None), "name", "") or "")


def default_state() -> dict[str, Any]:
    return {
        "summon_bonds": {name: 0 for name in SUMMON_NAMES},
        "case_journal": {},
        "bard_repertoire": {
            song: {"known": False, "practice_xp": 0, "clean_finishes": 0}
            for song in ADVANCED_SONGS
        },
        "lycan_control": {
            "rank": "Feral",
            "stress_events": 0,
            "dragon_essence": False,
            "rank_progress": {},
        },
    }


def _clamp_int(value: Any, low: int, high: int) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError):
        parsed = 0
    return max(low, min(high, parsed))


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if not isinstance(state, dict):
        return normalized

    bonds = state.get("summon_bonds", {})
    if isinstance(bonds, dict):
        for name in SUMMON_NAMES:
            normalized["summon_bonds"][name] = _clamp_int(bonds.get(name, 0), 0, 100)

    journal = state.get("case_journal", {})
    if isinstance(journal, dict):
        normalized["case_journal"] = {
            str(enemy_type): _clamp_int(progress, 0, 100)
            for enemy_type, progress in journal.items()
            if str(enemy_type).strip()
        }

    repertoire = state.get("bard_repertoire", {})
    if isinstance(repertoire, dict):
        for song in ADVANCED_SONGS:
            entry = repertoire.get(song, {})
            if not isinstance(entry, dict):
                continue
            normalized["bard_repertoire"][song] = {
                "known": bool(entry.get("known", False)),
                "practice_xp": _clamp_int(entry.get("practice_xp", 0), 0, 999),
                "clean_finishes": _clamp_int(entry.get("clean_finishes", 0), 0, 999),
            }

    control = state.get("lycan_control", {})
    if isinstance(control, dict):
        rank = str(control.get("rank", "Feral") or "Feral")
        if rank not in LYCAN_RANKS:
            rank = "Feral"
        progress = control.get("rank_progress", {})
        normalized["lycan_control"] = {
            "rank": rank,
            "stress_events": _clamp_int(control.get("stress_events", 0), 0, 999),
            "dragon_essence": bool(control.get("dragon_essence", False)),
            "rank_progress": {
                str(key): _clamp_int(value, 0, 999)
                for key, value in progress.items()
            } if isinstance(progress, dict) else {},
        }

    return normalized


def ensure_state(character: Any) -> dict[str, Any]:
    state = normalize_state(getattr(character, "promotion_kit_state", None))
    setattr(character, "promotion_kit_state", state)
    return state


def copy_state(character: Any) -> dict[str, Any]:
    return deepcopy(ensure_state(character))


def combat_state(character: Any) -> dict[str, Any]:
    defaults = {
        "foresight_threads": 0,
        "threaded_cast_pending": False,
        "rewind_thread_granted": False,
        "blade_charge": None,
        "arcane_tempo": 0,
        "bloodied_momentum": 0,
        "momentum_preserved": False,
        "oath_conviction": 0,
        "aerial_tempo": 0,
        "hold_the_line": 0,
        "fortune": 0,
        "misfortune": 0,
        "cheat_death_used": False,
        "revelation": {},
        "death_marks": {},
        "stolen_charge": 0,
        "devotion": 0,
        "prayer": 0,
        "ki": 0,
        "crescendo": 0,
        "jinx_turns": 0,
        "aspect_harmony": set(),
        "pending_companion_command": None,
        "conduit_command": False,
        "ring_preserved": set(),
    }
    state = getattr(character, "_promotion_kit_combat", None)
    if not isinstance(state, dict):
        state = {}
    for key, value in defaults.items():
        if key not in state:
            state[key] = deepcopy(value)
        setattr(character, "_promotion_kit_combat", state)
    return state


def clear_combat_state(character: Any) -> None:
    setattr(character, "_promotion_kit_combat", {})
    combat_state(character)
    _reset_shadowcaster_combat_fields(character)


def tick_combat_state(character: Any) -> str:
    state = combat_state(character)
    msg = ""
    jinx = int(state.get("jinx_turns", 0) or 0)
    if jinx > 0:
        state["jinx_turns"] = max(0, jinx - 1)
        if state["jinx_turns"] <= 0:
            msg += f"{character.name}'s Jinx fades.\n"
    return msg


def start_combat(character: Any) -> str:
    clear_combat_state(character)
    return ""


def end_combat(character: Any, *, victory: bool = False, enemy: Any | None = None) -> str:
    msg = ""
    if victory and enemy is not None:
        msg += gain_case_progress(character, getattr(enemy, "enemy_typ", None), 4, "victory")
        msg += gain_companion_bond(character, 4, reason="victory")
        if getattr(enemy, "enemy_typ", None) == favorite_enemy_type(character):
            msg += gain_companion_bond(character, 2, reason="Favored Enemy hunt")
        msg += gain_summon_bond_for_active(character, 5, "victory")
    msg += convert_shadow_backlash(character, fraction=0.05, reason="combat end")
    clear_combat_state(character)
    return msg


def _ring_awakened_equipped(character: Any, class_value: str | None = None) -> bool:
    try:
        from . import class_rings

        return bool(
            class_rings.is_awakened(character, class_value or class_name(character))
            and class_rings.has_equipped_class_ring(character)
        )
    except Exception:
        return False


def _has_skill(character: Any, skill_name: str) -> bool:
    return skill_name in getattr(character, "spellbook", {}).get("Skills", {})


def _is_weapon_hit(metadata: dict[str, Any] | None) -> bool:
    if not isinstance(metadata, dict):
        return False
    return metadata.get("attack_source") in {"weapon", "natural_weapon", "special_attack"}


def _message(character: Any, line: str) -> None:
    if not line:
        return
    messages = getattr(character, "_promotion_kit_messages", None)
    if not isinstance(messages, list):
        messages = []
        setattr(character, "_promotion_kit_messages", messages)
    messages.append(line)


def pop_messages(character: Any) -> str:
    messages = getattr(character, "_promotion_kit_messages", [])
    if not messages:
        return ""
    setattr(character, "_promotion_kit_messages", [])
    return "".join(messages)


def cap_for(character: Any, key: str) -> int:
    cls = class_name(character)
    if key == "foresight_threads":
        return 3 if cls == "Astromancer" else 0
    if key == "bloodied_momentum":
        scars = _class_ring_data(character, "Berserker").get("battle_scars", 0)
        return 5 if scars >= 20 else 4 if scars >= 10 else 3
    if key == "oath_conviction":
        return 3 if cls == "Crusader" else 2 if cls == "Paladin" else 0
    if key == "aerial_tempo":
        return 3 if cls == "Dragoon" else 2 if cls == "Lancer" else 0
    if key in {"fortune", "misfortune"}:
        return 3 if cls == "Rogue" else 2 if cls == "Thief" else 0
    if key == "revelation":
        return 3 if cls == "Seeker" else 2 if cls == "Inquisitor" else 0
    if key == "death_marks":
        return 3 if cls == "Ninja" else 1 if cls == "Assassin" else 0
    if key == "stolen_charge":
        return 3 if cls == "Arcane Trickster" else 2 if cls == "Spell Stealer" else 0
    if key == "devotion":
        return 5 if cls == "Templar" else 3 if cls == "Cleric" else 0
    if key == "prayer":
        return 7 if cls == "Archbishop" else 4 if cls == "Priest" else 0
    if key == "ki":
        return 5 if cls == "Master Monk" else 3 if cls == "Monk" else 0
    if key == "crescendo":
        return 3 if cls in {"Bard", "Troubadour"} else 0
    if key == "aspect_harmony":
        return 5 if _ring_awakened_equipped(character, "Archdruid") else 4
    if key == "totem_resonance":
        return 4 if _ring_awakened_equipped(character, "Soulcatcher") else 3
    return 0


def _class_ring_data(character: Any, class_value: str) -> dict[str, Any]:
    try:
        from . import class_rings

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


def spend_meter(character: Any, key: str) -> int:
    state = combat_state(character)
    value = int(state.get(key, 0) or 0)
    state[key] = 0
    return max(0, value)


def record_damage_event(
    actor: Any,
    target: Any,
    amount: int,
    damage_type: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> None:
    if not amount or amount <= 0:
        return
    cls = class_name(actor)
    damage_type = str(damage_type or "Physical")
    weapon_hit = _is_weapon_hit(metadata)
    if isinstance(metadata, dict):
        critical_hit = bool(metadata.get("is_critical"))
        if not critical_hit:
            try:
                critical_hit = float(metadata.get("crit", 1) or 1) > 1
            except (TypeError, ValueError):
                critical_hit = False
    else:
        critical_hit = False

    if cls == "Astromancer" and not weapon_hit:
        _message(actor, gain_meter(actor, "foresight_threads", 1, "successful spell thread"))

    if cls in {"Spellblade", "Knight Enchanter"} and not weapon_hit and damage_type in {
        "Fire", "Ice", "Electric", "Water", "Earth", "Wind", "Non-elemental", "Arcane",
    }:
        combat_state(actor)["blade_charge"] = damage_type
        _message(actor, f"{actor.name}'s blade stores a {damage_type} charge.\n")

    if cls == "Berserker" and weapon_hit and _hp_ratio(actor) < 0.50:
        bonus = 2 if _hp_ratio(actor) < 0.25 else 1
        _message(actor, gain_meter(actor, "bloodied_momentum", bonus, "bloodied weapon hit"))

    if cls in {"Lancer", "Dragoon"} and getattr(actor, "_jump_landed_cleanly", False):
        _message(actor, gain_meter(actor, "aerial_tempo", 1, "clean Jump landing"))
        actor._jump_landed_cleanly = False

    if cls in {"Thief", "Rogue"} and critical_hit:
        _message(actor, gain_meter(actor, "fortune", 1, "critical risky hit"))

    if cls in {"Cleric", "Templar"} and (damage_type == "Holy" or weapon_hit):
        _message(actor, gain_meter(actor, "devotion", 1, "holy or shield pressure"))

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
        _consume_weapon_payoffs(actor, target, amount, damage_type)


def record_damage_taken(defender: Any, amount: int, damage_type: str) -> None:
    if not amount or amount <= 0:
        return
    cls = class_name(defender)
    if cls == "Berserker" and _hp_ratio(defender) < 0.50:
        bonus = 2 if _hp_ratio(defender) < 0.25 else 1
        _message(defender, gain_meter(defender, "bloodied_momentum", bonus, "bloodied incoming damage"))
    if cls in {"Sentinel", "Stalwart Defender"}:
        build_resolve(defender, max(1, amount // 5), "mitigated pressure")
    if cls == "Archdruid" and damage_type == "Physical":
        _message(defender, add_aspect(defender, "Stone"))
    if cls == "Rogue" and int(getattr(getattr(defender, "health", None), "current", 1) or 0) <= 0:
        _message(defender, cheat_death(defender))


def record_healing_done(actor: Any, amount: int) -> str:
    if not amount or amount <= 0:
        return ""
    cls = class_name(actor)
    msg = ""
    if cls in {"Cleric", "Templar"}:
        msg += gain_meter(actor, "devotion", 1, "meaningful healing")
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

    charge = state.get("blade_charge")
    if cls in {"Spellblade", "Knight Enchanter"} and charge:
        extra += max(1, int(amount * 0.12))
        lines.append(f"{actor.name}'s {charge} blade charge follows through for {extra} magic damage.\n")
        state["blade_charge"] = None
        if cls == "Knight Enchanter" and _ring_awakened_equipped(actor, "Knight Enchanter"):
            tempo = min(3, int(state.get("arcane_tempo", 0) or 0) + 1)
            state["arcane_tempo"] = tempo
            lines.append(f"Arcane Tempo rises to {tempo}/3.\n")
            if tempo >= 3:
                burst = max(1, int(amount * 0.20))
                extra += burst
                state["arcane_tempo"] = 0
                lines.append(f"Arcane Tempo bursts for {burst} arcane damage.\n")

    aerial = int(state.get("aerial_tempo", 0) or 0)
    if cls in {"Lancer", "Dragoon"} and aerial:
        burst = max(1, int(amount * (0.06 * aerial)))
        extra += burst
        state["aerial_tempo"] = 0
        lines.append(f"Aerial Tempo drives a follow-through for {burst} damage.\n")
        if cls == "Dragoon" and _ring_awakened_equipped(actor, "Dragoon"):
            shield = _class_ring_data(actor, "Dragoon")
            shield["meteor_guard_shield"] = max(int(shield.get("meteor_guard_shield", 0) or 0), burst)
            shield["meteor_guard_turns"] = 2
            lines.append("Aerial Supremacy forms a landing shield.\n")

    stolen = int(state.get("stolen_charge", 0) or 0)
    if cls in {"Spell Stealer", "Arcane Trickster"} and stolen:
        burst = max(1, int(amount * (0.08 * stolen)))
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


def build_resolve(character: Any, amount: int, reason: str = "") -> str:
    if class_name(character) not in {"Sentinel", "Stalwart Defender"}:
        return ""
    cap = 100 if class_name(character) == "Stalwart Defender" else 50
    data = _class_ring_data(character, "Stalwart Defender")
    before = int(data.get("guard_meter", 0) or 0)
    data["guard_meter"] = min(cap, before + max(0, int(amount)))
    if data["guard_meter"] == before:
        return "Resolve is capped.\n"
    return f"{character.name} gains {data['guard_meter'] - before} Resolve from {reason} ({data['guard_meter']}/{cap}).\n"


def hold_the_line(character: Any) -> str:
    if class_name(character) not in {"Sentinel", "Stalwart Defender"}:
        return "Hold the Line belongs to the shield defender track.\n"
    if getattr(character.equipment.get("OffHand"), "subtyp", None) != "Shield":
        return "Hold the Line requires a shield.\n"
    combat_state(character)["hold_the_line"] = 3
    character.enter_defensive_stance(duration=3)
    return f"{character.name} holds the line behind their shield.\n"


def bulwark(character: Any) -> str:
    if class_name(character) != "Stalwart Defender":
        return "Bulwark requires Stalwart Defender training.\n"
    data = _class_ring_data(character, "Stalwart Defender")
    resolve = int(data.get("guard_meter", 0) or 0)
    if resolve < 25:
        return "Bulwark requires at least 25 Resolve.\n"
    spent = min(resolve, 50)
    data["guard_meter"] = resolve - spent
    effect = character.magic_effects["Nature Shield"]
    effect.active = True
    effect.duration = 2
    effect.extra = max(int(effect.extra or 0), spent)
    return f"{character.name} spends {spent} Resolve on Bulwark.\n"


def shield_riposte(character: Any, target: Any | None) -> str:
    if class_name(character) != "Stalwart Defender":
        return "Shield Riposte requires Stalwart Defender training.\n"
    if target is None:
        return "There is no target to riposte.\n"
    data = _class_ring_data(character, "Stalwart Defender")
    if int(data.get("guard_meter", 0) or 0) < 20:
        return "Shield Riposte requires 20 Resolve.\n"
    data["guard_meter"] -= 20
    msg, _hit, _crit = character.weapon_damage(target, dmg_mod=0.75, use_offhand=False)
    return f"{character.name} spends 20 Resolve on Shield Riposte.\n{msg}"


def conviction_action(character: Any, action_name: str, *, clean: bool = False) -> str:
    if class_name(character) not in {"Paladin", "Crusader"}:
        return ""
    state = combat_state(character)
    spent = spend_meter(character, "oath_conviction")
    msg = ""
    if spent:
        msg += f"Oath Conviction empowers {action_name} with {spent} stack(s).\n"
    msg += gain_meter(character, "oath_conviction", 1, action_name)
    if clean:
        msg += gain_meter(character, "oath_conviction", 1, "clean vow outcome")
        marker = "Crusader:oath_conviction"
        if spent and _ring_awakened_equipped(character, "Crusader") and marker not in state["ring_preserved"]:
            state["ring_preserved"].add(marker)
            state["oath_conviction"] = max(1, int(state.get("oath_conviction", 0) or 0))
            msg += "Vow Affirmation preserves 1 Oath Conviction.\n"
    return msg


def add_fortune(character: Any, success: bool, reason: str) -> str:
    if class_name(character) not in {"Thief", "Rogue"}:
        return ""
    return gain_meter(character, "fortune" if success else "misfortune", 1, reason)


def _preserve_spent_meter(character: Any, key: str, ring_class: str, label: str, msg: str) -> str:
    lines: list[str] = []
    _maybe_preserve(character, key, ring_class, label, lines)
    return msg + "".join(lines)


def consume_fortune_for_risky_action(character: Any, reason: str) -> tuple[bool, str]:
    if class_name(character) not in {"Thief", "Rogue"}:
        return False, ""
    state = combat_state(character)
    spent = int(state.get("fortune", 0) or 0)
    if spent <= 0:
        return False, ""
    state["fortune"] = 0
    force_hit = False
    try:
        import random

        force_hit = random.random() < min(0.25, 0.05 * spent)
    except Exception:
        force_hit = False
    msg = f"{character.name} spends {spent} Fortune smoothing {reason}."
    msg += " The risky line opens cleanly.\n" if force_hit else "\n"
    return force_hit, _preserve_spent_meter(character, "fortune", "Rogue", "Loaded Dice", msg)


def resolve_misfortune_payoff(character: Any, target: Any | None, base_damage: int, reason: str) -> str:
    if class_name(character) not in {"Thief", "Rogue"}:
        return ""
    state = combat_state(character)
    spent = int(state.get("misfortune", 0) or 0)
    if spent <= 0:
        return ""
    state["misfortune"] = 0
    bonus = max(1, int(max(1, base_damage) * (0.08 * spent)))
    if target is not None and base_damage > 0:
        target.health.current = max(0, target.health.current - bonus)
        msg = f"{character.name} cashes in {spent} Misfortune through {reason} for {bonus} extra pressure.\n"
    else:
        msg = f"{character.name} cashes in {spent} Misfortune through {reason} for a stronger payoff.\n"
    return _preserve_spent_meter(character, "misfortune", "Rogue", "Loaded Dice", msg)


def cheat_death(character: Any) -> str:
    if class_name(character) != "Rogue":
        return ""
    state = combat_state(character)
    if state.get("cheat_death_used"):
        return ""
    state["cheat_death_used"] = True
    misfortune = int(state.get("misfortune", 0) or 0)
    chance = min(0.65, 0.25 + (0.10 * misfortune))
    try:
        import random

        success = random.random() < chance
    except Exception:
        success = False
    if not success:
        return f"Cheat Death fails at {int(chance * 100)}% odds.\n"
    state["misfortune"] = 0
    state["jinx_turns"] = 2
    character.health.current = 1
    msg = f"Cheat Death spends {misfortune} Misfortune and leaves {character.name} standing at 1 HP.\n"
    return _preserve_spent_meter(character, "misfortune", "Rogue", "Loaded Dice", msg)


def apply_death_mark(character: Any, target: Any, reason: str = "setup") -> str:
    cap = cap_for(character, "death_marks")
    if cap <= 0 or target is None:
        return ""
    state = combat_state(character)
    marks = state.setdefault("death_marks", {})
    before = _target_stacks(marks, target)
    after = min(cap, before + 1)
    _set_target_stacks(marks, target, after)
    if after == before:
        return f"Death Mark is capped at {cap}.\n"
    return f"{target.name} gains a Death Mark from {reason} ({after}/{cap}).\n"


def add_revelation(character: Any, target: Any, amount: int = 1, reason: str = "insight") -> str:
    cap = cap_for(character, "revelation")
    if cap <= 0 or target is None:
        return ""
    state = combat_state(character)
    mapping = state.setdefault("revelation", {})
    before = _target_stacks(mapping, target)
    after = min(cap, before + amount)
    _set_target_stacks(mapping, target, after)
    if after == before:
        return f"Revelation is capped at {cap}.\n"
    return f"{character.name} gains Revelation on {target.name} from {reason} ({after}/{cap}).\n"


def gain_case_progress(character: Any, enemy_type: Any, amount: int, reason: str) -> str:
    if class_name(character) not in {"Inquisitor", "Seeker"} or not enemy_type:
        return ""
    state = ensure_state(character)
    key = str(enemy_type)
    before = int(state["case_journal"].get(key, 0) or 0)
    after = min(100, before + max(0, int(amount)))
    state["case_journal"][key] = after
    if after == before:
        return ""
    milestone = case_rank(after)
    suffix = f" ({milestone})" if milestone else ""
    return f"Case Journal records {key} +{after - before} from {reason}: {after}/100{suffix}.\n"


def case_rank(progress: int) -> str:
    for threshold, name in CASE_MILESTONES:
        if int(progress or 0) >= threshold:
            return name
    return "Unstudied"


def wayfinding_discount(character: Any) -> float:
    if class_name(character) != "Seeker":
        return 0.0
    best = max((int(v or 0) for v in ensure_state(character)["case_journal"].values()), default=0)
    discount = 0.10 if best >= 100 else 0.05 if best >= 50 else 0.0
    if _ring_awakened_equipped(character, "Seeker"):
        discount += 0.05
    return min(0.20, discount)


def gain_stolen_charge(character: Any, reason: str) -> str:
    return gain_meter(character, "stolen_charge", 1, reason)


def sanctuary_ward(character: Any) -> str:
    if class_name(character) not in {"Cleric", "Templar"}:
        return "Sanctuary Ward belongs to the Cleric and Templar track.\n"
    stacks = int(combat_state(character).get("devotion", 0) or 0)
    if stacks <= 0:
        return "Sanctuary Ward requires Devotion.\n"
    if not _spend_mp(character, 8):
        return "Not enough MP for Sanctuary Ward.\n"
    spent = spend_meter(character, "devotion")
    effect = character.magic_effects["Nature Shield"]
    effect.active = True
    effect.duration = 2
    effect.extra = max(10, spent * 12)
    msg = f"{character.name} spends {spent} Devotion on Sanctuary Ward.\n"
    if spent >= 3 and character.status_effects["Poison"].active:
        character.status_effects["Poison"].active = False
        msg += "Sanctuary Ward cleanses poison.\n"
    return _preserve_spent_meter(character, "devotion", "Templar", "Ordered Blessings", msg)


def relic_aegis(character: Any) -> str:
    if class_name(character) != "Templar":
        return "Relic Aegis requires Templar training.\n"
    if getattr(character.equipment.get("OffHand"), "subtyp", None) != "Shield":
        return "Relic Aegis requires a shield.\n"
    stacks = int(combat_state(character).get("devotion", 0) or 0)
    if stacks < 2:
        return "Relic Aegis requires at least 2 Devotion.\n"
    if not _spend_mp(character, 12):
        return "Not enough MP for Relic Aegis.\n"
    spent = spend_meter(character, "devotion")
    effect = character.magic_effects["Nature Shield"]
    effect.active = True
    effect.duration = 3
    effect.extra = max(20, spent * 18)
    msg = f"{character.name} spends {spent} Devotion on Relic Aegis.\n"
    return _preserve_spent_meter(character, "devotion", "Templar", "Ordered Blessings", msg)


def supplication(character: Any, target: Any | None = None) -> str:
    if class_name(character) not in {"Priest", "Archbishop"}:
        return "Supplication belongs to the Priest and Archbishop track.\n"
    stacks = int(combat_state(character).get("prayer", 0) or 0)
    if stacks <= 0:
        return "Supplication requires Prayer.\n"
    if not _spend_mp(character, 10):
        return "Not enough MP for Supplication.\n"
    target = target or character
    spent = spend_meter(character, "prayer")
    heal = min(target.health.max - target.health.current, max(1, 12 * spent + character.stats.wisdom // 2))
    target.health.current += heal
    msg = f"{character.name} spends {spent} Prayer; Supplication restores {heal} HP.\n"
    if target.status_effects["Poison"].active and spent >= 2:
        target.status_effects["Poison"].active = False
        msg += "Supplication cleanses poison.\n"
    return _preserve_spent_meter(character, "prayer", "Archbishop", "Divine Intervention", msg)


def great_benediction(character: Any) -> str:
    if class_name(character) != "Archbishop":
        return "Great Benediction requires Archbishop training.\n"
    stacks = int(combat_state(character).get("prayer", 0) or 0)
    if stacks < 3:
        return "Great Benediction requires at least 3 Prayer.\n"
    if not _spend_mp(character, 18):
        return "Not enough MP for Great Benediction.\n"
    spent = spend_meter(character, "prayer")
    character.stat_effects["Magic Defense"].active = True
    character.stat_effects["Magic Defense"].duration = 4
    character.stat_effects["Magic Defense"].extra = max(int(character.stat_effects["Magic Defense"].extra or 0), spent * 4)
    character.magic_effects["Regen"].active = True
    character.magic_effects["Regen"].duration = 4
    character.magic_effects["Regen"].extra = max(int(character.magic_effects["Regen"].extra or 0), spent * 5)
    msg = f"{character.name} spends {spent} Prayer on Great Benediction.\n"
    return _preserve_spent_meter(character, "prayer", "Archbishop", "Divine Intervention", msg)


def great_gospel_prayer(character: Any) -> str:
    if class_name(character) != "Archbishop":
        return ""
    cap = cap_for(character, "prayer")
    state = combat_state(character)
    state["prayer"] = max(int(state.get("prayer", 0) or 0), cap // 2)
    return f"Great Gospel raises Prayer to {state['prayer']}/{cap}.\n"


def dim_mak(character: Any, target: Any | None) -> str:
    if class_name(character) != "Master Monk":
        return "Dim Mak requires Master Monk training.\n"
    cap = cap_for(character, "ki")
    if int(combat_state(character).get("ki", 0) or 0) < cap:
        return "Dim Mak requires full Ki.\n"
    if target is None:
        return "There is no target for Dim Mak.\n"
    if not _spend_mp(character, 18):
        return "Not enough MP for Dim Mak.\n"
    spent = spend_meter(character, "ki")
    weapon = character.equipment.get("Weapon")
    subtyp = getattr(weapon, "subtyp", None)
    weapon_name = getattr(weapon, "name", "")
    penalty = 1.0
    drop_msg = ""
    if subtyp == "Fist" or subtyp == "None":
        penalty = 1.0
    elif subtyp == "Staff" and weapon_name == "Ruyi Jingu Bang":
        penalty = 1.0
    elif subtyp == "Staff":
        penalty = 0.80
        drop_msg = "The ordinary staff cannot hold the finisher and is disarmed.\n"
        character.equipment["Weapon"] = type("NoWeapon", (), {"name": "None", "subtyp": "None", "typ": "Weapon", "damage": 0, "crit": 0, "ignore": False, "element": None, "ultimate": False})()
    else:
        penalty = 0.90
    damage = max(1, int((character.check_mod("weapon", enemy=target) + character.stats.wisdom) * (1.5 + spent * 0.12) * penalty))
    target.health.current = max(0, target.health.current - damage)
    if not target.has_status_protection("Stun"):
        target.status_effects["Stun"].active = True
        target.status_effects["Stun"].duration = max(target.status_effects["Stun"].duration, 2)
    msg = f"{character.name} spends {spent} Ki on Dim Mak for {damage} damage.\n{drop_msg}"
    if _ring_awakened_equipped(character, "Master Monk"):
        combat_state(character)["ki"] = 1
        msg += "Martial Master refunds 1 Ki after the finisher.\n"
    return msg


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
    from . import nature_totems

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


def gain_summon_bond(character: Any, summon_name: str, amount: int, reason: str) -> str:
    if class_name(character) not in {"Summoner", "Grand Summoner"} or summon_name not in SUMMON_NAMES:
        return ""
    state = ensure_state(character)
    before = int(state["summon_bonds"].get(summon_name, 0) or 0)
    after = min(100, before + max(0, int(amount)))
    state["summon_bonds"][summon_name] = after
    if after == before:
        return ""
    return f"{summon_name} bond grows by {after - before} from {reason} ({after}/100).\n"


def summon_bond_multiplier(character: Any, summon_name: str) -> float:
    bond = int(ensure_state(character)["summon_bonds"].get(summon_name, 0) or 0)
    if bond >= 75:
        return 1.10
    if bond >= 25:
        return 1.05
    return 1.0


def invoke_summon(character: Any, target: Any | None, summon_name: str) -> str:
    if class_name(character) not in {"Summoner", "Grand Summoner"}:
        return "Only a Summoner can borrow an invocation.\n"
    bond = int(ensure_state(character)["summon_bonds"].get(summon_name, 0) or 0)
    if bond < 50:
        return f"Invoke {summon_name} requires bond 50.\n"
    if target is None:
        return "There is no invocation target.\n"
    if not _spend_mp(character, 12):
        return "Not enough MP for the invocation.\n"
    element = {
        "Patagon": "Earth", "Dilong": "Earth", "Agloolik": "Ice", "Cacus": "Fire",
        "Fuath": "Water", "Izulu": "Electric", "Hala": "Wind", "Grigori": "Holy",
        "Bardi": "Shadow", "Kobalos": "Poison", "Zahhak": "Arcane",
    }.get(summon_name, "Physical")
    damage = max(1, int(character.check_mod("magic", enemy=target) * 0.55))
    target.health.current = max(0, target.health.current - damage)
    return f"{character.name} invokes {summon_name}: {element} pressure deals {damage} damage.\n"


def conduit_command(character: Any) -> str:
    if class_name(character) != "Grand Summoner":
        return "Conduit Command requires Grand Summoner training.\n"
    if getattr(character, "familiar", None) is None and not getattr(character, "active_summon_name", None):
        return "Conduit Command requires an active living summon.\n"
    if not _spend_mp(character, 10):
        return "Not enough MP for Conduit Command.\n"
    combat_state(character)["conduit_command"] = True
    return f"{character.name} empowers the active summon's next action with Conduit Command.\n"


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


def gain_companion_bond(character: Any, amount: int, reason: str) -> str:
    if class_name(character) not in {"Ranger", "Beast Master"}:
        return ""
    state = getattr(character, "tamed_companion", None)
    if not isinstance(state, dict) or not state.get("active"):
        return ""
    before = _clamp_int(state.get("bond", 0), 0, 100)
    after = min(100, before + max(0, int(amount)))
    state["bond"] = after
    if after == before:
        return ""
    return f"{state.get('name') or 'Companion'} bond grows by {after - before} from {reason} ({after}/100, {companion_bond_rank(after)}).\n"


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
    if class_name(character) != "Beast Master":
        return f"{command} requires Beast Master training.\n"
    if getattr(character, "familiar", None) is None:
        return f"{command} requires a living tamed companion.\n"
    combat_state(character)["pending_companion_command"] = command
    return f"{character.name} orders their companion: {command}.\n"


def favorite_enemy_type(character: Any) -> str | None:
    try:
        from . import ability_mechanics

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
    "Archbishop": ("prayer",),
    "Troubadour": ("crescendo",),
}


def _ring_readiness_line(character: Any, cls: str) -> str | None:
    try:
        from . import class_rings

        if not class_rings.is_legacy_class(cls):
            return None
        if class_rings.is_awakened(character, cls):
            if class_rings.has_equipped_class_ring(character):
                return f"{'Ring Ready:':13} {class_rings.ring_mod(character)}"
            return f"{'Ring Ready:':13} Awakened, unequipped"
        if class_rings.has_visible_class_ring(character):
            return f"{'Ring Ready:':13} Dormant"
    except Exception:
        return None
    return None


def _preservation_line(character: Any, cls: str) -> str | None:
    keys = PRESERVATION_METERS.get(cls)
    if not keys or not _ring_awakened_equipped(character, cls):
        return None
    preserved = combat_state(character).setdefault("ring_preserved", set())
    used = all(f"{cls}:{key}" in preserved for key in keys)
    return f"{'Ring Preserve:':13} {'Used' if used else 'Ready'}"


def _totem_status_line(character: Any) -> str | None:
    effect = getattr(character, "magic_effects", {}).get("Totem")
    if not effect or not effect.active or not isinstance(effect.extra, dict):
        return None
    aspect = effect.extra.get("aspect") or "Unknown"
    resonance = totem_resonance(character)
    return f"{'Totem:':13} {aspect} {resonance}/{cap_for(character, 'totem_resonance')}"


def status_summary(character: Any) -> list[str]:
    cls = class_name(character)
    state = combat_state(character)
    lines: list[str] = []
    if cls == "Demonologist":
        try:
            from . import demonologist

            contracts = demonologist.ensure_state(character)
            patron = contracts.get("active_patron") or "None"
            mood = contracts.get("patron_moods", {}).get(patron, 0) if patron != "None" else 0
            echo = contracts.get("imprisoned_familiar") or {}
            lines.append(f"{'Corruption:':13} {int(contracts.get('corruption', 0) or 0)}/100")
            lines.append(f"{'Patron:':13} {patron} ({int(mood)})")
            if echo.get("name") or echo.get("spec"):
                lines.append(f"{'Echo:':13} {echo.get('name') or echo.get('spec')}")
            if contracts.get("ring_awakened"):
                ready = "Equipped" if demonologist.has_equipped_class_ring(character) else "Awakened"
                lines.append(f"{'Ring Ready:':13} {ready}")
        except Exception:
            pass
    if cls == "Astromancer":
        lines.append(f"{'Threads:':13} {int(state.get('foresight_threads', 0) or 0)}/3")
        if state.get("threaded_cast_pending"):
            lines.append(f"{'Threaded:':13} Pending")
    if cls == "Shadowcaster":
        data = _class_ring_data(character, "Shadowcaster")
        lines.append(f"{'Backlash:':13} {int(data.get('backlash', 0) or 0)}")
        eclipse = int(data.get("eclipse_turns", 0) or 0)
        if eclipse:
            lines.append(f"{'Eclipse:':13} {eclipse} turn(s)")
    if cls in {"Spellblade", "Knight Enchanter"}:
        lines.append(f"{'Blade Charge:':13} {state.get('blade_charge') or 'None'}")
        if cls == "Knight Enchanter":
            lines.append(f"{'Tempo:':13} {int(state.get('arcane_tempo', 0) or 0)}/3")
    if cls == "Berserker":
        lines.append(f"{'Momentum:':13} {int(state.get('bloodied_momentum', 0) or 0)}/{cap_for(character, 'bloodied_momentum')}")
    if cls in {"Paladin", "Crusader"}:
        lines.append(f"{'Conviction:':13} {int(state.get('oath_conviction', 0) or 0)}/{cap_for(character, 'oath_conviction')}")
    if cls in {"Lancer", "Dragoon"}:
        lines.append(f"{'Aerial Tempo:':13} {int(state.get('aerial_tempo', 0) or 0)}/{cap_for(character, 'aerial_tempo')}")
    if cls == "Sentinel":
        cap = 50
        lines.append(f"{'Resolve:':13} {int(_class_ring_data(character, 'Stalwart Defender').get('guard_meter', 0) or 0)}/{cap}")
    if cls in {"Sentinel", "Stalwart Defender"} and int(state.get("hold_the_line", 0) or 0) > 0:
        lines.append(f"{'Guard Stance:':13} Hold ({int(state.get('hold_the_line', 0) or 0)})")
    if cls in {"Thief", "Rogue"}:
        lines.append(f"{'Fortune:':13} {int(state.get('fortune', 0) or 0)}/{cap_for(character, 'fortune')}")
        lines.append(f"{'Misfortune:':13} {int(state.get('misfortune', 0) or 0)}/{cap_for(character, 'misfortune')}")
        if int(state.get("jinx_turns", 0) or 0) > 0:
            lines.append(f"{'Jinx:':13} {int(state.get('jinx_turns', 0) or 0)} turn(s)")
    if cls in {"Inquisitor", "Seeker"}:
        best = max(ensure_state(character)["case_journal"].values(), default=0)
        lines.append(f"{'Case:':13} {best}/100 {case_rank(best)}")
        revelation = state.get("revelation", {})
        current = max((int(value or 0) for value in revelation.values()), default=0) if isinstance(revelation, dict) else 0
        lines.append(f"{'Revelation:':13} {current}/{cap_for(character, 'revelation')}")
    if cls in {"Assassin", "Ninja"}:
        marks = state.get("death_marks", {})
        current = max((int(value or 0) for value in marks.values()), default=0) if isinstance(marks, dict) else 0
        lines.append(f"{'Death Mark:':13} {current}/{cap_for(character, 'death_marks')}")
    if cls in {"Spell Stealer", "Arcane Trickster"}:
        lines.append(f"{'Stolen Charge:':13} {int(state.get('stolen_charge', 0) or 0)}/{cap_for(character, 'stolen_charge')}")
    if cls in {"Cleric", "Templar"}:
        lines.append(f"{'Devotion:':13} {int(state.get('devotion', 0) or 0)}/{cap_for(character, 'devotion')}")
    if cls in {"Priest", "Archbishop"}:
        lines.append(f"{'Prayer:':13} {int(state.get('prayer', 0) or 0)}/{cap_for(character, 'prayer')}")
    if cls in {"Monk", "Master Monk"}:
        lines.append(f"{'Ki:':13} {int(state.get('ki', 0) or 0)}/{cap_for(character, 'ki')}")
    if cls in {"Bard", "Troubadour"}:
        lines.append(f"{'Crescendo:':13} {int(state.get('crescendo', 0) or 0)}/3")
        if cls == "Troubadour":
            repertoire = ensure_state(character)["bard_repertoire"]
            mastered = sum(1 for entry in repertoire.values() if entry.get("known"))
            lines.append(f"{'Repertoire:':13} {mastered}/{len(repertoire)} mastered")
    if cls == "Lycan":
        control = lycan_control_state(character)
        lines.append(f"{'Control:':13} {control['rank']}")
        lines.append(f"{'Dragon Essence:':13} {'Yes' if control['dragon_essence'] else 'No'}")
    if cls == "Archdruid":
        aspects = state.get("aspect_harmony", set())
        if not isinstance(aspects, set):
            aspects = set(aspects)
        lines.append(f"{'Harmony:':13} {','.join(sorted(aspects)) or 'None'}")
    if cls in {"Ranger", "Beast Master"}:
        companion = getattr(character, "tamed_companion", {}) or {}
        bond = _clamp_int(companion.get("bond", 0), 0, 100)
        lines.append(f"{'Companion:':13} {companion.get('name') or 'None'} {bond}/100 {companion_bond_rank(bond)}")
        command = state.get("pending_companion_command")
        if command:
            lines.append(f"{'Command:':13} {command}")
    if cls in {"Summoner", "Grand Summoner"}:
        bonds = ensure_state(character)["summon_bonds"]
        name, bond = max(bonds.items(), key=lambda item: item[1])
        lines.append(f"{'Summon Bond:':13} {name} {int(bond)}/100")
        if state.get("conduit_command"):
            lines.append(f"{'Conduit:':13} Primed")
    if cls in {"Shaman", "Soulcatcher"}:
        totem_line = _totem_status_line(character)
        if totem_line:
            lines.append(totem_line)
    ring_line = _ring_readiness_line(character, cls)
    if ring_line:
        lines.append(ring_line)
    preserve_line = _preservation_line(character, cls)
    if preserve_line:
        lines.append(preserve_line)
    return lines
