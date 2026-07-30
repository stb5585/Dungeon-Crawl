"""Promotion class-kit status presentation."""

from __future__ import annotations

from typing import Any

from .companions import (
    PRESERVATION_METERS,
    companion_bond_rank,
    lycan_control_state,
    totem_resonance,
)
from .meters import _class_ring_data, cap_for, eclipse, shadowcaster_debt_cap
from .resolve import _resolve_data, resolve_cap
from .state import (
    _clamp_int,
    _ring_awakened_equipped,
    class_name,
    combat_state,
    ensure_state,
)
from .tracks import case_rank


def _ring_readiness_row(character: Any, cls: str) -> tuple[str, str] | None:
    try:
        from .. import class_rings

        if not class_rings.is_legacy_class(cls):
            return None
        if class_rings.is_awakened(character, cls):
            if class_rings.has_equipped_class_ring(character):
                return ("Ring Ready", class_rings.ring_mod(character))
            return ("Ring Ready", "Awakened, unequipped")
        if class_rings.has_visible_class_ring(character):
            return ("Ring Ready", "Dormant")
    except Exception:
        return None
    return None


def _preservation_row(character: Any, cls: str) -> tuple[str, str] | None:
    keys = PRESERVATION_METERS.get(cls)
    if not keys or not _ring_awakened_equipped(character, cls):
        return None
    preserved = combat_state(character).setdefault("ring_preserved", set())
    used = all(f"{cls}:{key}" in preserved for key in keys)
    return ("Ring Preserve", "Used" if used else "Ready")


def _totem_status_row(character: Any) -> tuple[str, str] | None:
    effect = getattr(character, "magic_effects", {}).get("Totem")
    if not effect or not effect.active or not isinstance(effect.extra, dict):
        return None
    aspect = effect.extra.get("aspect") or "Unknown"
    resonance = totem_resonance(character)
    return ("Totem", f"{aspect} {resonance}/{cap_for(character, 'totem_resonance')}")


def _status_line(label: str, value: str) -> str:
    return f"{label + ':':13} {value}"


def _meter_hint(value: int, cap: int, ready: str = "Ready", empty: str = "Building") -> str:
    value = max(0, int(value or 0))
    cap = max(1, int(cap or 1))
    if value <= 0:
        hint = empty
    else:
        hint = ready
    return f"{value}/{cap} {hint}"


def _best_summon_bond(character: Any) -> tuple[str, int]:
    bonds = ensure_state(character)["summon_bonds"]
    active = str(getattr(character, "active_summon_name", "") or "")
    if active in bonds:
        return active, int(bonds.get(active, 0) or 0)
    return max(bonds.items(), key=lambda item: item[1])


def _active_summon_bond_hint(character: Any, summon_name: str, bond: int) -> str:
    summons = getattr(character, "summons", {}) or {}
    summon = summons.get(summon_name)
    level = getattr(getattr(summon, "level", None), "level", None)
    try:
        level_value = int(level)
    except (TypeError, ValueError):
        level_value = None
    if level_value is not None and level_value < 2:
        return "Needs level 2"
    if bond >= 100:
        return "True Name"
    if bond >= 50:
        return "Invoke ready"
    if bond >= 25:
        return "Attuned"
    return "Building"


