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

import random
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .battle_logger import BattleLogger
from .initiative import determine_initiative
from ..constants import SPECIAL_ATTACK_LUCK_FACTOR, SPECIAL_ATTACK_ROLL_MAX
from ..events.event_bus import get_event_bus, create_combat_event, EventType

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

        # Available actions refreshed each turn
        self.available_actions: list = tile.available_actions(player)

        self._event_bus = get_event_bus()

    # ── Lifecycle ────────────────────────────────────────────────────

    def start_battle(self) -> tuple[Character, Character]:
        """
        Initialise the battle: determine initiative, emit events, start logging.

        Returns:
            (first_actor, second_actor) — the initiative order.
        """
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

        return self.attacker, self.defender

    def battle_continues(self) -> bool:
        """Return True while both combatants are alive and nobody fled."""
        return self.player.is_alive() and self.enemy.is_alive() and not self.flee

    # ── Turn phases ──────────────────────────────────────────────────

    def pre_turn(self) -> PreTurnResult:
        """
        Process the attacker's start-of-turn effects and check activity.

        Call this at the beginning of each turn before requesting an action.
        """
        result = PreTurnResult()

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

        # Check if the attacker died from their own effects
        if not self.attacker.is_alive():
            result.died_from_effects = True
            result.can_act = False
            return result

        # Check if the attacker can act this turn
        active, text = self.attacker.check_active()
        if not active:
            result.can_act = False
            result.inactive_reason = text

        return result

    def get_forced_action(self) -> ForcedAction | None:
        """
        Check if the current attacker's action is forced.

        Returns a ForcedAction when the attacker must perform a specific action
        (berserk, charging skill, jump), or None when the actor has free choice.
        """
        # Berserk forces a basic attack
        if self.attacker.status_effects["Berserk"].active:
            return ForcedAction(action="Attack")

        # Ongoing charging ability (e.g. Charge, Crushing Blow)
        if self.charging_ability and self.attacker == self.player:
            charge_owner, ability_name, _skill_obj = self.charging_ability
            if charge_owner == self.attacker:
                return ForcedAction(action="Use Skill", choice=ability_name)

        # Jump in progress
        if self.attacker.class_effects["Jump"].active:
            if self.attacker.incapacitated():
                # Cancel the jump if incapacitated during charge
                try:
                    jump_choice = [x for x in self.attacker.spellbook['Skills'] if "Jump" in x][0]
                    jump_skill = self.attacker.spellbook['Skills'][jump_choice]
                    cancel_msg = jump_skill.cancel_charge(self.attacker)
                except (IndexError, KeyError, AttributeError):
                    cancel_msg = f"{self.attacker.name}'s Jump was cancelled.\n"
                self.attacker.class_effects["Jump"].active = False
                return ForcedAction(action="Cancelled", cancel_message=cancel_msg)
            else:
                choice = [x for x in self.attacker.spellbook['Skills'] if "Jump" in x][0]
                self.attacker.class_effects["Jump"].active = False
                return ForcedAction(action="Use Skill", choice=choice)

        # Enemy with a charging skill in progress
        if self.attacker != self.player:
            for skill_name, skill in self.attacker.spellbook.get('Skills', {}).items():
                if getattr(skill, 'charging', False):
                    return ForcedAction(action="Use Skill", choice=skill_name)

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

        if action == "Nothing" or action == "Cancelled":
            result.message = f"{self.attacker.name} does nothing.\n"
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

        elif action == "Defend":
            result.message = self._execute_defend()

        elif action == "Cast Spell":
            result.message = self._execute_spell(choice)

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

            # Refresh available actions
            self.available_actions = self.tile.available_actions(self.player)

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
            self.tile.enemy = None
        elif self.player.is_alive():
            outcome.result = "victory"
            outcome.winner = self.player.name
            outcome.message = self._process_victory()
            # Check for level up possibility
            if not self.player.max_level() and self.player.level.exp_to_gain <= 0:
                outcome.level_up = True
        else:
            outcome.result = "defeat"
            outcome.winner = self.enemy.name
            outcome.message = f"{self.player.name} was slain by {self.enemy.name}.\n"
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
        return self.attacker.enter_defensive_stance(duration=2, source="Defend")

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
        ))

        message = f"{self.attacker.name} casts {choice}.\n"
        message += str(spell.cast(self.attacker, target=self.defender))
        return message

    def _execute_skill(
        self,
        choice: str | None,
        slot_machine_callback: Callable | None = None,
    ) -> str:
        """Use a skill. Handles silence, Jump, Charge, Smoke Screen, etc."""
        if self.attacker.abilities_suppressed():
            reason = "the anti-magic field" if getattr(self.attacker, "anti_magic_active", False) else "silence"
            return f"{self.attacker.name} cannot use skills because of {reason}!\n"

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
        # even when the user is at 0 mana (otherwise the charge can never resolve).
        already_charging = bool(getattr(skill, "charging", False))
        if not already_charging and self.attacker.mana.current < skill.cost:
            return f"{self.attacker.name} does not have enough mana to use {choice}!\n"

        self._event_bus.emit(create_combat_event(
            EventType.SKILL_USE,
            actor=self.attacker,
            target=self.defender,
            skill_name=skill.name,
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
            if charge_time > 0:
                self.attacker.class_effects["Jump"].active = True
            message += skill.use(self.attacker, target=self.defender)

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
        target = self.attacker
        if itm.subtyp == "Scroll":
            if itm.spell.subtyp != "Support":
                target = self.defender

        self._event_bus.emit(create_combat_event(
            EventType.ITEM_USE,
            actor=self.attacker,
            target=target,
            item_name=itm.name,
        ))

        return str(itm.use(self.attacker, target=target))

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
        exp_gain = int(self.enemy.experience)
        try:
            exp_gain = max(0, int(exp_gain * float(self.player.exp_gain_multiplier())))
        except Exception:
            pass
        msg = f"{self.player.name} gained {exp_gain} experience.\n"

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

        # Kill tracking
        if self.enemy.enemy_typ not in self.player.kill_dict:
            self.player.kill_dict[self.enemy.enemy_typ] = {}
        if self.enemy.name not in self.player.kill_dict[self.enemy.enemy_typ]:
            self.player.kill_dict[self.enemy.enemy_typ][self.enemy.name] = 0
        self.player.kill_dict[self.enemy.enemy_typ][self.enemy.name] += 1
        if hasattr(self.player, "record_enemy_defeat"):
            self.player.record_enemy_defeat()

        # Loot
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

        return msg

    def _process_defeat(self) -> None:
        """Handle defeat bookkeeping: reset enemy, player death."""
        self.player.state = 'normal'
        if hasattr(self.player, 'transform_type') and self.player.cls != self.player.transform_type:
            self.player.transform(back=True)
        self.player.effects(end=True)

        # Reset enemy for potential re-fight
        self.enemy.effects(end=True)
        self.enemy.health.current = self.enemy.health.max
        self.enemy.mana.current = self.enemy.mana.max

        self.player.death()
