"""
Shop system for GUI - handles blacksmith, alchemist, and jeweler.
Implements the core shop logic from town.py adapted for Pygame presenter.
"""

from src.core import items as items_module
from .shop_screen import ShopScreen
from .confirmation_popup import ConfirmationPopup
from .town_base import TownScreenBase


class ShopManager(TownScreenBase):
    """Manages all shop interactions with pygame presenter."""
    
    def __init__(self, presenter, player_char):
        super().__init__(presenter)
        self.player_char = player_char
    
    def visit_blacksmith(self):
        """Visit Griswold's Blacksmith - weapons and shields."""
        if self.player_char.player_level() < 5:
            popup = ConfirmationPopup(self.presenter, "Sorry but the blacksmith is currently closed. Try again later.", show_buttons=False)
            popup.show()
            return
        
        # Check for unobtainium ultimate weapon quest
        if 'Unobtainium' in self.player_char.special_inventory:
            self.presenter.show_message(
                "Oh my...can it possibly be?...the legendary ore...Unobtainium?\n\n"
                "I can't believe you have found it!\n\n"
                "It has been a lifelong dream of mine to forge a weapon from the mythical metal.\n\n"
                "(Ultimate weapon crafting coming soon!)"
            )
        
        # Use ShopScreen for the main interface
        shop_screen = ShopScreen(self.presenter, self.player_char, "Griswold's Blacksmith")
        shop_screen.set_options(["Buy", "Sell", "Quests", "Leave"])

        from .quest_manager import QuestManager
        qm = QuestManager(
            self.presenter,
            self.player_char,
            quest_text_renderer=lambda text: shop_screen.display_quest_text(text),
        )
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                popup = ConfirmationPopup(self.presenter, "Come back whenever you'd like.", show_buttons=False)
                popup.show()
                break
            elif choice == "Buy":
                # Update options to show buy categories
                shop_screen.set_options(["Weapons", "Shields", "Armor", "Back"])
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Weapons":
                    self.buy_weapons()
                elif buy_choice == "Shields":
                    self.buy_shields()
                elif buy_choice == "Armor":
                    self.buy_armor()
                # Always restore main options after buy submenu (including ESC/Back)
                shop_screen.set_options(["Buy", "Sell", "Quests", "Leave"])
                shop_screen.shop_message = "Griswold's Blacksmith"
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Griswold')
    
    def visit_alchemist(self):
        """Visit the Alchemist - potions and consumables."""
        from .quest_manager import QuestManager
        
        # Use ShopScreen for the main interface
        shop_screen = ShopScreen(self.presenter, self.player_char, "Welcome to Ye Olde Item Shoppe.")
        qm = QuestManager(
            self.presenter,
            self.player_char,
            quest_text_renderer=lambda text: shop_screen.display_quest_text(text),
        )
        shop_screen.set_options(["Buy", "Sell", "Quests", "Leave"])
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                popup = ConfirmationPopup(self.presenter, "Good luck on your adventures!", show_buttons=False)
                popup.show()
                break
            elif choice == "Buy":
                # Update options to show buy categories
                shop_screen.set_options(["Potions", "Scrolls", "Misc", "Back"])
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Potions":
                    self.buy_potions()
                elif buy_choice == "Scrolls":
                    self.buy_scrolls()
                elif buy_choice == "Misc":
                    self.buy_misc()
                
                # Always restore main options after buying or going back
                shop_screen.set_options(["Buy", "Sell", "Quests", "Leave"])
                shop_screen.shop_message = "Welcome to Ye Olde Item Shoppe."
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Alchemist')
    
    def visit_jeweler(self):
        """Visit the Jeweler - rings and pendants."""
        if self.player_char.player_level() < 10:
            popup = ConfirmationPopup(self.presenter, "Sorry but the jeweler is currently closed. Try again later.", show_buttons=False)
            popup.show()
            return
        
        from .quest_manager import QuestManager
        
        # Use ShopScreen for the main interface
        shop_screen = ShopScreen(self.presenter, self.player_char, "Come glimpse the finest jewelry in the land.")
        qm = QuestManager(
            self.presenter,
            self.player_char,
            quest_text_renderer=lambda text: shop_screen.display_quest_text(text),
        )
        shop_screen.set_options(["Buy", "Sell", "Quests", "Leave"])
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                popup = ConfirmationPopup(self.presenter, "May fortune favor you!", show_buttons=False)
                popup.show()
                break
            elif choice == "Buy":
                # Update options to show buy categories
                shop_screen.set_options(["Rings", "Pendants", "Back"])
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Rings":
                    self.buy_rings()
                elif buy_choice == "Pendants":
                    self.buy_pendants()
                
                # Always restore main options after buying or going back
                shop_screen.set_options(["Buy", "Sell", "Quests", "Leave"])
                shop_screen.shop_message = "Come glimpse the finest jewelry in the land."
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Jeweler')
    
    def buy_weapons(self):
        """Buy weapons - choose 1H or 2H first."""
        # Use ShopScreen for weapon type selection
        shop_screen = ShopScreen(self.presenter, self.player_char, "Choose weapon type")
        shop_screen.set_options(["1-Handed", "2-Handed", "Back"])
        handed_choice = shop_screen.navigate_options()
        
        # Treat ESC ("Leave") the same as Back for submenus
        if handed_choice is None or handed_choice in ("Back", "Leave"):
            return
        
        handed = handed_choice
        weapon_dict = items_module.items_dict["Weapon"][handed]
        
        # Choose weapon subtype using ShopScreen, filtering out unavailable categories
        subtypes = []
        for subtype, item_list in weapon_dict.items():
            if self._has_available_items(item_list):
                subtypes.append(subtype)
        
        # If no items are available, return to main menu
        if not subtypes:
            return
        
        subtypes.append("Back")
        
        shop_screen.shop_message = f"Choose {handed.lower()} weapon type"
        shop_screen.set_options(subtypes)
        subtype_choice = shop_screen.navigate_options()
        
        # Treat ESC ("Leave") the same as Back for submenus
        if subtype_choice is None or subtype_choice in ("Back", "Leave"):
            return
        
        subtype = subtype_choice
        self.buy_equipment(weapon_dict[subtype], subtype, )
    
    def buy_shields(self):
        """Buy shields from blacksmith."""
        shield_list = items_module.items_dict["OffHand"]["Shield"]
        self.buy_equipment(shield_list, "Shield", )
    
    def buy_armor(self):
        """Buy armor from blacksmith - choose armor type first."""
        # Use ShopScreen for armor type selection
        shop_screen = ShopScreen(self.presenter, self.player_char, "Choose armor type")
        
        armor_dict = items_module.items_dict["Armor"]
        
        # Filter armor types by availability
        armor_types = []
        for armor_type, item_list in armor_dict.items():
            if self._has_available_items(item_list):
                armor_types.append(armor_type)
        
        # If no armor types available, return
        if not armor_types:
            return
        
        armor_types.append("Back")
        
        shop_screen.set_options(armor_types)
        armor_choice = shop_screen.navigate_options()
        
        # Treat ESC ("Leave") the same as Back for submenus
        if armor_choice is None or armor_choice in ("Back", "Leave"):
            return
        
        armor_type = armor_choice
        self.buy_equipment(armor_dict[armor_type], armor_type, )
    
    def buy_rings(self):
        """Buy rings from jeweler."""
        ring_list = items_module.items_dict["Accessory"]["Ring"]
        self.buy_equipment(ring_list, "Ring", )
    
    def buy_pendants(self):
        """Buy pendants from jeweler."""
        pendant_list = items_module.items_dict["Accessory"]["Pendant"]
        self.buy_equipment(pendant_list, "Pendant", )
    
    def buy_scrolls(self, background_image="town.png"):
        """Buy scrolls from alchemist."""
        scroll_list = items_module.items_dict["Misc"]["Scroll"]
        self.buy_equipment(scroll_list, "Scroll", background_image=background_image)

    def buy_misc(self):
        """Buy misc items from alchemist (excluding scrolls)."""
        misc_dict = dict(items_module.items_dict.get("Misc", {}))
        if "Scroll" in misc_dict:
            misc_dict.pop("Scroll")
        if not misc_dict:
            return
        self._buy_with_shop_screen(misc_dict, "Misc", )
    
    def buy_potions(self, background_image="town.png"):
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
        self._buy_with_shop_screen(potion_dict, "Potions", background_image=background_image)
    
    def buy_equipment(self, item_list, category_name, background_image="town.png"):
        """Generic equipment buying interface using ShopScreen."""
        # Build item dictionary
        itemdict = {category_name: item_list}
        
        # Use the new shop screen
        self._buy_with_shop_screen(itemdict, category_name, background_image=background_image)
    
    def _buy_with_shop_screen(self, itemdict, category_name, background_image="town.png"):
        """Use the new ShopScreen interface for buying items."""
        from .confirmation_popup import QuantityPopup
        
        shop_screen = ShopScreen(self.presenter, self.player_char, f"Buy {category_name}", background_image=background_image, options_list=[])
        shop_screen.update_item_list(itemdict, "Buy")
        
        # Create background function for popups
        bg_func = lambda: shop_screen.draw_all(do_flip=False)
        
        while True:
            result = shop_screen.navigate_items()
            
            # Result will be None if ESC was pressed (handled in navigate_items)
            if result is None:
                return
            
            display_str, item, cost, owned = result
            
            # Skip navigation items
            if display_str in ["Next Page"] or not item:
                continue
            
            # Use QuantityPopup for better quantity selection
            max_can_carry = self.player_char.stats.strength * 10
            max_qty = min(self.player_char.gold // cost, 99) if cost > 0 else 99
            
            qty_popup = QuantityPopup(self.presenter, item.name, cost, max_qty)
            quantity = qty_popup.show(background_draw_func=bg_func)
            
            if quantity is None or quantity == 0:
                continue
            
            total_cost = cost * quantity
            
            if self.player_char.gold < total_cost:
                self.presenter.show_message(f"Not enough gold! Need {total_cost}g")
                # Update the shop screen to reflect current gold
                shop_screen.draw_all()
                continue
            
            # Confirm purchase via popup
            confirm_popup = ConfirmationPopup(
                self.presenter,
                f"Buy {quantity}x {item.name} for {total_cost}g?"
            )
            confirmed = confirm_popup.show(background_draw_func=bg_func)
            if not confirmed:
                continue

            # Purchase items
            self.player_char.gold -= total_cost
            self.player_char.modify_inventory(item, num=quantity)

            # Show transaction summary in popup
            summary_popup = ConfirmationPopup(
                self.presenter,
                f"Purchased {quantity}x {item.name}!\n\nGold remaining: {self.player_char.gold}",
                show_buttons=False
            )
            summary_popup.show(background_draw_func=bg_func)
            
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
    
    def _has_available_items(self, item_classes):
        """Check if any items in the given list are available at the player's level."""
        player_level = self.player_char.player_level()
        
        for item_class in item_classes:
            item = item_class()
            
            # Check level restrictions
            if hasattr(item, 'restriction') and item.restriction:
                try:
                    if player_level < min(item.restriction):
                        continue
                except (TypeError, ValueError):
                    # Restriction contains non-numeric values (e.g., class names like "Ninja")
                    # Skip items with class restrictions
                    continue
            
            # Check rarity for town shops
            if self.player_char.in_town():
                min_rarity = max(0.4, (1.0 - (0.02 * player_level)))
                if item.rarity < min_rarity:
                    continue
            
            # If we get here, the item is available
            return True
        
        # No available items found
        return False
    
    def sell_items(self, background_image="town.png"):
        """Sell items from inventory using ShopScreen."""
        # Create background function for popups
        bg_func = None
        if background_image != "town.png":
            # For non-town shops, we'll set up bg_func after creating shop_screen
            pass
        
        if not self.player_char.inventory:
            popup = ConfirmationPopup(self.presenter, "You have nothing to sell!", show_buttons=False)
            popup.show(background_draw_func=bg_func if bg_func else None)
            return
        
        # Create ShopScreen once outside the loop to preserve cursor position
        shop_screen = ShopScreen(self.presenter, self.player_char, "Sell Items", background_image=background_image, options_list=[])
        
        # Now set up background function for popups if using custom background
        if background_image != "town.png":
            bg_func = lambda: shop_screen.draw_all(do_flip=False)
        
        while True:
            # Build sellable inventory (exclude ultimate items)
            sellable = {}
            for name, items_list in self.player_char.inventory.items():
                if items_list and not items_list[0].ultimate:
                    sellable[name] = items_list
            
            if not sellable:
                # Capture current shop background to avoid flicker
                shop_screen.draw_all(do_flip=False)
                popup = ConfirmationPopup(
                    self.presenter,
                    "You have no items to sell.",
                    show_buttons=False
                )
                popup.show(background_draw_func=bg_func if bg_func else None)
                return
            
            # Update the item list (preserves cursor position)
            shop_screen.update_item_list(sellable, "Sell")
            
            result = shop_screen.navigate_items()
            
            # Result will be None if ESC was pressed
            if result is None:
                return
            
            display_str, item, sell_price, count = result
            
            # Skip navigation items or items without data
            if display_str in ["Next Page"] or not item:
                continue
            
            # Use QuantityPopup for sell quantity selection
            from .confirmation_popup import QuantityPopup
            shop_screen.draw_all(do_flip=False)
            qty_popup = QuantityPopup(self.presenter, item.name, sell_price, count, action="sell", default_quantity=count)
            quantity = qty_popup.show(background_draw_func=bg_func if bg_func else None)
            
            if quantity is None or quantity == 0:
                continue
            
            total_gold = sell_price * quantity
            
            # Confirm sale via popup
            # Capture current shop screen as background to avoid flicker
            shop_screen.draw_all(do_flip=False)
            confirm_popup = ConfirmationPopup(
                self.presenter,
                f"Sell {quantity}x {item.name} for {total_gold}g?"
            )
            confirm = confirm_popup.show(background_draw_func=bg_func if bg_func else None)
            
            if confirm:
                self.player_char.gold += total_gold
                self.player_char.modify_inventory(item, num=quantity, subtract=True)

                # Show transaction summary in popup using captured background
                shop_screen.draw_all(do_flip=False)
                summary_popup = ConfirmationPopup(
                    self.presenter,
                    f"Sold {quantity}x {item.name} for {total_gold}g!\n\nGold: {self.player_char.gold}",
                    show_buttons=False
                )
                summary_popup.show(background_draw_func=bg_func if bg_func else None)
                # Continue selling (will reload inventory)
            else:
                # Continue browsing
                pass
    
    def visit_secret_shop(self):
        """Visit the secret shop in the dungeon - sells everything."""
        # Use ShopScreen with dungeon background
        shop_screen = ShopScreen(
            self.presenter, 
            self.player_char, 
            "Secret Shop - Rare Goods for Sale",
            background_image="dungeon.png"
        )
        shop_screen.set_options(["Buy", "Sell", "Leave"])
        
        # Create background function for popups
        bg_func = lambda: shop_screen.draw_all(do_flip=False)
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                popup = ConfirmationPopup(self.presenter, "Come back anytime!", show_buttons=False)
                popup.show(background_draw_func=bg_func)
                break
            elif choice == "Buy":
                # Show buy submenu
                shop_screen.set_options(["Weapons", "Shields & Tomes", "Armor", "Accessories", "Potions & Scrolls", "Back"])
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Weapons":
                    self._buy_secret_weapons(shop_screen)
                elif buy_choice == "Shields & Tomes":
                    self._buy_secret_offhand(shop_screen)
                elif buy_choice == "Armor":
                    self._buy_secret_armor(shop_screen)
                elif buy_choice == "Accessories":
                    self._buy_secret_accessories(shop_screen)
                elif buy_choice == "Potions & Scrolls":
                    self._buy_secret_consumables(shop_screen)
                
                # Restore main menu
                shop_screen.set_options(["Buy", "Sell", "Leave"])
                shop_screen.shop_message = "Secret Shop - Rare Goods for Sale"
            elif choice == "Sell":
                self.sell_items(background_image="dungeon.png")
                # Restore shop message after selling
                shop_screen.shop_message = "Secret Shop - Rare Goods for Sale"
    
    def _buy_secret_weapons(self, shop_screen):
        """Buy weapons from secret shop."""
        # Use shop screen for weapon type selection
        shop_screen.shop_message = "Choose weapon type"
        shop_screen.set_options(["1-Handed", "2-Handed", "Back"])
        
        handed_choice = shop_screen.navigate_options()
        
        if handed_choice is None or handed_choice == "Back":
            return
        
        handed = handed_choice
        weapon_dict = items_module.items_dict["Weapon"][handed]
        
        # Choose weapon subtype
        subtypes = list(weapon_dict.keys())
        subtypes.append("Back")
        
        shop_screen.shop_message = f"Choose {handed} weapon type"
        shop_screen.set_options(subtypes)
        subtype_choice = shop_screen.navigate_options()
        
        if subtype_choice is None or subtype_choice == "Back":
            return
        
        subtype = subtype_choice
        item_list = weapon_dict[subtype]
        
        self.buy_equipment(item_list, f"{handed} {subtype}", background_image="dungeon.png")
    
    def _buy_secret_offhand(self, shop_screen):
        """Buy shields, tomes, and rods from secret shop."""
        shop_screen.shop_message = "Choose off-hand type"
        shop_screen.set_options(["Shields", "Tomes", "Rods", "Back"])
        
        choice = shop_screen.navigate_options()
        
        if choice is None or choice == "Back":

            return
        
        offhand_types = {"Shields": "Shield", "Tomes": "Tome", "Rods": "Rod"}
        offhand_type = offhand_types[choice]
        item_list = items_module.items_dict["OffHand"][offhand_type]
        
        self.buy_equipment(item_list, offhand_type, background_image="dungeon.png")
    
    def _buy_secret_armor(self, shop_screen):
        """Buy armor from secret shop."""
        shop_screen.shop_message = "Choose armor type"
        shop_screen.set_options(["Cloth", "Light", "Medium", "Heavy", "Back"])
        
        choice = shop_screen.navigate_options()
        
        if choice is None or choice == "Back":
            return
        
        armor_type = choice
        item_list = items_module.items_dict["Armor"][armor_type]
        
        self.buy_equipment(item_list, f"{armor_type} Armor", background_image="dungeon.png")
    
    def _buy_secret_accessories(self, shop_screen):
        """Buy accessories from secret shop."""
        shop_screen.shop_message = "Choose accessory type"
        shop_screen.set_options(["Rings", "Pendants", "Back"])
        
        choice = shop_screen.navigate_options()
        
        if choice is None or choice == "Back":
            return
        
        acc_types = {"Rings": "Ring", "Pendants": "Pendant"}
        acc_type = acc_types[choice]
        item_list = items_module.items_dict["Accessory"][acc_type]
        
        self.buy_equipment(item_list, acc_type, background_image="dungeon.png")
    
    def _buy_secret_consumables(self, shop_screen):
        """Buy potions and scrolls from secret shop."""
        shop_screen.shop_message = "Choose consumable type"
        shop_screen.set_options(["Potions", "Stat Potions", "Scrolls", "Keys", "Back"])
        
        choice = shop_screen.navigate_options()
        
        if choice is None or choice == "Back":
            return
        
        if choice == "Potions":
            self.buy_potions(background_image="dungeon.png")
        elif choice == "Stat Potions":
            self._buy_secret_stat_potions()
        elif choice == "Keys":
            self._buy_secret_keys()
        else:  # Scrolls
            self.buy_scrolls(background_image="dungeon.png")

    def _buy_secret_stat_potions(self):
        """Buy stat potions from secret shop."""
        stat_potions = items_module.items_dict["Potion"].get("Stat", [])
        if not stat_potions:
            return
        self.buy_equipment(stat_potions, "Stat Potions", background_image="dungeon.png")

    def _buy_secret_keys(self):
        """Buy key items from secret shop."""
        key_items = items_module.items_dict.get("Misc", {}).get("Key", [])
        if not key_items:
            return
        self.buy_equipment(key_items, "Keys", background_image="dungeon.png")
