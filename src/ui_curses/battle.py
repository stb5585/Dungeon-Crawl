"""
BattleManager for curses-based UI combat.

Thin UI wrapper around the core BattleEngine.  All game-mechanical logic
(action execution, status effects, initiative, etc.) lives in the engine;
this class is responsible only for curses rendering and player input.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.battle_engine import BattleEngine
from src.core.combat.battle_logger import BattleLogger

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character


class BattleManager:
    """
    Curses UI wrapper for combat.

    Delegates all combat logic to :class:`BattleEngine` and provides
    curses-specific rendering, text output, and player input.

    Attributes:
        game: The current game instance.
        engine: The core BattleEngine driving combat logic.
        battle_ui: The UI for the battle screen.
        battle_popup: The UI for selecting spells, skills, or items.
        textbox: The UI for displaying text.
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
        self.battle_ui = battle_ui
        self.battle_popup = battle_popup
        self.textbox = textbox

        player = game.player_char
        tile = player.world_dict[(player.location_x, player.location_y, player.location_z)]

        self.engine = BattleEngine(
            player=player,
            enemy=enemy,
            tile=tile,
            game=game,
            logger=logger,
        )

    # ── Convenience accessors (keep API compatible for subclasses) ───

    @property
    def player_char(self) -> Character:
        return self.engine.player

    @property
    def enemy(self) -> Character:
        return self.engine.enemy

    @property
    def tile(self) -> Any:
        return self.engine.tile

    @property
    def logger(self) -> BattleLogger:
        return self.engine.logger

    @property
    def flee(self) -> bool:
        return self.engine.flee

    @flee.setter
    def flee(self, value: bool) -> None:
        self.engine.flee = value

    @property
    def boss(self) -> bool:
        return self.engine.boss

    @property
    def available_actions(self) -> list:
        return self.engine.available_actions

    @available_actions.setter
    def available_actions(self, value: list) -> None:
        self.engine.available_actions = value

    @property
    def summon_active(self) -> bool:
        return self.engine.summon_active

    @summon_active.setter
    def summon_active(self, value: bool) -> None:
        self.engine.summon_active = value

    @property
    def summon(self) -> Character | None:
        return self.engine.summon

    @summon.setter
    def summon(self, value: Character | None) -> None:
        self.engine.summon = value

    @property
    def attacker(self) -> Character | None:
        return self.engine.attacker

    @attacker.setter
    def attacker(self, value: Character | None) -> None:
        self.engine.attacker = value

    @property
    def defender(self) -> Character | None:
        return self.engine.defender

    @defender.setter
    def defender(self, value: Character | None) -> None:
        self.engine.defender = value

    @property
    def charging_ability(self):
        return self.engine.charging_ability

    @charging_ability.setter
    def charging_ability(self, value) -> None:
        self.engine.charging_ability = value

    # ── UI methods (curses-specific) ─────────────────────────────────

    def render_screen(self) -> None:
        """Renders the battle screen."""
        vision = self.engine.show_enemy_details()
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

    # ── Battle flow ──────────────────────────────────────────────────

    def determine_initiative(self) -> tuple[Character, Character]:
        """Determine who goes first using each character's dexterity plus luck."""
        return self.engine.start_battle()

    def execute_battle(self) -> bool:
        """Handles the entire battle flow."""
        self.engine.start_battle()

        while self.battle_continues():
            self.process_turn()

        self.end_battle()
        return self.flee

    def battle_continues(self) -> bool:
        """Checks if the battle should continue."""
        self.render_screen()
        return self.engine.battle_continues()

    def process_turn(self) -> None:
        """Handles the flow of a single turn."""
        self.before_turn()
        self.take_turn()
        self.after_turn()
        self.engine.swap_turns()

    def before_turn(self) -> None:
        """Pre-turn hook. Subclasses may override for queue-based processing."""
        pass

    def after_turn(self) -> None:
        """Post-turn: process special effects, summon state, resurrection."""
        post = self.engine.post_turn()
        for msg in post.messages:
            if msg:
                self.print_text(msg)

    def take_turn(self) -> None:
        """Handles the active combatant's turn."""
        # Pre-turn: process status effects, check if attacker can act
        pre = self.engine.pre_turn()
        if pre.effects_text:
            self.print_text(pre.effects_text)

        # If the attacker died from effects (poison, DOT, bleed), skip turn
        if pre.died_from_effects:
            return

        if not pre.can_act:
            self.print_text(pre.inactive_reason)
        else:
            # Check for forced actions (berserk, charging, jump)
            forced = self.engine.get_forced_action()
            if forced:
                if forced.action == "Cancelled":
                    # Jump was cancelled due to incapacitation
                    self.print_text(forced.cancel_message)
                else:
                    self.execute_action(forced.action, choice=forced.choice)
            elif self.engine.is_player_turn():
                # Get player input via curses UI
                action, choice = self._get_player_input()
                self.execute_action(action, choice=choice)
            else:
                # Enemy AI chooses action
                action, choice = self.engine.get_enemy_action()
                self.execute_action(action, choice=choice)

        # Companion / familiar turn
        companion_msg = self.engine.companion_turn()
        if companion_msg:
            self.print_text(companion_msg)

    def _get_player_input(self) -> tuple[str, str | None]:
        """Get the player's action choice via curses menus. Returns (action, choice)."""
        while True:
            choice = False
            action = self.battle_ui.navigate_menu()
            if action in ["Cast Spell", "Use Skill", "Use Item"]:
                self.battle_popup.update_options(action, tile=self.tile)
                choice = self.battle_popup.navigate_popup().split('  ')[0]
            elif action == "Summon":
                self.battle_popup.update_options(
                    "Summon", options=list(self.engine.attacker.summons)
                )
                choice = self.battle_popup.navigate_popup()
            elif action == "Untransform":
                self.print_text(self.engine.attacker.transform(back=True))
            elif action == "Transform":
                self.print_text(self.engine.attacker.transform())
            if action == "Attack" or (choice and choice != "Go Back"):
                break
            self.render_screen()
        return action, choice if choice else None

    def execute_action(self, action: str, choice: str = None, result: str = None):
        """Executes an action by delegating to the core engine."""
        action_result = self.engine.execute_action(action, choice=choice)

        # Sync flee state (engine updates it internally, but Smoke Screen
        # sets it via the skill's flee call inside the engine)
        # Sync summon state for Summon/Recall actions
        if action_result.summon_started:
            self.engine.summon_active = True
        if action_result.summon_recalled:
            self.engine.summon_active = False

        self.print_text(action_result.message)

    def companion_turn(self) -> None:
        """Handles the companion's turn (called from EnhancedBattleManager)."""
        companion_msg = self.engine.companion_turn()
        if companion_msg:
            self.print_text(companion_msg)

    def end_battle(self) -> None:
        """Handles cleanup and post-battle results (curses-specific)."""
        # Use player.end_combat for curses (handles textbox output)
        result_str = "victory" if self.player_char.is_alive() else "defeat"
        winner = self.player_char.name if self.player_char.is_alive() else self.enemy.name
        if self.flee:
            self.tile.enemy = None
            result_str = "flee"
            winner = None
        self.player_char.end_combat(
            self.game, self.enemy, self.tile,
            flee=self.flee, summon=self.summon, textbox=self.textbox,
        )
        if self.player_char.is_alive() and self.boss:
            self.tile.defeated = True
            self.tile.enemy = None
        self.logger.end_battle(result=result_str, winner=winner, boss=self.boss)

        # Emit combat end event
        from src.core.events.event_bus import get_event_bus, create_combat_event, EventType
        get_event_bus().emit(create_combat_event(
            EventType.COMBAT_END,
            actor=self.player_char,
            target=self.enemy,
            fled=self.flee,
            player_alive=self.player_char.is_alive(),
            enemy_alive=self.enemy.is_alive(),
        ))

        self.game.stdscr.getch()
