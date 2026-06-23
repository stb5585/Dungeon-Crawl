"""
Shop system for GUI - handles blacksmith, alchemist, and jeweler.
Implements the core shop logic from town.py adapted for Pygame presenter.
"""

from src.core import items as items_module
from src.core.classes import dragoon
from .shop_screen import ShopScreen
from .confirmation_popup import ConfirmationPopup
from .popup_menus import SelectionPopup
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
            popup.show(flush_events=True, require_key_release=True)
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
                popup.show(flush_events=True, require_key_release=True)
                break
            elif choice == "Buy":
                # Update options to show buy categories
                shop_screen.set_options(["Weapons", "Shields", "Armor", "Helmets", "Back"])
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Weapons":
                    self.buy_weapons()
                elif buy_choice == "Shields":
                    self.buy_shields()
                elif buy_choice == "Armor":
                    self.buy_armor()
                elif buy_choice == "Helmets":
                    self.buy_helmets()
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
                popup.show(flush_events=True, require_key_release=True)
                break
            elif choice == "Buy":
                self.buy_alchemist_goods()
                shop_screen.shop_message = "Welcome to Ye Olde Item Shoppe."
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Alchemist')
    
    def visit_jeweler(self):
        """Visit the Jeweler - rings and pendants."""
        if self.player_char.player_level() < 10:
            popup = ConfirmationPopup(self.presenter, "Sorry but the jeweler is currently closed. Try again later.", show_buttons=False)
            popup.show(flush_events=True, require_key_release=True)
            return
        
        from .quest_manager import QuestManager
        
        # Use ShopScreen for the main interface
        shop_screen = ShopScreen(self.presenter, self.player_char, "Come glimpse the finest jewelry in the land.")
        qm = QuestManager(
            self.presenter,
            self.player_char,
            quest_text_renderer=lambda text: shop_screen.display_quest_text(text),
        )
        options = ["Buy", "Sell", "Quests", "Leave"]
        if dragoon.can_craft_draconite_pendant(self.player_char):
            options.insert(3, "Craft Draconite Pendant")
        shop_screen.set_options(options)
        
        while True:
            choice = shop_screen.navigate_options()
            
            if choice is None or choice == "Leave":
                popup = ConfirmationPopup(self.presenter, "May fortune favor you!", show_buttons=False)
                popup.show(flush_events=True, require_key_release=True)
                break
            elif choice == "Buy":
                self.buy_jewelry()
                shop_screen.shop_message = "Come glimpse the finest jewelry in the land."
            elif choice == "Sell":
                self.sell_items()
            elif choice == "Quests":
                qm.check_and_offer('Jeweler')
            elif choice == "Craft Draconite Pendant":
                ok, message = dragoon.craft_draconite_pendant(self.player_char)
                self.presenter.show_message(message)
                options = ["Buy", "Sell", "Quests", "Leave"]
                if dragoon.can_craft_draconite_pendant(self.player_char):
                    options.insert(3, "Craft Draconite Pendant")
                shop_screen.set_options(options)
    
    def buy_weapons(self):
        """Buy weapons - choose handedness first, then browse subtype tabs."""
        # Use ShopScreen for weapon type selection
        shop_screen = ShopScreen(self.presenter, self.player_char, "Choose weapon type")
        shop_screen.set_options(["1-Handed", "2-Handed", "Back"])
        handed_choice = shop_screen.navigate_options()
        
        # Treat ESC ("Leave") the same as Back for submenus
        if handed_choice is None or handed_choice in ("Back", "Leave"):
            return
        
        handed = handed_choice
        weapon_tabs = self._available_item_groups(items_module.items_dict["Weapon"][handed])
        if not weapon_tabs:
            return

        self._buy_with_shop_screen(weapon_tabs, f"{handed} Weapons")
    
    def buy_shields(self):
        """Buy shields from blacksmith."""
        shield_list = items_module.items_dict["OffHand"]["Shield"]
        self.buy_equipment(shield_list, "Shield", )
    
    def buy_armor(self):
        """Buy armor from blacksmith with armor-type tabs."""
        armor_tabs = self._available_item_groups(items_module.items_dict["Armor"])
        if not armor_tabs:
            return

        self._buy_with_shop_screen(armor_tabs, "Armor")

    def buy_helmets(self):
        """Buy helmets from blacksmith with helmet-type tabs."""
        helmet_tabs = self._available_item_groups(items_module.items_dict["Helmet"])
        if not helmet_tabs:
            return

        self._buy_with_shop_screen(helmet_tabs, "Helmets")
    
    def buy_rings(self):
        """Buy rings from jeweler."""
        ring_list = items_module.items_dict["Accessory"]["Ring"]
        self.buy_equipment(ring_list, "Ring", )
    
    def buy_pendants(self):
        """Buy pendants from jeweler."""
        pendant_list = items_module.items_dict["Accessory"]["Pendant"]
        self.buy_equipment(pendant_list, "Pendant", )

    def buy_jewelry(self):
        """Buy rings and pendants from one tabbed jeweler browser."""
        jewelry_tabs = {
            "Rings": items_module.items_dict["Accessory"]["Ring"],
            "Pendants": items_module.items_dict["Accessory"]["Pendant"],
        }
        self._buy_with_shop_screen(jewelry_tabs, "Jewelry")
    
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
        self._buy_with_shop_screen(self._available_item_groups(misc_dict), "Misc", )
    
    def buy_potions(self, background_image="town.png"):
        """Buy potions from alchemist with level-based availability."""
        potion_dict = {"Restorative": self._potion_item_classes()}
        self._buy_with_shop_screen(potion_dict, "Potions", background_image=background_image)

    def buy_alchemist_goods(self):
        """Buy alchemist stock from one tabbed browser."""
        misc_dict = dict(items_module.items_dict.get("Misc", {}))
        scrolls = misc_dict.pop("Scroll", [])
        alchemist_tabs = {
            "Potions": self._potion_item_classes(),
            "Scrolls": scrolls,
            **self._available_item_groups(misc_dict),
        }
        self._buy_with_shop_screen(alchemist_tabs, "Alchemist Goods")

    def _potion_item_classes(self):
        """Return level-appropriate restorative potion classes."""
        # Get potion items from items_dict
        potion_classes = []
        player_level = self.player_char.player_level()
        
        # Basic potions
        potion_classes.append(items_module.HealthPotion)
        potion_classes.append(items_module.ManaPotion)
        
        # Better potions at higher levels
        if player_level >= 10:
            potion_classes.append(items_module.GreatHealthPotion)
            potion_classes.append(items_module.GreatManaPotion)
        
        if player_level >= 30:
            potion_classes.append(items_module.SuperHealthPotion)
            potion_classes.append(items_module.SuperManaPotion)

        return potion_classes
    
    def buy_equipment(self, item_list, category_name, background_image="town.png"):
        """Generic equipment buying interface using ShopScreen."""
        # Build item dictionary
        itemdict = {category_name: item_list}
        
        # Use the new shop screen
        self._buy_with_shop_screen(itemdict, category_name, background_image=background_image)
    
    def _buy_with_shop_screen(self, itemdict, category_name, background_image="town.png"):
        """Use the new ShopScreen interface for buying items."""
        from .confirmation_popup import QuantityPopup

        if not itemdict:
            return
        
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
            quantity = qty_popup.show(
                background_draw_func=bg_func,
                flush_events=True,
                require_key_release=True,
            )
            
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
            confirmed = confirm_popup.show(
                background_draw_func=bg_func,
                flush_events=True,
                require_key_release=True,
            )
            if not confirmed:
                continue

            equip_actions = self._equip_actions_for_purchase(item, quantity)

            # Purchase items
            self.player_char.gold -= total_cost
            if equip_actions:
                for _ in range(quantity):
                    self.player_char.modify_inventory(self._fresh_shop_item(item))
            else:
                self.player_char.modify_inventory(item, num=quantity)

            # Show transaction summary in popup
            summary_popup = ConfirmationPopup(
                self.presenter,
                f"Purchased {quantity}x {item.name}!\n\nGold remaining: {self.player_char.gold}",
                show_buttons=False
            )
            summary_popup.show(background_draw_func=bg_func, flush_events=True, require_key_release=True)
            if equip_actions:
                self._offer_equip_after_buy(shop_screen, item, quantity, equip_actions)
            
            # Update item list to reflect new owned count
            shop_screen.update_item_list(itemdict, "Buy")

    @staticmethod
    def _fresh_shop_item(item):
        try:
            return item.__class__()
        except TypeError:
            return item

    @staticmethod
    def _slot_label(slot: str) -> str:
        return "Main Hand" if slot == "Weapon" else slot

    def _equip_actions_for_purchase(self, item, quantity: int) -> dict[str, tuple[str, ...]]:
        slots = items_module.equipment_slots_for_item(item, self.player_char)
        actions: dict[str, tuple[str, ...]] = {}
        if not slots:
            return actions
        if getattr(item, "typ", None) == "Weapon":
            if "Weapon" in slots:
                actions["Main Hand"] = ("Weapon",)
            if "OffHand" in slots:
                actions["OffHand"] = ("OffHand",)
            if quantity >= 2 and "Weapon" in slots and "OffHand" in slots:
                actions["Dual Wield"] = ("Weapon", "OffHand")
            return actions
        actions["Equip Now"] = (slots[0],)
        return actions

    def _purchased_inventory_items(self, item, count: int) -> list:
        return list(getattr(self.player_char, "inventory", {}).get(item.name, []))[-count:]

    def _equip_purchased_item(self, item, slots: tuple[str, ...]) -> bool:
        purchased = self._purchased_inventory_items(item, len(slots))
        if len(purchased) < len(slots):
            return False
        for slot, purchased_item in zip(slots, purchased):
            equip_method = getattr(self.player_char, "equip", None)
            if not callable(equip_method) or equip_method(slot, purchased_item) is False:
                return False
        return True

    def _offer_equip_after_buy(self, shop_screen, item, quantity: int, actions=None) -> None:
        actions = actions or self._equip_actions_for_purchase(item, quantity)
        if not actions:
            return
        options = list(actions) + ["Cancel"]
        popup = SelectionPopup(
            self.presenter,
            shop_screen,
            title=f"Equip {item.name}?",
            header_message=f"Equip one purchased {item.name} now?",
            options=options,
        )
        result = popup.show(self.player_char, flush_events=True, require_key_release=True)
        if not result or result[0] != "selection":
            return
        action = result[1]
        if action == "Cancel":
            return
        slots = actions.get(action)
        if not slots:
            return
        if self._equip_purchased_item(item, slots):
            slot_text = " and ".join(self._slot_label(slot) for slot in slots)
            ConfirmationPopup(
                self.presenter,
                f"Equipped {item.name} to {slot_text}.",
                show_buttons=False,
            ).show(
                background_draw_func=lambda: shop_screen.draw_all(do_flip=False),
                flush_events=True,
                require_key_release=True,
            )
        else:
            ConfirmationPopup(
                self.presenter,
                f"Could not equip {item.name}. It remains in inventory.",
                show_buttons=False,
            ).show(
                background_draw_func=lambda: shop_screen.draw_all(do_flip=False),
                flush_events=True,
                require_key_release=True,
            )

    def _available_item_groups(self, itemdict):
        """Return item groups that have at least one item available to this player."""
        return {
            subtype: item_list
            for subtype, item_list in itemdict.items()
            if self._has_available_items(item_list)
        }
    
    def _format_item_info(self, item):
        """Format item information with description and stat comparison."""
        info_lines = []
        
        # Item name and type
        info_lines.append(f"Type: {item.typ}")
        themed_name = items_module.stat_themed_item_name(item)
        if themed_name != item.name:
            info_lines.append(f"Theme Name: {themed_name}")
        if hasattr(item, 'subtyp'):
            info_lines.append(f"Subtype: {item.subtyp}")
        info_lines.extend(items_module.item_metadata_lines(item))
        
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
        if item.typ in ["Weapon", "OffHand", "Armor", "Helmet", "Accessory"]:
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
            popup.show(background_draw_func=bg_func if bg_func else None, flush_events=True, require_key_release=True)
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
                popup.show(background_draw_func=bg_func if bg_func else None, flush_events=True, require_key_release=True)
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
            quantity = qty_popup.show(
                background_draw_func=bg_func if bg_func else None,
                flush_events=True,
                require_key_release=True,
            )
            
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
            confirm = confirm_popup.show(
                background_draw_func=bg_func if bg_func else None,
                flush_events=True,
                require_key_release=True,
            )
            
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
                summary_popup.show(background_draw_func=bg_func if bg_func else None, flush_events=True, require_key_release=True)
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
                popup.show(background_draw_func=bg_func, flush_events=True, require_key_release=True)
                break
            elif choice == "Buy":
                # Show buy submenu
                shop_screen.set_options(["Weapons", "Shields & Tomes", "Armor", "Helmets", "Accessories", "Potions & Scrolls", "Back"])
                buy_choice = shop_screen.navigate_options()
                
                if buy_choice == "Weapons":
                    self._buy_secret_weapons(shop_screen)
                elif buy_choice == "Shields & Tomes":
                    self._buy_secret_offhand(shop_screen)
                elif buy_choice == "Armor":
                    self._buy_secret_armor(shop_screen)
                elif buy_choice == "Helmets":
                    self._buy_secret_helmets(shop_screen)
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
        weapon_tabs = self._available_item_groups(items_module.items_dict["Weapon"][handed])
        if not weapon_tabs:
            return

        self._buy_with_shop_screen(weapon_tabs, f"{handed} Weapons", background_image="dungeon.png")
    
    def _buy_secret_offhand(self, shop_screen):
        """Buy shields, tomes, and rods from secret shop."""
        offhand_tabs = {
            "Shields": items_module.items_dict["OffHand"]["Shield"],
            "Tomes": items_module.items_dict["OffHand"]["Tome"],
            "Rods": items_module.items_dict["OffHand"]["Rod"],
        }
        self._buy_with_shop_screen(self._available_item_groups(offhand_tabs), "Off-Hand", background_image="dungeon.png")
    
    def _buy_secret_armor(self, shop_screen):
        """Buy armor from secret shop."""
        armor_tabs = self._available_item_groups(items_module.items_dict["Armor"])
        self._buy_with_shop_screen(armor_tabs, "Armor", background_image="dungeon.png")

    def _buy_secret_helmets(self, shop_screen):
        """Buy helmets from secret shop."""
        helmet_tabs = self._available_item_groups(items_module.items_dict["Helmet"])
        self._buy_with_shop_screen(helmet_tabs, "Helmets", background_image="dungeon.png")
    
    def _buy_secret_accessories(self, shop_screen):
        """Buy accessories from secret shop."""
        accessory_tabs = {
            "Rings": items_module.items_dict["Accessory"]["Ring"],
            "Pendants": items_module.items_dict["Accessory"]["Pendant"],
        }
        self._buy_with_shop_screen(self._available_item_groups(accessory_tabs), "Accessories", background_image="dungeon.png")
    
    def _buy_secret_consumables(self, shop_screen):
        """Buy potions and scrolls from secret shop."""
        consumable_tabs = {
            "Potions": self._potion_item_classes(),
            "Stat Potions": items_module.items_dict["Potion"].get("Stat", []),
            "Scrolls": items_module.items_dict["Misc"].get("Scroll", []),
            "Keys": items_module.items_dict.get("Misc", {}).get("Key", []),
        }
        self._buy_with_shop_screen(
            self._available_item_groups(consumable_tabs),
            "Consumables",
            background_image="dungeon.png",
        )

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
