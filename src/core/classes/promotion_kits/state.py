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

_HOSTILE_STATUS_GROUPS = ("status_effects", "physical_effects")


def _hostile_status_names(character: Any) -> list[str]:
    ignored = {"Defend", "Peaceful", "Shapeshifted", "Steal Success"}
    names: list[str] = []
    for group_name in _HOSTILE_STATUS_GROUPS:
        for name, effect in getattr(character, group_name, {}).items():
            if name not in ignored and getattr(effect, "active", False):
                names.append(name)
    return sorted(names)


def _cleanse_one_hostile_status(character: Any) -> str | None:
    names = _hostile_status_names(character)
    if not names:
        return None
    name = names[0]
    for group_name in _HOSTILE_STATUS_GROUPS:
        effect = getattr(character, group_name, {}).get(name)
        if effect is not None:
            effect.active = False
            effect.duration = 0
            effect.extra = 0
            return name
    return None


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


def _class_ring_data(character: Any, class_value: str) -> dict[str, Any]:
    """Return mutable ring state for a class, or an empty fallback."""
    try:
        from .. import class_rings

        return class_rings.ensure_state(character)["data"][class_value]
    except Exception:
        return {}


def _claim_action(character: Any, claim: str, *, incoming: bool = False) -> bool:
    """Claim one authored resource outcome inside the current action."""
    state = combat_state(character)
    key = "incoming_claims" if incoming else "action_claims"
    claims = state.setdefault(key, set())
    if not isinstance(claims, set):
        claims = set(claims)
        state[key] = claims
    if claim in claims:
        return False
    claims.add(claim)
    return True


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
