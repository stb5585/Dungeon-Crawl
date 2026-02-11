"""
BattleManager for curses-based UI combat.
Moved from core.battle to keep UI dependencies separate from core logic.
"""
from __future__ import annotations

import random
import re
from typing import TYPE_CHECKING

from src.core.combat.battle_logger import BattleLogger

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character


class BattleManager:
    """
    Handles the flow of combat between the player and an enemy.

    Attributes:
        game: The current game instance.
        player_char: The player character.
        enemy: The enemy character.
        logger: The logger for recording combat events.
        flee: Whether the player has chosen to flee combat.
        tile: The current tile the player is on.
        battle_ui: The UI for the battle screen.
        battle_popup: The UI for selecting spells, skills, or items.
        textbox: The UI for displaying text.
        available_actions: The actions the player can take in combat.
        summon_active: Whether the player has summoned a companion.
        summon: The player's summoned companion.
        attacker: The character currently taking their turn.
        defender: The character currently being attacked.
    """

    def __init__(
            self,
            game: Any,
            enemy: Character,
            logger: BattleLogger | None = None,
            battle_ui: Any | None = None,
            battle_popup: Any | None = None,
            textbox: Any | None = None,
            ):
        self.game = game
        self.player_char: Character = game.player_char
        self.enemy = enemy
        self.logger = logger if logger else BattleLogger()
        self.flee: bool = False
        self.tile: Any = game.player_char.world_dict[(game.player_char.location_x,
                                                          game.player_char.location_y,
                                                          game.player_char.location_z)]
        self.boss = False if "Boss" not in str(self.tile) else True
        self.battle_ui = battle_ui
        self.battle_popup = battle_popup
        self.textbox = textbox
        self.available_actions: list = self.tile.available_actions(game.player_char)
        self.summon_active: bool = False
        self.summon: Character | None = None
        self.attacker, self.defender = self.determine_initiative()

    def render_screen(self) -> None:
        """Renders the battle screen."""
        has_sight = any([
            self.player_char.cls.name in ["Inquisitor", "Seeker"],
            getattr(self.player_char.equipment.get("Pendant"), "mod", None) == "Vision",
            getattr(self.player_char, "sight", False),
        ])
        vision = all([
            has_sight,
            "Boss" not in str(self.tile),
            self.enemy.name != "Waitress",
        ])
        self.battle_ui.draw_enemy(self.enemy, vision=vision)
        self.battle_ui.draw_options(self.available_actions)
        if self.summon_active:
            self.battle_ui.draw_char(char=self.summon)
        else:
            self.battle_ui.draw_char()
        self.battle_ui.refresh_all()

    def print_text(self, text: str) -> None:
        """Prints text to the screen."""
        cleaned = self._filter_status_lines(text)
        if not cleaned:
            return
        self.textbox.print_text_in_rectangle(cleaned)
        self.textbox.clear_rectangle()

    def _filter_status_lines(self, text: str) -> str:
        """Remove status-effect log lines in favor of status icons."""
        kept_lines = []
        for line in text.split("\n"):
            if "is affected by" in line.lower():
                continue
            if line.strip():
                kept_lines.append(line)
        return "\n".join(kept_lines)

    def determine_initiative(self) -> tuple[Character, Character]:
        """Determine who goes first using each character's dexterity plus luck."""
        if self.player_char.encumbered:
            first = self.enemy
        elif self.player_char.invisible and not self.enemy.sight:
            if self.player_char.cls.name == "Shadowcaster" and self.player_char.power_up:
                self.player_char.class_effects["Power Up"].active = True
                self.player_char.class_effects["Power Up"].duration = 1
            first = self.player_char
        elif self.enemy.invisible and not self.player_char.sight:
            first = self.enemy
        else:
            p_chance = self.player_char.check_mod("speed", enemy=self.enemy) + \
                    self.player_char.check_mod('luck', enemy=self.enemy, luck_factor=10)
            e_chance = self.enemy.check_mod("speed", enemy=self.player_char) + \
                    self.enemy.check_mod('luck', enemy=self.player_char, luck_factor=10)
            total_chance = p_chance + e_chance
            chance_list = [p_chance / total_chance, e_chance / total_chance]
            first = random.choices([self.player_char, self.enemy], chance_list)[0]

        second = self.enemy if first == self.player_char else self.player_char
        return first, second

    def execute_battle(self) -> bool:
        """Handles the entire battle flow."""
        # Emit combat start event
        from src.core.events.event_bus import get_event_bus, create_combat_event, EventType
        event_bus = get_event_bus()
        event_bus.emit(create_combat_event(
            EventType.COMBAT_START,
            actor=self.player_char,
            target=self.enemy,
            initiative=self.attacker == self.player_char,
            boss=self.boss
        ))

        self.logger.start_battle(
            self.player_char, self.enemy, initiative=self.attacker == self.player_char, boss=self.boss
        )
        while self.battle_continues():
            self.process_turn()

        self.end_battle()

        # Emit combat end event
        event_bus.emit(create_combat_event(
            EventType.COMBAT_END,
            actor=self.player_char,
            target=self.enemy,
            fled=self.flee,
            player_alive=self.player_char.is_alive(),
            enemy_alive=self.enemy.is_alive()
        ))

        return self.flee

    def battle_continues(self) -> bool:
        """Checks if the battle should continue."""
        self.render_screen()
        return all([self.player_char.is_alive() and self.enemy.is_alive(),
                    not self.flee])

    def process_turn(self) -> None:
        """Handles the flow of a single turn."""
        self.before_turn()
        self.take_turn()
        self.after_turn()

        # switch active user for next turn
        active_user = self.player_char
        if self.summon_active:
            active_user = self.summon
        if self.attacker == active_user:
            self.attacker, self.defender = self.enemy, active_user
        else:
            self.attacker, self.defender = active_user, self.enemy

    def take_turn(self) -> None:
        """Handles the active combatant's turn."""
        effects_text = self.attacker.effects()
        if effects_text:
            self.print_text(effects_text)
            if "damage" in effects_text:
                # handles exploding shield for Crusader
                try:
                    self.defender.health.current -= int(effects_text.split(" damage")[0].split(" ")[-1])
                except ValueError:
                    pass
        active, text = self.attacker.check_active()
        if not active:
            self.print_text(text)
        else:
            choice = None
            combat_text = ""
            if self.attacker.status_effects["Berserk"].active:
                action = "Attack"
            elif self.attacker.class_effects["Jump"].active:
                # If incapacitated while charging, cancel the Jump
                if self.attacker.incapacitated():
                    jump_choice = [x for x in self.attacker.spellbook['Skills'] if "Jump" in x][0]
                    jump_skill = self.attacker.spellbook['Skills'][jump_choice]
                    self.print_text(jump_skill.cancel_charge(self.attacker))
                    self.attacker.class_effects["Jump"].active = False
                else:
                    action = "Use Skill"
                    choice = [x for x in self.attacker.spellbook['Skills'] if "Jump" in x][0]
                    self.attacker.class_effects["Jump"].active = False
            else:
                if self.attacker == self.player_char:
                    while True:
                        choice = False
                        action = self.battle_ui.navigate_menu()
                        if action in ["Cast Spell", "Use Skill", "Use Item"]:
                            self.battle_popup.update_options(action, tile=self.tile)
                            choice = self.battle_popup.navigate_popup().split('  ')[0]
                        elif action == "Summon":
                            self.battle_popup.update_options("Summon", options=list(self.attacker.summons))
                            choice = self.battle_popup.navigate_popup()
                        elif action == "Untransform":
                            self.print_text(self.attacker.transform(back=True))
                        elif action == "Transform":
                            self.print_text(self.attacker.transform())
                        if action == "Attack" or (choice and choice != "Go Back"):
                            break
                        self.render_screen()
                else:
                    action, choice = self.enemy.options(self.player_char, self.available_actions, self.tile)
            self.execute_action(action, choice=choice, result=combat_text)
        self.companion_turn()

    def execute_action(self, action: str, choice: str=None, result: str=None):
        """Executes an attack or skill selection."""
        from src.core.events.event_bus import get_event_bus, create_combat_event, EventType
        event_bus = get_event_bus()

        if action == "Nothing":
            result = f"{self.attacker.name} does nothing."
        elif action == "Attack":
            # Emit attack event
            event_bus.emit(create_combat_event(
                EventType.ATTACK,
                actor=self.attacker,
                target=self.defender,
                is_special=False
            ))

            if not random.randint(0, 9 - self.attacker.check_mod("luck", luck_factor=20)):
                try:
                    result = self.attacker.special_attack(target=self.defender)
                    # Mark as special attack
                    event_bus.emit(create_combat_event(
                        EventType.ATTACK,
                        actor=self.attacker,
                        target=self.defender,
                        is_special=True
                    ))
                except NotImplementedError:
                    result, _, _ = self.attacker.weapon_damage(self.defender)
            else:
                result, _, _ = self.attacker.weapon_damage(self.defender)
        elif action == "Pickup Weapon":
            result = f"{self.attacker.name} picks up their weapon."
            self.attacker.physical_effects["Disarm"].active = False
        elif action == "Flee":
            event_bus.emit(create_combat_event(
                EventType.FLEE_ATTEMPT,
                actor=self.attacker,
                target=self.defender
            ))
            self.flee, result = self.attacker.flee(self.defender)
        elif action == "Defend":
            event_bus.emit(create_combat_event(
                EventType.DEFEND,
                actor=self.attacker,
                target=self.defender
            ))
            result = self.attacker.enter_defensive_stance(duration=1, source="Defend")
        elif action == "Cast Spell":
            # Emit spell cast event
            event_bus.emit(create_combat_event(
                EventType.SPELL_CAST,
                actor=self.attacker,
                target=self.defender,
                spell_name=choice
            ))
            result = f"{self.attacker.name} casts {choice}.\n"
            result += self.attacker.spellbook['Spells'][choice].cast(self.attacker, target=self.defender)
        elif action == "Use Skill":
            if choice == "Remove Shield":
                choice = "Mana Shield"
            skill = self.attacker.spellbook['Skills'][choice]

            # Emit skill use event
            event_bus.emit(create_combat_event(
                EventType.SKILL_USE,
                actor=self.attacker,
                target=self.defender,
                skill_name=skill.name
            ))

            result = f"{self.attacker.name} uses {skill.name}.\n"
            if skill.name == 'Smoke Screen':
                result += skill.use(self.attacker, target=self.defender)
                self.flee, flee_str = self.attacker.flee(self.defender, smoke=True)
                result += flee_str
            elif skill.name == "Slot Machine":
                result += skill.use(self.game, self.attacker, target=self.defender)
            elif skill.name in ["Doublecast", "Triplecast"]:
                result += skill.use(self.attacker, self.defender, game=self.game)
            elif "Jump" in skill.name:
                charge_time = skill.get_charge_time() if hasattr(skill, "get_charge_time") else 1
                if charge_time > 0:
                    self.attacker.class_effects["Jump"].active = True
                    result += f"{self.attacker.name} prepares to leap into the air.\n"
                result += skill.use(self.attacker, target=self.defender)
            else:
                result += skill.use(self.attacker, target=self.defender)
        elif action == "Use Item":
            itm = self.attacker.inventory[re.split(r"\s{2,}", choice)[0]][0]
            target = self.attacker
            if itm.subtyp == "Scroll":
                if itm.spell.subtyp != "Support":
                    target = self.defender

            # Emit item use event
            event_bus.emit(create_combat_event(
                EventType.ITEM_USE,
                actor=self.attacker,
                target=target,
                item_name=itm.name
            ))
            result = itm.use(self.attacker, target=target)
        elif action == "Summon":
            self.summon = self.attacker.summons[choice]
            self.attacker = self.summon
            result = f"{self.player_char.name} summons {self.summon.name} to aid them in combat."
        elif action == "Recall":
            result = f"{self.player_char.name} recalls {self.summon.name}."
            self.summon_active = False
            self.attacker = self.player_char
        elif action == "Totem":
            pass
        self.print_text(result)
        self.logger.log_event("Action", self.attacker, action=action, outcome=result)

    def companion_turn(self) -> None:
        """Handles the companion's turn."""  # TODO add other companions
        familiar_text = self.attacker.familiar_turn(self.defender)
        if familiar_text:
            self.print_text(familiar_text)
            self.logger.log_event("Familiar", self.attacker, target=self.defender, outcome=familiar_text)

    def end_battle(self) -> None:
        """Handles cleanup and post-battle results."""
        result = "victory" if self.player_char.is_alive() else "defeat"
        winner = self.player_char.name if self.player_char.is_alive() else self.enemy.name
        if self.flee:
            self.tile.enemy = None
            result = "flee"
            winner = None
        self.player_char.end_combat(self.game,
                                    self.enemy,
                                    self.tile,
                                    flee=self.flee,
                                    summon=self.summon,
                                    textbox=self.textbox)
        if self.player_char.is_alive() and self.boss:
            self.tile.defeated = True
            self.tile.enemy = None
        self.logger.end_battle(result=result, winner=winner, boss=self.boss)
        self.game.stdscr.getch()

    def before_turn(self) -> None:
        """Hook for pre-turn effects like buffs, debuffs, or AI strategy changes."""
        pass

    def after_turn(self) -> None:
        """Hook for post-turn effects."""
        if not self.flee:
            result = self.defender.special_effects(self.attacker)
            if result:
                self.print_text(result)
                self.logger.log_event(
                    "Special Effect", self.defender, target=self.attacker, outcome=result
                )
            self.available_actions = self.tile.available_actions(self.player_char)
            if self.summon_active:
                if self.summon.is_alive():
                    self.available_actions.append("Recall")
                else:
                    self.print_text(f"{self.summon.name} has been slain.")
                    self.summon_active = False
                    self.summon = None
                    self.defender = self.player_char
            if not self.defender.is_alive():
                if 'Resurrection' in self.defender.spellbook['Spells'] and \
                        abs(self.defender.health.current) <= self.defender.mana.current:
                    result = self.defender.spellbook['Spells']['Resurrection'].cast(self.defender)
                else:
                    if self.defender.name == "Behemoth":
                        result = self.defender.special_effects(self.attacker)
                if result:
                    self.print_text(result)
        self.logger.next_turn()
