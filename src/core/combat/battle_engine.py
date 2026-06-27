"""
Core Battle Engine — UI-agnostic combat logic.

This module contains all the game-mechanical combat logic that was previously
duplicated between the curses BattleManager and the pygame GUICombatManager.
Both UI layers should delegate to this engine for action execution, turn flow,
and state management, keeping only rendering and input handling in their own code.

Usage:
    engine = BattleEngine(player, enemy, tile)
    engine.start_battle()

    while engine.battle_continues():
        # Pre-turn: process status effects, check if attacker can act
        pre = engine.pre_turn()

        if pre.can_act:
            forced = engine.get_forced_action()
            if forced:
                action, choice = forced.action, forced.choice
            elif engine.is_player_turn():
                action, choice = <UI gets player input>
            else:
                action, choice = engine.get_enemy_action()

            result = engine.execute_action(action, choice)
            <UI displays result.message>

        companion_msg = engine.companion_turn()
        post = engine.post_turn()
        engine.swap_turns()

    outcome = engine.end_battle()
"""

from __future__ import annotations

import inspect
import random
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .battle_logger import BattleLogger
from .initiative import determine_initiative
from ..constants import SPECIAL_ATTACK_LUCK_FACTOR, SPECIAL_ATTACK_ROLL_MAX
from .. import items
from ..events.event_bus import get_event_bus, create_combat_event, EventType
from ..classes import astromancer, bard, berserker, class_rings, dragoon, lycan, nature_totems, ability_mechanics, paladin, wizard

if TYPE_CHECKING:
    from typing import Any, Callable

    from ..character import Character
    from ..player import Player


# ── Result dataclasses ───────────────────────────────────────────────

@dataclass
class PreTurnResult:
    """Result of pre-turn processing (status effects, activity check)."""
    effects_text: str = ""
    can_act: bool = True
    inactive_reason: str = ""
    # Exploding shield damage dealt to the defender during effects processing
    shield_explosion_damage: int = 0
    # True when the attacker died from their own effects (poison, DOT, bleed)
    died_from_effects: bool = False


@dataclass
class ForcedAction:
    """Represents an automatically-determined action (berserk, charging, jump)."""
    action: str = ""
    choice: str | None = None
    cancel_message: str = ""  # non-empty when a charging ability was cancelled


@dataclass
class ActionResult:
    """Result of executing a combat action."""
    message: str = ""
    fled: bool = False
    summon_started: bool = False
    summon_recalled: bool = False
    summon: Character | None = None


@dataclass
class PostTurnResult:
    """Result of post-turn processing."""
    messages: list[str] = field(default_factory=list)
    defender_died: bool = False
    resurrected: bool = False
    summon_died: bool = False


@dataclass
class BattleOutcome:
    """Final result of a completed battle."""
    result: str = ""          # "victory", "defeat", "flee"
    winner: str | None = None
    message: str = ""         # Summary text (exp, loot, quests, etc.)
    level_up: bool = False
    boss: bool = False


# ── Core Engine ──────────────────────────────────────────────────────

