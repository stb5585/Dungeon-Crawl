"""Promotion class-kit status presentation."""

from __future__ import annotations

from typing import Any

from .companions import (
    PRESERVATION_METERS,
    companion_bond_rank,
    lycan_control_state,
    totem_resonance,
)
from .meters import cap_for, eclipse, shadowcaster_debt_cap
from .resolve import _resolve_data, resolve_cap
from .state import (
    _clamp_int,
    _class_ring_data,
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
    if bond >= 100:
        return "Perfected"
    if bond >= 50:
        return "Invoke ready"
    if bond >= 25:
        return "Attuned"
    return "Building"


def status_summary_rows(character: Any, target: Any | None = None) -> list[tuple[str, str]]:
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
                ready = (
                    "Equipped" if demonologist.has_equipped_class_ring(character) else "Awakened"
                )
                rows.append(("Ring Ready", ready))
        except Exception:
            pass
    if cls == "Astromancer":
        threads = int(state.get("foresight_threads", 0) or 0)
        rows.append(("Threads", _meter_hint(threads, 3, ready="Threaded ready")))
        if state.get("threaded_cast_pending"):
            rows.append(("Threaded", "Pending next spell"))
    if cls == "Shadowcaster":
        data = _class_ring_data(character, "Shadowcaster")
        debt = int(data.get("debt", 0) or 0)
        rows.append(
            (
                "Umbral Debt",
                _meter_hint(debt, shadowcaster_debt_cap(character), ready="Shade ready"),
            )
        )
        rows.append(("Backlash", str(int(data.get("backlash", 0) or 0))))
        eclipse = int(data.get("eclipse_turns", 0) or 0)
        if eclipse:
            rows.append(("Shade of Ahool", f"{eclipse} turn(s)"))
    if cls in {"Spellblade", "Knight Enchanter"}:
        charge = state.get("blade_charge")
        if isinstance(charge, dict):
            arcane = int(charge.get("Arcane", 0) or 0)
            elemental = int(charge.get("Elemental", 0) or 0)
        else:
            arcane = 0
            elemental = 0
        charge_text = f"Arcane ×{arcane} · Elemental ×{elemental}"
        rows.append(("Blade Charge", charge_text))
        novel_shield = state.get("novel_shield")
        if isinstance(novel_shield, dict):
            rows.append(
                (
                    "Novel Shielding",
                    (
                        f"{int(novel_shield.get('remaining', 0) or 0)} / "
                        f"{int(novel_shield.get('maximum', 0) or 0)} · "
                        f"{int(novel_shield.get('turns', 0) or 0)} turn(s)"
                    ),
                )
            )
        breakdown = state.get("breakdown_stacks", {})
        if isinstance(breakdown, dict) and breakdown:
            rows.append(("Breakdown", f"{max(int(value or 0) for value in breakdown.values())}/5"))
        if cls == "Knight Enchanter":
            from .weaves import weave_preview

            foundation = state.get("weave_foundation") or "Open"
            accent = state.get("weave_accent") or "Open"
            rows.append(("Foundation", str(foundation)))
            rows.append(("Accent", str(accent)))
            rows.append(("Weave", weave_preview(character)))
            if isinstance(state.get("spellbind"), dict):
                turns = int(state["spellbind"].get("turns", 0) or 0)
                rows.append(("Spellbind", f"Ready · {turns} turn(s)"))
            defensive_stacks = int(state.get("defensive_release", 0) or 0)
            if defensive_stacks:
                rows.append(
                    (
                        "Defensive Release",
                        f"{defensive_stacks}/3 · +{defensive_stacks * 25}%",
                    )
                )
            if isinstance(state.get("echoing_weave"), dict):
                rows.append(("Echoing Blade", "Repeats next turn"))
    if cls == "Berserker":
        from .. import berserker

        momentum = int(state.get("bloodied_momentum", 0) or 0)
        cap = cap_for(character, "bloodied_momentum")
        hp_max = max(1, int(getattr(character.health, "max", 1) or 1))
        hp_ratio = character.health.current / hp_max
        if hp_ratio < 0.25:
            threshold = "Critical (<25%)"
        elif hp_ratio < 0.50:
            threshold = "Bloodied (<50%)"
        else:
            threshold = "Steady"
        scars = berserker.scar_count(character)
        scar_ready = (
            "Locked (<10 scars)"
            if scars < 10
            else "Used" if state.get("battle_scar_momentum_preserved") else "Ready"
        )
        rows.append(
            (
                "Bloodied Momentum",
                _meter_hint(momentum, cap, ready="Heavy art"),
            )
        )
        rows.append(("Bloodied State", threshold))
        rows.append(("Scar Cap", f"+{cap - 3} from {scars} scars"))
        rows.append(("Scar Preserve", scar_ready))
        if _ring_awakened_equipped(character, "Berserker"):
            ring_ready = "Used" if state.get("bloodied_ring_miss_preserved") else "Ready"
            rows.append(("Ring Preserve", ring_ready))
    if cls in {"Paladin", "Crusader"}:
        conviction = int(state.get("oath_conviction", 0) or 0)
        rows.append(
            (
                "Conviction",
                _meter_hint(conviction, cap_for(character, "oath_conviction"), ready="Vow ready"),
            )
        )
    if cls in {"Lancer", "Dragoon"}:
        aerial = int(state.get("aerial_tempo", 0) or 0)
        rows.append(
            (
                "Aerial Tempo",
                _meter_hint(aerial, cap_for(character, "aerial_tempo"), ready="Follow-up"),
            )
        )
        shield = _class_ring_data(character, "Dragoon")
        if int(shield.get("meteor_guard_turns", 0) or 0) > 0:
            rows.append(
                ("Landing Shield", f"{int(shield.get('meteor_guard_turns', 0) or 0)} turn(s)")
            )
    if cls in {"Sentinel", "Stalwart Defender"}:
        cap = resolve_cap(character)
        resolve = int(_resolve_data(character).get("guard_meter", 0) or 0)
        rows.append(("Resolve", _meter_hint(resolve, cap, ready="Guard ready")))
    if cls in {"Sentinel", "Stalwart Defender"} and int(state.get("hold_the_line", 0) or 0) > 0:
        rows.append(("Guard Stance", f"Hold ({int(state.get('hold_the_line', 0) or 0)})"))
    if cls in {"Thief", "Rogue"}:
        fortune = int(state.get("fortune", 0) or 0)
        misfortune = int(state.get("misfortune", 0) or 0)
        rows.append(
            ("Fortune", _meter_hint(fortune, cap_for(character, "fortune"), ready="Steal/Mug"))
        )
        rows.append(
            (
                "Misfortune",
                _meter_hint(misfortune, cap_for(character, "misfortune"), ready="Payoff on hit"),
            )
        )
        if int(state.get("jinx_turns", 0) or 0) > 0:
            rows.append(("Jinx", f"{int(state.get('jinx_turns', 0) or 0)} turn(s)"))
    if cls in {"Inquisitor", "Seeker"}:
        if target is not None:
            studied = int(
                ensure_state(character)["case_journal"].get(
                    str(getattr(target, "enemy_typ", "")),
                    0,
                )
                or 0
            )
        else:
            studied = max(ensure_state(character)["case_journal"].values(), default=0)
        rows.append(("Case", case_rank(studied)))
        revelation = state.get("revelation", {})
        if target is not None and isinstance(revelation, dict):
            from .meters import _target_stacks

            current = _target_stacks(revelation, target)
        else:
            current = 0
        rows.append(
            (
                "Revelation",
                _meter_hint(current, cap_for(character, "revelation"), ready="Target read"),
            )
        )
        details_visible = bool(
            target is not None
            and not getattr(target, "boss", False)
            and getattr(target, "name", "") != "Waitress"
        )
        rows.append(
            (
                "Enemy Detail",
                "Visible" if details_visible else "No visible target selected",
            )
        )
    if cls in {"Assassin", "Ninja"}:
        marks = state.get("death_marks", {})
        if target is not None and isinstance(marks, dict):
            from .meters import _target_stacks

            current = _target_stacks(marks, target)
        else:
            current = (
                max((int(value or 0) for value in marks.values()), default=0)
                if isinstance(marks, dict)
                else 0
            )
        rows.append(
            (
                "Death Mark",
                _meter_hint(current, cap_for(character, "death_marks"), ready="Finisher"),
            )
        )
    if cls in {"Spell Stealer", "Arcane Trickster"}:
        stolen = int(state.get("stolen_charge", 0) or 0)
        rows.append(
            (
                "Stolen Charge",
                _meter_hint(
                    stolen,
                    cap_for(character, "stolen_charge"),
                    ready="Charge ready",
                    empty="Steal first",
                ),
            )
        )
        if cls == "Arcane Trickster" and _ring_awakened_equipped(character, "Arcane Trickster"):
            from .. import class_rings

            turns = int(
                class_rings.ensure_state(character)["data"]["Arcane Trickster"].get(
                    "buff_turns",
                    0,
                )
                or 0
            )
            preserved = "Arcane Trickster:stolen_charge" in state.setdefault(
                "ring_preserved",
                set(),
            )
            if turns > 0:
                rows.append(("Arcane Larceny", f"Active · {turns} turns"))
            rows.append(
                (
                    "Ring Preserve",
                    "Spent" if preserved else "Arcane Larceny ready",
                )
            )
    if cls in {"Cleric", "Templar", "Hierophant"}:
        devotion = int(state.get("devotion", 0) or 0)
        if cls == "Templar" and devotion >= 2:
            hint = "Aegis ready"
        elif cls == "Hierophant" and devotion >= 1:
            hint = "Conduit ready"
        else:
            hint = "Ward ready"
        rows.append(("Devotion", _meter_hint(devotion, cap_for(character, "devotion"), ready=hint)))
        if cls == "Templar" and _ring_awakened_equipped(character, "Templar"):
            try:
                from .. import class_rings

                blessing = class_rings.current_ordered_blessing(character)
                if blessing:
                    rows.append(("Blessing", blessing))
            except Exception:
                pass
        if cls == "Templar" and (
            state.get("relic_aegis_counter") or state.get("ordered_blessing_counter")
        ):
            rows.append(("Holy Counter", "Armed"))
        if cls == "Hierophant" and state.get("consecrated_conduit"):
            rows.append(("Conduit", "Pending payoff"))
    if cls in {"Priest", "Archbishop"}:
        prayer = int(state.get("prayer", 0) or 0)
        hint = "Benediction ready" if cls == "Archbishop" and prayer >= 3 else "Supplication ready"
        rows.append(("Prayer", _meter_hint(prayer, cap_for(character, "prayer"), ready=hint)))
        benediction = state.get("great_benediction")
        if isinstance(benediction, dict) and int(benediction.get("turns", 0) or 0) > 0:
            rows.append(("Benediction", f"{int(benediction['turns'])} turns"))
        power_up = getattr(character, "class_effects", {}).get("Power Up")
        if cls == "Archbishop" and power_up is not None and power_up.active:
            rows.append(("Great Gospel", f"{int(power_up.duration or 0)} rounds"))
    if cls in {"Monk", "Master Monk"}:
        ki = int(state.get("ki", 0) or 0)
        rows.append(("Ki", _meter_hint(ki, cap_for(character, "ki"), ready="Dim Mak")))
    if cls in {"Bard", "Troubadour"}:
        crescendo = int(state.get("crescendo", 0) or 0)
        rows.append(
            (
                "Crescendo",
                _meter_hint(crescendo, cap_for(character, "crescendo"), ready="Coda"),
            )
        )
        if cls == "Troubadour":
            repertoire = ensure_state(character)["bard_repertoire"]
            mastered = sum(1 for entry in repertoire.values() if entry.get("known"))
            rows.append(("Repertoire", f"{mastered}/{len(repertoire)} mastered"))
    if cls == "Lycan":
        control = lycan_control_state(character)
        rows.append(("Control", str(control["rank"])))
        try:
            from .. import lycan

            rows.append(("Form", "Shifted" if lycan.is_transformed(character) else "Human"))
        except Exception:
            pass
        rows.append(("Dragon Essence", "Yes" if control["dragon_essence"] else "No"))
    if cls == "Archdruid":
        raw_aspects = state.get("aspect_harmony", {})
        if isinstance(raw_aspects, set):
            aspects = {name: 1 for name in raw_aspects}
        elif isinstance(raw_aspects, dict):
            aspects = {
                str(name): int(count or 0)
                for name, count in raw_aspects.items()
                if int(count or 0) > 0
            }
        else:
            aspects = {}
        harmony_value = (
            ",".join(
                f"{name}×{count}" if count > 1 else name for name, count in sorted(aspects.items())
            )
            or "None"
        )
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
        active_companion = bool(
            isinstance(companion, dict) and companion.get("active") and companion.get("name")
        )
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
    if cls == "Thaumaturgist":
        name, bond = _best_summon_bond(character)
        rows.append(
            (
                "Xenid Conduit",
                f"{name} {int(bond)}/100 {_active_summon_bond_hint(character, name, int(bond))}",
            )
        )
        if state.get("conduit_command"):
            rows.append(("Conduit", "Primed next Xenid action"))
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
