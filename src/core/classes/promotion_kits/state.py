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
    "Hodag",
    "Caladrius",
    "Patagon",
    "Kobalos",
    "Dilong",
    "Cacus",
    "Agloolik",
    "Izulu",
    "Hala",
    "Lamashtu",
    "Seraphim",
    "Bardi",
    "Tiamat",
    "Zahhak",
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
    "arcane riposte",
    "arcane larceny",
    "aspect harmony",
    "beast command",
    "blade charge",
    "bloodied momentum",
    "case journal",
    "class ring",
    "cleaving edge",
    "companion bond",
    "companion command",
    "conduit",
    "corruption",
    "crescendo",
    "death mark",
    "defensive release",
    "devotion",
    "divine intervention",
    "dragon essence",
    "echo",
    "echoing blade",
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
    "re-debuff",
    "revelation",
    "resolve",
    "resonant strike",
    "ring preserve",
    "ring ready",
    "scavenger",
    "stolen charge",
    "summon bond",
    "threaded cast",
    "totem resonance",
    "umbral",
    "weave",
    "weave reservoir",
    "vow affirmation",
)


def class_name(character: Any) -> str:
    from .. import transformation

    return transformation.permanent_class_name(character)


def default_state() -> dict[str, Any]:
    return {
        "summon_bonds": {name: 0 for name in SUMMON_NAMES},
        "case_journal": {},
        "case_focus": None,
        "bard_repertoire": {
            song: {"known": False, "practice_xp": 0, "clean_finishes": 0} for song in ADVANCED_SONGS
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
    focus = state.get("case_focus")
    normalized["case_focus"] = str(focus) if focus and str(focus).strip() else None

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
            "rank_progress": (
                {str(key): _clamp_int(value, 0, 999) for key, value in progress.items()}
                if isinstance(progress, dict)
                else {}
            ),
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
        "foresight_thread_action": None,
        "blade_charge": None,
        "blade_charge_action_token": None,
        "counter_charge_action_token": None,
        "breakdown_stacks": {},
        "novel_shield": None,
        "weave_foundation": None,
        "weave_accent": None,
        "spellbind": None,
        "defensive_release": 0,
        "echoing_weave": None,
        "bloodied_momentum": 0,
        "bloodied_bonus_round": None,
        "bloodied_payoff_action_token": None,
        "battle_scar_momentum_preserved": False,
        "bloodied_ring_miss_preserved": False,
        "oath_conviction": 0,
        "aerial_tempo": 0,
        "pending_aerial_follow_through": None,
        "hold_the_line": 0,
        "oath_judgment_counter": None,
        "oath_protection_guard": None,
        "oath_retribution_shelter": None,
        "fortune": 0,
        "misfortune": 0,
        "pending_fortune_payoff": None,
        "cheat_death_used": False,
        "revelation": {},
        "active_revelation_payoff": None,
        "inspect_studied_bonus_used": False,
        "seeker_insight_smoothed": False,
        "telegraph_reads": set(),
        "pending_case_prediction": {},
        "active_case_prediction": None,
        "visible_enemy_types": set(),
        "death_marks": {},
        "death_mark_action_tokens": set(),
        "stolen_charge": 0,
        "pending_stolen_charge_payoff": None,
        "arcane_larceny_skip_tick": False,
        "devotion": 0,
        "pending_devotion_gains": [],
        "defer_devotion_until_survival": False,
        "action_claims": set(),
        "action_round": 0,
        "incoming_action_token": 0,
        "incoming_claims": set(),
        "holy_retribution_gain_round": None,
        "great_gospel_gain_round": None,
        "aspect_gain_round": None,
        "consecrated_conduit": None,
        "consecrated_conduit_action": None,
        "relic_aegis_counter": None,
        "ordered_blessing_counter": None,
        "action_token": 0,
        "action_name": None,
        "action_choice": None,
        "hierophant_devotion_token": None,
        "pending_hierophant_devotion_token": None,
        "prayer": 0,
        "great_benediction": None,
        "defensive_regen_prayer_armed": False,
        "ki": 0,
        "ki_action_token": None,
        "ki_spender": None,
        "ki_reaction_token": 0,
        "ki_reaction_claimed": None,
        "martial_master_refund_used": False,
        "crescendo": 0,
        "jinx_turns": 0,
        "aspect_harmony": {},
        "aspect_harmony_order": [],
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
    try:
        from .. import astromancer

        astromancer.clear_threaded_spell(character)
    except Exception:
        pass
    _reset_shadowcaster_combat_fields(character)


def tick_combat_state(character: Any) -> str:
    from .. import class_rings
    from .resolve import tick_resolve_effects

    state = combat_state(character)
    character._shadow_evasion_turns = max(
        0,
        int(getattr(character, "_shadow_evasion_turns", 0) or 0) - 1,
    )
    msg = class_rings.tick_aerial_supremacy_shield(character)
    msg += class_rings.tick_arcane_larceny(character)
    msg += tick_resolve_effects(character)
    benediction = state.get("great_benediction")
    if isinstance(benediction, dict):
        turns = max(0, int(benediction.get("turns", 0) or 0))
        if turns > 0:
            mana = getattr(character, "mana", None)
            restored = 0
            if mana is not None:
                restored = min(
                    max(0, int(mana.max) - int(mana.current)),
                    max(0, int(benediction.get("mana", 0) or 0)),
                )
                mana.current += restored
            benediction["turns"] = turns - 1
            if restored:
                msg += f"Great Benediction restores {restored} MP.\n"
            if turns == 1:
                state["great_benediction"] = None
                msg += f"{character.name}'s Great Benediction fades.\n"
    for key in ("relic_aegis_counter", "ordered_blessing_counter"):
        counter = state.get(key)
        if not isinstance(counter, dict):
            continue
        turns = max(0, int(counter.get("turns", 0) or 0) - 1)
        counter["turns"] = turns
        if turns <= 0:
            state[key] = None
    if class_name(character) == "Knight Enchanter":
        from .weaves import resolve_echoing_blade, weave_reservoir_regeneration

        msg += resolve_echoing_blade(character)
        msg += weave_reservoir_regeneration(character)
    if class_name(character) == "Shadowcaster":
        from .meters import (
            _class_ring_data,
            _fairy_debt_echo,
            _normalize_shadowcaster_data,
            convert_shadow_backlash,
        )

        shadow = _class_ring_data(character, "Shadowcaster")
        _normalize_shadowcaster_data(shadow)
        turns = int(shadow.get("eclipse_turns", 0) or 0)
        if turns > 0:
            shadow["eclipse_turns"] = turns - 1
            if turns == 1:
                character.flying = False
                msg += f"{character.name} returns from the Shade of Ahool.\n"
                conversion = convert_shadow_backlash(
                    character,
                    fraction=0.10,
                    reason="Shade expiration",
                )
                msg += conversion
                if conversion:
                    msg += _fairy_debt_echo(character, 20)
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
    novel_shield = state.get("novel_shield")
    if isinstance(novel_shield, dict):
        turns = max(0, int(novel_shield.get("turns", 0) or 0) - 1)
        novel_shield["turns"] = turns
        if turns <= 0:
            state["novel_shield"] = None
            msg += f"{character.name}'s Novel Shielding fades.\n"
    spellbind = state.get("spellbind")
    if isinstance(spellbind, dict):
        turns = max(0, int(spellbind.get("turns", 0) or 0) - 1)
        spellbind["turns"] = turns
        if turns <= 0:
            state["spellbind"] = None
            msg += f"{character.name}'s Spellbind fades.\n"
    return msg


def start_combat(character: Any) -> str:
    from .. import class_rings, lycan

    clear_combat_state(character)
    class_rings.reset_combat_flags(character)
    return lycan.start_combat(character)


def end_combat(
    character: Any,
    *,
    victory: bool = False,
    enemy: Any | None = None,
    exp_gain: int | None = None,
    boss: bool = False,
    show_progress_messages: bool = False,
) -> str:
    from .. import lycan
    from .companions import (
        clear_conduit_command,
        favorite_enemy_type,
        gain_companion_bond,
        gain_summon_bond_for_active,
        record_lycan_stress,
        summon_bond_gain_for_victory,
    )
    from .meters import convert_shadow_backlash
    from .tracks import gain_case_progress

    msg = ""
    msg += clear_conduit_command(character, "leaves combat")
    state = combat_state(character)
    if class_name(character) == "Lycan" and state.get("lycan_stressed"):
        lycan_state = lycan.ensure_state(character)
        lycan_state["stressed_combat_complete"] = bool(victory)
        if victory:
            control = ensure_state(character)["lycan_control"]
            if control.get("rank") == "Feral":
                msg += record_lycan_stress(character, "survive")
    if victory and enemy is not None:
        visible_types = state.get("visible_enemy_types", set())
        enemy_type = str(getattr(enemy, "enemy_typ", "") or "")
        case_msg = ""
        if enemy_type and enemy_type in visible_types:
            case_msg = gain_case_progress(character, enemy_type, 4, "victory")
        if case_msg:
            msg += case_msg
        companion_bond_before = None
        companion_state = getattr(character, "tamed_companion", None)
        if isinstance(companion_state, dict):
            companion_bond_before = _clamp_int(companion_state.get("bond", 0), 0, 100)
        companion_bond_msg = gain_companion_bond(character, 4, reason="victory", announce=False)
        if getattr(enemy, "enemy_typ", None) == favorite_enemy_type(character):
            companion_bond_msg += gain_companion_bond(
                character, 2, reason="Favored Enemy hunt", announce=False
            )
            try:
                from .. import ability_mechanics

                practice_msg = ability_mechanics.gain_favored_enemy_practice(
                    character, enemy, 1, "the hunt"
                )
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
    if int(combat_state(character).get("boast_turns", 0) or 0) > 0:
        from .resolve import build_resolve

        msg += build_resolve(character, 5, "Boast's combat-end refund")
    msg += convert_shadow_backlash(
        character,
        fraction=0.05,
        reason="combat end",
        ring_stability=False,
    )
    clear_combat_state(character)
    from .. import class_rings

    class_rings.reset_combat_flags(character)
    return msg


def _ring_awakened_equipped(character: Any, class_value: str | None = None) -> bool:
    try:
        from .. import class_rings

        target = class_value or class_name(character)
        awakened = class_rings.is_awakened(character, target)
        if not awakened and target == class_name(character):
            awakened = bool(class_rings._special_system_awakened(character, target))
        return bool(awakened and class_rings.has_equipped_class_ring(character))
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
    round_number: int | None = None,
) -> None:
    state = combat_state(character)
    if bool(getattr(character, "mage_refueling", False)) and choice != "Refueling":
        character.mage_refueling = False
        character.mage_refueling_streak = 0
    state["action_token"] = int(state.get("action_token", 0) or 0) + 1
    state["action_name"] = action
    state["action_choice"] = choice
    state["action_claims"] = set()
    state["active_revelation_payoff"] = None
    if round_number is not None:
        state["action_round"] = max(0, int(round_number))
    state["hierophant_devotion_token"] = None
    state["pending_hierophant_devotion_token"] = None
    state["pending_devotion_gains"] = []
    state["defer_devotion_until_survival"] = bool(defer_devotion)
    if action is not None:
        from .aerial import arm_aerial_follow_through
        from .meters import prepare_action_payoffs

        arm_aerial_follow_through(character, action, choice)
        prepare_action_payoffs(character, action, choice)


def begin_incoming_action(
    character: Any,
    round_number: int | None = None,
    actor: Any | None = None,
) -> None:
    """Open one hostile-action boundary for defensive kit reactions."""
    state = combat_state(character)
    state["incoming_action_token"] = int(state.get("incoming_action_token", 0) or 0) + 1
    state["incoming_claims"] = set()
    state["active_case_prediction"] = None
    if actor is not None:
        from .tracks import begin_case_prediction

        begin_case_prediction(character, actor)
    if round_number is not None:
        state["action_round"] = max(0, int(round_number))


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