class BattleEngine:
    """
    UI-agnostic combat engine.

    Holds all combat state and provides methods for each phase of a turn.
    UI layers drive the loop and call these methods; the engine never
    renders or reads input itself.
    """

    def __init__(
        self,
        player: Player,
        enemy: Character,
        tile: Any,
        game: Any | None = None,
        logger: BattleLogger | None = None,
    ):
        self.player: Player = player
        self.enemy: Character = enemy
        self.tile: Any = tile
        self.game: Any = game
        self.logger: BattleLogger = logger if logger else BattleLogger()

        self.flee: bool = False
        self.boss: bool = "Boss" in str(tile)

        self.summon_active: bool = False
        self.summon: Character | None = None

        self.attacker: Character | None = None
        self.defender: Character | None = None

        # Track charging abilities across turns
        self.charging_ability: tuple[Character, str, Any] | None = None  # (owner, name, skill_obj)
        self.delayed_spells: list[dict[str, Any]] = []

        # Available actions refreshed each turn
        self.available_actions: list = self._available_actions()

        self._event_bus = get_event_bus()

    def _is_class_ring_trial_enemy(self) -> bool:
        """Return whether this fight should use Class Ring trial bookkeeping."""
        return bool(
            getattr(self.enemy, "grandmaster_trial_enemy", False)
            or getattr(self.enemy, "class_ring_trial_enemy", False)
        )

    def _class_ring_trial_name(self) -> str:
        return str(getattr(self.enemy, "class_ring_trial_name", "Class Ring trial"))

    def _no_healing_duel_active(self) -> bool:
        return bool(getattr(self.enemy, "class_ring_no_healing_duel", False))

    def _available_actions(self) -> list:
        actions = list(self.tile.available_actions(self.player))
        if astromancer.boostable_spells(self.player) and "Runic Boost" not in actions:
            insert_at = actions.index("Cast Spell") + 1 if "Cast Spell" in actions else len(actions)
            actions.insert(insert_at, "Runic Boost")
        return actions

    def _fail_no_healing_duel_if_healed(self, hp_before: int) -> str:
        """Fail the Berserker duel when the player restores HP during the bout."""
        if not self._no_healing_duel_active():
            return ""
        if self.player.health.current <= hp_before:
            return ""
        self.player.health.current = 0
        return "The No Healing Duel rejects restored life. You yield the bout.\n"

    # ── Lifecycle ────────────────────────────────────────────────────

    def start_battle(self) -> tuple[Character, Character]:
        """
        Initialise the battle: determine initiative, emit events, start logging.

        Returns:
            (first_actor, second_actor) — the initiative order.
        """
        self._clear_stale_charging_actions(self.player)
        self._clear_stale_charging_actions(self.enemy)
        self.player._final_assault_used = False
        self.player._last_stand_used = False
        self.player._foretell_snapshot = None
        self.player._rewind_snapshot = None
        self.attacker, self.defender = determine_initiative(self.player, self.enemy)

        self._event_bus.emit(create_combat_event(
            EventType.COMBAT_START,
            actor=self.player,
            target=self.enemy,
            initiative=self.attacker == self.player,
            boss=self.boss,
        ))

        self.logger.start_battle(
            self.player,
            self.enemy,
            initiative=self.attacker == self.player,
            boss=self.boss,
        )

        if hasattr(self.player, "record_bestiary_encounter"):
            self.player.record_bestiary_encounter(self.enemy, getattr(self.enemy, "enemy_typ", None))

        paladin.advance_encounter(self.player)
        paladin.clear_transient_marks(self.player)
        debuff_text = bard.apply_enemy_opening_debuffs(self.player, self.enemy)
        if debuff_text:
            self.logger.log_event("Bard Song", self.player, target=self.enemy, outcome=debuff_text)
        return self.attacker, self.defender

    def battle_continues(self) -> bool:
        """Return True while both combatants are alive and nobody fled."""
        return self.player.is_alive() and self.enemy.is_alive() and not self.flee

    # ── Turn phases ──────────────────────────────────────────────────

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

        if action == "Nothing" or action == "Cancelled":
            result.message = f"{self.attacker.name} does nothing.\n"
            return result

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

        # Log the action
        self.logger.log_event(
            event_type="Action",
            actor=self.attacker,
            target=self.defender,
            action=action,
            outcome=result.message,
        )

        return result

    def companion_turn(self) -> str:
        """Process the attacker's familiar/companion turn. Returns message text."""
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
            if hasattr(self.player, "_grandmaster_battle_hit_types"):
                self.player._grandmaster_battle_hit_types.clear()
            self.tile.enemy = None
        elif self.player.is_alive():
            outcome.result = "victory"
            outcome.winner = self.player.name
            if getattr(self.enemy, "grandmaster_trial_enemy", False):
                outcome.message = self._process_grandmaster_trial_victory()
            elif self._is_class_ring_trial_enemy():
                outcome.message = self._process_class_ring_trial_victory()
            else:
                outcome.message = self._process_victory()
            # Check for level up possibility
            if not self.player.max_level() and self.player.level.exp_to_gain <= 0:
                outcome.level_up = True
        else:
            outcome.result = "defeat"
            outcome.winner = self.enemy.name
            outcome.message = f"{self.player.name} was slain by {self.enemy.name}.\n"
            if self._is_class_ring_trial_enemy():
                outcome.message = f"{self.player.name} yields the trial bout.\n"
                self._process_class_ring_trial_defeat()
            else:
                self._process_defeat()

        # Mark boss tile defeated
        if self.player.is_alive() and self.boss:
            self.tile.defeated = True
            self.tile.enemy = None

        self.logger.end_battle(
            result=outcome.result, winner=outcome.winner, boss=self.boss
        )

        # Emit combat end event
        self._event_bus.emit(create_combat_event(
            EventType.COMBAT_END,
            actor=self.player,
            target=self.enemy,
            fled=self.flee,
            player_alive=self.player.is_alive(),
            enemy_alive=self.enemy.is_alive(),
        ))

        return outcome

    # ── Sight / vision helpers ───────────────────────────────────────

    def player_has_sight(self) -> bool:
        """Check if the player can see enemy details (Seeker/Inquisitor/Vision)."""
        return any([
            self.player.cls.name in ["Inquisitor", "Seeker"],
            getattr(self.player.equipment.get("Pendant"), "mod", None) == "Vision",
            getattr(self.player, "sight", False),
        ])

    def show_enemy_details(self) -> bool:
        """Return True if enemy details should be visible (has sight + not boss/waitress)."""
        return all([
            self.player_has_sight(),
            not self.boss,
            self.enemy.name != "Waitress",
        ])

    # ── Private action helpers ───────────────────────────────────────

    def _execute_attack(self) -> str:
        """Execute a basic/special attack."""
        self._event_bus.emit(create_combat_event(
            EventType.ATTACK,
            actor=self.attacker,
            target=self.defender,
            is_special=False,
            source="weapon_damage",
            attack_source="weapon",
            weapon_name=getattr(self.attacker.equipment.get("Weapon"), "name", None),
            weapon_slot="Weapon",
            weapon_type=getattr(self.attacker.equipment.get("Weapon"), "subtyp", None),
        ))

        # Roll for special attack
        luck_mod = self.attacker.check_mod("luck", luck_factor=SPECIAL_ATTACK_LUCK_FACTOR)
        roll_max = max(1, SPECIAL_ATTACK_ROLL_MAX - luck_mod)
        if not random.randint(0, roll_max):
            try:
                result = self.attacker.special_attack(target=self.defender)
                self._event_bus.emit(create_combat_event(
                    EventType.ATTACK,
                    actor=self.attacker,
                    target=self.defender,
                    is_special=True,
                    source="special_attack",
                    attack_source="special_attack",
                ))
                return result
            except NotImplementedError:
                pass

        message, _hit, _damage = self.attacker.weapon_damage(self.defender)
        return message

    def _execute_flee(self) -> tuple[str, bool]:
        """Attempt to flee. Returns (message, success)."""
        self._event_bus.emit(create_combat_event(
            EventType.FLEE_ATTEMPT,
            actor=self.attacker,
            target=self.defender,
        ))
        success, message = self.attacker.flee(self.defender)
        return message, success

    def _execute_defend(self) -> str:
        """Enter defensive stance."""
        self._event_bus.emit(create_combat_event(
            EventType.DEFEND,
            actor=self.attacker,
            target=self.defender,
        ))
        message = self.attacker.enter_defensive_stance(duration=1, source="Defend")
        if self.attacker == self.player:
            class_rings.build_guard_meter(self.player, 25)
        return message

    def _execute_spell(self, choice: str | None) -> str:
        """Cast a spell. Handles silence check."""
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot cast spells because of {reason}!\n"

        if not choice or choice not in self.attacker.spellbook.get('Spells', {}):
            return f"{self.attacker.name} fumbles the spell.\n"

        spell = self.attacker.spellbook['Spells'][choice]
        if self.attacker.mana.current < spell.cost:
            return f"{self.attacker.name} does not have enough mana to cast {choice}!\n"

        self._event_bus.emit(create_combat_event(
            EventType.SPELL_CAST,
            actor=self.attacker,
            target=self.defender,
            spell_name=choice,
            ability_name=choice,
            source="spell",
        ))

        defender_was_alive = self.defender.is_alive()
        message = f"{self.attacker.name} casts {choice}.\n"
        message += str(self._cast_spell_with_context(spell, self.attacker, self.defender))
        if self.attacker == self.player:
            if (
                choice in {"Turn Undead", "TurnUndead", "Turn Undead 2", "TurnUndead2"}
                and defender_was_alive
                and not self.defender.is_alive()
                and "Pious Bounty" in self.player.spellbook.get("Skills", {})
            ):
                self.defender._pious_bounty_gold = True
            message += wizard.process_cast(self.player, spell, self.defender)
            if not self.defender.is_alive():
                message += self._record_player_natural_spell_kill(spell)
            if astromancer.is_astromancer(self.player) and astromancer.sign_for_spell(spell):
                astromancer.advance_constellation(self.player)
        return message

    def _record_player_natural_spell_kill(self, spell: object) -> str:
        if not astromancer.has_rune_system(self.player):
            return ""
        gained, sign, _chance = astromancer.maybe_award_rune(self.player, self.enemy, spell)
        if gained and sign:
            return f"{self.player.name} claims an {sign} rune.\n"
        return ""

    def _cast_spell_with_context(self, spell: object, caster: object, target: object) -> object:
        """Cast a spell, passing this engine only when the spell accepts it."""
        cast = getattr(spell, "cast")
        try:
            signature = inspect.signature(cast)
        except (TypeError, ValueError):
            return cast(caster, target=target)
        accepts_engine = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            or parameter.name == "battle_engine"
            for parameter in signature.parameters.values()
        )
        if accepts_engine:
            return cast(caster, target=target, battle_engine=self)
        return cast(caster, target=target)

    def _execute_runic_boost(self, choice: str | None) -> str:
        """Spend a rune to empower and cast a matching natural spell."""
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot cast spells because of {reason}!\n"

        if self.attacker != self.player or not astromancer.has_rune_system(self.player):
            return f"{self.attacker.name} cannot shape runes.\n"

        if not choice or choice not in self.player.spellbook.get("Spells", {}):
            return f"{self.player.name} fumbles the rune pattern.\n"

        spell = self.player.spellbook["Spells"][choice]
        sign = astromancer.sign_for_spell(spell)
        if not sign:
            return f"{choice} cannot be empowered by the current rune lore.\n"
        if self.player.mana.current < spell.cost:
            return f"{self.player.name} does not have enough mana to cast {choice}!\n"
        if not astromancer.consume_rune(self.player, sign):
            return f"{self.player.name} has no {sign} runes.\n"

        floor = astromancer.runic_boost_floor(self.player, sign)
        prior_floor = getattr(self.player, "_runic_boost_floor", None)
        self.player._runic_boost_floor = floor
        try:
            message = f"{self.player.name} spends one {sign} rune to boost {choice}.\n"
            message += str(spell.cast(self.player, target=self.defender))
        finally:
            if prior_floor is None:
                try:
                    delattr(self.player, "_runic_boost_floor")
                except AttributeError:
                    pass
            else:
                self.player._runic_boost_floor = prior_floor

        message += wizard.process_cast(self.player, spell, self.defender)
        if not self.defender.is_alive():
            message += self._record_player_natural_spell_kill(spell)
        if astromancer.is_astromancer(self.player):
            astromancer.advance_constellation(self.player)
        return message

    def _execute_steal_as_well(self, choice: str | None) -> str:
        """Cast a selected spell or stolen-spell scroll, then steal if damage lands."""
        if self.attacker != self.player:
            return f"{self.attacker.name} cannot use Steal As Well.\n"
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot use Steal As Well because of {reason}!\n"
        if not choice:
            return f"{self.attacker.name} fumbles the spell theft.\n"

        from .. import abilities, items

        message = f"{self.attacker.name} weaves theft into {choice}.\n"
        before_hp = self.defender.health.current
        if choice in self.attacker.spellbook.get("Spells", {}):
            spell = self.attacker.spellbook["Spells"][choice]
            if self.attacker.mana.current < getattr(spell, "cost", 0):
                return f"{self.attacker.name} does not have enough mana to cast {choice}!\n"
            message += str(self._cast_spell_with_context(spell, self.attacker, self.defender))
        elif choice in self.attacker.inventory and self.attacker.inventory[choice]:
            scroll = self.attacker.inventory[choice][0]
            if not isinstance(scroll, items.InscribedSpellScroll):
                return f"{choice} is not a stolen spell scroll.\n"
            message += str(scroll.use(self.attacker, target=self.defender))
        else:
            return f"{self.attacker.name} cannot find {choice}.\n"

        if before_hp > self.defender.health.current:
            steal_skill = self.attacker.spellbook.get("Skills", {}).get("Steal") or abilities.Steal()
            message += str(steal_skill.use(self.attacker, target=self.defender))
        else:
            message += "The spell fails to open a path for theft.\n"
        return message

    def _execute_skill(
        self,
        choice: str | None,
        slot_machine_callback: Callable | None = None,
    ) -> str:
        """Use a skill. Handles silence, Jump, Charge, Smoke Screen, etc."""
        if not choice:
            return f"{self.attacker.name} does nothing.\n"

        # Handle "Remove Shield" alias for Mana Shield
        if choice == "Remove Shield":
            choice = "Mana Shield"

        skills = self.attacker.spellbook.get('Skills', {})
        if choice not in skills:
            return f"{self.attacker.name} does not know {choice}.\n"

        skill = skills[choice]
        # Charging skills deduct mana at start, then must be allowed to continue
        # even when the user is at 0 mana or becomes silenced (otherwise the
        # charge can never resolve).
        already_charging = bool(getattr(skill, "charging", False))
        if self.attacker.abilities_suppressed() and not already_charging:
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot use skills because of {reason}!\n"

        if not already_charging and self.attacker.mana.current < skill.cost:
            return f"{self.attacker.name} does not have enough mana to use {choice}!\n"

        self._event_bus.emit(create_combat_event(
            EventType.SKILL_USE,
            actor=self.attacker,
            target=self.defender,
            skill_name=skill.name,
            ability_name=skill.name,
            source="skill",
        ))

        message = f"{self.attacker.name} uses {skill.name}.\n"

        # ── Special skill handling ───────────────────────────────────
        if skill.name == "Smoke Screen":
            message += skill.use(self.attacker, target=self.defender)
            self.flee, flee_str = self.attacker.flee(self.defender, smoke=True)
            message += flee_str
            if self.flee and hasattr(self.player, "record_flee"):
                self.player.record_flee()

        elif skill.name == "Slot Machine":
            if slot_machine_callback:
                message += skill.use(
                    self.attacker,
                    target=self.defender,
                    slot_machine_callback=slot_machine_callback,
                )
            else:
                message += skill.use(self.attacker, target=self.defender)

        elif skill.name in ["Doublecast", "Triplecast"]:
            message += skill.use(self.attacker, self.defender, game=self.game)

        elif "Jump" in skill.name:
            charge_time = skill.get_charge_time() if hasattr(skill, "get_charge_time") else 1
            continuing_charge = already_charging and int(getattr(skill, "charge_turns", 0) or 0) > 1
            if charge_time > 0 and (not already_charging or continuing_charge):
                self.attacker.class_effects["Jump"].active = True
                message = ""
            message += skill.use(self.attacker, target=self.defender)
            self.attacker.class_effects["Jump"].active = bool(getattr(skill, "charging", False))

        elif hasattr(skill, 'get_charge_time') and skill.get_charge_time() > 0:
            # Charging abilities (Charge, Crushing Blow, etc.)
            message += skill.use(self.attacker, target=self.defender)
            if getattr(skill, 'charging', False):
                self.charging_ability = (self.attacker, choice, skill)
            else:
                # Charge completed this turn
                self.charging_ability = None

        else:
            message += str(skill.use(self.attacker, target=self.defender))

        return message

    def _execute_item(self, choice: str | None) -> str:
        """Use an inventory item."""
        if not choice:
            return f"{self.attacker.name} fumbles with their items.\n"

        item_key = re.split(r"\s{2,}", choice)[0]
        if item_key not in self.attacker.inventory or not self.attacker.inventory[item_key]:
            return f"{self.attacker.name} can't find {item_key}.\n"

        itm = self.attacker.inventory[item_key][0]
        if isinstance(itm, type):
            itm = itm()
        target = self.attacker
        if itm.subtyp == "Scroll" and hasattr(itm, "spell"):
            if itm.spell.subtyp != "Support":
                target = self.defender

        self._event_bus.emit(create_combat_event(
            EventType.ITEM_USE,
            actor=self.attacker,
            target=target,
            item_name=itm.name,
            item_type=getattr(itm, "typ", ""),
            item_subtype=getattr(itm, "subtyp", ""),
            source="item",
        ))

        message = str(itm.use(self.attacker, target=target))
        if isinstance(itm, items.Potion):
            message += ability_mechanics.trigger_drunken_brawler(self.attacker)
        return message

    def _execute_summon(self, choice: str | None) -> tuple[str, bool, Character | None]:
        """Summon a companion. Returns (message, success, summon_character)."""
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "being silenced"
            return f"{self.attacker.name} cannot summon because of {reason}!\n", False, None

        if not choice or choice not in self.attacker.summons:
            return f"{self.attacker.name} has nothing to summon.\n", False, None

        summon = self.attacker.summons[choice]
        self.summon = summon
        self.summon_active = True
        self.attacker = summon
        message = f"{self.player.name} summons {summon.name} to aid them in combat.\n"
        return message, True, summon

    def _execute_recall(self) -> tuple[str, bool]:
        """Recall a summoned companion. Returns (message, success)."""
        if not self.summon:
            return "No summon to recall.\n", False

        message = f"{self.player.name} recalls {self.summon.name}.\n"
        self.summon_active = False
        self.attacker = self.player
        return message, True

    def _execute_totem(self) -> str:
        """Use the Totem skill."""
        skills = self.attacker.spellbook.get("Skills", {})
        totem_skill = skills.get("Totem")
        if not totem_skill:
            for sk in skills.values():
                if getattr(sk, "name", "") == "Totem":
                    totem_skill = sk
                    break

        if totem_skill:
            return str(totem_skill.use(self.attacker, target=self.defender))
        else:
            return f"{self.attacker.name} does not know how to summon a totem.\n"

    # ── End-of-battle bookkeeping ────────────────────────────────────

    def _process_victory(self) -> str:
        """Handle victory bookkeeping: exp, loot, quests, kill tracking."""
        mercy = bool(getattr(self.enemy, "paladin_mercy_victory", False))
        exp_gain = int(self.enemy.experience)
        try:
            exp_gain = max(0, int(exp_gain * float(self.player.exp_gain_multiplier())))
        except Exception:
            pass
        msg = dragoon.red_dragon_victory_text(self.enemy)
        msg += f"{self.player.name} gained {exp_gain} experience.\n"

        # Handle summon experience
        if self.summon:
            self.summon.effects(end=True)
            msg += f"{self.summon.name} gained {exp_gain} experience.\n"
            self.summon.level.exp += exp_gain
            if self.summon.level.level < 10:
                self.summon.level.exp_to_gain -= exp_gain
                while self.summon.level.exp_to_gain <= 0:
                    msg += self.summon.level_up(self.player)
                    if self.summon.level.level == 10:
                        break

        if mercy:
            msg += self._award_mercy_gold()
        else:
            # Kill tracking
            if self.enemy.enemy_typ not in self.player.kill_dict:
                self.player.kill_dict[self.enemy.enemy_typ] = {}
            if self.enemy.name not in self.player.kill_dict[self.enemy.enemy_typ]:
                self.player.kill_dict[self.enemy.enemy_typ][self.enemy.name] = 0
            self.player.kill_dict[self.enemy.enemy_typ][self.enemy.name] += 1
            if hasattr(self.player, "record_enemy_defeat"):
                self.player.record_enemy_defeat()
            if hasattr(self.player, "refresh_demonologist_contracts"):
                self.player.refresh_demonologist_contracts()

            vow_text = paladin.on_enemy_defeated(
                self.player,
                self.enemy,
                bounty_target=self._enemy_is_active_bounty(),
                mercy=False,
            )
            if vow_text:
                msg += vow_text

            _scar_gained, scar_text = berserker.record_battle_scar(self.player)
            if scar_text:
                msg += scar_text
            class_rings.record_soul_harvest(self.player, getattr(self.enemy, "enemy_typ", None))
            frenzy_triggered, frenzy_text = lycan.maybe_trigger_frenzy(self.player, reason="kill")
            if frenzy_triggered:
                msg += frenzy_text

            # Loot
            if getattr(self.enemy, "windswept_ejected", False):
                msg += f"{self.enemy.name} is too far away to loot.\n"
            else:
                loot_msg = self.player.loot(self.enemy, self.tile)
                if loot_msg:
                    msg += loot_msg

            # Quest progress
            quest_msg = self.player.quests(enemy=self.enemy)
            if quest_msg:
                msg += quest_msg

        # Experience and levelling
        self.player.level.exp += exp_gain
        if not self.player.max_level():
            self.player.level.exp_to_gain -= exp_gain

        # Clear effects
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        if hasattr(self.player, "award_grandmaster_victory_xp"):
            self.player.award_grandmaster_victory_xp()

        return msg

    def _award_mercy_gold(self) -> str:
        gold = max(0, int(getattr(self.enemy, "gold", 0) or 0))
        if not gold:
            return ""
        try:
            gold = max(0, int(gold * paladin.redemption_reward_multiplier(self.player)))
        except Exception:
            pass
        self.player.gold += gold
        return f"{self.enemy.name} offers {gold} gold in restitution.\n"

    def _enemy_is_active_bounty(self) -> bool:
        try:
            bounties = self.player.quest_dict.get("Bounty", {})
            if not isinstance(bounties, dict):
                return False
            return self.enemy.name in bounties or any(
                getattr(data.get("enemy", None), "name", None) == self.enemy.name
                for data in bounties.values()
                if isinstance(data, dict)
            )
        except Exception:
            return False

    def _process_grandmaster_trial_victory(self) -> str:
        """Handle Secret Master trial victory without normal combat rewards."""
        rank_ups = []
        if hasattr(self.player, "award_grandmaster_victory_xp"):
            for weapon_type, (before, after) in self.player.award_grandmaster_victory_xp().items():
                if after > before:
                    rank_ups.append(f"{weapon_type} Discipline reached rank {after}.")

        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        self.enemy.effects(end=True)

        msg = "You complete this Secret Master bout.\n"
        if rank_ups:
            msg += "\n".join(rank_ups) + "\n"
        return msg

    def _process_class_ring_trial_victory(self) -> str:
        """Handle legacy Class Ring trial victory without normal combat rewards."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        self.enemy.effects(end=True)
        return f"You complete the {self._class_ring_trial_name()}.\n"

    def _process_class_ring_trial_defeat(self) -> None:
        """Handle Class Ring trial defeat without normal death rules."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        if hasattr(self.player, "_grandmaster_battle_hit_types"):
            self.player._grandmaster_battle_hit_types.clear()
        self.player.health.current = max(1, self.player.health.current)
        self.enemy.effects(end=True)
        self.enemy.health.current = self.enemy.health.max
        self.enemy.mana.current = self.enemy.mana.max

    def _process_defeat(self) -> None:
        """Handle defeat bookkeeping: reset enemy, player death."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)
        if hasattr(self.player, "_grandmaster_battle_hit_types"):
            self.player._grandmaster_battle_hit_types.clear()

        # Reset enemy for potential re-fight
        self.enemy.effects(end=True)
        self.enemy.health.current = self.enemy.health.max
        self.enemy.mana.current = self.enemy.mana.max

        self.player.death()
