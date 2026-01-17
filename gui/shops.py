"""
Shop system for GUI - handles blacksmith, alchemist, and jeweler.
Implements the core shop logic from town.py adapted for Pygame presenter.
"""

import items as items_module
from gui.shop_screen import ShopScreen


class ShopManager:
    """Manages all shop interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        self.presenter = presenter
        self.player_char = player_char
    
    def visit_blacksmith(self):
        """Visit Griswold's Blacksmith - weapons and shields."""
        if self.player_char.player_level() < 5:
            self.presenter.show_message("Sorry but the blacksmith is currently closed. Try again later.")
            return
        
        # Check for unobtainium ultimate weapon quest
        if 'Unobtainium' in self.player_char.special_inventory:
            self.presenter.show_message(
                "Oh my...can it possibly be?...the legendary ore...Unobtainium?\n\n"
                "I can't believe you have found it!\n\n"
                "It has been a lifelong dream of mine to forge a weapon from the mythical metal.\n\n"
                "(Ultimate weapon crafting coming soon!)"
            )
        
        from gui.quest_manager import QuestManager
        qm = QuestManager(self.presenter, self.player_char)
        
        # Use ShopScreen for the main interface
        shop_screen = ShopScreen(self.presenter, self.player_char, "Griswold's Blacksmith")
        shop_screen.options_list = ["Buy", "Sell", "Quests", "Leave"]
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                self.presenter.show_message("Come back whenever you'd like.")
                break
            elif choice == "Buy":
                # Update options to show buy categories
                shop_screen.options_list = ["Weapons", "Shields", "Back"]
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Weapons":
                    self.buy_weapons()
                elif buy_choice == "Shields":
                    self.buy_shields()
                elif buy_choice == "Back":
                    # Restore main options
                    shop_screen.options_list = ["Buy", "Sell", "Quests", "Leave"]
                    shop_screen.shop_message = "Griswold's Blacksmith"
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Griswold')
    
    def visit_alchemist(self):
        """Visit the Alchemist - potions and consumables."""
        from gui.quest_manager import QuestManager
        qm = QuestManager(self.presenter, self.player_char)
        
        # Use ShopScreen for the main interface
        shop_screen = ShopScreen(self.presenter, self.player_char, "Welcome to Ye Olde Item Shoppe.")
        shop_screen.options_list = ["Buy", "Sell", "Quests", "Leave"]
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                self.presenter.show_message("Good luck on your adventures!")
                break
            elif choice == "Buy":
                # Update options to show buy categories
                shop_screen.options_list = ["Potions", "Scrolls", "Back"]
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Potions":
                    self.buy_potions()
                elif buy_choice == "Scrolls":
                    self.buy_scrolls()
                
                # Always restore main options after buying or going back
                shop_screen.options_list = ["Buy", "Sell", "Quests", "Leave"]
                shop_screen.shop_message = "Welcome to Ye Olde Item Shoppe."
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Alchemist')
    
    def visit_jeweler(self):
        """Visit the Jeweler - rings and pendants."""
        if self.player_char.player_level() < 10:
            self.presenter.show_message("Sorry but the jeweler is currently closed. Try again later.")
            return
        
        from gui.quest_manager import QuestManager
        qm = QuestManager(self.presenter, self.player_char)
        
        # Use ShopScreen for the main interface
        shop_screen = ShopScreen(self.presenter, self.player_char, "Come glimpse the finest jewelry in the land.")
        shop_screen.options_list = ["Buy", "Sell", "Quests", "Leave"]
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                self.presenter.show_message("May fortune favor you!")
                break
            elif choice == "Buy":
                # Update options to show buy categories
                shop_screen.options_list = ["Rings", "Pendants", "Back"]
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Rings":
                    self.buy_rings()
                elif buy_choice == "Pendants":
                    self.buy_pendants()
                
                # Always restore main options after buying or going back
                shop_screen.options_list = ["Buy", "Sell", "Quests", "Leave"]
                shop_screen.shop_message = "Come glimpse the finest jewelry in the land."
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Jeweler')
    
    def buy_weapons(self):
        """Buy weapons - choose 1H or 2H first."""
        # Use ShopScreen for weapon type selection
        shop_screen = ShopScreen(self.presenter, self.player_char, "Choose weapon type")
        shop_screen.options_list = ["1-Handed", "2-Handed", "Back"]
        handed_choice = shop_screen.navigate_options()
        
        if handed_choice is None or handed_choice == "Back":
            return
        
        handed = handed_choice
        weapon_dict = items_module.items_dict["Weapon"][handed]
        
        # Choose weapon subtype using ShopScreen
        subtypes = list(weapon_dict.keys())
        subtypes.append("Back")
        
        shop_screen.shop_message = f"Choose {handed.lower()} weapon type"
        shop_screen.options_list = subtypes
        subtype_choice = shop_screen.navigate_options()
        
        if subtype_choice is None or subtype_choice == "Back":
            return
        
        subtype = subtype_choice
        self.buy_equipment(weapon_dict[subtype], subtype)
    
    def buy_shields(self):
        """Buy shields from blacksmith."""
        shield_list = items_module.items_dict["OffHand"]["Shield"]
        self.buy_equipment(shield_list, "Shield")
    
    def buy_rings(self):
        """Buy rings from jeweler."""
        ring_list = items_module.items_dict["Accessory"]["Ring"]
        self.buy_equipment(ring_list, "Ring")
    
    def buy_pendants(self):
        """Buy pendants from jeweler."""
        pendant_list = items_module.items_dict["Accessory"]["Pendant"]
        self.buy_equipment(pendant_list, "Pendant")
    
    def buy_scrolls(self):
        """Buy scrolls from alchemist."""
        scroll_list = items_module.items_dict["Misc"]["Scroll"]
        self.buy_equipment(scroll_list, "Scroll")
    
    def buy_potions(self):
        """Buy potions from alchemist with level-based availability."""
        # Get potion items from items_dict
        potion_dict = {"Misc": []}
        player_level = self.player_char.player_level()
        
        # Basic potions
        potion_dict["Misc"].append(items_module.HealthPotion)
        potion_dict["Misc"].append(items_module.ManaPotion)
        
        # Better potions at higher levels
        if player_level >= 10:
            potion_dict["Misc"].append(items_module.GreatHealthPotion)
            potion_dict["Misc"].append(items_module.GreatManaPotion)
        
        if player_level >= 30:
            potion_dict["Misc"].append(items_module.SuperHealthPotion)
            potion_dict["Misc"].append(items_module.SuperManaPotion)
        
        # Use the new shop screen
        self._buy_with_shop_screen(potion_dict, "Potions")
    
    def buy_equipment(self, item_list, category_name):
        """Generic equipment buying interface using ShopScreen."""
        # Build item dictionary
        itemdict = {category_name: item_list}
        
        # Use the new shop screen
        self._buy_with_shop_screen(itemdict, category_name)
    
    def _buy_with_shop_screen(self, itemdict, category_name):
        """Use the new ShopScreen interface for buying items."""
        shop_screen = ShopScreen(self.presenter, self.player_char, f"Buy {category_name}")
        shop_screen.update_item_list(itemdict, "Buy")
        
        while True:
            result = shop_screen.navigate_items()
            
            # Result will be None if ESC was pressed (handled in navigate_items)
            if result is None:
                return
            
            display_str, item, cost, owned = result
            
            # Skip navigation items
            if display_str in ["Next Page"] or not item:
                continue
            
            # Ask quantity
            qty_choice = self.presenter.render_menu(
                f"Buy {item.name} for {cost}g each?",
                ["Buy 1", "Buy 5", "Cancel"]
            )
            
            if qty_choice is None or qty_choice == 2:
                continue
            
            quantity = 1 if qty_choice == 0 else 5
            total_cost = cost * quantity
            
            if self.player_char.gold < total_cost:
                self.presenter.show_message(f"Not enough gold! Need {total_cost}g")
                # Update the shop screen to reflect current gold
                shop_screen.draw_all()
                continue
            
            # Purchase items
            self.player_char.gold -= total_cost
            self.player_char.modify_inventory(item, num=quantity)
            self.presenter.show_message(
                f"Purchased {quantity}x {item.name}!\n\n"
                f"Gold remaining: {self.player_char.gold}"
            )
            
            # Update item list to reflect new owned count
            shop_screen.update_item_list(itemdict, "Buy")
    
    def _format_item_info(self, item):
        """Format item information with description and stat comparison."""
        info_lines = []
        
        # Item name and type
        info_lines.append(f"Type: {item.typ}")
        if hasattr(item, 'subtyp'):
            info_lines.append(f"Subtype: {item.subtyp}")
        
        # Item stats
        info_lines.append("")
        if hasattr(item, 'damage') and item.damage > 0:
            info_lines.append(f"Damage: {item.damage}")
        if hasattr(item, 'armor') and item.armor > 0:
            info_lines.append(f"Armor: {item.armor}")
        if hasattr(item, 'magic') and item.magic != 0:
            info_lines.append(f"Magic: {item.magic:+d}")
        if hasattr(item, 'magic_defense') and item.magic_defense != 0:
            info_lines.append(f"Magic Defense: {item.magic_defense:+d}")
        
        # Description
        if item.description:
            info_lines.append("")
            # Word wrap the description
            words = item.description.split()
            current_line = []
            for word in words:
                current_line.append(word)
                line = " ".join(current_line)
                if len(line) > 50:
                    current_line.pop()
                    info_lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                info_lines.append(" ".join(current_line))
        
        # Value
        info_lines.append("")
        info_lines.append(f"Value: {item.value}g")
        
        # Equipment comparison for equipment items
        if item.typ in ["Weapon", "OffHand", "Armor", "Accessory"]:
            equip_slot = item.typ
            if item.typ == "Accessory":
                equip_slot = item.subtyp
            
            # Get current equipped item
            current_item = self.player_char.equipment.get(equip_slot)
            
            if current_item and current_item.name != "None":
                info_lines.append("")
                info_lines.append("=== Currently Equipped ===")
                info_lines.append(f"{current_item.name}")
                
                # Show stat comparison
                stat_diff = self.player_char.equip_diff(item, equip_slot, buy=True)
                
                if stat_diff:
                    info_lines.append("")
                    info_lines.append("=== If Equipped ===")
                    for line in stat_diff.splitlines():
                        if line.strip():
                            # Parse the stat difference
                            parts = line.split('  ')
                            if len(parts) >= 2:
                                stat_name = parts[0].strip()
                                stat_value = parts[1].strip()
                                # Add color indicator
                                if stat_value.startswith('+'):
                                    indicator = "(Better)"
                                elif stat_value.startswith('-'):
                                    indicator = "(Worse)"
                                else:
                                    indicator = ""
                                info_lines.append(f"{stat_name}: {stat_value} {indicator}".strip())
            else:
                info_lines.append("")
                info_lines.append(f"(No {equip_slot} currently equipped)")
        
        return "\n".join(info_lines)
        
        return "\n".join(info_lines)
    
    def sell_items(self):
        """Sell items from inventory using ShopScreen."""
        if not self.player_char.inventory:
            self.presenter.show_message("You have nothing to sell!")
            return
        
        while True:
            # Build sellable inventory (exclude ultimate items)
            sellable = {}
            for name, items_list in self.player_char.inventory.items():
                if items_list and not items_list[0].ultimate:
                    sellable[name] = items_list
            
            if not sellable:
                self.presenter.show_message("You have no items to sell.")
                return
            
            # Use ShopScreen for selling
            shop_screen = ShopScreen(self.presenter, self.player_char, "Sell Items")
            shop_screen.update_item_list(sellable, "Sell")
            
            result = shop_screen.navigate_items()
            
            # Result will be None if ESC was pressed
            if result is None:
                return
            
            display_str, item, sell_price, count = result
            
            # Skip navigation items or items without data
            if display_str in ["Next Page"] or not item:
                continue
            
            # Choose quantity
            qty_options = ["Sell 1"]
            if count >= 5:
                qty_options.append("Sell 5")
            if count >= 10:
                qty_options.append("Sell 10")
            qty_options.append("Sell All")
            qty_options.append("Cancel")
            
            qty_choice = self.presenter.render_menu(
                f"Sell {item.name} ({sell_price}g each):",
                qty_options
            )
            
            if qty_choice is None or qty_options[qty_choice] == "Cancel":
                continue
            
            if qty_options[qty_choice] == "Sell 1":
                quantity = 1
            elif qty_options[qty_choice] == "Sell 5":
                quantity = 5
            elif qty_options[qty_choice] == "Sell 10":
                quantity = 10
            else:  # Sell All
                quantity = count
            
            total_gold = sell_price * quantity
            
            # Confirm sale
            confirm = self.presenter.render_menu(
                f"Sell {quantity}x {item.name} for {total_gold}g?",
                ["Yes", "No"]
            )
            
            if confirm == 0:
                self.player_char.gold += total_gold
                self.player_char.modify_inventory(item, num=quantity, subtract=True)
                self.presenter.show_message(
                    f"Sold {quantity}x {item.name} for {total_gold}g!\n\n"
                    f"Gold: {self.player_char.gold}"
                )
                # Continue selling (will reload inventory)
            else:
                # Continue browsing
                pass
    
    def visit_secret_shop(self):
        """Visit the secret shop in the dungeon - sells everything."""
        secret_options = ["Weapons", "Shields & Tomes", "Armor", "Accessories", "Potions & Scrolls", "Leave"]
        
        while True:
            choice = self.presenter.render_menu(
                f"Secret Shop - Gold: {self.player_char.gold}",
                secret_options
            )
            
            if choice is None or choice == 5:  # Leave
                self.presenter.show_message("Come back anytime!")
                break
            elif choice == 0:  # Weapons
                self._buy_secret_weapons()
            elif choice == 1:  # Shields & Tomes
                self._buy_secret_offhand()
            elif choice == 2:  # Armor
                self._buy_secret_armor()
            elif choice == 3:  # Accessories
                self._buy_secret_accessories()
            elif choice == 4:  # Potions & Scrolls
                self._buy_secret_consumables()
    
    def _buy_secret_weapons(self):
        """Buy weapons from secret shop."""
        handed_choice = self.presenter.render_menu(
            "Choose weapon type:",
            ["1-Handed", "2-Handed", "Back"]
        )
        
        if handed_choice is None or handed_choice == 2:
            return
        
        handed = "1-Handed" if handed_choice == 0 else "2-Handed"
        weapon_dict = items_module.items_dict["Weapon"][handed]
        
        # Choose weapon subtype
        subtypes = list(weapon_dict.keys())
        subtypes.append("Back")
        
        subtype_choice = self.presenter.render_menu(
            f"Choose {handed} weapon type:",
            subtypes
        )
        
        if subtype_choice is None or subtype_choice == len(subtypes) - 1:
            return
        
        subtype = subtypes[subtype_choice]
        item_list = weapon_dict[subtype]
        
        self.buy_equipment(item_list, f"{handed} {subtype}")
    
    def _buy_secret_offhand(self):
        """Buy shields, tomes, and rods from secret shop."""
        offhand_options = ["Shields", "Tomes", "Rods", "Back"]
        
        choice = self.presenter.render_menu("Choose off-hand type:", offhand_options)
        
        if choice is None or choice == 3:
            return
        
        offhand_types = ["Shield", "Tome", "Rod"]
        offhand_type = offhand_types[choice]
        item_list = items_module.items_dict["OffHand"][offhand_type]
        
        self.buy_equipment(item_list, offhand_type)
    
    def _buy_secret_armor(self):
        """Buy armor from secret shop."""
        armor_options = ["Cloth", "Light", "Medium", "Heavy", "Back"]
        
        choice = self.presenter.render_menu("Choose armor type:", armor_options)
        
        if choice is None or choice == 4:
            return
        
        armor_types = ["Cloth", "Light", "Medium", "Heavy"]
        armor_type = armor_types[choice]
        item_list = items_module.items_dict["Armor"][armor_type]
        
        self.buy_equipment(item_list, f"{armor_type} Armor")
    
    def _buy_secret_accessories(self):
        """Buy accessories from secret shop."""
        acc_options = ["Rings", "Pendants", "Back"]
        
        choice = self.presenter.render_menu("Choose accessory type:", acc_options)
        
        if choice is None or choice == 2:
            return
        
        acc_types = ["Ring", "Pendant"]
        acc_type = acc_types[choice]
        item_list = items_module.items_dict["Accessory"][acc_type]
        
        self.buy_equipment(item_list, acc_type)
    
    def _buy_secret_consumables(self):
        """Buy potions and scrolls from secret shop."""
        consumable_options = ["Potions", "Scrolls", "Back"]
        
        choice = self.presenter.render_menu("Choose consumable type:", consumable_options)
        
        if choice is None or choice == 2:
            return
        
        if choice == 0:  # Potions
            self.buy_potions()
        else:  # Scrolls
            self.buy_scrolls()
