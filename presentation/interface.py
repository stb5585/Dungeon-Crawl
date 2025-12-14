"""
Presentation Layer Interface

This module defines the abstract interface that all presenters must implement.
This allows the game logic to remain independent of the UI technology (curses, pygame, web, etc.)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from character import Character


class GamePresenter(ABC):
    """
    Abstract base class for game presentation/rendering.
    
    All UI implementations (terminal, GUI, web) should inherit from this
    and implement these methods.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the presenter (setup window, screen, etc.)"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources (close window, restore terminal, etc.)"""
        pass
    
    @abstractmethod
    def render_combat(
        self,
        player: Character,
        enemy: Character,
        available_actions: list[str],
        message: str = ""
    ) -> None:
        """
        Render the combat screen.
        
        Args:
            player: The player character
            enemy: The enemy character
            available_actions: List of actions the player can take
            message: Optional message to display
        """
        pass
    
    @abstractmethod
    def render_menu(
        self,
        title: str,
        options: list[str],
        selected_index: int = 0
    ) -> None:
        """
        Render a menu screen.
        
        Args:
            title: Menu title
            options: List of menu options
            selected_index: Currently selected option index
        """
        pass
    
    @abstractmethod
    def render_character_sheet(self, character: Character) -> None:
        """
        Render the character sheet/stats screen.
        
        Args:
            character: The character to display
        """
        pass
    
    @abstractmethod
    def render_map(
        self,
        world_map: list[list[str]],
        player_x: int,
        player_y: int
    ) -> None:
        """
        Render the game map.
        
        Args:
            world_map: 2D array representing the map
            player_x: Player's X coordinate
            player_y: Player's Y coordinate
        """
        pass
    
    @abstractmethod
    def show_message(
        self,
        message: str,
        wait_for_input: bool = True
    ) -> None:
        """
        Display a message to the player.
        
        Args:
            message: The message to display
            wait_for_input: Whether to wait for user input before continuing
        """
        pass
    
    @abstractmethod
    def show_dialogue(
        self,
        speaker: str,
        text: str,
        choices: list[str] = None
    ) -> int | None:
        """
        Display dialogue with optional choices.
        
        Args:
            speaker: Name of the speaking character/NPC
            text: The dialogue text
            choices: Optional list of response choices
            
        Returns:
            Index of selected choice, or None if no choices
        """
        pass
    
    @abstractmethod
    def get_player_action(
        self,
        available_actions: list[str]
    ) -> str:
        """
        Get the player's chosen action.
        
        Args:
            available_actions: List of valid actions
            
        Returns:
            The selected action
        """
        pass
    
    @abstractmethod
    def get_text_input(self, prompt: str, max_length: int = 50) -> str:
        """
        Get text input from the player.
        
        Args:
            prompt: The input prompt
            max_length: Maximum allowed input length
            
        Returns:
            The entered text
        """
        pass
    
    @abstractmethod
    def confirm(self, question: str) -> bool:
        """
        Ask for yes/no confirmation.
        
        Args:
            question: The question to ask
            
        Returns:
            True for yes, False for no
        """
        pass
    
    @abstractmethod
    def update(self) -> None:
        """Refresh/update the display."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the display."""
        pass


class NullPresenter(GamePresenter):
    """
    A presenter that does nothing.
    Useful for testing or headless simulation.
    """
    
    def initialize(self) -> None:
        pass
    
    def cleanup(self) -> None:
        pass
    
    def render_combat(
        self,
        player: Character,
        enemy: Character,
        available_actions: list[str],
        message: str = ""
    ) -> None:
        pass
    
    def render_menu(
        self,
        title: str,
        options: list[str],
        selected_index: int = 0
    ) -> None:
        pass
    
    def render_character_sheet(self, character: Character) -> None:
        pass
    
    def render_map(
        self,
        world_map: list[list[str]],
        player_x: int,
        player_y: int
    ) -> None:
        pass
    
    def show_message(
        self,
        message: str,
        wait_for_input: bool = True
    ) -> None:
        pass
    
    def show_dialogue(
        self,
        speaker: str,
        text: str,
        choices: list[str] = None
    ) -> int | None:
        return 0 if choices else None
    
    def get_player_action(
        self,
        available_actions: list[str]
    ) -> str:
        # Return first action by default
        return available_actions[0] if available_actions else "Nothing"
    
    def get_text_input(self, prompt: str, max_length: int = 50) -> str:
        return ""
    
    def confirm(self, question: str) -> bool:
        return False
    
    def update(self) -> None:
        pass
    
    def clear(self) -> None:
        pass


