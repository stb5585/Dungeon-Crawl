"""Promotion-kit combat lifecycle orchestration.

State storage remains dependency-light in :mod:`state`; this module coordinates
the richer meter, track, companion, aerial, and class-ring behaviors.
"""

from __future__ import annotations

from typing import Any

from .state import _clamp_int, class_name, combat_state, ensure_state


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
