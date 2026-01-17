"""
Inn/Tavern system for GUI - handles rest, patron dialogue, and bounty board.
Implements the core tavern logic from town.py adapted for Pygame presenter.
"""

import random
from gui.level_up import LevelUpScreen


class InnManager:
    """Manages inn/tavern interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        self.presenter = presenter
        self.player_char = player_char
        self.level_up_screen = LevelUpScreen(presenter.screen, presenter)
    
    def visit_inn(self):
        """Visit the inn/tavern - integrates with The Thirsty Dog tavern."""
        inn_options = ["Talk to Patrons", "Leave"]
        
        while True:
            choice = self.presenter.render_menu("The Thirsty Dog Tavern", inn_options)
            
            if choice is None or choice == 1:  # Leave
                self.presenter.show_message("Come back whenever you'd like.")
                break
            
            elif choice == 0:  # Talk to patrons
                self.talk_to_patrons()
    
    def rest(self):
        """Rest at the inn to restore HP/MP."""
        cost = 10
        
        if self.player_char.gold >= cost:
            confirm = self.presenter.render_menu(
                f"Rest for {cost} gold?\n\nThis will fully restore your HP and MP.",
                ["Yes", "No"]
            )
            
            if confirm == 0:
                self.player_char.gold -= cost
                self.player_char.health.current = self.player_char.health.max
                self.player_char.mana.current = self.player_char.mana.max
                self.presenter.show_message(
                    "You rest at the inn and wake up feeling refreshed!\n\n"
                    f"HP: {self.player_char.health.max}/{self.player_char.health.max}\n"
                    f"MP: {self.player_char.mana.max}/{self.player_char.mana.max}"
                )
        else:
            self.presenter.show_message(f"You need {cost} gold to rest here.")
    
    def talk_to_patrons(self):
        """Talk to tavern patrons and access their quests."""
        from gui.quest_manager import QuestManager
        qm = QuestManager(self.presenter, self.player_char)

        # Build patron list similar to town.patron_list
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

        while True:
            choice = self.presenter.render_menu("The Thirsty Dog - Patrons", options)
            if choice is None or options[choice] == 'Back':
                return

            patron = options[choice]
            # Route to quest manager for applicable quest givers
            if patron in ("Barkeep", "Waitress", "Soldier", "Busboy", "Hooded Figure", "Drunkard"):
                qm.check_and_offer(patron)
            else:
                # Flavor-only dialogue for Drunkard and others
                patron_dialogue = random.choice([
                    "I heard there are powerful artifacts deep in the dungeon...",
                    "Many adventurers have entered the dungeon, but few return.",
                    "They say the evil grows stronger with each passing day.",
                    "Be careful down there, adventurer. The monsters are cunning.",
                    "I lost my brother to the dungeon. Please, be safe.",
                    "The blacksmith Griswold is the best in the kingdom!",
                    "If you need potions, visit the alchemist. They saved my life once.",
                    "I've heard rumors of a secret shop somewhere in town...",
                    "The barracks offers bounties for hunting dangerous creatures.",
                    "Some say there's treasure beyond imagination in the depths."
                ])
                self.presenter.show_message(patron_dialogue, patron)
    
    def show_bounty_board(self):
        """Show and manage bounty quests from the tavern."""
        # Check for completable bounties
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        bounty_options = ["Accept Bounty", "View Active Bounties"]
        
        # Check if any bounties are complete
        completable = [name for name, data in bounty_dict.items() if data[2]]
        if completable:
            bounty_options.insert(1, "Turn In Bounty")
        
        bounty_options.append("Leave")
        
        while True:
            choice = self.presenter.render_menu("Bounty Board", bounty_options)
            
            if choice is None or bounty_options[choice] == "Leave":
                break
            
            if bounty_options[choice] == "Accept Bounty":
                self.accept_bounty()
            
            elif bounty_options[choice] == "Turn In Bounty":
                self.turn_in_bounty(completable)
                # Refresh completable list
                completable = [name for name, data in bounty_dict.items() if data[2]]
                if not completable and "Turn In Bounty" in bounty_options:
                    bounty_options.pop(bounty_options.index("Turn In Bounty"))
            
            elif bounty_options[choice] == "View Active Bounties":
                self.view_active_bounties()
    
    def accept_bounty(self):
        """Accept a bounty from the board."""
        from pygame_game import PygameGame
        
        # Get available bounties (from the game instance if accessible)
        # For now, we'll need to get bounties from somewhere - check if we have access to them
        # The bounties should be in a game.bounties dict
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        # Try to access bounties through the presenter (which should have a reference to the game)
        bounties_available = []
        if hasattr(self.presenter, 'game') and hasattr(self.presenter.game, 'bounties'):
            game_bounties = self.presenter.game.bounties
            # Only offer bounties the player doesn't already have
            for bounty_name in game_bounties.keys():
                if bounty_name not in bounty_dict:
                    bounties_available.append(bounty_name)
        
        if not bounties_available:
            self.presenter.show_message("No new bounties available at this time.")
            return
        
        bounty_names = bounties_available + ["Back"]
        choice = self.presenter.render_menu("Accept Bounty", bounty_names)
        
        if choice is None or choice == len(bounty_names) - 1:
            return
        
        bounty_name = bounty_names[choice]
        bounty_data = self.presenter.game.bounties[bounty_name]
        enemy_obj = bounty_data.get("enemy")
        enemy_name = getattr(enemy_obj, "name", bounty_data.get("enemy_name", "Unknown"))
        
        # Add bounty to player's quest dict
        # Format: (bounty_data, enemy_count, completed)
        self.player_char.quest_dict['Bounty'][bounty_name] = [bounty_data, 0, False]
        
        # Show bounty info
        info_msg = (
            f"Bounty Accepted: {bounty_name}\n\n"
            f"Description: {bounty_data.get('description', 'No description')}\n\n"
            f"Target: {enemy_name}\n"
            f"Enemies to defeat: {bounty_data.get('count', 1)}\n\n"
            f"Reward: {bounty_data.get('gold', 0)} Gold, {bounty_data.get('exp', 0)} Experience"
        )
        self.presenter.show_message(info_msg)
    
    def turn_in_bounty(self, completable):
        """Turn in completed bounties."""
        if not completable:
            self.presenter.show_message("No bounties to turn in.")
            return
        
        bounty_names = list(completable)
        bounty_names.append("Back")
        
        choice = self.presenter.render_menu("Turn In Bounty", bounty_names)
        
        if choice is None or choice == len(bounty_names) - 1:
            return
        
        bounty_name = bounty_names[choice]
        bounty_data = self.player_char.quest_dict['Bounty'][bounty_name]
        bounty = bounty_data[0]
        
        # Award rewards
        gold = bounty["gold"]
        exp = bounty["exp"]
        self.player_char.gold += gold
        self.player_char.level.exp += exp
        
        if not self.player_char.max_level():
            self.player_char.level.exp_to_gain -= exp
        
        reward_msg = (
            f"Bounty Complete: {bounty_name}\n\n"
            f"Rewards:\n"
            f"• {gold} Gold\n"
            f"• {exp} Experience"
        )
        
        if bounty.get("reward"):
            reward_item = bounty["reward"]()
            self.player_char.modify_inventory(reward_item)
            reward_msg += f"\n• {reward_item.name}"
        
        self.presenter.show_message(reward_msg)
        
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
            self.presenter.show_message("No active bounties.\n\nCheck back later for new opportunities!")
            return
        
        bounty_info = "Active Bounties:\n\n"
        
        for name, data in bounty_dict.items():
            bounty = data[0]
            killed = data[1]
            complete = data[2]
            
            status = "✓ Complete" if complete else f"{killed}/{bounty['num']} killed"
            bounty_info += f"• {name}: {status}\n"
            bounty_info += f"  Reward: {bounty['gold']}g, {bounty['exp']} exp\n\n"
        
        self.presenter.show_message(bounty_info, "Active Bounties")
    
    def level_up(self):
        """Handle level up with GUI interface."""
        level_info = self.level_up_screen.show_level_up(self.player_char, None)
        hp_gain = level_info.get("health_gain", 0)
        mp_gain = level_info.get("mana_gain", 0)

        self.presenter.show_message(
            f"Level Up!\n\n"
            f"You are now level {self.player_char.level.level}!\n\n"
            f"HP +{hp_gain}\n"
            f"MP +{mp_gain}\n"
            f"All stats +1"
        )