class EventDrivenPresenter(GamePresenter):
    """
    A presenter that responds to events from the EventBus.
    
    This is a base class that other presenters can extend to automatically
    respond to game events.
    """
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """Subscribe to relevant events. Override in subclasses."""
        from events import EventType
        
        # Example subscriptions
        self.event_bus.subscribe(EventType.DAMAGE_DEALT, self.on_damage_dealt)
        self.event_bus.subscribe(EventType.STATUS_APPLIED, self.on_status_applied)
        self.event_bus.subscribe(EventType.MESSAGE_DISPLAY, self.on_message)
    
    def on_damage_dealt(self, event) -> None:
        """Handle damage dealt event. Override in subclasses."""
        pass
    
    def on_status_applied(self, event) -> None:
        """Handle status applied event. Override in subclasses."""
        pass
    
    def on_message(self, event) -> None:
        """Handle message event. Override in subclasses."""
        if 'message' in event.data:
            self.show_message(event.data['message'])


class ConsolePresenter(GamePresenter):
    """
    Simple console-based presenter using print statements.
    No fancy UI, just text output. Useful for debugging or simple playthroughs.
    """
    
    def initialize(self) -> None:
        print("=== Dungeon Crawl - Console Mode ===")
    
    def cleanup(self) -> None:
        print("=== Game Over ===")
    
    def render_combat(
        self,
        player: Character,
        enemy: Character,
        available_actions: list[str],
        message: str = ""
    ) -> None:
        print("\n" + "=" * 50)
        print(f"{player.name} (HP: {player.health.current}/{player.health.max})")
        print(f"  VS  ")
        print(f"{enemy.name} (HP: {enemy.health.current}/{enemy.health.max})")
        print("=" * 50)
        if message:
            print(f"\n{message}\n")
    
    def render_menu(
        self,
        title: str,
        options: list[str],
        selected_index: int = 0
    ) -> None:
        print(f"\n=== {title} ===")
        for i, option in enumerate(options):
            prefix = "> " if i == selected_index else "  "
            print(f"{prefix}{i+1}. {option}")
    
    def render_character_sheet(self, character: Character) -> None:
        print(f"\n=== {character.name} ===")
        print(f"Level: {character.level.level}")
        print(f"HP: {character.health.current}/{character.health.max}")
        print(f"MP: {character.mana.current}/{character.mana.max}")
        print(f"Attack: {character.combat.attack}")
        print(f"Defense: {character.combat.defense}")
    
    def render_map(
        self,
        world_map: list[list[str]],
        player_x: int,
        player_y: int
    ) -> None:
        print("\n=== Map ===")
        for y, row in enumerate(world_map):
            line = ""
            for x, tile in enumerate(row):
                if x == player_x and y == player_y:
                    line += "@"
                else:
                    line += tile
            print(line)
    
    def show_message(
        self,
        message: str,
        wait_for_input: bool = True
    ) -> None:
        print(f"\n{message}")
        if wait_for_input:
            input("\nPress Enter to continue...")
    
    def show_dialogue(
        self,
        speaker: str,
        text: str,
        choices: list[str] = None
    ) -> int | None:
        print(f"\n{speaker}: {text}")
        
        if choices:
            for i, choice in enumerate(choices):
                print(f"  {i+1}. {choice}")
            
            while True:
                try:
                    choice_input = input("\nYour choice: ")
                    choice_idx = int(choice_input) - 1
                    if 0 <= choice_idx < len(choices):
                        return choice_idx
                except ValueError:
                    pass
                print("Invalid choice. Try again.")
        
        return None
    
    def get_player_action(
        self,
        available_actions: list[str]
    ) -> str:
        print("\nAvailable Actions:")
        for i, action in enumerate(available_actions):
            print(f"  {i+1}. {action}")
        
        while True:
            try:
                choice_input = input("\nYour action: ")
                choice_idx = int(choice_input) - 1
                if 0 <= choice_idx < len(available_actions):
                    return available_actions[choice_idx]
            except ValueError:
                pass
            print("Invalid action. Try again.")
    
    def get_text_input(self, prompt: str, max_length: int = 50) -> str:
        text = input(f"{prompt}: ")
        return text[:max_length]
    
    def confirm(self, question: str) -> bool:
        response = input(f"{question} (y/n): ").lower()
        return response in ['y', 'yes']
    
    def update(self) -> None:
        pass  # Console doesn't need explicit updates
    
    def clear(self) -> None:
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