def status_summary_rows(character: Any) -> list[tuple[str, str]]:
    cls = class_name(character)
    state = combat_state(character)
    rows: list[tuple[str, str]] = []
    if cls == "Demonologist":
        try:
            from .. import demonologist

            contracts = demonologist.ensure_state(character)
            patron = contracts.get("active_patron") or "None"
            mood = contracts.get("patron_moods", {}).get(patron, 0) if patron != "None" else 0
            echo = contracts.get("imprisoned_familiar") or {}
            rows.append(("Corruption", f"{int(contracts.get('corruption', 0) or 0)}/100"))
            rows.append(("Patron", f"{patron} ({int(mood)})"))
            if echo.get("name") or echo.get("spec"):
                rows.append(("Echo", str(echo.get("name") or echo.get("spec"))))
            if contracts.get("ring_awakened"):
                ready = "Equipped" if demonologist.has_equipped_class_ring(character) else "Awakened"
                rows.append(("Ring Ready", ready))
        except Exception:
            pass
    if cls == "Astromancer":
        threads = int(state.get('foresight_threads', 0) or 0)
        rows.append(("Threads", _meter_hint(threads, 3, ready="Threaded ready")))
        if state.get("threaded_cast_pending"):
            rows.append(("Threaded", "Pending next spell"))
    if cls == "Shadowcaster":
        data = _class_ring_data(character, "Shadowcaster")
        debt = int(data.get("debt", 0) or 0)
        rows.append(("Umbral Debt", _meter_hint(debt, shadowcaster_debt_cap(character), ready="Eclipse ready")))
        rows.append(("Backlash", str(int(data.get('backlash', 0) or 0))))
        eclipse = int(data.get("eclipse_turns", 0) or 0)
        if eclipse:
            rows.append(("Eclipse", f"{eclipse} turn(s)"))
    if cls in {"Spellblade", "Knight Enchanter"}:
        charge = state.get('blade_charge')
        rows.append(("Blade Charge", f"{charge} Ready" if charge else "None, cast first"))
        if cls == "Knight Enchanter":
            tempo = int(state.get('arcane_tempo', 0) or 0)
            rows.append(("Arcane Tempo", _meter_hint(tempo, 3, ready="Burst at 3")))
    if cls == "Berserker":
        momentum = int(state.get('bloodied_momentum', 0) or 0)
        rows.append(("Momentum", _meter_hint(momentum, cap_for(character, 'bloodied_momentum'), ready="Heavy art")))
    if cls in {"Paladin", "Crusader"}:
        conviction = int(state.get('oath_conviction', 0) or 0)
        rows.append(("Conviction", _meter_hint(conviction, cap_for(character, 'oath_conviction'), ready="Vow ready")))
    if cls in {"Lancer", "Dragoon"}:
        aerial = int(state.get('aerial_tempo', 0) or 0)
        rows.append(("Aerial Tempo", _meter_hint(aerial, cap_for(character, 'aerial_tempo'), ready="Follow-up")))
        shield = _class_ring_data(character, "Dragoon")
        if int(shield.get("meteor_guard_turns", 0) or 0) > 0:
            rows.append(("Landing Shield", f"{int(shield.get('meteor_guard_turns', 0) or 0)} turn(s)"))
    if cls in {"Sentinel", "Stalwart Defender"}:
        cap = resolve_cap(character)
        resolve = int(_resolve_data(character).get('guard_meter', 0) or 0)
        rows.append(("Resolve", _meter_hint(resolve, cap, ready="Guard ready")))
    if cls in {"Sentinel", "Stalwart Defender"} and int(state.get("hold_the_line", 0) or 0) > 0:
        rows.append(("Guard Stance", f"Hold ({int(state.get('hold_the_line', 0) or 0)})"))
    if cls in {"Thief", "Rogue"}:
        fortune = int(state.get('fortune', 0) or 0)
        misfortune = int(state.get('misfortune', 0) or 0)
        rows.append(("Fortune", _meter_hint(fortune, cap_for(character, 'fortune'), ready="Steal/Mug")))
        rows.append(("Misfortune", _meter_hint(misfortune, cap_for(character, 'misfortune'), ready="Payoff on hit")))
        if int(state.get("jinx_turns", 0) or 0) > 0:
            rows.append(("Jinx", f"{int(state.get('jinx_turns', 0) or 0)} turn(s)"))
    if cls in {"Inquisitor", "Seeker"}:
        best = max(ensure_state(character)["case_journal"].values(), default=0)
        rows.append(("Case", f"{best}/100 {case_rank(best)}"))
        revelation = state.get("revelation", {})
        current = max((int(value or 0) for value in revelation.values()), default=0) if isinstance(revelation, dict) else 0
        rows.append(("Revelation", _meter_hint(current, cap_for(character, 'revelation'), ready="Target read")))
    if cls in {"Assassin", "Ninja"}:
        marks = state.get("death_marks", {})
        current = max((int(value or 0) for value in marks.values()), default=0) if isinstance(marks, dict) else 0
        rows.append(("Death Mark", _meter_hint(current, cap_for(character, 'death_marks'), ready="Finisher")))
    if cls in {"Spell Stealer", "Arcane Trickster"}:
        stolen = int(state.get('stolen_charge', 0) or 0)
        rows.append(("Stolen Charge", _meter_hint(stolen, cap_for(character, 'stolen_charge'), ready="Charge ready", empty="Steal first")))
    if cls in {"Cleric", "Templar", "Hierophant"}:
        devotion = int(state.get('devotion', 0) or 0)
        if cls == "Templar" and devotion >= 2:
            hint = "Aegis ready"
        elif cls == "Hierophant" and devotion >= 1:
            hint = "Conduit ready"
        else:
            hint = "Ward ready"
        rows.append(("Devotion", _meter_hint(devotion, cap_for(character, 'devotion'), ready=hint)))
        if cls == "Hierophant" and state.get("consecrated_conduit"):
            rows.append(("Conduit", "Pending payoff"))
    if cls in {"Priest", "Archbishop"}:
        prayer = int(state.get('prayer', 0) or 0)
        hint = "Benediction ready" if cls == "Archbishop" and prayer >= 3 else "Supplication ready"
        rows.append(("Prayer", _meter_hint(prayer, cap_for(character, 'prayer'), ready=hint)))
    if cls in {"Monk", "Master Monk"}:
        ki = int(state.get('ki', 0) or 0)
        rows.append(("Ki", _meter_hint(ki, cap_for(character, 'ki'), ready="Dim Mak")))
    if cls in {"Bard", "Troubadour"}:
        crescendo = int(state.get('crescendo', 0) or 0)
        rows.append(("Crescendo", _meter_hint(crescendo, 3, ready="Coda")))
        if cls == "Troubadour":
            repertoire = ensure_state(character)["bard_repertoire"]
            mastered = sum(1 for entry in repertoire.values() if entry.get("known"))
            rows.append(("Repertoire", f"{mastered}/{len(repertoire)} mastered"))
    if cls == "Lycan":
        control = lycan_control_state(character)
        rows.append(("Control", str(control['rank'])))
        try:
            from .. import lycan

            rows.append(("Form", "Shifted" if lycan.is_transformed(character) else "Human"))
        except Exception:
            pass
        rows.append(("Dragon Essence", "Yes" if control["dragon_essence"] else "No"))
    if cls == "Archdruid":
        aspects = state.get("aspect_harmony", set())
        if not isinstance(aspects, set):
            aspects = set(aspects)
        harmony_value = ",".join(sorted(aspects)) or "None"
        if len(aspects) >= 2:
            harmony_value += " Surge ready"
        rows.append(("Harmony", harmony_value))
    if cls in {"Ranger", "Beast Master"}:
        try:
            from .. import ability_mechanics

            rows.append(("Favored Enemy", ability_mechanics.favored_enemy_label(character)))
        except Exception:
            pass
        companion = getattr(character, "tamed_companion", {}) or {}
        active_companion = bool(isinstance(companion, dict) and companion.get("active") and companion.get("name"))
        if active_companion:
            bond = _clamp_int(companion.get("bond", 0), 0, 100)
            try:
                companion_name = ability_mechanics.tamed_companion_display_name(companion)
            except Exception:
                companion_name = f"{companion.get('name') or 'None'}"
            rows.append(("Companion", companion_name))
            evolution = str(companion.get("evolution") or "")
            if evolution:
                rows.append(("Form", evolution))
            rows.append(("Bond", f"{bond}/100 {companion_bond_rank(bond)}"))
        command = state.get("pending_companion_command")
        if command and active_companion:
            rows.append(("Command", f"{command} Pending"))
    if cls in {"Summoner", "Grand Summoner"}:
        name, bond = _best_summon_bond(character)
        rows.append(("Summon Bond", f"{name} {int(bond)}/100 {_active_summon_bond_hint(character, name, int(bond))}"))
        if state.get("conduit_command"):
            rows.append(("Conduit", "Primed next summon action"))
    if cls in {"Shaman", "Soulcatcher"}:
        totem_row = _totem_status_row(character)
        if totem_row:
            rows.append(totem_row)
    ring_row = _ring_readiness_row(character, cls)
    if ring_row:
        rows.append(ring_row)
    preserve_row = _preservation_row(character, cls)
    if preserve_row:
        rows.append(preserve_row)
    return rows


def status_summary(character: Any) -> list[str]:
    return [_status_line(label, value) for label, value in status_summary_rows(character)]
