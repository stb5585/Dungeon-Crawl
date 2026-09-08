"""All-enemy action resolution for the battle engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...classes import (
    ability_mechanics,
    astromancer,
    lycan,
    mage_mechanics,
    promotion_kits,
    wizard,
)
from ...events.event_bus import EventType, create_combat_event
from ..combat_result import CombatResult, CombatResultGroup
from ..targeting import TargetScope
from .models import ActionIntent, ActionResult, ActionValidationCode

if TYPE_CHECKING:
    pass


class AreaActionResolutionMixin:
    """Resolve committed actions that target every living enemy."""

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
