"""Battle turn preparation, execution flow, and lifecycle handling."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...classes import ability_mechanics, bard, lycan, nature_totems, paladin, promotion_kits
from ...events.event_bus import EventType, create_combat_event
from ..encounter import EnemyResolution
from .models import ActionResult, BattleOutcome, ForcedAction, PostTurnResult, PreTurnResult

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
        if self.attacker == self.enemy:
            thirst_text = ability_mechanics.trigger_hemorrhage_thirst(
                self.player,
                getattr(self.enemy, "_last_bleed_tick_damage", 0),
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

        if self.attacker == self.enemy and bard.active_song(self.player) == "Chorus Time":
            performer_stat = int(getattr(self.player.stats, "charisma", 0)) + int(getattr(self.player.stats, "intel", 0)) // 2
            enemy_con = max(1, int(getattr(self.enemy.stats, "con", 1) or 1))
            if random.randint(1, max(2, performer_stat)) > random.randint(1, enemy_con * 2):
                result.effects_text = f"{result.effects_text or ''}{self.enemy.name} is dumbfounded by Chorus Time and loses the turn.\n"
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
        if self.attacker.status_effects["Berserk"].active:
            return ForcedAction(action="Attack")

        return None

    def get_enemy_action(self) -> tuple[str, str | None]:
        """Ask the enemy AI for its chosen action. Returns (action, choice)."""
        try:
            return self.enemy.options(self.player, self.available_actions, self.tile)
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
        """
        Execute a combat action for the current attacker.

        Args:
            action: The action type string (Attack, Cast Spell, Use Skill, etc.)
            choice: The specific spell/skill/item name (when applicable).
            slot_machine_callback: Optional UI callback for Slot Machine animation.

        Returns:
            ActionResult with the message text and status flags.
        """
        result = ActionResult()
        hp_before = self.player.health.current
        if self.attacker == self.player and not (action == "Cast Spell" and choice == "Rewind"):
            ability_mechanics.store_rewind_snapshot(self)
            promotion_kits.begin_action(
                self.player,
                defer_devotion=True,
                action=action,
                choice=choice,
            )

        if action == "Nothing" or action == "Cancelled":
            result.message = f"{self.attacker.name} does nothing.\n"
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
            return result

        elif action == "Attack":
            result.message = self._execute_attack()

        elif action == "Pickup Weapon":
            self.attacker.physical_effects["Disarm"].active = False
            result.message = f"{self.attacker.name} picks up their weapon.\n"

        elif action == "Flee":
            result.message, result.fled = self._execute_flee()
            if result.fled:
                self.flee = True
                if hasattr(self.player, "record_flee"):
                    self.player.record_flee()
                vow_text = paladin.on_flee(self.player, success=True)
                if vow_text:
                    result.message += vow_text

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

        elif action == "Use Item":
            result.message = self._execute_item(choice)

        elif action == "Summon":
            result.message, result.summon_started, result.summon = self._execute_summon(choice)

        elif action == "Recall":
            result.message, result.summon_recalled = self._execute_recall()

        elif action == "Totem":
            result.message = self._execute_totem()

        elif action == "Untransform":
            result.message = self.attacker.transform(back=True)

        elif action == "Transform":
            result.message = self.attacker.transform()

        else:
            result.message = f"{self.attacker.name} does nothing.\n"

        duel_text = self._fail_no_healing_duel_if_healed(hp_before)
        if duel_text:
            result.message = f"{result.message}{duel_text}"
        self._record_failed_enemy_debuff(self.attacker, choice, self.defender, debuff_snapshot)
        if self.attacker == self.player:
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
        )

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
        if snapshot is None or actor is not self.enemy:
            return
        if self._debuff_snapshot_gained_effect(snapshot, target):
            return
        record_failure = getattr(actor, "record_debuff_failure", None)
        if callable(record_failure):
            record_failure(str(ability_name), turns=2)

    def companion_turn(self) -> str:
        """Process the attacker's familiar/companion turn. Returns message text."""
        if (
            self.defender is None
            or not self.defender.is_alive()
            or getattr(self.defender, "tamed_by_player", False)
            or getattr(self.defender, "no_victory_rewards", False)
        ):
            return ""
        familiar_text = self.attacker.familiar_turn(self.defender)
        if familiar_text:
            self.logger.log_event(
                "Familiar", self.attacker, target=self.defender, outcome=familiar_text
            )
        return familiar_text or ""

    def _tick_delayed_spells(self) -> list[str]:
        messages: list[str] = []
        remaining: list[dict[str, Any]] = []
        for entry in self.delayed_spells:
            entry["turns"] = int(entry.get("turns", 0) or 0) - 1
            if entry["turns"] > 0:
                remaining.append(entry)
                continue
            caster = entry.get("caster")
            spell = entry.get("spell")
            if caster is None or spell is None:
                continue
            target = self.enemy if self.enemy.is_alive() else self.defender
            messages.append(f"{getattr(spell, 'name', 'A delayed spell')} emerges from the wormhole.\n")
            messages.append(str(self._cast_spell_with_context(spell, caster, target)))
        self.delayed_spells = remaining
        return messages

    def post_turn(self) -> PostTurnResult:
        """
        Process end-of-turn logic: special effects, summon state, resurrection.

        Call after execute_action and companion_turn.
        """
        result = PostTurnResult()

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

            if (
                self.attacker == self.player
                and self.defender == self.enemy
                and self.defender.is_alive()
            ):
                pulse_msg = nature_totems.resolve_totem_pulse(self.player, self.enemy)
                if pulse_msg:
                    result.messages.append(pulse_msg)
                resonance_msg = promotion_kits.pop_messages(self.player)
                if resonance_msg:
                    result.messages.append(resonance_msg)

            # Manage summon state
            if self.summon_active:
                if self.summon and self.summon.is_alive():
                    if "Recall" not in self.available_actions:
                        self.available_actions.append("Recall")
                else:
                    msg = f"{self.summon.name} has been slain.\n" if self.summon else ""
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

            if self.attacker == self.enemy and self.defender == self.player:
                riposte = paladin.resolve_riposte(self.player, self.enemy)
                if riposte:
                    result.messages.append(riposte)

        paladin.tick_turn(self.player)
        if self.defender == self.player and self.player.is_alive():
            hp_max = max(1, int(self.player.health.max or 1))
            if self.player.health.current / hp_max <= 0.25:
                triggered, frenzy_msg = lycan.maybe_trigger_frenzy(self.player, reason="low_hp")
                if triggered:
                    result.messages.append(frenzy_msg)
        paladin.clear_transient_marks(self.player)
        self.logger.next_turn()
        return result

    def swap_turns(self) -> None:
        """Swap attacker/defender for the next turn."""
        active_user = self.summon if self.summon_active else self.player
        if self.attacker == active_user:
            self.attacker, self.defender = self.enemy, active_user
        else:
            self.attacker, self.defender = active_user, self.enemy
        self.available_actions = self._available_actions()

    def end_battle(self) -> BattleOutcome:
        """
        Finalise combat: determine outcome, emit events, clean up state.

        Note: This handles the core bookkeeping. UI layers should handle
        display (popups, animations, level-up screens) based on the returned
        BattleOutcome.
        """
        outcome = BattleOutcome(boss=self.boss)

        if self.flee:
            outcome.result = "flee"
            outcome.winner = None
            outcome.message = f"{self.player.name} fled from combat.\n"
            outcome.message += promotion_kits.end_combat(self.player, victory=False, enemy=self.enemy)
            if hasattr(self.player, "_grandmaster_battle_hit_types"):
                self.player._grandmaster_battle_hit_types.clear()
            self.tile.enemy = None
        elif self.player.is_alive():
            outcome.result = "victory"
            outcome.winner = self.player.name
            self._record_singleton_resolution()
            if getattr(self.enemy, "grandmaster_trial_enemy", False):
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
            outcome.winner = self.enemy.name
            outcome.message = f"{self.player.name} was slain by {self.enemy.name}.\n"
            outcome.message += promotion_kits.end_combat(self.player, victory=False, enemy=self.enemy)
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
        paladin.clear_condemnation(self.enemy)

        # Emit combat end event
        self._event_bus.emit(create_combat_event(
            EventType.COMBAT_END,
            actor=self.player,
            target=self.enemy,
            fled=self.flee,
            player_alive=self.player.is_alive(),
            enemy_alive=self.enemy.is_alive(),
            encounter_id=self.encounter.encounter_id,
            enemies=self.encounter.roster_summary(),
        ))

        self.player._active_combat = False
        return outcome

    def _record_singleton_resolution(self) -> None:
        """Record the existing singleton outcome without changing its rewards."""
        member = self.encounter.primary_member
        if member.resolution is not None:
            return

        resolution = EnemyResolution.DEFEATED
        cause = None
        if getattr(self.enemy, "paladin_mercy_victory", False):
            resolution = EnemyResolution.MERCY
            cause = "paladin_mercy"
        elif getattr(self.enemy, "tamed_by_player", False):
            resolution = EnemyResolution.TAMED
            cause = "tame"
        elif getattr(self.enemy, "windswept_ejected", False):
            resolution = EnemyResolution.EJECTED
            cause = "windswept"
        elif getattr(self.enemy, "paladin_repelled", False):
            resolution = EnemyResolution.ESCAPED
            cause = "paladin_repel"
        elif getattr(self.enemy, "no_victory_rewards", False):
            resolution = EnemyResolution.ESCAPED
            cause = "no_victory_rewards"

        self.encounter.resolve_enemy(
            member.combatant_id,
            resolution,
            cause=cause,
        )
