#!/usr/bin/env python3
"""
GUI Game Launcher for Dungeon Crawl
Uses Pygame for graphical presentation instead of curses text interface.
"""

import sys
import signal

import pygame

from src.core.character import Combat, Level, Resource, Stats
from src.core.classes import classes_dict
from src.core.data.data_loader import get_special_events
from src.core.races import races_dict
from src.core.save_system import SaveManager
from src.core import items
from .presentation.pygame_presenter import PygamePresenter

# GUI modules
from .gui.shops import ShopManager
from .gui.church import ChurchManager
from .gui.inn import InnManager
from .gui.barracks import BarracksManager
from .gui.dungeon_manager import DungeonManager
from .gui.character_screen import CharacterScreen
from .gui.main_menu import MainMenuScreen
from .gui.load_game import LoadGameScreen
from .gui.race_selection import RaceSelectionScreen
from .gui.class_selection import ClassSelectionScreen
from .gui.confirmation_popup import ConfirmationPopup, confirm_yes_no
from .gui.town_menu import TownMenuScreen
from .gui.shop_selection import ShopSelectionScreen

# Use enhanced combat by default
USE_ENHANCED_COMBAT = True


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nExiting game...")
    pygame.quit()
    sys.exit(0)


# Set up signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)


class PygameGame:
    """
    GUI version of the Dungeon Crawl game using Pygame.
    """
    
    def __init__(self, debug_mode=False):
        pygame.init()
        self.presenter = PygamePresenter()
        self.presenter.game = self  # Expose game to presenter for managers (bounties, etc.)
        self.event_bus = self.presenter.event_bus  # Use the same event bus as presenter
        self.debug_mode = debug_mode
        self._random_combat = True
        self.load_files = SaveManager.list_saves()
        self.races_dict = races_dict
        self.classes_dict = classes_dict
        self.player_char = None
        self.running = True
        self.bounties = {}  # Populated by update_bounties()
        
        # Initialize managers (will be set after player_char is created)
        self.shop_manager = None
        self.church_manager = None
        self.inn_manager = None
        self.barracks_manager = None
        self.dungeon_manager = None
        
        # Initialize character menu
        # CharacterScreen is created on-demand when needed
        
        self.presenter.debug_mode = debug_mode  # Propagate debug mode to presenter

        # Provide a minimal curses-compatible shim for legacy code paths
        class _PygameStdscr:
            def __init__(self, presenter):
                self.presenter = presenter

            def getch(self):
                """Wait briefly for any key event and return a dummy value.

                Many legacy calls just block on `getch()` to pause until the user presses a key
                after a popup. Our GUI popups already block, so this can return immediately.
                """
                # Drain pending events to keep window responsive
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        return 13  # Enter key
                # No strict blocking required; return quickly
                return 13

            def getmaxyx(self):
                # Provide screen size for code that queries it
                return (self.presenter.height, self.presenter.width)

        # Attach shim so existing code using `game.stdscr.getch()` works in GUI mode
        self.stdscr = _PygameStdscr(self.presenter)

    def special_event(self, name: str):
        """GUI implementation of narrative special events.

        Displays a formatted modal message using the Pygame confirmation popup.
        """
        try:
            special_event_dict = get_special_events()
            lines = special_event_dict.get(name, {}).get("Text", [])
        except Exception:
            lines = []

        if lines:
            # Join lines into paragraphs and let the popup handle wrapping
            message = " ".join(line.strip() for line in lines if line is not None).strip()
        else:
            message = name

        # Show message-only popup (any key to continue)
        # Pass a background draw function that maintains current screen state
        def draw_current_screen():
            """Redraw the current game state (dungeon or town) to screen."""
            try:
                if self.dungeon_manager and self.player_char.location_z > 0:
                    # In dungeon: render the dungeon view
                    self.dungeon_manager._render()
                else:
                    # In town: render town (currently just black, which is fine)
                    # The TownMenuScreen would be responsible for drawing if we're in town UI
                    pass
            except Exception:
                pass
        
        popup = ConfirmationPopup(self.presenter, message, show_buttons=False, slow_print=True)
        popup.show(
            background_draw_func=draw_current_screen,
            flush_events=True,
            require_key_release=True,
            min_display_ms=300
        )

    def debug_level_up(self):
        """Debug-only shortcut to trigger a single level-up."""
        if not self.debug_mode or not self.player_char:
            return
        if self.player_char.max_level():
            self.presenter.show_message("Already at max level.")
            return
        
        # Add the experience needed to level up and reset exp_to_gain
        self.player_char.level.exp += self.player_char.level.exp_to_gain
        self.player_char.level.exp_to_gain = 0
        
        from .gui.level_up import LevelUpScreen

        level_up_screen = LevelUpScreen(self.presenter.screen, self.presenter)
        level_up_screen.show_level_up(self.player_char, self)
    
    def initialize_managers(self):
        """Initialize location managers after player character is created."""
        self.shop_manager = ShopManager(self.presenter, self.player_char)
        self.church_manager = ChurchManager(self.presenter, self.player_char)
        self.inn_manager = InnManager(self.presenter, self.player_char)
        self.barracks_manager = BarracksManager(self.presenter, self.player_char)
        self.dungeon_manager = DungeonManager(self.presenter, self.player_char, self)

    def _build_player_character(self, race_name, class_name, name="Hero"):
        """Build a player character from selected race/class and name."""
        from src.core.player import Player

        race_ctor = self.races_dict.get(race_name)
        class_entry = self.classes_dict.get(class_name, {})
        class_ctor = class_entry.get("class") if isinstance(class_entry, dict) else None

        if race_ctor is None:
            race_name, race_ctor = next(iter(self.races_dict.items()))
        race = race_ctor()

        if class_ctor is None:
            class_name = race.cls_res["Base"][0]
            class_ctor = self.classes_dict[class_name]["class"]
        char_class = class_ctor()

        location_x, location_y, location_z = (5, 10, 0)
        stats_tuple = tuple(map(
            lambda x, y: x + y,
            (race.strength, race.intel, race.wisdom, race.con, race.charisma, race.dex),
            (char_class.str_plus, char_class.int_plus, char_class.wis_plus,
             char_class.con_plus, char_class.cha_plus, char_class.dex_plus)
        ))
        hp = stats_tuple[3] * 2
        mp = stats_tuple[1] * 2
        attack = race.base_attack + char_class.att_plus
        defense = race.base_defense + char_class.def_plus
        magic = race.base_magic + char_class.magic_plus
        magic_def = race.base_magic_def + char_class.magic_def_plus
        gold = stats_tuple[4] * 25

        player_char = Player(
            location_x, location_y, location_z,
            level=Level(),
            health=Resource(hp, hp),
            mana=Resource(mp, mp),
            stats=Stats(stats_tuple[0], stats_tuple[1], stats_tuple[2],
                       stats_tuple[3], stats_tuple[4], stats_tuple[5]),
            combat=Combat(attack=attack, defense=defense, magic=magic, magic_def=magic_def),
            gold=gold,
            resistance=race.resistance
        )
        player_char.name = name or "Hero"
        player_char.race = race
        player_char.cls = char_class
        player_char.equipment = char_class.equipment

        from ..core import abilities
        if "1" in abilities.spell_dict.get(char_class.name, {}):
            spell_gain = abilities.spell_dict[char_class.name]["1"]()
            player_char.spellbook['Spells'][spell_gain.name] = spell_gain

        player_char.storage["Health Potion"] = [items.HealthPotion() for _ in range(5)]
        player_char.load_tiles()
        return player_char

    def create_default_character(self, name="Hero"):
        """Create a default preview character for quick UI testing."""
        return self._build_player_character(race_name="Human", class_name="Warrior", name=name)
        
    def main_menu(self):
        """Display main menu and handle selection."""
        # Check debug mode settings
        if self.debug_mode:
            if confirm_yes_no(self.presenter, "Debug Mode - Turn off random encounters?"):
                self._random_combat = False
                popup = ConfirmationPopup(self.presenter, "Random encounters disabled", show_buttons=False)
                popup.show()
            else:
                self._random_combat = True
                popup = ConfirmationPopup(self.presenter, "Random encounters enabled", show_buttons=False)
                popup.show()
        
        # Create main menu screen
        main_menu = MainMenuScreen(self.presenter)
        
        while self.running:
            # Build menu options each iteration to pick up new save files
            menu_options = ['New Game']
            if self.load_files:
                menu_options.append('Load Game')
            menu_options.append('Settings')
            menu_options.append('Exit')
            
            choice = main_menu.navigate(menu_options)
            
            if choice is None:
                # ESC pressed
                self.running = False
            elif menu_options[choice] == 'New Game':
                self.player_char = self.new_game()
                if self.player_char:
                    self.run()
            elif menu_options[choice] == 'Load Game':
                self.player_char = self.load_game()
                if self.player_char:
                    self.run()
            elif menu_options[choice] == 'Settings':
                # TODO: Implement settings menu
                self.presenter.show_message("Settings menu coming soon!")
            elif menu_options[choice] == 'Exit':
                self.running = False
                
    def new_game(self):
        """Create a new character."""
        # Loop for race selection with confirmation
        while True:
            # Choose race using RaceSelectionScreen
            race_screen = RaceSelectionScreen(self.presenter)
            race_name = race_screen.navigate(self.races_dict)
            if race_name is None:
                return None  # ESC pressed, return to main menu
            race = self.races_dict[race_name]()  # Instantiate the race class
            
            # Confirm race selection with popup
            confirm_race = ConfirmationPopup(
                self.presenter,
                f"You have selected {race_name} as your race. Continue?",
                show_buttons=True,
            )
            if confirm_race.show():
                break  # Yes selected, continue to class selection
            # No selected, loop back to race selection
        
        # Loop for class selection with confirmation
        while True:
            # Choose class using ClassSelectionScreen
            class_screen = ClassSelectionScreen(self.presenter)
            class_name = class_screen.navigate(race_name, race, self.classes_dict)
            if class_name is None:
                return None  # ESC pressed, return to main menu
            char_class = self.classes_dict[class_name]["class"]()  # Get class from nested dict
            
            # Confirm class selection with popup
            confirm_class = ConfirmationPopup(
                self.presenter,
                f"You have selected {class_name} as your class. Continue?",
                show_buttons=True,
            )
            if confirm_class.show():
                break  # Yes selected, continue to name input
            # No selected, loop back to class selection
        
        # Get character name (moved to after race and class selection)
        self.presenter.show_message("Create Your Character")
        name = self.presenter.get_text_input("Enter your character name:")
        if not name:
            name = "Hero"  # Default name
        
        # Create player character using the same logic as the original game
        player_char = self._build_player_character(race_name, class_name, name=name)
        
        self.presenter.show_message(
            f"Character Created!\n\n"
            f"Name: {name}\n"
            f"Race: {race_name}\n"
            f"Class: {class_name}\n\n"
            f"HP: {player_char.health.max}\n"
            f"MP: {player_char.mana.max}"
        )
        
        self.player_char = player_char
        self.initialize_managers()  # Initialize location managers
        
        return player_char
        
    def load_game(self):
        """Load a saved game."""
        if not self.load_files:
            self.presenter.show_message("No saved games found!")
            return None
        
        # Use the new LoadGameScreen interface
        load_screen = LoadGameScreen(self.presenter)
        selected_file = load_screen.navigate(self.load_files)
        
        if selected_file is None:
            return None
        
        # Show loading popup similar to curses UI
        self.presenter.show_progress_popup(header="Load Game", message="Loading game file...")

        # Load the character from the selected file
        player_char = SaveManager.load_player(selected_file)
        if player_char is None:
            self.presenter.show_message("Failed to load character!")
            return None
            
        # Reset quit flag - player is loading to continue playing
        player_char.quit = False
        
        # Set flag to suppress heal message if loading in town
        if player_char.in_town():
            player_char._suppress_heal_message = True
        # Skip blocking message; jump straight into the game
        
        self.player_char = player_char
        self.initialize_managers()
        
        return player_char
        
    def run(self):
        """Main game loop."""
        if not self.player_char:
            return

        # Ensure bounties are available for GUI bounty board
        self.update_bounties()
        
        # Show intro story for new characters (level 1)
        if self.player_char.level.level == 1 and not hasattr(self.player_char, 'intro_shown'):
            self.show_intro()
            self.player_char.intro_shown = True
            
        # Main game loop
        while True:
            # Check if player quit
            if self.player_char.quit:
                break
                
            # Check if player is in town
            if self.player_char.in_town():
                choice = self.town_menu()
                if choice == "quit":
                    break
                elif choice == "dungeon":
                    # Enter the dungeon in first-person mode
                    self.enter_dungeon()
            else:
                # Already in dungeon - show exploration interface
                self.enter_dungeon()

    def update_bounties(self):
        """Generate bounties (parity with text-mode game)."""
        from src.core import town

        bounty_board = town.BountyBoard()
        bounty_board.generate_bounties(self)
        self.bounties = {bounty["enemy"].name: bounty for bounty in bounty_board.bounties}
    
    def show_intro(self):
        """Show the game introduction story."""
        intro_texts = [
            "A great evil has taken hold in the unlikeliest of places,\n"
            "a small town on the edge of the kingdom.",
            
            "The town of Silvana has sent out a plea for help,\n"
            "with many coming from far and wide to test their mettle.",
            
            "You, bright-eyed and bushy-tailed,\n"
            "decided that fame and glory were within reach.",
            
            "What you didn't know was that all who had attempted this feat\n"
            "have never been heard from again.",
            
            "Will you be different or just another lost soul?"
        ]
        
        for text in intro_texts:
            self.presenter.show_message(text, "The Story Begins...")

    def town_menu(self):
        """Display town menu and handle selection."""
        # Build options list first so it can be reused for popups
        options = [
            "Visit Barracks",
            "Visit Shop",
            "Visit Inn",
            "Visit Church",
            "Enter Dungeon",
            "Character Menu",
        ]

        # Add Warp Point or Old Warehouse based on player progress
        if getattr(self.player_char, 'warp_point', False):
            options.insert(5, "Warp Point")
        else:
            options.insert(5, "Old Warehouse")

        options.append("Quit to Main Menu")
        
        # Create and use the new town menu screen
        town_screen = TownMenuScreen(self.presenter)
        
        # Auto-heal when entering town menu
        try:
            self.player_char.town_heal()
            # Check if we should suppress the heal message (loading in town)
            if not getattr(self.player_char, '_suppress_heal_message', False):
                popup = ConfirmationPopup(self.presenter, "You rest in town. HP and MP fully restored.", show_buttons=False)
                popup.show(background_draw_func=lambda: (town_screen.draw_background(), town_screen.draw_menu_panel(options)))
            else:
                # Clear the flag after first use
                self.player_char._suppress_heal_message = False
        except Exception:
            # If any issue occurs, continue without blocking town menu
            pass

        # Check for Rookie Mistake quest completion upon entering town
        if ("Dead Soldier" in self.player_char.special_inventory and 
                'Rookie Mistake' in self.player_char.quest_dict.get('Side', {}) and
                not self.player_char.quest_dict['Side']['Rookie Mistake']['Completed']):
            self.player_char.quest_dict['Side']['Rookie Mistake']['Completed'] = True
            self.player_char.modify_inventory(items.DeadSoldier(), subtract=True, rare=True)
            popup = ConfirmationPopup(self.presenter, "You have completed the quest Rookie Mistake.", show_buttons=False)
            popup.show(background_draw_func=lambda: (town_screen.draw_background(), town_screen.draw_menu_panel(options)))

        while True:
            choice_idx = town_screen.navigate(options)
            
            if choice_idx is None or choice_idx == len(options) - 1:  # Quit
                popup = ConfirmationPopup(self.presenter, "Return to the main menu?")
                if popup.show(background_draw_func=lambda: (town_screen.draw_background(), town_screen.draw_menu_panel(options))):
                    return "quit"
                continue

            elif choice_idx == 0:  # Visit Barracks
                self.visit_barracks()

            elif choice_idx == 1:  # Visit Shop
                self.visit_shop()

            elif choice_idx == 2:  # Visit Inn
                self.visit_inn()
                
            elif choice_idx == 3:  # Visit Church
                self.visit_church()

            elif choice_idx == 4:  # Enter Dungeon
                # Move player to dungeon entrance
                if self.player_char.location_z == 0:
                    # Town is at (5, 10, 0), stairs up from dungeon are at (5, 10, 1)
                    self.player_char.location_x = 5
                    self.player_char.location_y = 10
                    self.player_char.location_z = 1  # First dungeon level (map_level_1.txt)
                    self.player_char.facing = "east"  # Face into dungeon (east has CavePath0)
                return "dungeon"

            elif choice_idx == 5:  # Warp Point or Old Warehouse
                if getattr(self.player_char, 'warp_point', False):
                    result = self.use_warp_point()
                    if result == "dungeon":
                        return "dungeon"
                else:
                    popup = ConfirmationPopup(self.presenter, "Authorized personnel only.\nPlease leave.", show_buttons=False)
                    popup.show(background_draw_func=lambda: (town_screen.draw_background(), town_screen.draw_menu_panel(options)))

            elif choice_idx == 6:  # Character Menu
                self.show_character_info()
                # Check if player quit while in character menu
                if self.player_char.quit:
                    return "quit"

    def use_warp_point(self):
        """Use the warp point to teleport to dungeon level 5."""
        confirm = self.presenter.render_menu(
            f"Hello, {self.player_char.name}.\n\nDo you want to warp down to level 5?",
            ["Yes", "No"]
        )
        
        if confirm == 0:  # Yes
            # Mark the destination as visited
            if (3, 0, 5) in self.player_char.world_dict:
                if not self.player_char.world_dict[(3, 0, 5)].visited:
                    self.player_char.world_dict[(3, 0, 5)].visited = True
                    # Mark adjacent tiles as near
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        adj_pos = (3 + dx, 0 + dy, 5)
                        if adj_pos in self.player_char.world_dict:
                            self.player_char.world_dict[adj_pos].near = True
                
                # Mark as warped
                self.player_char.world_dict[(3, 0, 5)].warped = True
            
            self.presenter.show_message(
                "You step into the warp point,\n"
                "taking you deep into the dungeon."
            )
            
            # Warp player to level 5
            self.player_char.location_x = 3
            self.player_char.location_y = 0
            self.player_char.location_z = 5
            self.player_char.facing = "south"
            
            # Return to dungeon
            return "dungeon"
        else:
            self.presenter.show_message("Not a problem, come back when you change your mind.")
    
    def visit_shop(self):
        """Visit the town shop - routes to appropriate shop via ShopManager."""
        shop_options = ["Blacksmith", "Alchemist", "Jeweler", "Go Back"]
        
        # Create shop selection screen
        shop_screen = ShopSelectionScreen(self.presenter)
        
        while True:
            choice = shop_screen.navigate(shop_options)
            
            if choice is None or choice == 3:  # Go Back
                break
                
            elif choice == 0:  # Blacksmith
                self.shop_manager.visit_blacksmith()
            elif choice == 1:  # Alchemist
                self.shop_manager.visit_alchemist()
            elif choice == 2:  # Jeweler
                self.shop_manager.visit_jeweler()
    
    def visit_church(self):
        """Visit the Church - managed by ChurchManager."""
        self.church_manager.visit_church()
    
    def visit_barracks(self):
        """Visit the Barracks - managed by BarracksManager."""
        self.barracks_manager.visit_barracks()
    
    def visit_inn(self):
        """Visit the Inn/Tavern - managed by InnManager."""
        self.inn_manager.visit_inn()
    
    def enter_dungeon(self):
        """Enter first-person dungeon exploration mode."""
        # Use DungeonManager for exploration
        self.dungeon_manager.explore_dungeon()

        if hasattr(self.presenter, "set_background_provider"):
            self.presenter.set_background_provider(None)
        
        # After exiting dungeon (returned to town, quit, etc.)
        # Check if player quit the game
        if self.player_char.quit:
            return
    
    def show_character_info(self):
        """Display character information using the character screen."""
        char_screen = CharacterScreen(self.presenter)

        while True:
            choice = char_screen.navigate(self.player_char)

            if choice == "Exit Menu":
                break
            elif choice == "Quit Game":
                from .gui.confirmation_popup import confirm_yes_no
                if confirm_yes_no(self.presenter, "Are you sure you want to quit?"):
                    self.player_char.quit = True
                    break
    
    def save_game(self):
        """Save the current game."""
        filename = f"{str(self.player_char.name).lower()}.save"

        if SaveManager.save_player(self.player_char, filename):
            self.presenter.show_message(
                f"Game saved successfully!\n\nSaved to: save_files/{filename}"
            )
            self.load_files = SaveManager.list_saves()
        else:
            self.presenter.show_message("Save failed. Please try again.")
        
    def cleanup(self):
        """Clean up resources."""
        self.presenter.cleanup()
        pygame.quit()


def main():
    """Entry point for GUI game."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dungeon Crawl GUI Game')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (disable random combat)')
    parser.add_argument(
        '--character-menu',
        action='store_true',
        help='Launch directly into Character Menu using a default Human Warrior character'
    )
    parser.add_argument(
        '--preview-name',
        default='Menu Preview',
        help='Character name used with --character-menu (default: Menu Preview)'
    )
    args = parser.parse_args()
    
    try:
        game = PygameGame(debug_mode=args.debug)
        if args.character_menu:
            game.player_char = game.create_default_character(name=args.preview_name)
            game.initialize_managers()
            game.show_character_info()
        else:
            game.main_menu()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'game' in locals():
            game.cleanup()


if __name__ == '__main__':
    main()
