"""
Inn/Tavern system for GUI - handles rest, patron dialogue, and bounty board.
Implements the core tavern logic from town.py adapted for Pygame presenter.
"""

import random
import textwrap

from src.core.town import PATRON_DIALOGUES, TAVERN_FLAVOR_DIALOGUES
from .level_up import LevelUpScreen
from .confirmation_popup import ConfirmationPopup
from .location_menu import LocationMenuScreen
from .town_base import TownScreenBase


class InnManager(TownScreenBase):
    """Manages inn/tavern interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        super().__init__(presenter)
        self.player_char = player_char
        self.level_up_screen = LevelUpScreen(presenter.screen, presenter)
    
    def visit_inn(self):
        """Visit the inn/tavern - integrates with The Thirsty Dog tavern."""
        inn_options = ["Talk to Patrons", "Bounty Board", "Leave"]
        
        inn_screen = LocationMenuScreen(self.presenter, "The Thirsty Dog Tavern")
        
        while True:
            choice_idx = inn_screen.navigate(inn_options, reset_cursor=False)
            
            if choice_idx is None or choice_idx == 2:  # Leave
                popup = ConfirmationPopup(self.presenter, "Come back whenever you'd like.", show_buttons=False)
                popup.show(**self.popup_show_kwargs())
                break
            
            elif choice_idx == 0:  # Talk to patrons
                self.talk_to_patrons()
            
            elif choice_idx == 1:  # Bounty Board
                self.show_bounty_board()

    def _random_patron_comment(self, patron: str) -> str | None:
        # Gather patron-specific dialogues eligible for the player's level
        combined_pool: list[str] = []
        dialogues = PATRON_DIALOGUES.get(patron)
        player_level = self.player_char.player_level()
        if dialogues:
            eligible_levels = [lvl for lvl in dialogues if player_level >= lvl]
            if dialogues and eligible_levels:
                # Drunkard uses only the high-tier messages once level 65 is reached
                if patron == "Drunkard" and player_level >= 65:
                    eligible_levels = [lvl for lvl in eligible_levels if lvl == 65]
                chosen_level = random.choice(eligible_levels)
                combined_pool.extend(dialogues[chosen_level])

        # Always include general tavern flavor comments in the random pool
        combined_pool.extend(TAVERN_FLAVOR_DIALOGUES)

        return random.choice(combined_pool) if combined_pool else None
    
    def _build_patron_list(self):
        """Build the list of available patrons based on quest state."""
        options = ["Barkeep"]
        if 'A Bad Dream' in self.player_char.quest_dict.get('Main', {}):
            if not self.player_char.quest_dict['Main']['A Bad Dream'].get('Turned In'):
                options.append("Waitress")
            else:
                options.append('Busboy')
        else:
            options.append('Waitress')
        if self.player_char.player_level() >= 8:
            options.append("Drunkard")
            if self.player_char.player_level() >= 10:
                options.append("Soldier")
                if self.player_char.player_level() >= 25:
                    if 'Red Dragon' in self.player_char.quest_dict.get('Main', {}):
                        if not self.player_char.quest_dict['Main']['Red Dragon'].get('Turned In'):
                            options.append("Hooded Figure")
                    else:
                        options.append("Hooded Figure")
        options.append('Back')
        return options
    
    def talk_to_patrons(self):
        """Talk to tavern patrons and access their quests."""
        patrons_screen = LocationMenuScreen(self.presenter, "The Thirsty Dog - Patrons")
        
        while True:
            # Rebuild patron list each iteration to reflect quest state changes
            options = self._build_patron_list()
            choice = patrons_screen.navigate(options, reset_cursor=False)
            if choice is None or (choice is not None and options[choice] == 'Back'):
                return

            patron = options[choice]
            # Route to quest manager for applicable quest givers
            if patron in ("Barkeep", "Waitress", "Soldier", "Busboy", "Hooded Figure", "Drunkard"):
                from .quest_manager import QuestManager
                qm = QuestManager(
                    self.presenter, 
                    self.player_char, 
                    quest_text_renderer=lambda text: patrons_screen.display_quest_text(text)
                )
                did_action, showed_message = qm.check_and_offer(patron, show_help=False, suppress_no_quests_message=True)
                if not did_action and not showed_message:
                    # Mix a random patron comment with a random quest help hint
                    pool = []
                    hint = qm.get_random_help_hint(patron)
                    if hint:
                        pool.append(hint)
                    comment = self._random_patron_comment(patron)
                    if comment:
                        pool.append(comment)
                    if pool:
                        selection = random.choice(pool)
                        wrapped_selection = "\n".join(textwrap.wrap(selection, width=52))
                        qm.quest_text_renderer(wrapped_selection)
            else:
                # This branch is not used since all patrons are handled above,
                # but keep a fallback to show a general tavern flavor comment.
                patron_dialogue = random.choice(TAVERN_FLAVOR_DIALOGUES)
                popup = ConfirmationPopup(self.presenter, patron_dialogue, show_buttons=False)
                popup.show(**self.popup_show_kwargs())
    
    def show_bounty_board(self):
        """Show and manage bounty quests from the tavern."""
        # Check for completable bounties
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        bounty_screen = LocationMenuScreen(self.presenter, "Bounty Board")
        
        while True:
            bounty_options = ["Accept Bounty", "View Active Bounties", "Leave"]
            
            # Check if any bounties are complete
            completable = [name for name, data in bounty_dict.items() if data[2]]
            if completable:
                bounty_options.insert(1, "Turn In Bounty")
            
            choice_idx = bounty_screen.navigate(bounty_options, reset_cursor=False)
            
            if choice_idx is None or bounty_options[choice_idx] == "Leave":
                break
            
            if bounty_options[choice_idx] == "Accept Bounty":
                self.accept_bounty()
            
            elif bounty_options[choice_idx] == "Turn In Bounty":
                self.turn_in_bounty(completable)
            
            elif bounty_options[choice_idx] == "View Active Bounties":
                self.view_active_bounties()
    
    def accept_bounty(self):
        """Accept a bounty from the board."""
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        # Get available bounties
        bounties_available = []
        if hasattr(self.presenter, 'game') and hasattr(self.presenter.game, 'bounties'):
            game_bounties = self.presenter.game.bounties
            # Only offer bounties the player doesn't already have
            for bounty_name in game_bounties.keys():
                if bounty_name not in bounty_dict:
                    bounties_available.append(bounty_name)
        
        if not bounties_available:
            popup = ConfirmationPopup(self.presenter, "No new bounties available at this time.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return
        
        bounty_screen = LocationMenuScreen(self.presenter, "Accept Bounty")
        
        # Build display list
        bounty_display = [(name, 0) for name in bounties_available]
        bounty_display.append(("Back", 0))
        
        choice = bounty_screen.navigate_with_content(bounty_display)
        
        if choice is None or bounty_display[choice][0] == "Back":
            return
        
        bounty_name = bounty_display[choice][0]
        bounty_data = self.presenter.game.bounties[bounty_name]
        enemy_obj = bounty_data.get("enemy")
        enemy_name = getattr(enemy_obj, "name", bounty_data.get("enemy_name", "Unknown"))
        
        # Add bounty to player's quest dict
        self.player_char.quest_dict['Bounty'][bounty_name] = [bounty_data, 0, False]
        
        # Show bounty info
        info_msg = (
            f"Bounty Accepted: {bounty_name}\n"
            f"Target: {enemy_name}\n"
            f"Enemies to defeat: {bounty_data.get('num', 1)}\n"
            f"Reward: {bounty_data.get('gold', 0)} Gold, {bounty_data.get('exp', 0)} Experience"
        )
        popup = ConfirmationPopup(self.presenter, info_msg, show_buttons=False)
        popup.show(**self.popup_show_kwargs())
    
    def turn_in_bounty(self, completable):
        """Turn in completed bounties using the inn UI."""
        if not completable:
            popup = ConfirmationPopup(self.presenter, "No bounties to turn in.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        bounty_screen = LocationMenuScreen(self.presenter, "Turn In Bounty")
        bounty_options = list(completable) + ["Back"]

        choice_idx = bounty_screen.navigate(bounty_options, reset_cursor=False)

        if choice_idx is None or bounty_options[choice_idx] == "Back":
            return

        bounty_name = bounty_options[choice_idx]
        bounty_data = self.player_char.quest_dict['Bounty'].get(bounty_name)
        if not bounty_data:
            popup = ConfirmationPopup(self.presenter, "That bounty is no longer available.", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return

        bounty = bounty_data[0]

        # Award rewards
        gold = bounty.get("gold", 0)
        exp = bounty.get("exp", 0)
        self.player_char.gold += gold
        self.player_char.level.exp += exp

        if not self.player_char.max_level():
            self.player_char.level.exp_to_gain -= exp

        reward_lines = [
            f"Bounty Complete: {bounty_name}",
            "",
            "Rewards:",
            f"• {gold} Gold",
            f"• {exp} Experience",
        ]

        if bounty.get("reward"):
            reward_item = bounty["reward"]()
            self.player_char.modify_inventory(reward_item)
            reward_lines.append(f"• {reward_item.name}")

        reward_msg = "\n".join(reward_lines)
        popup = ConfirmationPopup(self.presenter, reward_msg, show_buttons=False)
        popup.show(**self.popup_show_kwargs())

        # Remove completed bounty
        del self.player_char.quest_dict['Bounty'][bounty_name]

        # Check for level up
        if not self.player_char.max_level():
            while self.player_char.level.exp_to_gain <= 0:
                self.level_up()
                if self.player_char.level.exp_to_gain == "MAX":
                    break
    
    def view_active_bounties(self):
        """View all active bounty quests."""
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        if not bounty_dict:
            popup = ConfirmationPopup(self.presenter, "No active bounties.\n\nCheck back later for new opportunities!", show_buttons=False)
            popup.show(**self.popup_show_kwargs())
            return
        
        bounty_screen = LocationMenuScreen(self.presenter, "Active Bounties")
        
        # Build display list
        bounty_display = []
        for name, data in bounty_dict.items():
            bounty = data[0]
            killed = data[1]
            complete = data[2]
            status = "✓ Complete" if complete else f"{killed}/{bounty['num']} killed"
            display_text = f"{name} - {status}"
            bounty_display.append((display_text, 0))
        
        bounty_display.append(("Back", 0))
        
        choice = bounty_screen.navigate_with_content(bounty_display)
        
        if choice is None or bounty_display[choice][0] == "Back":
            return
    
    def level_up(self):
        """Handle level up with GUI interface."""
        # show_level_up already displays all level-up information
        self.level_up_screen.show_level_up(self.player_char, None)
