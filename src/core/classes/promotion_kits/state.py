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

CLASS_KIT_LOG_TERMS = (
    "aerial",
    "arcane larceny",
    "arcane tempo",
    "aspect harmony",
    "beast command",
    "blade charge",
    "bloodied momentum",
    "case journal",
    "class ring",
    "companion bond",
    "companion command",
    "conduit",
    "corruption",
    "crescendo",
    "death mark",
    "devotion",
    "divine intervention",
    "dragon essence",
    "echo",
    "encore",
    "foresight",
    "fortune",
    "harmony bonus",
    "finders keepers",
    "ki",
    "loaded dice",
    "misfortune",
    "no-trace",
    "oath conviction",
    "ordered blessings",
    "patron",
    "prayer",
    "revelation",
    "resolve",
    "ring preserve",
    "ring ready",
    "scavenger",
    "stolen charge",
    "summon bond",
    "threaded cast",
    "totem resonance",
    "umbral",
    "vow affirmation",
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
        "favored_enemy": {
            "type": None,
            "practice": 0,
            "switches": 0,
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

    favored = state.get("favored_enemy", {})
    if isinstance(favored, dict):
        marked = favored.get("type")
        normalized["favored_enemy"] = {
            "type": str(marked) if marked else None,
            "practice": _clamp_int(favored.get("practice", 0), 0, 999),
            "switches": _clamp_int(favored.get("switches", 0), 0, 999),
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
        "pending_aerial_follow_through": None,
        "hold_the_line": 0,
        "spell_reflection_turns": 0,
        "spell_reflection_skip_tick": False,
        "oath_judgment_counter": None,
        "oath_protection_guard": None,
        "oath_retribution_shelter": None,
        "fortune": 0,
        "misfortune": 0,
        "cheat_death_used": False,
        "revelation": {},
        "death_marks": {},
        "stolen_charge": 0,
        "devotion": 0,
        "pending_devotion_gains": [],
        "defer_devotion_until_survival": False,
        "consecrated_conduit": None,
        "action_token": 0,
        "hierophant_devotion_token": None,
        "pending_hierophant_devotion_token": None,
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
    from .meters import _reset_shadowcaster_combat_fields

    setattr(character, "_promotion_kit_combat", {})
    combat_state(character)
    _reset_shadowcaster_combat_fields(character)


def tick_combat_state(character: Any) -> str:
    from .. import class_rings
    from .resolve import tick_spell_reflection

    state = combat_state(character)
    msg = class_rings.tick_aerial_supremacy_shield(character)
    msg += tick_spell_reflection(character)
    hold_turns = int(state.get("hold_the_line", 0) or 0)
    if hold_turns > 0:
        state["hold_the_line"] = max(0, hold_turns - 1)
        if state["hold_the_line"] <= 0:
            msg += f"{character.name} is no longer holding the line.\n"
    for key in (
        "oath_judgment_counter",
        "oath_protection_guard",
        "oath_retribution_shelter",
    ):
        payload = state.get(key)
        if not isinstance(payload, dict):
            continue
        turns = max(0, int(payload.get("turns", 0) or 0) - 1)
        payload["turns"] = turns
        if turns <= 0:
            state[key] = None
            label = {
                "oath_judgment_counter": "Oath's Judgment counter",
                "oath_protection_guard": "Oath's Shelter guard",
                "oath_retribution_shelter": "Oath's Shelter reprisal",
            }[key]
            msg += f"{character.name}'s {label} expires.\n"
    jinx = int(state.get("jinx_turns", 0) or 0)
    if jinx > 0:
        state["jinx_turns"] = max(0, jinx - 1)
        if state["jinx_turns"] <= 0:
            msg += f"{character.name}'s Jinx fades.\n"
    return msg


def start_combat(character: Any) -> str:
    from .. import class_rings

    clear_combat_state(character)
    class_rings.reset_combat_flags(character)
    return ""


def end_combat(
    character: Any,
    *,
    victory: bool = False,
    enemy: Any | None = None,
    exp_gain: int | None = None,
    boss: bool = False,
    show_progress_messages: bool = False,
) -> str:
    from .companions import (
        favorite_enemy_type,
        gain_companion_bond,
        gain_summon_bond_for_active,
        summon_bond_gain_for_victory,
    )
    from .meters import convert_shadow_backlash
    from .tracks import gain_case_progress

    msg = ""
    if victory and enemy is not None:
        case_msg = gain_case_progress(character, getattr(enemy, "enemy_typ", None), 4, "victory")
        if show_progress_messages:
            msg += case_msg
        companion_bond_before = None
        companion_state = getattr(character, "tamed_companion", None)
        if isinstance(companion_state, dict):
            companion_bond_before = _clamp_int(companion_state.get("bond", 0), 0, 100)
        companion_bond_msg = gain_companion_bond(character, 4, reason="victory", announce=False)
        if getattr(enemy, "enemy_typ", None) == favorite_enemy_type(character):
            companion_bond_msg += gain_companion_bond(character, 2, reason="Favored Enemy hunt", announce=False)
            try:
                from .. import ability_mechanics

                practice_msg = ability_mechanics.gain_favored_enemy_practice(character, enemy, 1, "the hunt")
                if show_progress_messages:
                    msg += practice_msg
            except Exception:
                pass
        companion_state = getattr(character, "tamed_companion", None)
        if isinstance(companion_state, dict) and companion_bond_before is not None:
            companion_bond_after = _clamp_int(companion_state.get("bond", 0), 0, 100)
            if companion_bond_after > companion_bond_before:
                msg += f"{companion_state.get('name') or 'Companion'} bond increased.\n"
                msg += companion_bond_msg
        msg += gain_summon_bond_for_active(
            character,
            summon_bond_gain_for_victory(
                character,
                exp_gain if exp_gain is not None else getattr(enemy, "experience", 0),
                guaranteed=bool(boss),
                multiplier=2 if boss else 1,
            ),
            "boss victory" if boss else "victory",
        )
        if hasattr(character, "_active_summon_bond_level_span_xp"):
            try:
                delattr(character, "_active_summon_bond_level_span_xp")
            except Exception:
                pass
        if hasattr(character, "_active_summon_bond_note"):
            try:
                delattr(character, "_active_summon_bond_note")
            except Exception:
                pass
    msg += convert_shadow_backlash(character, fraction=0.05, reason="combat end")
    clear_combat_state(character)
    from .. import class_rings

    class_rings.reset_combat_flags(character)
    return msg


def _ring_awakened_equipped(character: Any, class_value: str | None = None) -> bool:
    try:
        from .. import class_rings

        return bool(
            class_rings.is_awakened(character, class_value or class_name(character))
            and class_rings.has_equipped_class_ring(character)
        )
    except Exception:
        return False


def _has_skill(character: Any, skill_name: str) -> bool:
    return skill_name in getattr(character, "spellbook", {}).get("Skills", {})


def _hierophant_overchannel_active(character: Any) -> bool:
    effect = getattr(character, "class_effects", {}).get("Power Up")
    return bool(
        class_name(character) == "Hierophant"
        and getattr(character, "power_up", False)
        and _has_skill(character, "Sacred Overchannel")
        and effect is not None
        and getattr(effect, "active", False)
    )


def begin_action(
    character: Any,
    *,
    defer_devotion: bool = False,
    action: str | None = None,
    choice: str | None = None,
) -> None:
    state = combat_state(character)
    state["action_token"] = int(state.get("action_token", 0) or 0) + 1
    state["hierophant_devotion_token"] = None
    state["pending_hierophant_devotion_token"] = None
    state["pending_devotion_gains"] = []
    state["defer_devotion_until_survival"] = bool(defer_devotion)
    if action is not None:
        from .aerial import arm_aerial_follow_through

        arm_aerial_follow_through(character, action, choice)


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
