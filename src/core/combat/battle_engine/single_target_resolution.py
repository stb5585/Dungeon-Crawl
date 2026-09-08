"""Single-target committed action resolution for the battle engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...classes import (
    ability_mechanics,
    astromancer,
    bard,
    lycan,
    paladin,
    promotion_kits,
    warrior,
)
from ..visibility import detect, is_concealed
from .models import ActionResult

if TYPE_CHECKING:
    from collections.abc import Callable


class SingleTargetActionResolutionMixin:
    """Resolve a committed action against one target or the acting combatant."""

    def _execute_committed_action(
        self,
        action: str,
        choice: str | None = None,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """Execute a validated single-target action for the current attacker."""
        result = ActionResult()
        self._last_combat_result = None
        hp_before = self.player.health.current
        defender_alive_before = bool(self.defender and self.defender.is_alive())
        if self.attacker != self.player:
            promotion_kits.begin_incoming_ki_action(self.player)
            promotion_kits.begin_incoming_action(
                self.player,
                round_number=self.round_number,
                actor=self.attacker,
            )
        if self.attacker == self.player:
            warrior.begin_action(self.player)
        if self.attacker == self.player and not (action == "Cast Spell" and choice == "Rewind"):
            ability_mechanics.store_rewind_snapshot(self)
            promotion_kits.begin_action(
                self.player,
                defer_devotion=True,
                action=action,
                choice=choice,
                round_number=self.round_number,
            )

        if action == "Nothing" or action == "Cancelled":
            result.message = f"{self.attacker.name} does nothing.\n"
            if self.attacker == self.player:
                warrior.finish_action(self.player)
            return result

        if action == "Detect":
            if self._member_for_character(self.attacker) is not None:
                concealed = (
                    [self.active_player_character]
                    if is_concealed(self.active_player_character)
                    else []
                )
            else:
                concealed = [
                    member.enemy
                    for member in self.encounter.living_members
                    if is_concealed(member.enemy)
                ]
            if not concealed:
                result.message = f"{self.attacker.name} finds no concealed opponents.\n"
            else:
                found = sum(detect(self.attacker, target, rng=self._rng) for target in concealed)
                result.message = f"{self.attacker.name} detects {found} of {len(concealed)} concealed opponents.\n"
            return result

        if self.attacker.status_effects["Sleep"].active and astromancer.silent_lucidity_active(
            self.attacker
        ):
            spell = self.attacker.spellbook.get("Spells", {}).get(choice)
            if action != "Cast Spell" or not astromancer.can_cast_while_asleep(
                self.attacker,
                spell,
            ):
                result.message = (
                    f"{self.attacker.name} can shape only lucid Time or "
                    "Divination spells while asleep.\n"
                )
                return result

        if self._tunneled_action_blocked(action, choice):
            result.message = f"{self.attacker.name} must surface before doing that.\n"
            return result

        debuff_snapshot = self._debuff_state_snapshot(self.attacker, choice, self.defender)

        if (
            action == "Attack"
            and getattr(self.attacker, "magic_effects", {}).get("Tree of Life")
            and self.attacker.magic_effects["Tree of Life"].active
        ):
            result.message = (
                f"{self.attacker.name} is rooted as the Tree of Life and cannot attack.\n"
            )
            if self.attacker == self.player:
                warrior.finish_action(self.player)
            return result

        conduit_payoff = None
        if self.summon_active and self.summon is self.attacker:
            conduit_payoff = promotion_kits.begin_conduit_payoff(
                self.player,
                self.summon,
                action,
                self.defender,
            )

        if action == "Attack":
            result.message = self._execute_attack()
        elif action == "Pickup Weapon":
            self.attacker.physical_effects["Disarm"].active = False
            result.message = f"{self.attacker.name} picks up their weapon.\n"
        elif action == "Flee":
            result.message, result.fled = self._execute_flee()
            if result.fled and self.attacker == self.player:
                self.flee = True
                if hasattr(self.player, "record_flee"):
                    self.player.record_flee()
                vow_text = paladin.on_flee(self.player, success=True)
                if vow_text:
                    result.message += vow_text
            elif self.attacker != self.player:
                result.fled = False
        elif action == "Defend":
            result.message = self._execute_defend()
        elif action == "Cast Spell":
            result.message = self._execute_spell(choice)
        elif action == "Runic Boost":
            result.message = self._execute_runic_boost(choice)
        elif action == "Steal As Well":
            result.message = self._execute_steal_as_well(choice)
        elif action == "Use Skill":
            result.message = self._execute_skill(choice, slot_machine_callback)
            result.fled = bool(self.flee)
        elif action == "Tame":
            result.message = self._execute_skill("Tame", slot_machine_callback)
            result.fled = bool(self.flee)
        elif action == "Companion":
            if not choice:
                result.message = f"{self.attacker.name} needs to choose a companion command.\n"
            else:
                result.message = promotion_kits.beast_command(self.player, choice)
        elif action == "Repertoire":
            if not choice:
                result.message = f"{self.attacker.name} needs to choose a mastered song.\n"
            else:
                _success, result.message = bard.perform_repertoire_song(
                    self.player,
                    choice,
                    target=self.defender,
                    battle_engine=self,
                )
        elif action == "Use Item":
            result.message = self._execute_item(choice)
        elif action == "Summon":
            result.message, result.summon_started, result.summon = self._execute_summon(choice)
        elif action == "Recall":
            result.message, result.summon_recalled = self._execute_recall()
        elif action == "Totem":
            result.message = self._execute_totem(choice)
        elif action in {"Untransform", "Dismiss Form"}:
            result.message = self.attacker.transform(back=True)
        elif action == "Transform":
            if choice:
                select_form = getattr(self.attacker, "select_transform_form", None)
                if not callable(select_form) or not select_form(choice):
                    result.message = f"{self.attacker.name} cannot transform into {choice}.\n"
                    return result
            result.message = self.attacker.transform()
        else:
            result.message = f"{self.attacker.name} does nothing.\n"

        if conduit_payoff is not None:
            result.message += promotion_kits.finish_conduit_payoff(
                self.player,
                self.summon,
                self.defender,
                conduit_payoff,
                self._last_combat_result,
            )

        duel_text = self._fail_no_healing_duel_if_healed(hp_before)
        if duel_text:
            result.message = f"{result.message}{duel_text}"
        self._record_failed_enemy_debuff(self.attacker, choice, self.defender, debuff_snapshot)
        if self.attacker == self.player and choice in promotion_kits.INVESTIGATION_SETUP_ACTIONS:
            setup_text = str(result.message).lower()
            setup_success = not any(
                marker in setup_text
                for marker in (
                    "resists",
                    "immune",
                    "no effect",
                    "already",
                    "cannot cast",
                    "not enough mana",
                )
            )
            if debuff_snapshot is not None:
                setup_success = self._debuff_snapshot_gained_effect(
                    debuff_snapshot,
                    self.defender,
                )
            result.message += promotion_kits.record_investigation_setup(
                self.player,
                self.defender,
                str(choice),
                setup_success,
            )
        elif self.attacker != self.player and choice:
            ability = self.attacker.spellbook.get("Skills", {}).get(choice)
            if ability is not None and getattr(ability, "charging", False):
                result.message += promotion_kits.record_visible_telegraph(
                    self.player,
                    self.attacker,
                    visible=self.show_enemy_details(self.attacker),
                )
        if self.attacker != self.player:
            from ...classes import nature_totems

            result.message += nature_totems.record_enemy_miss(
                self.player,
                self.attacker,
                self._last_combat_result,
            )
        if self.attacker == self.player:
            warrior.finish_action(self.player)
            if defender_alive_before and self.defender and not self.defender.is_alive():
                result.message += lycan.record_transformed_kill(self.player)
                promotion_kits.clear_revelation(self.player, self.defender)
            result.message += lycan.record_player_turn(self.player)
            result.message += promotion_kits.record_action_resolution(
                self.player,
                self._last_combat_result,
            )
            result.message += promotion_kits.finish_action(
                self.player,
                defender_survived=bool(self.defender and self.defender.is_alive()),
            )
            result.message += promotion_kits.pop_messages(self.player)
            result.message += promotion_kits.pop_messages(self.defender)

        self.logger.log_event(
            event_type="Action",
            actor=self.attacker,
            target=self.defender,
            action=action,
            outcome=result.message,
            actor_id=self.current_actor_id,
            target_id=self._actor_id_for(self.defender),
        )

        if self.attacker != self.player:
            from ...classes import pathfinder

            pathfinder.record_incoming_action_end(self.player, hp_before)
            state = promotion_kits.combat_state(self.player)
            if int(state.get("winged_pounce_flight", 0) or 0) > 0:
                state["winged_pounce_flight"] = 0
                self.player.flying = bool(state.pop("winged_pounce_previous_flying", False))
            if (
                hp_before >= self.player.health.max * 0.25
                and self.player.health.current < self.player.health.max * 0.25
                and not state.get("lycan_low_hp_checked")
            ):
                state["lycan_low_hp_checked"] = True
                result.message += lycan.maybe_trigger_frenzy(
                    self.player,
                    reason="low_hp",
                )[1]

        return result
