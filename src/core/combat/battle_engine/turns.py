"""Battle turn preparation, execution flow, and lifecycle handling."""

from __future__ import annotations

from copy import deepcopy
import math
import random
from typing import TYPE_CHECKING

from ...classes import (
    ability_mechanics,
    astromancer,
    bard,
    lycan,
    mage_mechanics,
    nature_totems,
    paladin,
    promotion_kits,
    warrior,
    wizard,
)
from ...events.event_bus import combat_event_context, EventType, create_combat_event
from ..actor_cycle import PLAYER_ACTOR_ID
from ..combat_result import CombatResult, CombatResultGroup
from ..encounter import EnemyResolution
from ..targeting import TargetScope
from .models import (
    ActionIntent,
    ActionResult,
    ActionValidationCode,
    BattleOutcome,
    ForcedAction,
    LootAward,
    PostTurnResult,
    PreTurnResult,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from ...character import Character


class BattleTurnMixin:
    @staticmethod
    def _clear_stale_charging_actions(character: Character) -> None:
        """Clear charge state that should never persist across battles."""
        if hasattr(character, "class_effects") and "Jump" in character.class_effects:
            character.class_effects["Jump"].active = False

        for skill_group in getattr(character, "spellbook", {}).values():
            for skill in getattr(skill_group, "values", lambda: [])():
                if not getattr(skill, "charging", False):
                    continue
                skill.charging = False
                if hasattr(skill, "charge_turns"):
                    skill.charge_turns = 0
                if hasattr(skill, "charge_target"):
                    skill.charge_target = None

    def pre_turn(self) -> PreTurnResult:
        """
        Process the attacker's start-of-turn effects and check activity.

        Call this at the beginning of each turn before requesting an action.
        """
        result = PreTurnResult()

        # Capture activity before ticking durations so single-turn control-loss
        # effects still consume the current turn when they expire this tick.
        active_at_turn_start, inactive_reason_at_turn_start = self.attacker.check_active()

        hp_before = self.player.health.current if self.attacker == self.player else 0

        # Process status effects (poison ticks, bleed, regen, etc.)
        with combat_event_context(
            encounter_id=self.encounter.encounter_id,
            actor_id=self.current_actor_id,
            target_id=self.current_actor_id,
            target_scope=TargetScope.SELF.value,
            expanded_target_ids=[self.current_actor_id],
        ):
            effects_text = self.attacker.effects()
        if effects_text:
            result.effects_text = effects_text

            # Handle exploding shield (Crusader Power Up expiring deals damage)
            if "damage" in effects_text:
                try:
                    dmg = int(effects_text.split(" damage")[0].split(" ")[-1])
                    self.defender.health.current -= dmg
                    result.shield_explosion_damage = dmg
                except (ValueError, IndexError):
                    pass
        enemy_member = self._member_for_character(self.attacker)
        if enemy_member is not None:
            thirst_text = ability_mechanics.trigger_hemorrhage_thirst(
                self.player,
                getattr(self.attacker, "_last_bleed_tick_damage", 0),
            )
            if thirst_text:
                result.effects_text = f"{result.effects_text or ''}{thirst_text}"

        if self.attacker == self.player:
            song_text = bard.tick_song(self.player)
            if song_text:
                result.effects_text = f"{result.effects_text or ''}{song_text}"
            frenzy_text = lycan.tick_frenzy(self.player)
            if frenzy_text:
                result.effects_text = f"{result.effects_text or ''}{frenzy_text}"

        if self.attacker == self.player:
            duel_text = self._fail_no_healing_duel_if_healed(hp_before)
            if duel_text:
                result.effects_text = f"{result.effects_text or ''}{duel_text}"
                result.died_from_effects = True
                result.can_act = False
                return result

        # Check if the attacker died from their own effects
        if not self.attacker.is_alive():
            result.died_from_effects = True
            result.can_act = False
            return result

        if enemy_member is not None:
            active_chorus = bard.active_song(self.player) == "Chorus Time"
            dumbfounded = (
                bard.chorus_time_dumbfounds(
                    self.player,
                    self.attacker,
                    rng=random,
                )
                if active_chorus
                else bard.consume_chorus_time_coda(
                    self.player,
                    self.attacker,
                    rng=random,
                )
            )
            if dumbfounded:
                result.effects_text = (
                    f"{result.effects_text or ''}{self.attacker.name} is "
                    "dumbfounded by Chorus Time and loses the turn.\n"
                )
                result.can_act = False
                result.inactive_reason = "Dumbfounded by Chorus Time."
                return result

        if not active_at_turn_start:
            interrupted = self._cancel_interrupted_charging_action()
            if interrupted:
                result.effects_text = f"{result.effects_text or ''}{interrupted}"
            if self.attacker == self.player:
                vow_text = paladin.on_incapacitated(self.player)
                if vow_text:
                    result.effects_text = f"{result.effects_text or ''}{vow_text}"
            result.can_act = False
            result.inactive_reason = self._inactive_reason_after_effects(
                inactive_reason_at_turn_start,
                result.effects_text,
            )
            return result

        # Check if the attacker can act this turn
        active, text = self.attacker.check_active()
        if not active:
            result.can_act = False
            result.inactive_reason = text

        return result

    @staticmethod
    @staticmethod
    def _inactive_reason_after_effects(reason: str, effects_text: str) -> str:
        """Suppress stale incapacity text when the logged status tick already explains recovery."""
        recovery_terms = (
            "is no longer stunned",
            "is no longer asleep",
            "is no longer prone",
            "returns to their true form",
        )
        effects_lower = (effects_text or "").lower()
        if any(term in effects_lower for term in recovery_terms):
            return ""
        return reason

    def _cancel_interrupted_charging_action(self) -> str:
        """Cancel active charge-up actions when the actor is incapacitated before acting."""
        if not self.attacker or not self.attacker.incapacitated():
            return ""

        if self.attacker.class_effects["Jump"].active:
            skills = self.attacker.spellbook.get("Skills", {})
            jump_choice = next((name for name in skills if "Jump" in name), None)
            jump_skill = skills.get(jump_choice) if jump_choice else None
            unstoppable = bool(getattr(jump_skill, "modifications", {}).get("Unstoppable", False))
            if unstoppable:
                return ""
            try:
                cancel_msg = jump_skill.cancel_charge(self.attacker) if jump_skill else ""
            except AttributeError:
                cancel_msg = ""
            self.attacker.class_effects["Jump"].active = False
            return cancel_msg or f"{self.attacker.name}'s Jump was cancelled.\n"

        for _skill_name, skill in self.attacker.spellbook.get("Skills", {}).items():
            if getattr(skill, "charging", False):
                try:
                    return skill.cancel_charge(self.attacker)
                except AttributeError:
                    skill.charging = False
                    return f"{self.attacker.name}'s {getattr(skill, 'name', 'charge')} was interrupted!\n"
        return ""

    def get_forced_action(self) -> ForcedAction | None:
        """
        Check if the current attacker's action is forced.

        Returns a ForcedAction when the attacker must perform a specific action
        (berserk, charging skill, jump), or None when the actor has free choice.
        """
        # Jump in progress. Resolve the airborne/charging state before Berserk
        # can force a basic attack, especially when Unstoppable is active.
        if self.attacker.class_effects["Jump"].active:
            skills = self.attacker.spellbook.get("Skills", {})
            jump_choice = next((name for name in skills if "Jump" in name), None)
            jump_skill = skills.get(jump_choice) if jump_choice else None
            unstoppable = bool(getattr(jump_skill, "modifications", {}).get("Unstoppable", False))

            if self.attacker.incapacitated() and not unstoppable:
                # Cancel the jump if incapacitated during charge.
                try:
                    cancel_msg = jump_skill.cancel_charge(self.attacker) if jump_skill else ""
                except AttributeError:
                    cancel_msg = ""
                if not cancel_msg:
                    cancel_msg = f"{self.attacker.name}'s Jump was cancelled.\n"
                self.attacker.class_effects["Jump"].active = False
                return ForcedAction(action="Cancelled", cancel_message=cancel_msg)

            if jump_choice:
                self.attacker.class_effects["Jump"].active = False
                return ForcedAction(action="Use Skill", choice=jump_choice)

        # Ongoing charging ability (e.g. Charge, Crushing Blow, Dragon Breath).
        for skill_name, skill in self.attacker.spellbook.get('Skills', {}).items():
            if getattr(skill, 'charging', False):
                return ForcedAction(action="Use Skill", choice=skill_name)

        if self.charging_ability:
            charge_owner, ability_name, _skill_obj = self.charging_ability
            if charge_owner == self.attacker:
                return ForcedAction(action="Use Skill", choice=ability_name)

        # Berserk forces a basic attack unless a higher-priority forced action
        # such as an active Jump or charge-up has already claimed the turn.
        berserk = self.attacker.status_effects["Berserk"]
        composed_wrath = (
            getattr(berserk, "source", None) == "Frenzy"
            and "Composed Wrath" in self.attacker.spellbook.get("Skills", {})
        )
        if berserk.active and not composed_wrath:
            return ForcedAction(action="Attack")

        return None

    def get_enemy_action(self) -> tuple[str, str | None]:
        """Ask the enemy AI for its chosen action. Returns (action, choice)."""
        try:
            return self.attacker.options(
                self.active_player_character,
                self.available_actions,
                self.tile,
            )
        except Exception:
            return "Attack", None

    def is_player_turn(self) -> bool:
        """Return True if the current attacker is the player (or summon)."""
        return self.attacker == self.player or self.attacker == self.summon

    # ── Action execution ─────────────────────────────────────────────

    def execute_action(
        self,
        action: str,
        choice: str | None = None,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """Compatibility adapter for callers that do not construct intents."""
        scope = self._target_scope_for_action(action, choice)
        target_ids: tuple[str, ...] = ()
        player_side = (
            self.current_actor_id == PLAYER_ACTOR_ID
            or (self.current_actor_id is None and self.is_player_turn())
        )
        if (
            scope == TargetScope.SINGLE_ENEMY
            and player_side
            and len(self.encounter.members) == 1
            and len(self.encounter.living_members) == 1
        ):
            target_ids = (self.encounter.living_members[0].combatant_id,)
        elif scope == TargetScope.SINGLE_ENEMY and player_side:
            pending = self.pending_actions.get(PLAYER_ACTOR_ID)
            if pending:
                target_id = pending.get("target_id")
                try:
                    member = self.encounter.member_by_id(target_id)
                except KeyError:
                    member = None
                policy = pending.get("policy")
                if member is not None and member.is_living_hostile:
                    target_ids = (member.combatant_id,)
                elif getattr(policy, "value", policy) == "retarget_focus":
                    self._refresh_focus()
                    if self.encounter.living_members:
                        member = self.encounter.member_by_id(self._focus_target_id)
                        target_ids = (member.combatant_id,)
                        skill = pending.get("ability")
                        if skill is not None and hasattr(skill, "charge_target"):
                            skill.charge_target = member.enemy
                else:
                    skill = pending.get("ability")
                    if skill is not None:
                        skill.charging = False
                        if hasattr(skill, "charge_turns"):
                            skill.charge_turns = 0
                        if hasattr(skill, "charge_target"):
                            skill.charge_target = None
                    self.pending_actions.pop(PLAYER_ACTOR_ID, None)
                    message = (
                        f"{getattr(skill, 'name', 'The charged action')} fizzles "
                        "because its locked target is gone.\n"
                    )
                    group = CombatResultGroup(
                        action=getattr(skill, "name", action),
                        actor_id=PLAYER_ACTOR_ID,
                        target_scope=TargetScope.SINGLE_ENEMY,
                        message=message,
                    )
                    return ActionResult(message=message, combat_results=group)
            elif self.attacker.status_effects["Berserk"].active:
                self._refresh_focus()
                if self.encounter.living_members:
                    target_ids = (self._focus_target_id,)
        return self.execute_intent(
            ActionIntent(action=action, choice=choice, target_ids=target_ids),
            slot_machine_callback=slot_machine_callback,
        )

    def _ability_for_action(self, action: str, choice: str | None):
        if not choice:
            return None
        if action in {"Cast Spell", "Runic Boost"}:
            return self.attacker.spellbook.get("Spells", {}).get(choice)
        if action in {"Use Skill", "Tame"}:
            return self.attacker.spellbook.get("Skills", {}).get(
                choice if action == "Use Skill" else "Tame"
            )
        return None

    def _target_scope_for_action(
        self,
        action: str,
        choice: str | None,
    ) -> TargetScope:
        """Derive the canonical target scope for a legacy action."""
        if action in {
            "Nothing",
            "Cancelled",
            "Pickup Weapon",
            "Flee",
            "Recall",
            "Companion",
            "Repertoire",
            "Totem",
            "Transform",
            "Untransform",
            "Dismiss Form",
        }:
            return TargetScope.NONE
        if action in {"Defend", "Summon"}:
            return TargetScope.SELF
        if action == "Use Item":
            if choice:
                import re

                item_key = re.split(r"\s{2,}", choice)[0]
                items = self.attacker.inventory.get(item_key, [])
                item = items[0] if items else None
                if isinstance(item, type):
                    item = item()
                spell = getattr(item, "spell", None)
                if (
                    getattr(item, "subtyp", None) == "Scroll"
                    and getattr(spell, "subtyp", None) != "Support"
                ):
                    return TargetScope.SINGLE_ENEMY
            return TargetScope.SELF
        ability = self._ability_for_action(action, choice)
        if ability is not None:
            declared = getattr(ability, "target_scope", TargetScope.SINGLE_ENEMY)
            if (
                declared == TargetScope.ALL_ENEMIES
                and self.attacker != self.player
                and getattr(ability, "name", "") in {
                    "Photon Sphere",
                    "Prismatic Cataclysm",
                }
            ):
                # Enemy AI still has a single player-side target. The player
                # version expands across the hostile encounter roster.
                return TargetScope.SINGLE_ENEMY
            raw_data = getattr(ability, "_raw_data", {})
            if isinstance(raw_data, dict) and "target_scope" in raw_data:
                return declared
            if declared in {TargetScope.NONE, TargetScope.ALL_ENEMIES}:
                return declared
            if getattr(ability, "passive", False):
                return TargetScope.NONE
            if (
                getattr(ability, "subtyp", None) in {"Heal", "Support"}
                or getattr(ability, "self_target", False)
            ):
                return TargetScope.SELF
            return declared
        return TargetScope.SINGLE_ENEMY

    def target_scope_for_action(
        self,
        action: str,
        choice: str | None = None,
    ) -> TargetScope:
        """Return the canonical target scope for a prospective action."""
        return self._target_scope_for_action(action, choice)

    def _reject_intent(
        self,
        code: ActionValidationCode,
        message: str,
    ) -> ActionResult:
        self._turn_action_committed = False
        return ActionResult(
            message=message,
            committed=False,
            validation_code=code,
            combat_results=CombatResultGroup(message=message),
        )

    def _validated_intent_targets(
        self,
        intent: ActionIntent,
        scope: TargetScope,
    ):
        supplied = intent.target_ids
        if scope in {TargetScope.NONE, TargetScope.SELF, TargetScope.ALL_ENEMIES}:
            if supplied:
                return self._reject_intent(
                    ActionValidationCode.WRONG_TARGET_SCOPE,
                    f"{scope.value} actions do not accept explicit target IDs.\n",
                )
            if scope == TargetScope.ALL_ENEMIES:
                return list(self.encounter.living_members)
            return []

        player_side = (
            self.current_actor_id == PLAYER_ACTOR_ID
            or (self.current_actor_id is None and self.is_player_turn())
        )
        if not player_side:
            if supplied:
                return self._reject_intent(
                    ActionValidationCode.WRONG_TARGET_SCOPE,
                    "Enemy actions target the active player-side combatant.\n",
                )
            return []
        if not supplied:
            return self._reject_intent(
                ActionValidationCode.MISSING_TARGET,
                "Choose one enemy target.\n",
            )
        if len(supplied) != 1:
            return self._reject_intent(
                ActionValidationCode.WRONG_TARGET_COUNT,
                "Single-enemy actions require exactly one target.\n",
            )
        try:
            member = self.encounter.member_by_id(supplied[0])
        except KeyError:
            return self._reject_intent(
                ActionValidationCode.UNKNOWN_TARGET,
                "That target is not part of this encounter.\n",
            )
        if not member.is_living_hostile:
            return self._reject_intent(
                ActionValidationCode.UNAVAILABLE_TARGET,
                "That target is dead or has already left the encounter.\n",
            )
        return [member]

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
                        f"Mana Barbs deal {spent} damage back to "
                        f"{self.attacker.name}.\n"
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
                resurrection = member.enemy.spellbook.get("Spells", {}).get(
                    "Resurrection"
                )
                if (
                    resurrection is not None
                    and abs(member.enemy.health.current) <= member.enemy.mana.current
                ):
                    resurrection_message = resurrection.cast(member.enemy)
                    if resurrection_message:
                        result.message += str(resurrection_message)
            self._record_final_enemy_resolutions()

        target_id = member.combatant_id if member else (
            actor_id
            if scope == TargetScope.SELF
            else PLAYER_ACTOR_ID
            if scope == TargetScope.SINGLE_ENEMY
            else None
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
        self._event_bus.emit(create_combat_event(
            EventType.ACTION_RESULT,
            actor=self.attacker,
            target=portion.target,
            result=portion,
            encounter_id=self.encounter.encounter_id,
            actor_id=actor_id,
            target_id=target_id,
            target_scope=scope.value,
            expanded_target_ids=list(target_ids),
        ))
        result.combat_results = group
        if (
            member is not None
            and actor_id == PLAYER_ACTOR_ID
            and bool(intent.target_ids)
        ):
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
            message = (
                f"{self.attacker.name} does not have enough mana to cast "
                f"{intent.choice}!\n"
            )
            group.add(CombatResult(
                action=intent.choice or intent.action,
                actor=self.attacker,
                actor_id=self.current_actor_id,
                message=message,
            ))
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
        if self.attacker != self.player:
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
        event_type = (
            EventType.SPELL_CAST
            if intent.action == "Cast Spell"
            else EventType.SKILL_USE
        )
        self._event_bus.emit(create_combat_event(
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
        ))
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
                    self._event_bus.emit(create_combat_event(
                        EventType.ACTION_RESULT,
                        actor=self.attacker,
                        target=portion.target,
                        result=portion,
                        encounter_id=self.encounter.encounter_id,
                        actor_id=self.current_actor_id,
                        target_id=portion.target_id,
                        target_scope=TargetScope.ALL_ENEMIES.value,
                        expanded_target_ids=list(group.target_ids),
                    ))
            else:
                ability_result = ability.cast(
                    self.attacker,
                    target=targets[0].enemy if targets else None,
                    targets=[member.enemy for member in targets],
                    battle_engine=self,
                )
                for member in targets:
                    group.add(CombatResult(
                        action=intent.choice or intent.action,
                        actor=self.attacker,
                        target=member.enemy,
                        actor_id=self.current_actor_id,
                        target_id=member.combatant_id,
                        message=str(ability_result) if member is targets[0] else "",
                    ))
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
                            group.message += self._record_player_natural_spell_kill(
                                ability
                            )
                if (
                    astromancer.is_astromancer(self.player)
                    and astromancer.sign_for_spell(ability)
                ):
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

        if self._tunneled_action_blocked(action, choice):
            result.message = f"{self.attacker.name} must surface before doing that.\n"
            return result

        debuff_snapshot = self._debuff_state_snapshot(self.attacker, choice, self.defender)

        if (
            action == "Attack"
            and getattr(self.attacker, "magic_effects", {}).get("Tree of Life")
            and self.attacker.magic_effects["Tree of Life"].active
        ):
            result.message = f"{self.attacker.name} is rooted as the Tree of Life and cannot attack.\n"
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
                    result.message = (
                        f"{self.attacker.name} cannot transform into {choice}.\n"
                    )
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
                self.player.flying = bool(
                    state.pop("winged_pounce_previous_flying", False)
                )
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

    def _record_failed_enemy_debuff(self, actor, ability_name: str | None, target, snapshot: dict | None) -> None:
        if snapshot is None or self._member_for_character(actor) is None:
            return
        if self._debuff_snapshot_gained_effect(snapshot, target):
            return
        record_failure = getattr(actor, "record_debuff_failure", None)
        if callable(record_failure):
            record_failure(str(ability_name), turns=2)

    def companion_turn(self) -> str:
        """Process the attacker's familiar/companion turn. Returns message text."""
        undead_text = ""
        allies = list(getattr(self.attacker, "temporary_undead_allies", []))
        if allies and self.defender is not None and self.defender.is_alive():
            remaining = []
            for ally in allies:
                damage = min(self.defender.health.current, int(ally.get("damage", 1) or 1))
                self.defender.health.current -= damage
                undead_text += f"Undead {ally['name']} attacks {self.defender.name} for {damage} damage.\n"
                ally["turns"] = int(ally.get("turns", 0) or 0) - 1
                if ally["turns"] > 0:
                    remaining.append(ally)
            self.attacker.temporary_undead_allies = remaining
        if self.current_actor_id == PLAYER_ACTOR_ID and self.encounter.living_members:
            focused = self._focused_enemy()
            if (
                self._member_for_character(self.defender) is None
                or not self._member_for_character(self.defender).is_living_hostile
            ):
                self.defender = focused
        if (
            self.defender is None
            or not self.defender.is_alive()
            or getattr(self.defender, "tamed_by_player", False)
            or getattr(self.defender, "no_victory_rewards", False)
        ):
            return undead_text
        familiar_text = self.attacker.familiar_turn(self.defender)
        if familiar_text:
            self.logger.log_event(
                "Familiar", self.attacker, target=self.defender, outcome=familiar_text
            )
        return undead_text + (familiar_text or "")

    def _tick_delayed_spells(self) -> list[str]:
        messages: list[str] = []
        remaining: list[dict[str, Any]] = []
        for entry in self.delayed_spells:
            if entry.get("owner_id") not in {None, self.current_actor_id}:
                remaining.append(entry)
                continue
            if entry.pop("skip_next_owner_tick", False):
                remaining.append(entry)
                continue
            entry["turns"] = int(entry.get("turns", 0) or 0) - 1
            if entry["turns"] > 0:
                remaining.append(entry)
                continue
            caster = entry.get("caster")
            spell = entry.get("spell")
            if caster is None or spell is None:
                continue
            target_id = entry.get("target_id")
            try:
                member = self.encounter.member_by_id(target_id) if target_id else None
            except KeyError:
                member = None
            if member is not None and member.is_living_hostile:
                target = member.enemy
            elif len(self.encounter.members) == 1 and self.encounter.living_members:
                target = self.encounter.primary_enemy
            else:
                messages.append(
                    f"{getattr(spell, 'name', 'A delayed spell')} emerges, "
                    "but its locked target is gone.\n"
                )
                continue
            messages.append(f"{getattr(spell, 'name', 'A delayed spell')} emerges from the wormhole.\n")
            with self._target_resolution_context(
                member,
                TargetScope.SINGLE_ENEMY,
                (member.combatant_id,) if member else (),
            ):
                messages.append(str(self._cast_spell_with_context(spell, caster, target)))
        self.delayed_spells = remaining
        return messages

    def post_turn(self) -> PostTurnResult:
        """
        Process end-of-turn logic: special effects, summon state, resurrection.

        Call after execute_action and companion_turn.
        """
        result = PostTurnResult()
        if not self._turn_action_committed:
            return result

        if not self.flee:
            # Defender's passive special effects (e.g. thorns, counter-attack)
            special = self.defender.special_effects(self.attacker)
            if special:
                result.messages.append(special)
                self.logger.log_event(
                    "Special Effect", self.defender, target=self.attacker, outcome=special
                )

            delayed_messages = self._tick_delayed_spells()
            if delayed_messages:
                result.messages.extend(delayed_messages)

            # Refresh available actions
            self.available_actions = self._available_actions()

            if self.attacker == self.player and self.encounter.living_members:
                self._refresh_focus()
                focus_enemy = self.encounter.member_by_id(self._focus_target_id).enemy
                pulse_msg = nature_totems.resolve_totem_pulse(self.player, focus_enemy)
                if pulse_msg:
                    result.messages.append(pulse_msg)
                resonance_msg = promotion_kits.pop_messages(self.player)
                if resonance_msg:
                    result.messages.append(resonance_msg)
                from ...classes import mage_mechanics

                companion_message = mage_mechanics.transient_companion_action(
                    self.player,
                    [member.enemy for member in self.encounter.living_members],
                )
                if companion_message:
                    result.messages.append(companion_message)
                    self._record_final_enemy_resolutions()
                crystal = getattr(self.player, "floating_crystal", None)
                if isinstance(crystal, dict) and self.encounter.living_members:
                    maximum_mana = max(
                        1,
                        int(getattr(self.player.mana, "max", 1) or 1),
                    )
                    miracle = bool(crystal.get("miracle", False))
                    if miracle:
                        siphoned = max(
                            1,
                            int(crystal.get("generated_per_turn", 1) or 1),
                        )
                    else:
                        siphon_percent = max(
                            0.0,
                            float(crystal.get("siphon_percent", 0.10) or 0.10),
                        )
                        siphoned = min(
                            max(1, math.ceil(maximum_mana * siphon_percent)),
                            max(0, int(self.player.mana.current)),
                        )
                        self.player.mana.current -= siphoned
                    crystal["mana"] = int(crystal.get("mana", 0) or 0) + siphoned
                    if int(crystal["mana"]) >= int(crystal.get("threshold", 30) or 30):
                        target = self.encounter.living_members[0].enemy
                        spell_power = max(
                            0,
                            int(self.player.check_mod("magic", enemy=target)),
                        )
                        damage = max(
                            1,
                            int(
                                int(crystal["mana"])
                                * (1.0 + spell_power / 100.0)
                            ),
                        )
                        targets = (
                            [member.enemy for member in self.encounter.living_members]
                            if miracle
                            else [target]
                        )
                        for crystal_target in targets:
                            crystal_target.health.current -= damage
                        if miracle:
                            names = ", ".join(target.name for target in targets)
                            result.messages.append(
                                f"The miraculous crystal creates {crystal['mana']} "
                                f"MP from nothing and ruptures reality for {damage} "
                                f"damage to every enemy ({names}).\n"
                            )
                        else:
                            result.messages.append(
                                f"The floating crystal amplifies {crystal['mana']} "
                                f"stored MP with {spell_power} spell power and "
                                f"explodes for {damage} damage to {target.name}.\n"
                            )
                        self.player.floating_crystal = None
                        self._record_final_enemy_resolutions()
                    elif siphoned:
                        result.messages.append(
                            (
                                f"The miraculous crystal creates {siphoned} MP "
                                f"from nothing ({crystal['mana']}/"
                                f"{crystal.get('threshold', 30)}).\n"
                            )
                            if miracle
                            else f"The floating crystal siphons {siphoned} MP "
                            f"({crystal['mana']}/{crystal.get('threshold', 30)}).\n"
                        )

            # Manage summon state
            if self.summon_active:
                if self.summon and self.summon.is_alive():
                    if "Recall" not in self.available_actions:
                        self.available_actions.append("Recall")
                else:
                    msg = f"{self.summon.name} has been slain.\n" if self.summon else ""
                    if self.summon is not None:
                        msg += promotion_kits.record_xenid_death(
                            self.player,
                            self.summon.name,
                        )
                    result.messages.append(msg)
                    result.summon_died = True
                    self.summon_active = False
                    self.player.active_summon_name = None
                    self.summon = None
                    self.defender = self.player

            # Check defender resurrection (e.g. Resurrection spell)
            if not self.defender.is_alive():
                result.defender_died = True
                if 'Resurrection' in self.defender.spellbook.get('Spells', {}):
                    res_spell = self.defender.spellbook['Spells']['Resurrection']
                    if abs(self.defender.health.current) <= self.defender.mana.current:
                        res_msg = res_spell.cast(self.defender)
                        if res_msg:
                            result.messages.append(res_msg)
                            result.resurrected = True

                # Behemoth death special (Meteor on death)
                if self.defender.name == "Behemoth":
                    special = self.defender.special_effects(self.attacker)
                    if special:
                        result.messages.append(special)

            if (
                self._member_for_character(self.attacker) is not None
                and self.defender == self.player
            ):
                riposte = paladin.resolve_riposte(self.player, self.attacker)
                if riposte:
                    result.messages.append(riposte)

        self._record_final_enemy_resolutions()
        result.new_resolutions = self._consume_new_resolution_records()
        paladin.tick_turn(self.player)
        if self.defender == self.player and self.player.is_alive():
            hp_max = max(1, int(self.player.health.max or 1))
            if self.player.health.current / hp_max <= 0.25:
                triggered, frenzy_msg = lycan.maybe_trigger_frenzy(self.player, reason="low_hp")
                if triggered:
                    result.messages.append(frenzy_msg)
        paladin.clear_transient_marks(self.player)
        self._event_bus.emit(create_combat_event(
            EventType.TURN_END,
            actor=self.attacker,
            target=self.defender,
            encounter_id=self.encounter.encounter_id,
            actor_id=self.current_actor_id,
            round=self.round_number,
            actor_turn_id=self._current_actor_turn_id,
        ))
        self.logger.next_turn()
        return result

    def swap_turns(self) -> None:
        """Advance the fixed actor cycle while preserving legacy aliases."""
        if not self._turn_action_committed:
            self._turn_action_committed = True
            return
        if not self._actor_cycle:
            active_user = self.summon if self.summon_active else self.player
            if self.attacker == active_user:
                self.attacker = self.encounter.primary_enemy
                self.defender = active_user
            else:
                self.attacker = active_user
                self.defender = self.encounter.primary_enemy
            self.available_actions = self._available_actions()
            return
        old_round = self.round_number
        dragon_soul_turn = bool(
            promotion_kits.combat_state(self.player).pop(
                "dragon_soul_immediate_turn",
                False,
            )
        )
        if dragon_soul_turn and PLAYER_ACTOR_ID in self._actor_cycle.order:
            player_index = self._actor_cycle.order.index(PLAYER_ACTOR_ID)
            self._actor_cycle.cursor = (player_index - 1) % len(self._actor_cycle.order)
        wrapped, _actor_id = self._actor_cycle.advance(self._valid_actor_ids())
        if wrapped:
            self.logger.next_round()
            self._event_bus.emit(create_combat_event(
                EventType.ROUND_END,
                actor=self.attacker,
                target=self.defender,
                encounter_id=self.encounter.encounter_id,
                round=old_round,
                actor_turn_id=self._current_actor_turn_id,
            ))
        self._sync_actor_aliases()
        self._current_actor_turn_id = self._actor_cycle.start_current_turn()
        if wrapped:
            self._event_bus.emit(create_combat_event(
                EventType.ROUND_START,
                actor=self.attacker,
                target=self.defender,
                encounter_id=self.encounter.encounter_id,
                actor_id=self.current_actor_id,
                round=self.round_number,
                actor_turn_id=self._current_actor_turn_id,
            ))
        self._event_bus.emit(create_combat_event(
            EventType.TURN_START,
            actor=self.attacker,
            target=self.defender,
            encounter_id=self.encounter.encounter_id,
            actor_id=self.current_actor_id,
            round=self.round_number,
            actor_turn_id=self._current_actor_turn_id,
        ))
        self.available_actions = self._available_actions()

    def end_battle(self) -> BattleOutcome:
        """
        Finalise combat: determine outcome, emit events, clean up state.

        Note: This handles the core bookkeeping. UI layers should handle
        display (popups, animations, level-up screens) based on the returned
        BattleOutcome.
        """
        if self._completed_outcome is not None:
            return self._completed_outcome
        self.player.floating_crystal = None
        self.player.barrier_wall_hp = 0
        if len(self.encounter.members) > 1:
            self._completed_outcome = self._end_multi_battle()
            return self._completed_outcome

        enemy = self.encounter.primary_enemy
        outcome = BattleOutcome(boss=self.boss)

        if self.flee:
            outcome.result = "flee"
            outcome.winner = None
            outcome.message = f"{self.player.name} fled from combat.\n"
            outcome.message += promotion_kits.end_combat(self.player, victory=False, enemy=enemy)
            if hasattr(self.player, "_grandmaster_battle_hit_types"):
                self.player._grandmaster_battle_hit_types.clear()
            self.tile.enemy = None
        elif self.player.is_alive():
            outcome.result = "victory"
            outcome.winner = self.player.name
            self._record_singleton_resolution()
            if getattr(enemy, "grandmaster_trial_enemy", False):
                outcome.message = self._process_grandmaster_trial_victory()
            elif self._is_thieves_guild_trial_enemy():
                outcome.message = self._process_thieves_guild_trial_victory()
            elif self._is_class_ring_trial_enemy():
                outcome.message = self._process_class_ring_trial_victory()
            else:
                outcome.message = self._process_victory()
            # Check for level up possibility
            pending_level = getattr(self.player, "_pending_level_up_result", None)
            if (
                pending_level is not None
                and pending_level.new_level > pending_level.old_level
            ):
                outcome.level_up = True
        else:
            outcome.result = "defeat"
            outcome.winner = enemy.name
            outcome.message = f"{self.player.name} was slain by {enemy.name}.\n"
            outcome.message += promotion_kits.end_combat(self.player, victory=False, enemy=enemy)
            if self._is_thieves_guild_trial_enemy():
                outcome.message = f"{self.player.name} yields the guild initiation bout.\n"
                self._process_class_ring_trial_defeat()
            elif self._is_class_ring_trial_enemy():
                outcome.message = f"{self.player.name} yields the trial bout.\n"
                self._process_class_ring_trial_defeat()
            else:
                self._process_defeat()

        # Mark boss tile defeated
        if self.player.is_alive() and self.boss:
            self.tile.defeated = True
            self.tile.enemy = None

        self.logger.end_battle(
            result=outcome.result,
            winner=outcome.winner,
            boss=self.boss,
            encounter=self.encounter,
        )
        paladin.clear_condemnation(enemy)

        # Emit combat end event
        self._event_bus.emit(create_combat_event(
            EventType.COMBAT_END,
            actor=self.player,
            target=enemy,
            fled=self.flee,
            player_alive=self.player.is_alive(),
            enemy_alive=enemy.is_alive(),
            encounter_id=self.encounter.encounter_id,
            enemies=self.encounter.roster_summary(),
        ))

        self.player._active_combat = False
        self.player._combat_encounter = None
        self._completed_outcome = outcome
        return outcome

    def _end_multi_battle(self) -> BattleOutcome:
        """Finalize a multi-member encounter with atomic ledger settlement."""
        if not self.flee and self.player.is_alive():
            for member in self.encounter.members:
                self._attempt_member_resurrection(member)
            self._record_final_enemy_resolutions()
        if self.flee:
            result = "flee"
            winner = None
            message = f"{self.player.name} fled from combat.\n"
        elif self.player.is_alive():
            result = "victory"
            winner = self.player.name
            (
                message,
                settlements,
                total_exp,
                level_up,
                notices,
            ) = self._process_multi_victory()
        else:
            result = "defeat"
            winner = self.encounter.primary_enemy.name
            message = f"{self.player.name} was defeated in the multi-enemy encounter.\n"

        if result in {"flee", "defeat"}:
            self.encounter.clear_resolutions()
            settlements = ()
            total_exp = 0
            level_up = False
            notices = ()
            message += promotion_kits.end_combat(
                self.player,
                victory=False,
                enemy=self.encounter.primary_enemy,
            )
            if hasattr(self.player, "_grandmaster_battle_hit_types"):
                self.player._grandmaster_battle_hit_types.clear()
            for member in self.encounter.members:
                enemy = member.enemy
                enemy.effects(end=True)
                enemy.health.current = enemy.health.max
                enemy.mana.current = enemy.mana.max
            self.player.state = "normal"
            self.player.effects(end=True)
            if result == "defeat":
                self.player.death()
        combined_loot = {}
        for settlement in settlements:
            for award in settlement.loot_awards:
                key = (award.destination, award.item_name)
                combined_loot[key] = combined_loot.get(key, 0) + award.quantity
        loot_awards = tuple(
            LootAward(item_name=name, quantity=quantity, destination=destination)
            for (destination, name), quantity in sorted(combined_loot.items())
        )
        resolution_counts = tuple(
            (resolution, sum(
                settlement.resolution == resolution
                for settlement in settlements
            ))
            for resolution in EnemyResolution
            if any(settlement.resolution == resolution for settlement in settlements)
        )
        outcome = BattleOutcome(
            result=result,
            winner=winner,
            message=message,
            boss=False,
            rewards_settled=True,
            member_settlements=settlements,
            total_experience=total_exp,
            total_gold=sum(settlement.gold for settlement in settlements),
            loot_awards=loot_awards,
            resolution_counts=resolution_counts,
            notices=notices,
            level_up=level_up,
        )
        self.logger.end_battle(
            result=result,
            winner=winner,
            boss=False,
            encounter=self.encounter,
            settlements=settlements,
            total_experience=total_exp,
        )
        self._event_bus.emit(create_combat_event(
            EventType.COMBAT_END,
            actor=self.player,
            target=self.encounter.primary_enemy,
            fled=self.flee,
            player_alive=self.player.is_alive(),
            enemy_alive=bool(self.encounter.living_members),
            encounter_id=self.encounter.encounter_id,
            enemies=self.encounter.roster_summary(),
            rewards_settled=True,
            settlements=[
                {
                    "combatant_id": settlement.combatant_id,
                    "resolution": settlement.resolution.value,
                    "experience": settlement.experience,
                    "gold": settlement.gold,
                }
                for settlement in settlements
            ],
            total_experience=total_exp,
        ))
        self.player._active_combat = False
        self.player._combat_encounter = None
        return outcome

    def _record_final_enemy_resolutions(self) -> None:
        """Record terminal enemy states after action/resurrection handling."""
        for member in self.encounter.members:
            enemy = member.enemy
            if member.resolution is not None:
                promotion_kits.clear_revelation(self.player, enemy)
                continue
            if enemy.is_alive():
                continue
            promotion_kits.clear_revelation(self.player, enemy)
            resolution = EnemyResolution.DEFEATED
            cause = None
            if getattr(enemy, "paladin_mercy_victory", False):
                resolution = EnemyResolution.MERCY
                cause = "paladin_mercy"
            elif getattr(enemy, "tamed_by_player", False):
                resolution = EnemyResolution.TAMED
                cause = "tame"
            elif getattr(enemy, "windswept_ejected", False):
                resolution = EnemyResolution.EJECTED
                cause = "windswept"
            elif getattr(enemy, "paladin_repelled", False):
                resolution = EnemyResolution.ESCAPED
                cause = "paladin_repel"
            elif getattr(enemy, "no_victory_rewards", False):
                resolution = EnemyResolution.ESCAPED
                cause = "no_victory_rewards"
            self.encounter.resolve_enemy(
                member.combatant_id,
                resolution,
                cause=cause,
            )

    def _consume_new_resolution_records(self):
        """Return terminal records not yet attached to an action/turn result."""
        reported = getattr(self, "_reported_resolution_ids", set())
        records = tuple(
            record
            for record in self.encounter.resolution_ledger
            if record.combatant_id not in reported
        )
        for record in records:
            member = self.encounter.member_by_id(record.combatant_id)
            promotion_kits.clear_death_marks(self.player, member.enemy)
        reported.update(record.combatant_id for record in records)
        self._reported_resolution_ids = reported
        return records

    @staticmethod
    def _attempt_member_resurrection(member) -> bool:
        """Resolve a member's resurrection before recording terminal state."""
        enemy = member.enemy
        if enemy.is_alive():
            return False
        spell = enemy.spellbook.get("Spells", {}).get("Resurrection")
        if spell is None or abs(enemy.health.current) > enemy.mana.current:
            return False
        message = spell.cast(enemy)
        return bool(message) and enemy.is_alive()

    def _record_singleton_resolution(self) -> None:
        """Record the existing singleton outcome without changing its rewards."""
        member = self.encounter.primary_member
        enemy = member.enemy
        if member.resolution is not None:
            return

        resolution = EnemyResolution.DEFEATED
        cause = None
        if getattr(enemy, "paladin_mercy_victory", False):
            resolution = EnemyResolution.MERCY
            cause = "paladin_mercy"
        elif getattr(enemy, "tamed_by_player", False):
            resolution = EnemyResolution.TAMED
            cause = "tame"
        elif getattr(enemy, "windswept_ejected", False):
            resolution = EnemyResolution.EJECTED
            cause = "windswept"
        elif getattr(enemy, "paladin_repelled", False):
            resolution = EnemyResolution.ESCAPED
            cause = "paladin_repel"
        elif getattr(enemy, "no_victory_rewards", False):
            resolution = EnemyResolution.ESCAPED
            cause = "no_victory_rewards"

        self.encounter.resolve_enemy(
            member.combatant_id,
            resolution,
            cause=cause,
        )
