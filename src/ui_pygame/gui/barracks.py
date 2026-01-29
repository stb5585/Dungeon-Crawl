"""
Barracks system for GUI - handles quests and storage.
Implements the core barracks logic from town.py adapted for Pygame presenter.
"""

from .confirmation_popup import ConfirmationPopup
from .location_menu import LocationMenuScreen
from .town_base import TownScreenBase


class BarracksManager(TownScreenBase):
    """Manages barracks interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        super().__init__(presenter)
        self.player_char = player_char
    
    def visit_barracks(self):
        """Visit the barracks for quests and storage."""
        barracks_options = ["Quests", "Storage", "Leave"]
        
        barracks_screen = LocationMenuScreen(self.presenter, "Barracks")
        
        while True:
            choice_idx = barracks_screen.navigate(barracks_options)
            
            if choice_idx is None or choice_idx == 2:  # Leave
                popup = ConfirmationPopup(self.presenter, "Take care, soldier.", show_buttons=False)
                popup.show(background_draw_func=lambda: self.draw_background())
                break
            
            elif choice_idx == 0:  # Quests
                from .quest_manager import QuestManager
                qm = QuestManager(
                    self.presenter, 
                    self.player_char, 
                    background_draw_func=lambda: self.draw_background(),
                    quest_text_renderer=lambda text: barracks_screen.display_quest_text(text)
                )
                qm.check_and_offer('Sergeant')
            
            elif choice_idx == 1:  # Storage
                self.manage_storage()
    
    def manage_storage(self):
        """Access storage system."""
        storage_options = ["Store Items", "Leave"]
        
        # Add retrieve option if storage has items
        if self.player_char.storage:
            storage_options.insert(1, "Retrieve Items")
        
        storage_screen = LocationMenuScreen(self.presenter, "Storage Locker")
        
        while True:
            choice = storage_screen.navigate(storage_options)
            
            if choice is None or (choice is not None and storage_options[choice] == "Leave"):
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
            popup = ConfirmationPopup(self.presenter, "You have no items to store.", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
            return
        
        from .confirmation_popup import QuantityPopup
        
        store_screen = LocationMenuScreen(self.presenter, "Store Items")
        
        while True:
            # Build item list
            item_options = []
            item_data_list = []
            items_display = []
            
            for name, items_list in self.player_char.inventory.items():
                if items_list:
                    count = len(items_list)
                    item = items_list[0]  # Get first item as representative
                    item_options.append(name)
                    item_data_list.append((item, count))
                    items_display.append((item.name, count))
            
            if not item_options:
                popup = ConfirmationPopup(self.presenter, "You have no items to store.", show_buttons=False)
                popup.show(background_draw_func=lambda: self.draw_background())
                return
            
            item_options.append("Back")
            items_display.append(("Back", 0))
            
            # Show items list in right panel and navigate on right
            choice = store_screen.navigate_with_content(items_display)
            
            if choice is None or items_display[choice][0] == "Back":
                return
            
            item, count = item_data_list[choice]
            
            # Use QuantityPopup for quantity selection
            qty_popup = QuantityPopup(self.presenter, item.name, unit_cost=0, max_quantity=count, action="store")
            quantity = qty_popup.show(background_draw_func=lambda: self.draw_background())
            
            if quantity is None or quantity == 0:
                continue
            
            # Move to storage
            self.player_char.modify_inventory(item, num=quantity, storage=True)
            popup = ConfirmationPopup(self.presenter, f"Stored {quantity}x {item.name}", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
    
    def retrieve_items(self):
        """Retrieve items from storage locker."""
        if not self.player_char.storage:
            popup = ConfirmationPopup(self.presenter, "Your storage is empty.", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
            return
        
        from .confirmation_popup import QuantityPopup
        
        storage_screen = LocationMenuScreen(self.presenter, "Retrieve Items")
        
        while True:
            # Build storage list
            storage_options = []
            storage_data_list = []
            storage_display = []
            
            for name, item_list in self.player_char.storage.items():
                if item_list:
                    count = len(item_list)
                    storage_options.append(name)
                    storage_data_list.append((item_list[0], count))
                    storage_display.append((item_list[0].name, count))
            
            if not storage_options:
                popup = ConfirmationPopup(self.presenter, "Your storage is empty.", show_buttons=False)
                popup.show(background_draw_func=lambda: self.draw_background())
                return
            
            storage_options.append("Back")
            storage_display.append(("Back", 0))
            
            # Show items list in right panel and navigate on right
            choice = storage_screen.navigate_with_content(storage_display)
            
            if choice is None or storage_display[choice][0] == "Back":
                return
            
            item, count = storage_data_list[choice]
            
            # Use QuantityPopup for quantity selection
            qty_popup = QuantityPopup(self.presenter, item.name, unit_cost=0, max_quantity=count, action="retrieve")
            quantity = qty_popup.show(background_draw_func=lambda: self.draw_background())
            
            if quantity is None or quantity == 0:
                continue
            
            # Move from storage to inventory (subtract=False means add to inventory, remove from storage)
            self.player_char.modify_inventory(item, num=quantity, storage=True, subtract=False)
            popup = ConfirmationPopup(self.presenter, f"Retrieved {quantity}x {item.name}", show_buttons=False)
            popup.show(background_draw_func=lambda: self.draw_background())
    