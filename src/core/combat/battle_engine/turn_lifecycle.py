"""Post-action and battle lifecycle handling for the battle engine."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ...classes import (
    lycan,
    nature_totems,
    paladin,
    promotion_kits,
)
from ...events.event_bus import EventType, create_combat_event
from ..actor_cycle import PLAYER_ACTOR_ID
from ..encounter import EnemyResolution
from ..targeting import TargetScope
from .models import (
    BattleOutcome,
    LootAward,
    PostTurnResult,
)

if TYPE_CHECKING:
    from typing import Any


class TurnLifecycleMixin:
    """Advance turns and settle completed combat encounters."""

    def _resolve_reaction_once(self, reaction_id: str, resolver) -> str:
        """Resolve one engine-owned reaction once for the current action result."""
        key = (self._current_actor_turn_id, reaction_id)
        if key in self._reaction_executions:
            return ""
        self._reaction_executions.add(key)
        return resolver()

    def companion_turn(self) -> str:
        """Process the attacker's familiar/companion turn. Returns message text."""
        undead_text = ""
        allies = list(getattr(self.attacker, "temporary_undead_allies", []))
        if allies and self.defender is not None and self.defender.is_alive():
            remaining = []
            for ally in allies:
                damage = min(self.defender.health.current, int(ally.get("damage", 1) or 1))
                self.defender.health.current -= damage
                undead_text += (
                    f"Undead {ally['name']} attacks {self.defender.name} for {damage} damage.\n"
                )
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
            messages.append(
                f"{getattr(spell, 'name', 'A delayed spell')} emerges from the wormhole.\n"
            )
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
            special = self._resolve_reaction_once(
                f"post_action_special:{self._actor_id_for(self.defender)}",
                lambda: self.defender.special_effects(self.attacker),
            )
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
                            int(int(crystal["mana"]) * (1.0 + spell_power / 100.0)),
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
                if "Resurrection" in self.defender.spellbook.get("Spells", {}):
                    res_spell = self.defender.spellbook["Spells"]["Resurrection"]
                    if abs(self.defender.health.current) <= self.defender.mana.current:
                        res_msg = res_spell.cast(self.defender)
                        if res_msg:
                            result.messages.append(res_msg)
                            result.resurrected = True

                # Behemoth death special (Meteor on death)
                if self.defender.name == "Behemoth":
                    special = self._resolve_reaction_once(
                        f"death_special:{self._actor_id_for(self.defender)}",
                        lambda: self.defender.special_effects(self.attacker),
                    )
                    if special:
                        result.messages.append(special)

            if (
                self._member_for_character(self.attacker) is not None
                and self.defender == self.player
            ):
                riposte = self._resolve_reaction_once(
                    "judgment_riposte",
                    lambda: paladin.resolve_riposte(self.player, self.attacker),
                )
                if riposte:
                    result.messages.append(riposte)

        self._record_final_enemy_resolutions()
        result.new_resolutions = self._consume_new_resolution_records()
        if self.defender == self.player and self.player.is_alive():
            hp_max = max(1, int(self.player.health.max or 1))
            if self.player.health.current / hp_max <= 0.25:
                triggered, frenzy_msg = lycan.maybe_trigger_frenzy(self.player, reason="low_hp")
                if triggered:
                    result.messages.append(frenzy_msg)
        paladin.clear_transient_marks(self.player)
        self._event_bus.emit(
            create_combat_event(
                EventType.TURN_END,
                actor=self.attacker,
                target=self.defender,
                encounter_id=self.encounter.encounter_id,
                actor_id=self.current_actor_id,
                round=self.round_number,
                actor_turn_id=self._current_actor_turn_id,
            )
        )
        self.logger.next_turn()
        return result

    def swap_turns(self) -> None:
        """Advance the fixed actor cycle while preserving legacy aliases."""
        self._reaction_executions.clear()
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
        readiness_cost = self.readiness_cost(self.attacker)
        dragon_soul_turn = bool(
            promotion_kits.combat_state(self.player).pop(
                "dragon_soul_immediate_turn",
                False,
            )
        )
        if dragon_soul_turn:
            self._actor_cycle.schedule_immediate(PLAYER_ACTOR_ID)
        wrapped, _actor_id = self._actor_cycle.advance(
            self._valid_actor_ids(),
            readiness_cost=readiness_cost,
        )
        if wrapped:
            self.logger.next_round()
            self._event_bus.emit(
                create_combat_event(
                    EventType.ROUND_END,
                    actor=self.attacker,
                    target=self.defender,
                    encounter_id=self.encounter.encounter_id,
                    round=old_round,
                    actor_turn_id=self._current_actor_turn_id,
                )
            )
        self._sync_actor_aliases()
        self._current_actor_turn_id = self._actor_cycle.start_current_turn()
        if wrapped:
            self._event_bus.emit(
                create_combat_event(
                    EventType.ROUND_START,
                    actor=self.attacker,
                    target=self.defender,
                    encounter_id=self.encounter.encounter_id,
                    actor_id=self.current_actor_id,
                    round=self.round_number,
                    actor_turn_id=self._current_actor_turn_id,
                )
            )
        self._event_bus.emit(
            create_combat_event(
                EventType.TURN_START,
                actor=self.attacker,
                target=self.defender,
                encounter_id=self.encounter.encounter_id,
                actor_id=self.current_actor_id,
                round=self.round_number,
                actor_turn_id=self._current_actor_turn_id,
            )
        )
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
            if pending_level is not None and pending_level.new_level > pending_level.old_level:
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
        self._event_bus.emit(
            create_combat_event(
                EventType.COMBAT_END,
                actor=self.player,
                target=enemy,
                fled=self.flee,
                player_alive=self.player.is_alive(),
                enemy_alive=enemy.is_alive(),
                encounter_id=self.encounter.encounter_id,
                enemies=self.encounter.roster_summary(),
            )
        )

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
            (resolution, sum(settlement.resolution == resolution for settlement in settlements))
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
        self._event_bus.emit(
            create_combat_event(
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
            )
        )
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
