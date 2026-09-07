"""Inventory behavior for the popup menus package."""

import pygame

from src.core import items

from ..confirmation_popup import ConfirmationPopup
from .base import BasePopupMenu
from .selections import SelectionPopup


class InventoryPopupMenu(BasePopupMenu):
    def __init__(self, presenter, parent_screen):
        super().__init__(presenter, parent_screen, title="Inventory")
        self.sort_modes = ["Name", "Type", "Quantity", "Combat"]
        stored_mode = getattr(parent_screen, "_inventory_sort_mode", self.sort_modes[0])
        self.sort_mode_idx = (
            self.sort_modes.index(stored_mode) if stored_mode in self.sort_modes else 0
        )

    def _store_sort_mode(self, player_char=None):
        if self.parent_screen is not None:
            setattr(self.parent_screen, "_inventory_sort_mode", self._current_mode())
        if player_char is not None:
            setattr(player_char, "inventory_sort_mode", self._current_mode())

    def _is_combat_usable(self, item) -> bool:
        subtyp = getattr(item, "subtyp", None)
        return subtyp in ("Health", "Mana", "Elixir", "Status") or (
            subtyp == "Scroll" and getattr(item, "name", "") != "Sanctuary Scroll"
        )

    def _current_mode(self) -> str:
        return self.sort_modes[self.sort_mode_idx]

    def _cycle_mode(self, player_char=None):
        self.sort_mode_idx = (self.sort_mode_idx + 1) % len(self.sort_modes)
        self._store_sort_mode(player_char)

    def _sort_inventory_items(self, items):
        mode = self._current_mode()
        if mode == "Combat":
            combat_items = [entry for entry in items if self._is_combat_usable(entry[1])]
            non_combat_items = [entry for entry in items if not self._is_combat_usable(entry[1])]
            return (
                sorted(combat_items, key=lambda entry: str(getattr(entry[1], "name", "")).lower())
                + non_combat_items
            )
        if mode == "Type":
            return sorted(
                items,
                key=lambda entry: (
                    str(getattr(entry[1], "subtyp", "")),
                    str(getattr(entry[1], "name", "")).lower(),
                ),
            )
        if mode == "Quantity":
            return sorted(
                items, key=lambda entry: (-entry[2], str(getattr(entry[1], "name", "")).lower())
            )
        return sorted(items, key=lambda entry: str(getattr(entry[1], "name", "")).lower())

    def build_items(self, player_char):
        stored_mode = getattr(player_char, "inventory_sort_mode", None)
        if stored_mode in self.sort_modes:
            self.sort_mode_idx = self.sort_modes.index(stored_mode)
        items = []
        # Flatten inventory dict: {category: [items]} and group identical items
        inv = getattr(player_char, "inventory", {})
        for category, lst in inv.items():
            # Group items by name
            grouped = {}
            for it in lst:
                name = getattr(it, "name", str(it))
                if name not in grouped:
                    grouped[name] = []
                grouped[name].append(it)

            # Create entries with count
            for name, item_list in grouped.items():
                # Use first item as representative
                items.append((category, item_list[0], len(item_list)))

        items = self._sort_inventory_items(items)

        self.items = items
        self.selected_index = 0 if items else -1
        self.scroll_offset = 0
        self.title = f"Inventory [{self._current_mode()}]"
        self._store_sort_mode(player_char)

    def item_display_text(self, item):
        category, obj, count = item
        name = getattr(obj, "name", str(obj))
        qty = getattr(obj, "qty", None)
        if count > 1:
            return f"{name} x{count}"
        elif qty is not None:
            return f"{name} x{qty}"
        else:
            return name

    def draw_details(self, player_char):
        """Override to extract object from (category, obj, count) tuple."""
        if not self.items:
            x = self.details_rect.left + 16
            y = self.details_rect.top + 12
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        category, obj, count = self.items[self.selected_index]
        x = self.details_rect.left + 16
        y = self.draw_item_detail_layout(obj, category=category)

        # Custom details hook
        self.draw_details_extra(player_char, (category, obj, count), x, y)

    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width in pixels."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line = " ".join(current_line)
            line_width = self.normal_font.size(line)[0]

            if line_width > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def draw_details_extra(self, player_char, item, x, y):
        return None

    def on_select(self, player_char, item):
        # Show action submenu for selected inventory item
        category, obj, count = item

        # Build action options based on item type
        actions = []

        # Map item typ to equipment slot
        item_typ = getattr(obj, "typ", None)
        typ_to_slot = {
            "Weapon": "Weapon",
            "Armor": "Armor",
            "Helmet": "Helmet",
            "OffHand": "OffHand",
            "Ring": "Ring",
            "Pendant": "Pendant",
        }

        # For accessories, check if it's a ring or pendant
        if item_typ == "Accessory":
            subtyp = getattr(obj, "subtyp", None)
            if subtyp == "Ring":
                item_slot = "Ring"
            elif subtyp == "Pendant":
                item_slot = "Pendant"
            else:
                item_slot = None
        else:
            item_slot = typ_to_slot.get(item_typ)

        # Can equip if it has a valid slot and isn't already equipped
        if item_slot:
            current_equipped = player_char.equipment.get(item_slot)
            if current_equipped != obj:
                actions.append("Equip")

        # Check if item is usable (consumable) - check subtyp, not category
        item_subtyp = getattr(obj, "subtyp", None)
        if (
            item_subtyp in ("Health", "Mana", "Elixir", "Stat")
            or getattr(obj, "name", "") == "Sanctuary Scroll"
        ):
            actions.append("Use")

        actions.extend(["Drop", "Cancel"])

        # Show action menu
        action_popup = SelectionPopup(
            self.presenter,
            self.parent_screen,
            title=f"Action: {getattr(obj, 'name', 'Item')}",
            header_message=f"What would you like to do with {getattr(obj, 'name', 'this item')}?",
            options=actions,
        )

        item_name = getattr(obj, "name", str(obj))

        # Capture inventory view once to avoid flicker between action menu uses
        self.parent_screen.draw_all(player_char, do_flip=False)
        self.draw_background(self.screen.copy())
        self.draw_popup(player_char)
        self.draw_list()
        self.draw_details(player_char)
        pygame.display.flip()
        base_bg = self.screen.copy()

        while True:
            # Temporarily override draw_background for nested popup
            original_draw_bg = action_popup.draw_background
            action_popup.draw_background = lambda surf: self.screen.blit(base_bg, (0, 0))
            try:
                result = action_popup.show(player_char, flush_events=True, require_key_release=True)
            finally:
                action_popup.draw_background = original_draw_bg

            if not result or result[0] != "selection":
                break

            action = result[1]
            action_bg = self.screen.copy()

            if action == "Cancel":
                break
            if action == "Equip":
                self._equip_item(player_char, obj, category, background_surface=action_bg)
                break
            if action == "Use":
                self._use_item(player_char, obj, category, background_surface=action_bg)
            elif action == "Drop":
                self._drop_item(player_char, obj, category, background_surface=action_bg)

            remaining = [
                it
                for it in player_char.inventory.get(category, [])
                if getattr(it, "name", str(it)) == item_name
            ]
            if not remaining:
                break
            obj = remaining[0]

        # Return None to keep inventory open
        return None

    def handle_key_down(self, player_char, event) -> bool:
        if event.key in (pygame.K_s,):
            self._cycle_mode(player_char)
            self.build_items(player_char)
            if self.items and self.selected_index < 0:
                self.selected_index = 0
            self._ensure_visible()
            return True
        return False

    def help_footer(self) -> str:
        return (
            "Arrows: Navigate  Enter: Select  S: Cycle Sort/Filter  Esc: Close  PgUp/PgDn: Scroll"
        )

    def _show_inventory_notice(self, player_char, message: str, background_surface=None) -> None:
        menu_bg = background_surface or self._capture_menu_surface(player_char)
        popup = ConfirmationPopup(self.presenter, message, show_buttons=False)
        popup.show(
            background_draw_func=lambda: self.screen.blit(menu_bg, (0, 0)),
            flush_events=True,
            require_key_release=True,
        )

    def _equip_item(self, player_char, item, category, background_surface=None):
        """Equip an item from inventory with class restrictions respected."""
        # Map item typ to equipment slot
        typ_to_slot = {
            "Weapon": "Weapon",
            "Armor": "Armor",
            "OffHand": "OffHand",
            "Ring": "Ring",
            "Pendant": "Pendant",
        }

        item_typ = getattr(item, "typ", None)
        slot = typ_to_slot.get(item_typ)

        # For accessories, check if it's a ring or pendant
        if item_typ == "Accessory":
            subtyp = getattr(item, "subtyp", None)
            if subtyp == "Ring":
                slot = "Ring"
            elif subtyp == "Pendant":
                slot = "Pendant"

        if not slot:
            self._show_inventory_notice(
                player_char,
                f"You cannot equip {getattr(item, 'name', 'that item')}.",
                background_surface,
            )
            return

        # Enforce class equip restrictions
        if hasattr(player_char, "cls") and hasattr(player_char.cls, "equip_check"):
            can_equip = getattr(player_char, "can_equip_item", None)
            allowed = (
                can_equip(item, slot)
                if callable(can_equip)
                else player_char.cls.equip_check(item, slot)
            )
            if not allowed:
                self._show_inventory_notice(
                    player_char,
                    f"You cannot equip {getattr(item, 'name', 'that item')}.",
                    background_surface,
                )
                return
        equip_method = getattr(player_char, "equip", None)
        if callable(equip_method):
            result = equip_method(slot, item)
            if result is False:
                self._show_inventory_notice(
                    player_char,
                    f"You cannot equip {getattr(item, 'name', 'that item')}.",
                    background_surface,
                )
                return
        else:
            # Check if current item can be unequipped
            current = player_char.equipment.get(slot)
            if current and not getattr(current, "unequip", True):
                self._show_inventory_notice(
                    player_char,
                    f"You cannot unequip {getattr(current, 'name', 'this item')}.",
                    background_surface,
                )
                return

            # Move current item to inventory (if it exists and is not a placeholder)
            if current and getattr(current, "name", None) not in (None, "None"):
                player_char.inventory.setdefault(current.name, []).append(current)

            # Equip new item
            player_char.equipment[slot] = item

            # Remove from inventory
            if category in player_char.inventory and item in player_char.inventory[category]:
                player_char.inventory[category].remove(item)
                if not player_char.inventory[category]:
                    del player_char.inventory[category]

        # Rebuild items list
        self.build_items(player_char)

    def _use_item(self, player_char, item, category, background_surface=None):
        """Use a consumable item."""
        menu_bg = background_surface or self._capture_menu_surface(player_char)

        # Call the item's use method if it has one
        if hasattr(item, "use") and callable(item.use):
            try:
                result = item.use(player_char)
                if result:
                    result_bg = background_surface or self._capture_menu_surface(player_char)
                    result_popup = ConfirmationPopup(self.presenter, result, show_buttons=False)
                    result_popup.show(
                        background_draw_func=lambda: self.screen.blit(result_bg, (0, 0)),
                        flush_events=True,
                        require_key_release=True,
                    )
            except Exception as e:
                self.presenter.show_message(f"Error using item: {e}")

        # Remove item from inventory
        if category in player_char.inventory and item in player_char.inventory[category]:
            player_char.inventory[category].remove(item)
            if not player_char.inventory[category]:
                del player_char.inventory[category]

        # Rebuild items list
        self.build_items(player_char)

    def _drop_item(self, player_char, item, category, background_surface=None):
        """Drop an item from inventory."""
        # Confirm drop
        menu_bg = background_surface or self._capture_menu_surface(player_char)
        popup = ConfirmationPopup(
            self.presenter, f"Drop {getattr(item, 'name', 'this item')}? This cannot be undone."
        )
        if not popup.show(
            background_draw_func=lambda: self.screen.blit(menu_bg, (0, 0)),
            flush_events=True,
            require_key_release=True,
        ):
            return

        # Remove from inventory
        if category in player_char.inventory and item in player_char.inventory[category]:
            player_char.inventory[category].remove(item)
            if not player_char.inventory[category]:
                del player_char.inventory[category]

        # Rebuild items list
        self.build_items(player_char)
