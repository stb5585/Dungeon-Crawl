"""
This module handles combat between the player and enemies. It includes functions for determining initiative, handling
turns, and executing actions. The BattleManager class manages the flow of combat, while the BattleLogger class records
combat events for later analysis.
"""
from __future__ import annotations

import datetime
import random
import re
from typing import TYPE_CHECKING

from utils import CombatMenu, CombatPopupMenu, TextBox

if TYPE_CHECKING:
    from enemies import Enemy
    from game import Game
    from character import Character
    from player import Player
    from map_tiles import MapTile


class BattleLogger:
    def __init__(self):
        self.events = []
        self.metadata = {}
        self.turn_counter = 0

    def start_battle(self, player: Player, enemy: Enemy, initiative: bool, boss: bool) -> None:
        """
        Initializes the battle logger with metadata about the battle.
        Args:
            player (Player): The player character.
            enemy (Enemy): The enemy character.
        """
        self.metadata = {
            "start_time": datetime.datetime.now().isoformat(),
            "player": {
                "name": player.name,
                "cls": player.cls.name,
                "level": player.level.level,
                "pro level": player.level.pro_level,
                "attributes": player.stats,
                "combat stats": player.combat,
                "hp": player.health.current,
                "mp": player.mana.current,
                "resistances": player.resistance,
                "dungeon level": player.location_z,
                "initiative": initiative,
            },
            "enemy": {
                "name": enemy.name,
                "type": enemy.enemy_typ,
                "level": enemy.level,
                "attributes": enemy.stats,
                "combat stats": player.combat,
                "hp": enemy.health.current,
                "mp": enemy.mana.current,
                "resistances": enemy.resistance,
                "boss": boss,
            }
        }

    def log_event(
            self,
            event_type: str,
            actor: Character,
            target: Character=None,
            action: str=None,
            outcome: str=None,
            damage: int=None,
            flags: list=None,
            status_changes: dict=None,
            notes: str=None,
            ) -> None:
        """
        Logs a combat event with details about the action taken.
        Args:
            event_type (str): The type of event (e.g., "attack", "spell", "item").
            actor (Character): The character performing the action.
            target (Character): The character being targeted (if applicable).
            action (str): The action taken (e.g., "attack", "spell", "item").
            outcome (str): The outcome of the action.
            damage (int): The amount of damage dealt (if applicable).
            flags (list): Any special flags or conditions associated with the event.
                Example: ["critical", "miss", "dodge"]
            status_changes (dict): Any changes to status effects or conditions.
            notes (str): Additional notes about the event.
        """
        event = {
            "turn": self.turn_counter,
            "event_type": event_type,
            "actor": actor.name if actor else None,
            "target": target.name if target else None,
            "action": action,
            "outcome": outcome,
            "damage": damage,
            "flags": flags or [],
            "status_changes": status_changes or {},
            "notes": notes,
            "actor_health": actor.health.current / actor.health.max if actor else None,
            "actor_mana": actor.mana.current / actor.mana.max if actor else None,
            "target_health": target.health.current / target.health.max if target else None,
            "target_mana": target.mana.current / target.mana.max if target else None,
        }
        self.events.append(event)

    def next_turn(self) -> None:
        self.turn_counter += 1

    def end_battle(self, result: str, winner: str | None, boss: bool) -> None:
        self.metadata.update({
            "result": result,
            "winner": winner,
            "boss": boss,
            "turns": self.turn_counter,
            "end_time": datetime.datetime.now().isoformat(),
        })

    def export(self) -> list:
        """
        Exports the logged events for analysis or storage.
        Returns:
            list: A list of dictionaries containing the logged events.
        """
        # This could be extended to save to a file or database
        # For now, we just return the events
        # as a list of dictionaries
        # Example: [{"event": "attack", "actor": "Player", "target": "Enemy", "details": "Hit for 10 damage"}]
        # This is a placeholder for actual export logic
        # You could save to a JSON file or a database here
        return self.events


