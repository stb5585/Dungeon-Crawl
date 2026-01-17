"""
Barracks system for GUI - handles quests and storage.
Implements the core barracks logic from town.py adapted for Pygame presenter.
"""


class BarracksManager:
    """Manages barracks interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        self.presenter = presenter
        self.player_char = player_char
    
    def visit_barracks(self):
        """Visit the barracks for quests and storage."""
        barracks_options = ["Quests", "Bounty Board", "Storage", "Leave"]
        
        while True:
            choice = self.presenter.render_menu("Barracks", barracks_options)
            
            if choice is None or choice == 3:  # Leave
                self.presenter.show_message("Take care, soldier.")
                break
            
            elif choice == 0:  # Quests
                from gui.quest_manager import QuestManager
                qm = QuestManager(self.presenter, self.player_char)
                qm.check_and_offer('Sergeant')
            
            elif choice == 1:  # Bounty Board
                self.show_bounty_board()
            
            elif choice == 2:  # Storage
                self.manage_storage()
    
    def manage_storage(self):
        """Access storage system."""
        storage_options = ["Store Items", "Leave"]
        
        # Add retrieve option if storage has items
        if self.player_char.storage:
            storage_options.insert(1, "Retrieve Items")
        
        while True:
            choice = self.presenter.render_menu("Storage Locker", storage_options)
            
            if choice is None or storage_options[choice] == "Leave":
                break
            
            if storage_options[choice] == "Store Items":
                self.store_items()
                # Update menu if storage now has items
                if self.player_char.storage and "Retrieve Items" not in storage_options:
                    storage_options.insert(1, "Retrieve Items")
            
            elif storage_options[choice] == "Retrieve Items":
                self.retrieve_items()
                # Update menu if storage is now empty
                if not self.player_char.storage and "Retrieve Items" in storage_options:
                    storage_options.remove("Retrieve Items")
    
    def store_items(self):
        """Store items in storage locker."""
        if not self.player_char.inventory:
            self.presenter.show_message("You have no items to store.")
            return
        
        while True:
            # Build item list
            item_options = []
            item_data_list = []
            
            for name, items_list in self.player_char.inventory.items():
                if items_list:
                    count = len(items_list)
                    item = items_list[0]  # Get first item as representative
                    item_options.append(f"{name} x{count}")
                    item_data_list.append((item, count))
            
            if not item_options:
                self.presenter.show_message("You have no items to store.")
                return
            
            item_options.append("Back")
            
            choice = self.presenter.render_menu("Store Items:", item_options, max_visible=6)
            
            if choice is None or choice == len(item_options) - 1:
                return
            
            item, count = item_data_list[choice]
            
            # Choose quantity
            qty_options = ["Store 1"]
            if count >= 5:
                qty_options.append("Store 5")
            if count >= 10:
                qty_options.append("Store 10")
            qty_options.append("Store All")
            qty_options.append("Cancel")
            
            qty_choice = self.presenter.render_menu(
                f"Store {item.name}:",
                qty_options
            )
            
            if qty_choice is None or qty_options[qty_choice] == "Cancel":
                continue
            
            if qty_options[qty_choice] == "Store 1":
                quantity = 1
            elif qty_options[qty_choice] == "Store 5":
                quantity = 5
            elif qty_options[qty_choice] == "Store 10":
                quantity = 10
            else:  # Store All
                quantity = count
            
            # Move to storage
            self.player_char.modify_inventory(item, num=quantity, storage=True)
            self.presenter.show_message(f"Stored {quantity}x {item.name}")
    
    def retrieve_items(self):
        """Retrieve items from storage locker."""
        if not self.player_char.storage:
            self.presenter.show_message("Your storage is empty.")
            return
        
        while True:
            # Build storage list
            storage_options = []
            storage_data_list = []
            
            for name, item_list in self.player_char.storage.items():
                if item_list:
                    count = len(item_list)
                    storage_options.append(f"{name} x{count}")
                    storage_data_list.append((item_list[0], count))
            
            if not storage_options:
                self.presenter.show_message("Your storage is empty.")
                return
            
            storage_options.append("Back")
            
            choice = self.presenter.render_menu("Retrieve Items:", storage_options, max_visible=6)
            
            if choice is None or choice == len(storage_options) - 1:
                return
            
            item, count = storage_data_list[choice]
            
            # Choose quantity
            qty_options = ["Retrieve 1"]
            if count >= 5:
                qty_options.append("Retrieve 5")
            if count >= 10:
                qty_options.append("Retrieve 10")
            qty_options.append("Retrieve All")
            qty_options.append("Cancel")
            
            qty_choice = self.presenter.render_menu(
                f"Retrieve {item.name}:",
                qty_options
            )
            
            if qty_choice is None or qty_options[qty_choice] == "Cancel":
                continue
            
            if qty_options[qty_choice] == "Retrieve 1":
                quantity = 1
            elif qty_options[qty_choice] == "Retrieve 5":
                quantity = 5
            elif qty_options[qty_choice] == "Retrieve 10":
                quantity = 10
            else:  # Retrieve All
                quantity = count
            
            # Move from storage to inventory (subtract=False means add to inventory, remove from storage)
            self.player_char.modify_inventory(item, num=quantity, storage=True, subtract=False)
            self.presenter.show_message(f"Retrieved {quantity}x {item.name}")
    
    def show_bounty_board(self):
        """Show and manage bounty quests."""
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        bounty_options = ["Accept Bounty"]
        
        # Check if any bounties are complete
        completable = [name for name, data in bounty_dict.items() if data[2]]
        if completable:
            bounty_options.append("Turn In Bounty")
        
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
    
    def accept_bounty(self):
        """Accept a bounty from the board."""
        bounty_dict = self.player_char.quest_dict.get('Bounty', {})
        
        # Get available bounties from the game instance
        bounties_available = []
        if hasattr(self.presenter, 'game') and hasattr(self.presenter.game, 'bounties'):
            game_bounties = self.presenter.game.bounties
            # Only offer bounties the player doesn't already have
            for bounty_name in game_bounties.keys():
                if bounty_name not in bounty_dict:
                    bounties_available.append(bounty_name)
        
        if not bounties_available:
            self.presenter.show_message("No new bounties available at this time.\n\nCheck your character menu to view active bounties.")
            return
        
        bounty_names = bounties_available + ["Back"]
        choice = self.presenter.render_menu("Accept Bounty", bounty_names)
        
        if choice is None or choice == len(bounty_names) - 1:
            return
        
        bounty_name = bounty_names[choice]
        bounty_data = self.presenter.game.bounties[bounty_name]
        
        # Add bounty to player's quest dict
        # Format: (bounty_data, enemy_count, completed)
        self.player_char.quest_dict['Bounty'][bounty_name] = [bounty_data, 0, False]
        
        # Show bounty info
        target_name = bounty_data["enemy"].name if "enemy" in bounty_data else "Unknown"
        info_msg = (
            f"Bounty Accepted: {bounty_name}\n\n"
            f"Description: Hunt dangerous creatures in the dungeon.\n\n"
            f"Target: {target_name}\n"
            f"Enemies to defeat: {bounty_data.get('num', 1)}\n\n"
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
            from gui.level_up import LevelUpScreen
            level_up_screen = LevelUpScreen(self.presenter.screen, self.presenter)
            
            while self.player_char.level.exp_to_gain <= 0:
                level_up_screen.show_level_up(self.player_char, None)
                if self.player_char.level.exp_to_gain == "MAX":
                    break
