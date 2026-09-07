"""Validated action resolution for the battle engine."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import TYPE_CHECKING

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