class BattleManager:
    """
    Handles the flow of combat between the player and an enemy.
    
    Attributes:
        game (Game): The current game instance.
        player_char (Character): The player character.
        enemy (Character): The enemy character.
        logger (BattleLogger): The logger for recording combat events.
        flee (bool): Whether the player has chosen to flee combat.
        tile (MapTile): The current tile the player is on.
        battle_ui (CombatMenu): The UI for the battle screen.
        battle_popup (CombatPopupMenu): The UI for selecting spells, skills, or items.
        textbox (TextBox): The UI for displaying text.
        available_actions (list): The actions the player can take in combat.
        summon_active (bool): Whether the player has summoned a companion.
        summon (Character): The player's summoned companion.
        attacker (Character): The character currently taking their turn.
        defender (Character): The character currently being attacked.
    """

    def __init__(
            self,
            game: Game,
            enemy: Character,
            logger: BattleLogger | None = None,
            ):
        self.game = game
        self.player_char: Character = game.player_char
        self.enemy = enemy
        self.logger = logger if logger else BattleLogger()
        self.flee: bool = False
        self.tile: MapTile = game.player_char.world_dict[(game.player_char.location_x,
                                                          game.player_char.location_y,
                                                          game.player_char.location_z)]
        self.boss = False if "Boss" not in str(self.tile) else True
        self.battle_ui = CombatMenu(game)
        self.battle_popup = CombatPopupMenu(game)
        self.textbox = TextBox(game)
        self.available_actions: list = self.tile.available_actions(game.player_char)
        self.summon_active: bool = False
        self.summon: Character = None
        self.attacker, self.defender = self.determine_initiative()

    def render_screen(self) -> None:
        """Renders the battle screen."""
        vision = all([self.player_char.sight,
                      "Boss" not in str(self.tile),
                      self.enemy.name != "Waitress"])
        self.battle_ui.draw_enemy(self.enemy, vision=vision)
        self.battle_ui.draw_options(self.available_actions)
        if self.summon_active:
            self.battle_ui.draw_char(char=self.summon)
        else:
            self.battle_ui.draw_char()
        self.battle_ui.refresh_all()

    def print_text(self, text: str) -> None:
        """Prints text to the screen."""
        self.textbox.print_text_in_rectangle(text)
        self.game.stdscr.getch()
        self.textbox.clear_rectangle()

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
        self.logger.start_battle(
            self.player_char, self.enemy, initiative=self.attacker == self.player_char, boss=self.boss
            )
        while self.battle_continues():
            self.process_turn()

        self.end_battle()
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
        if action == "Nothing":
            result = f"{self.attacker.name} does nothing."
        elif action == "Attack":
            if not random.randint(0, 9 - self.attacker.check_mod("luck", luck_factor=20)):
                try:
                    result = self.attacker.special_attack(target=self.defender)
                except NotImplementedError:
                    result, _, _ = self.attacker.weapon_damage(self.defender)
            else:
                result, _, _ = self.attacker.weapon_damage(self.defender)
        elif action == "Pickup Weapon":
            result = f"{self.attacker.name} picks up their weapon."
            self.attacker.physical_effects["Disarm"].active = False
        elif action == "Flee":
            self.flee, result = self.attacker.flee(self.defender)
        elif action == "Cast Spell":
            result = self.attacker.spellbook['Spells'][choice].cast(self.attacker, target=self.defender)
        elif action == "Use Skill":
            if choice == "Remove Shield":
                choice = "Mana Shield"
            skill = self.attacker.spellbook['Skills'][choice]
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
                self.attacker.class_effects["Jump"].active = True
                result += f"{self.attacker.name} prepares to leap into the air.\n"
            else:
                result += skill.use(self.attacker, target=self.defender)
        elif action == "Use Item":
            itm = self.attacker.inventory[re.split(r"\s{2,}", choice)[0]][0]
            target = self.attacker
            if itm.subtyp == "Scroll":
                if itm.spell.subtyp != "Support":
                    target = self.defender
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
                                    summon=self.summon)
        if self.player_char.is_alive() and self.boss:
            self.tile.defeated = True
        self.logger.end_battle(result=result, winner=winner, boss=self.boss)

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
