"""Validated action resolution for the battle engine."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import TYPE_CHECKING

from ...classes import (
    ability_mechanics,
    astromancer,
    bard,
    lycan,
    mage_mechanics,
    paladin,
    promotion_kits,
    warrior,
    wizard,
)
from ...events.event_bus import EventType, create_combat_event
from ..actor_cycle import PLAYER_ACTOR_ID
from ..combat_result import CombatResult, CombatResultGroup
from ..targeting import TargetScope
from .models import (
    ActionIntent,
    ActionResult,
    ActionValidationCode,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class TurnResolutionMixin:
    """Resolve validated intents and their combat side effects."""

    def execute_intent(
        self,
        intent: ActionIntent,
        *,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """Execute an intent and report terminal resolutions produced by it."""
        mana_before = max(0, int(getattr(self.attacker.mana, "current", 0) or 0))
        result = self._execute_intent(
            intent,
            slot_machine_callback=slot_machine_callback,
        )
        if result.committed:
            barbs = getattr(self.attacker, "mana_barbs", None)
            if isinstance(barbs, dict) and int(barbs.get("turns", 0) or 0) > 0:
                mana_after = max(
                    0,
                    int(getattr(self.attacker.mana, "current", 0) or 0),
                )
                spent = max(0, mana_before - mana_after)
                if spent:
                    self.attacker.health.current -= spent
                    result.message += (
                        f"Mana Barbs deal {spent} damage back to {self.attacker.name}.\n"
                    )
                barbs["turns"] = int(barbs["turns"]) - 1
                if barbs["turns"] <= 0:
                    self.attacker.mana_barbs = None
            result.new_resolutions = self._consume_new_resolution_records()
        return result

    def _execute_intent(
        self,
        intent: ActionIntent,
        *,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """Validate and execute an action for the engine-owned active actor."""
        scope = self._target_scope_for_action(intent.action, intent.choice)
        actor_id = self.current_actor_id or self._actor_id_for(self.attacker)
        targets = self._validated_intent_targets(intent, scope)
        if isinstance(targets, ActionResult):
            return targets
        confused_friendly_fire = False
        if (
            scope == TargetScope.SINGLE_ENEMY
            and actor_id != PLAYER_ACTOR_ID
            and int(getattr(self.attacker, "confused_turns", 0) or 0) > 0
        ):
            self.attacker.confused_turns = max(0, int(self.attacker.confused_turns) - 1)
            allies = [
                member
                for member in self.encounter.living_members
                if member.enemy is not self.attacker
            ]
            if allies and random.random() < 0.50:
                targets = [random.choice(allies)]
                confused_friendly_fire = True
        if scope == TargetScope.ALL_ENEMIES and actor_id != PLAYER_ACTOR_ID:
            return self._reject_intent(
                ActionValidationCode.ENEMY_AREA_UNSUPPORTED,
                "Enemy-authored all-enemy actions are not supported yet.\n",
            )
        self._turn_action_committed = True

        target_ids = tuple(member.combatant_id for member in targets)
        if scope == TargetScope.SELF:
            target_ids = (actor_id or PLAYER_ACTOR_ID,)
        elif (
            scope == TargetScope.SINGLE_ENEMY
            and actor_id != PLAYER_ACTOR_ID
            and not confused_friendly_fire
        ):
            target_ids = (PLAYER_ACTOR_ID,)
        group = CombatResultGroup(
            action=intent.choice or intent.action,
            actor_id=actor_id,
            target_scope=scope,
            target_ids=target_ids,
        )

        if scope == TargetScope.ALL_ENEMIES:
            return self._execute_all_enemy_intent(intent, targets, group)

        member = targets[0] if targets else None
        original_defender = self.defender
        if member is not None:
            self.defender = member.enemy
        elif scope == TargetScope.SELF:
            self.defender = self.attacker
        resolved_target = self.defender
        try:
            with self._target_resolution_context(member, scope, target_ids):
                result = self._execute_committed_action(
                    intent.action,
                    intent.choice,
                    slot_machine_callback,
                )
        finally:
            if member is None:
                self.defender = original_defender

        # Multi-enemy rendering depends on the ledger to distinguish a newly
        # defeated member that should fade out from a merely dead, unresolved
        # combatant. Finalize the target before returning the action so pygame
        # never renders an intermediate "dead but unresolved" frame.
        if len(self.encounter.members) > 1:
            if member is not None and not member.enemy.is_alive():
                resurrection = member.enemy.spellbook.get("Spells", {}).get("Resurrection")
                if (
                    resurrection is not None
                    and abs(member.enemy.health.current) <= member.enemy.mana.current
                ):
                    resurrection_message = resurrection.cast(member.enemy)
                    if resurrection_message:
                        result.message += str(resurrection_message)
            self._record_final_enemy_resolutions()

        target_id = (
            member.combatant_id
            if member
            else (
                actor_id
                if scope == TargetScope.SELF
                else PLAYER_ACTOR_ID if scope == TargetScope.SINGLE_ENEMY else None
            )
        )
        raw_portion = getattr(self, "_last_combat_result", None)
        if isinstance(raw_portion, CombatResult):
            portion = deepcopy(raw_portion)
            portion.action = intent.choice or intent.action
            portion.actor = self.attacker
            portion.target = member.enemy if member else resolved_target
            portion.actor_id = actor_id
            portion.target_id = target_id
            portion.message = result.message
        else:
            portion = CombatResult(
                action=intent.choice or intent.action,
                actor=self.attacker,
                target=member.enemy if member else resolved_target,
                actor_id=actor_id,
                target_id=target_id,
                message=result.message,
            )
        group.add(portion)
        self._event_bus.emit(
            create_combat_event(
                EventType.ACTION_RESULT,
                actor=self.attacker,
                target=portion.target,
                result=portion,
                encounter_id=self.encounter.encounter_id,
                actor_id=actor_id,
                target_id=target_id,
                target_scope=scope.value,
                expanded_target_ids=list(target_ids),
            )
        )
        result.combat_results = group
        if member is not None and actor_id == PLAYER_ACTOR_ID and bool(intent.target_ids):
            self._focus_target_id = member.combatant_id
        return result

    def _execute_all_enemy_intent(
        self,
        intent: ActionIntent,
        targets,
        group: CombatResultGroup,
    ) -> ActionResult:
        """Resolve a committed all-enemy cast in authored order."""
        ability = self._ability_for_action(intent.action, intent.choice)
        if intent.action not in {"Cast Spell", "Use Skill"} or ability is None:
            return self._reject_intent(
                ActionValidationCode.WRONG_TARGET_SCOPE,
                "This all-enemy action has no multi-target resolver.\n",
            )
        effective_cost = (
            mage_mechanics.spell_mana_cost(self.attacker, ability)
            if intent.action == "Cast Spell"
            else ability.cost
        )
        if self.attacker.mana.current < effective_cost:
            message = f"{self.attacker.name} does not have enough mana to cast {intent.choice}!\n"
            group.add(
                CombatResult(
                    action=intent.choice or intent.action,
                    actor=self.attacker,
                    actor_id=self.current_actor_id,
                    message=message,
                )
            )
            return ActionResult(message=message, combat_results=group)

        threaded_message = ""
        if self.attacker == self.player and intent.action == "Cast Spell":
            _thread_count, threaded_message = astromancer.begin_threaded_spell(
                self.player,
                ability,
            )
        if self.attacker == self.player:
            threaded_message += promotion_kits.prepare_stolen_charge_payoff(
                self.player,
                intent.action,
                ability,
            )

        hp_before = self.player.health.current
        if self._member_for_character(self.attacker) is not None:
            from ...classes import pathfinder

            pathfinder.record_incoming_action_start(self.player)
            promotion_kits.begin_incoming_action(
                self.player,
                round_number=self.round_number,
                actor=self.attacker,
            )
        if self.attacker == self.player:
            ability_mechanics.store_rewind_snapshot(self)
            promotion_kits.begin_action(
                self.player,
                defer_devotion=True,
                action=intent.action,
                choice=intent.choice,
                round_number=self.round_number,
            )
        event_type = EventType.SPELL_CAST if intent.action == "Cast Spell" else EventType.SKILL_USE
        self._event_bus.emit(
            create_combat_event(
                event_type,
                actor=self.attacker,
                target=targets[0].enemy if targets else None,
                **(
                    {"spell_name": intent.choice}
                    if intent.action == "Cast Spell"
                    else {"skill_name": intent.choice}
                ),
                ability_name=intent.choice,
                source="spell" if intent.action == "Cast Spell" else "skill",
                encounter_id=self.encounter.encounter_id,
                actor_id=self.current_actor_id,
                target_scope=TargetScope.ALL_ENEMIES.value,
                expanded_target_ids=list(group.target_ids),
            )
        )
        verb = "casts" if intent.action == "Cast Spell" else "uses"
        prefix = f"{self.attacker.name} {verb} {intent.choice}.\n{threaded_message}"
        group.message = prefix
        group_resolver = getattr(
            ability,
            "cast_group" if intent.action == "Cast Spell" else "use_group",
            None,
        )
        try:
            if callable(group_resolver):
                resolved = group_resolver(
                    self.attacker,
                    [(member.combatant_id, member.enemy) for member in targets],
                    battle_engine=self,
                )
                for portion in resolved.results:
                    group.add(portion)
                    self._event_bus.emit(
                        create_combat_event(
                            EventType.ACTION_RESULT,
                            actor=self.attacker,
                            target=portion.target,
                            result=portion,
                            encounter_id=self.encounter.encounter_id,
                            actor_id=self.current_actor_id,
                            target_id=portion.target_id,
                            target_scope=TargetScope.ALL_ENEMIES.value,
                            expanded_target_ids=list(group.target_ids),
                        )
                    )
            else:
                ability_result = ability.cast(
                    self.attacker,
                    target=targets[0].enemy if targets else None,
                    targets=[member.enemy for member in targets],
                    battle_engine=self,
                )
                for member in targets:
                    group.add(
                        CombatResult(
                            action=intent.choice or intent.action,
                            actor=self.attacker,
                            target=member.enemy,
                            actor_id=self.current_actor_id,
                            target_id=member.combatant_id,
                            message=str(ability_result) if member is targets[0] else "",
                        )
                    )
        finally:
            astromancer.clear_threaded_spell(self.attacker)
        self._record_final_enemy_resolutions()
        if self.attacker == self.player:
            primary_target = targets[0].enemy if targets else None
            if intent.action == "Cast Spell":
                from ...classes import healer

                if "Holy" in {
                    str(getattr(ability, "subtyp", "")),
                    str(getattr(ability, "school", "")),
                }:
                    group.message += healer.flash_blindness(
                        self.player,
                        [member.enemy for member in self.encounter.living_members],
                    )
                group.message += wizard.process_cast(
                    self.player,
                    ability,
                    primary_target,
                )
                group.message += astromancer.record_thread_action(
                    self.player,
                    intent.choice or "",
                    successful=any(
                        astromancer.spell_resolution_succeeded(portion, ability)
                        for portion in group.results
                    ),
                )
                if len(self.encounter.members) == 1 and targets:
                    member = targets[0]
                    if not member.enemy.is_alive():
                        with self._target_resolution_context(
                            member,
                            TargetScope.ALL_ENEMIES,
                            group.target_ids,
                        ):
                            group.message += self._record_player_natural_spell_kill(ability)
                if astromancer.is_astromancer(self.player) and astromancer.sign_for_spell(ability):
                    astromancer.advance_constellation(self.player)
            group.message += promotion_kits.record_action_resolution(
                self.player,
                group,
            )
            for member in targets:
                if not member.enemy.is_alive():
                    promotion_kits.clear_revelation(self.player, member.enemy)
            group.message += promotion_kits.finish_action(
                self.player,
                defender_survived=bool(self.encounter.living_members),
            )
            if any(not member.enemy.is_alive() for member in targets):
                group.message += lycan.record_transformed_kill(self.player)
            group.message += lycan.record_player_turn(self.player)
            group.message += promotion_kits.pop_messages(self.player)
            for member in targets:
                group.message += promotion_kits.pop_messages(member.enemy)
        elif intent.action == "Cast Spell":
            learned_result = next(
                (
                    portion
                    for portion in group.results
                    if astromancer.spell_resolution_succeeded(portion, ability)
                ),
                None,
            )
            if learned_result is not None:
                group.message += astromancer.learn_witnessed_spell(
                    self.player,
                    ability,
                    learned_result,
                )
        duel_text = self._fail_no_healing_duel_if_healed(hp_before)
        if duel_text:
            group.message += duel_text
        result = ActionResult(message=group.message, combat_results=group)
        self.logger.log_event(
            "Action",
            self.attacker,
            target=targets[0].enemy if targets else None,
            action=intent.action,
            outcome=result.message,
            actor_id=self.current_actor_id,
            target_id=targets[0].combatant_id if targets else None,
        )
        return result

    def _execute_committed_action(
        self,
        action: str,
        choice: str | None = None,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """
        Execute a validated combat action for the current attacker.

        Args:
            action: The action type string (Attack, Cast Spell, Use Skill, etc.)
            choice: The specific spell/skill/item name (when applicable).
            slot_machine_callback: Optional UI callback for Slot Machine animation.

        Returns:
            ActionResult with the message text and status flags.
        """
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

        # Log the action
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

    def _tunneled_action_blocked(self, action: str, choice: str | None) -> bool:
        if not getattr(self.attacker, "tunnel", False):
            return False
        if action in {"Recall", "Support", "Nothing", "Cancelled"}:
            return False
        if action == "Use Skill" and choice == "Surface":
            return False
        return action in {"Attack", "Cast Spell", "Use Skill"}

    @staticmethod
    @staticmethod
    def _debuff_state_snapshot(actor, ability_name: str | None, target) -> dict | None:
        rules = getattr(actor, "_DEBUFF_REAPPLY_RULES", None)
        if not ability_name or not isinstance(rules, dict) or target is None:
            return None
        rule = rules.get(ability_name)
        if not rule:
            return None

        snapshot = {"rule": rule}
        status_name = rule.get("status")
        if status_name:
            effect = getattr(target, "status_effects", {}).get(status_name)
            snapshot["status"] = bool(getattr(effect, "active", False))

        physical_name = rule.get("physical")
        if physical_name:
            effect = getattr(target, "physical_effects", {}).get(physical_name)
            snapshot["physical"] = bool(getattr(effect, "active", False))

        stat_all = rule.get("stat_all")
        if stat_all:
            stat_effects = getattr(target, "stat_effects", {})
            snapshot["stats"] = {
                stat_name: bool(getattr(stat_effects.get(stat_name), "active", False))
                for stat_name in stat_all
            }
        return snapshot

    @staticmethod
    @staticmethod
    def _debuff_snapshot_gained_effect(snapshot: dict | None, target) -> bool:
        if not snapshot or target is None:
            return True
        rule = snapshot.get("rule", {})

        status_name = rule.get("status")
        if status_name:
            effect = getattr(target, "status_effects", {}).get(status_name)
            return bool(getattr(effect, "active", False)) and not snapshot.get("status", False)

        physical_name = rule.get("physical")
        if physical_name:
            effect = getattr(target, "physical_effects", {}).get(physical_name)
            return bool(getattr(effect, "active", False)) and not snapshot.get("physical", False)

        stat_all = rule.get("stat_all")
        if stat_all:
            before = snapshot.get("stats", {})
            stat_effects = getattr(target, "stat_effects", {})
            return any(
                bool(getattr(stat_effects.get(stat_name), "active", False))
                and not before.get(stat_name, False)
                for stat_name in stat_all
            )
        return True

    def _record_failed_enemy_debuff(
        self, actor, ability_name: str | None, target, snapshot: dict | None
    ) -> None:
        if snapshot is None or self._member_for_character(actor) is None:
            return
        if self._debuff_snapshot_gained_effect(snapshot, target):
            return
        record_failure = getattr(actor, "record_debuff_failure", None)
        if callable(record_failure):
            record_failure(str(ability_name), turns=2)
