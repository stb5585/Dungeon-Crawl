"""
Docstring for gui.popup_menus
"""

import pygame

from src.core import items
from src.core import map_tiles
from .confirmation_popup import ConfirmationPopup


class BasePopupMenu:
    def __init__(self, presenter, parent_screen, title="Menu"):
        self.presenter = presenter
        self.parent_screen = parent_screen  # CharacterScreen instance for background draw
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height

        self.title = title

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (192, 192, 192)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)

        # Fonts
        self.title_font = presenter.title_font
        self.large_font = presenter.large_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font

        # Layout
        self.popup_rect = pygame.Rect(self.width // 10, self.height // 8, self.width * 8 // 10, self.height * 3 // 4)
        self.list_rect = pygame.Rect(self.popup_rect.left + 24, self.popup_rect.top + 72, self.popup_rect.width * 2 // 5, self.popup_rect.height - 120)
        self.details_rect = pygame.Rect(self.popup_rect.left + self.popup_rect.width * 2 // 5 + 40, self.popup_rect.top + 72, self.popup_rect.width * 3 // 5 - 64, self.popup_rect.height - 120)

        # Data
        self.items = []  # list of displayable items (objects or strings)
        self.selected_index = 0
        self.scroll_offset = 0
        self.line_height = 24

    def _truncate_text(self, text, max_width):
        """Truncate text with ellipsis to fit within max_width pixels."""
        if self.normal_font.size(text)[0] <= max_width:
            return text
        ellipsis = "..."
        max_width = max(0, max_width - self.normal_font.size(ellipsis)[0])
        if max_width <= 0:
            return ellipsis
        truncated = text
        while truncated and self.normal_font.size(truncated)[0] > max_width:
            truncated = truncated[:-1]
        return f"{truncated}{ellipsis}"

    def _ensure_visible(self):
        """Ensure selected_index is visible and scroll_offset is clamped."""
        if not self.items:
            self.selected_index = 0
            self.scroll_offset = 0
            return
        max_visible = max(1, self.list_rect.height // self.line_height)
        max_scroll = max(0, len(self.items) - max_visible)
        self.selected_index = max(0, min(self.selected_index, len(self.items) - 1))
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        if self.selected_index >= self.scroll_offset + max_visible:
            self.scroll_offset = self.selected_index - max_visible + 1
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def build_items(self, player_char):
        """Override in subclass to populate self.items."""
        self.items = []

    def item_display_text(self, item):
        """Override for how to show each row's text."""
        return str(item)

    def handle_key_down(self, player_char, event) -> bool:
        """Subclass hook for custom key handling. Return True if handled."""
        return False

    def help_footer(self) -> str:
        return "Arrows: Navigate  Enter: Select  Esc: Close  PgUp/PgDn: Scroll"

    def draw_background(self, background_surface):
        # Blit pre-rendered background and a semi-transparent overlay
        self.screen.blit(background_surface, (0, 0))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

    def draw_popup(self, player_char):
        pygame.draw.rect(self.screen, self.BLACK, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, 2)

        # Title
        title_text = self.title_font.render(self.title, True, self.GOLD)
        self.screen.blit(title_text, (self.popup_rect.centerx - title_text.get_width() // 2, self.popup_rect.top + 16))

        # Column borders
        pygame.draw.rect(self.screen, self.BLACK, self.list_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.list_rect, 2)
        pygame.draw.rect(self.screen, self.BLACK, self.details_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.details_rect, 2)

        # Help footer
        help_str = self.help_footer()
        help_text = self.small_font.render(help_str, True, self.WHITE)
        self.screen.blit(help_text, (self.popup_rect.left + 16, self.popup_rect.bottom - help_text.get_height() - 12))

    def draw_list(self):
        # Visible rows
        max_visible = max(1, self.list_rect.height // self.line_height)
        start = self.scroll_offset
        end = min(len(self.items), start + max_visible)
        y = self.list_rect.top + 8
        text_max_width = self.list_rect.width - 32

        for idx in range(start, end):
            item = self.items[idx]
            is_header = isinstance(item, dict) and item.get("is_header")
            text_str = self._truncate_text(self.item_display_text(item), text_max_width)
            row_rect = pygame.Rect(self.list_rect.left + 8, y - 2, self.list_rect.width - 16, self.line_height)
            if is_header:
                text = self.normal_font.render(text_str, True, self.GOLD)
            elif idx == self.selected_index:
                pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, row_rect)
                text = self.normal_font.render(text_str, True, self.GOLD)
            else:
                text = self.normal_font.render(text_str, True, self.WHITE)
            self.screen.blit(text, (self.list_rect.left + 16, y))
            y += self.line_height

        # Scrollbar indicator (simple)
        if len(self.items) > max_visible:
            bar_height = int(self.list_rect.height * max_visible / len(self.items))
            bar_height = max(24, bar_height)
            max_scroll = len(self.items) - max_visible
            scrolled = 0 if max_scroll <= 0 else int(self.scroll_offset * (self.list_rect.height - bar_height) / max_scroll)
            bar_rect = pygame.Rect(self.list_rect.right - 12, self.list_rect.top + scrolled + 4, 8, bar_height)
            pygame.draw.rect(self.screen, self.GRAY, bar_rect)

    def draw_details(self, player_char):
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        # Extract header/value metadata when present
        is_header = isinstance(item, dict) and item.get("is_header")
        value = item.get("value") if isinstance(item, dict) else item
        text_label = item.get("text") if isinstance(item, dict) else None

        if is_header:
            header_text = self.large_font.render(text_label or "", True, self.GOLD)
            self.screen.blit(header_text, (x, y))
            return

        # Name
        name = getattr(value, "name", text_label if text_label else str(value))
        name_text = self.large_font.render(name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        # Generic attributes if present
        attrs = []
        for key in ("description", "slot", "subtyp", "value", "weight"):
            if hasattr(value, key):
                val = getattr(value, key)
                attrs.append((key.capitalize(), val))

        for label, val in attrs:
            line = f"{label}: {val}"
            text = self.normal_font.render(line, True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height

        # Custom details hook
        self.draw_details_extra(player_char, value, x, y)

    def draw_details_extra(self, player_char, item, x, y):
        """Subclasses can render more information."""
        pass

    def on_select(self, player_char, item):
        """Handle selection. Subclasses should override. Return a result or None."""
        return ("selected", item)

    def _capture_menu_surface(self, player_char):
        """Render the menu without popups and return a surface snapshot."""
        self.parent_screen.draw_all(player_char, do_flip=False)
        background_surface = self.screen.copy()
        self.draw_background(background_surface)
        self.draw_popup(player_char)
        self.draw_list()
        self.draw_details(player_char)
        pygame.display.flip()
        return self.screen.copy()

    def show(self, player_char):
        # Prepare items
        self.build_items(player_char)
        if not self.items:
            self.items = []
            self.selected_index = 0
            self.scroll_offset = 0
        # Ensure initial selection is on a selectable item (not a header)
        while self.items and isinstance(self.items[self.selected_index], dict) and self.items[self.selected_index].get("is_header"):
            if self.selected_index < len(self.items) - 1:
                self.selected_index += 1
            else:
                break

        running = True
        result = None
        clock = self.presenter.clock

        # Render and capture background once to prevent flicker
        self.parent_screen.draw_all(player_char, do_flip=False)
        background_surface = self.screen.copy()

        prev_provider = getattr(self.presenter, "_background_provider", None)
        menu_surface_ref = [None]
        if hasattr(self.presenter, "set_background_provider"):
            self.presenter.set_background_provider(lambda: menu_surface_ref[0] or self.screen.copy())

        while running:
            self.draw_background(background_surface)
            self.draw_popup(player_char)
            self.draw_list()
            self.draw_details(player_char)
            pygame.display.flip()
            menu_surface_ref[0] = self.screen.copy()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if self.handle_key_down(player_char, event):
                        self.parent_screen.draw_all(player_char, do_flip=False)
                        background_surface = self.screen.copy()
                        menu_surface_ref[0] = None
                        continue
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        result = None
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.items:
                            current_item = self.items[self.selected_index]
                            # Skip headers
                            if not (isinstance(current_item, dict) and current_item.get("is_header")):
                                result = self.on_select(player_char, current_item)
                                # If on_select returns None, keep menu open (for actions that update in place)
                                if result is not None:
                                    running = False
                                else:
                                    # Rebuild display after action
                                    self.parent_screen.draw_all(player_char, do_flip=False)
                                    background_surface = self.screen.copy()
                                    menu_surface_ref[0] = None
                    elif event.key == pygame.K_UP:
                        if self.items:
                            self.selected_index -= 1
                            while self.selected_index >= 0 and isinstance(self.items[self.selected_index], dict) and self.items[self.selected_index].get("is_header"):
                                self.selected_index -= 1
                            if self.selected_index < 0:
                                # Wrap to last selectable item
                                self.selected_index = len(self.items) - 1
                                while self.selected_index >= 0 and isinstance(self.items[self.selected_index], dict) and self.items[self.selected_index].get("is_header"):
                                    self.selected_index -= 1
                        self._ensure_visible()
                    elif event.key == pygame.K_DOWN:
                        if self.items:
                            self.selected_index += 1
                            while self.selected_index < len(self.items) and isinstance(self.items[self.selected_index % len(self.items)], dict) and self.items[self.selected_index % len(self.items)].get("is_header"):
                                self.selected_index += 1
                            if self.selected_index >= len(self.items):
                                self.selected_index = 0
                                while self.selected_index < len(self.items) and isinstance(self.items[self.selected_index], dict) and self.items[self.selected_index].get("is_header"):
                                    self.selected_index += 1
                        self._ensure_visible()
                    elif event.key == pygame.K_PAGEUP:
                        if self.items:
                            max_visible = max(1, self.list_rect.height // self.line_height)
                            self.selected_index = max(0, self.selected_index - max_visible)
                            while self.selected_index >= 0 and isinstance(self.items[self.selected_index], dict) and self.items[self.selected_index].get("is_header"):
                                self.selected_index -= 1
                            if self.selected_index < 0:
                                self.selected_index = 0
                        self._ensure_visible()
                    elif event.key == pygame.K_PAGEDOWN:
                        if self.items:
                            max_visible = max(1, self.list_rect.height // self.line_height)
                            self.selected_index = min(len(self.items) - 1, self.selected_index + max_visible)
                            while self.selected_index < len(self.items) and isinstance(self.items[self.selected_index], dict) and self.items[self.selected_index].get("is_header"):
                                self.selected_index += 1
                            if self.selected_index >= len(self.items):
                                self.selected_index = len(self.items) - 1
                                while self.selected_index >= 0 and isinstance(self.items[self.selected_index], dict) and self.items[self.selected_index].get("is_header"):
                                    self.selected_index -= 1
                        self._ensure_visible()
            clock.tick(30)

        if hasattr(self.presenter, "set_background_provider"):
            self.presenter.set_background_provider(prev_provider)

        return result


class InventoryPopupMenu(BasePopupMenu):
    def __init__(self, presenter, parent_screen):
        super().__init__(presenter, parent_screen, title="Inventory")
        self.sort_modes = ["Name", "Type", "Quantity", "Combat"]
        self.sort_mode_idx = 0

    def _is_combat_usable(self, item) -> bool:
        subtyp = getattr(item, "subtyp", None)
        return (
            subtyp in ("Health", "Mana", "Elixir", "Status")
            or (subtyp == "Scroll" and getattr(item, "name", "") != "Sanctuary Scroll")
        )

    def _current_mode(self) -> str:
        return self.sort_modes[self.sort_mode_idx]

    def _cycle_mode(self):
        self.sort_mode_idx = (self.sort_mode_idx + 1) % len(self.sort_modes)

    def _sort_inventory_items(self, items):
        mode = self._current_mode()
        if mode == "Combat":
            combat_items = [entry for entry in items if self._is_combat_usable(entry[1])]
            non_combat_items = [entry for entry in items if not self._is_combat_usable(entry[1])]
            return sorted(combat_items, key=lambda entry: str(getattr(entry[1], "name", "")).lower()) + non_combat_items
        if mode == "Type":
            return sorted(items, key=lambda entry: (
                str(getattr(entry[1], "subtyp", "")),
                str(getattr(entry[1], "name", "")).lower(),
            ))
        if mode == "Quantity":
            return sorted(items, key=lambda entry: (-entry[2], str(getattr(entry[1], "name", "")).lower()))
        return sorted(items, key=lambda entry: str(getattr(entry[1], "name", "")).lower())

    def build_items(self, player_char):
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
        y = self.details_rect.top + 12

        # Name
        name = getattr(obj, "name", str(obj))
        name_text = self.large_font.render(name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        # Category first
        text = self.normal_font.render(f"Category: {category}", True, self.WHITE)
        self.screen.blit(text, (x, y))
        y += self.line_height

        # Generic attributes if present
        attrs = []
        for key in ("description", "slot", "subtyp", "value", "weight"):
            if hasattr(obj, key):
                val = getattr(obj, key)
                attrs.append((key.capitalize(), val))

        for label, val in attrs:
            if label == "Value":
                line = f"{label}: {val}G"
            else:
                line = f"{label}: {val}"
            # Handle newlines in value
            if isinstance(val, str) and "\n" in val:
                self.screen.blit(self.normal_font.render(label + ":", True, self.WHITE), (x, y))
                y += self.line_height
                for desc_line in val.split("\n"):
                    # Wrap long description lines
                    wrapped = self._wrap_text(desc_line, self.details_rect.width - 32)
                    for wrapped_line in wrapped:
                        text = self.normal_font.render(wrapped_line, True, self.WHITE)
                        self.screen.blit(text, (x + 16, y))
                        y += self.line_height
            else:
                # Wrap long attribute values
                if isinstance(val, str):
                    wrapped = self._wrap_text(str(val), self.details_rect.width - 32 - 100)
                    if len(wrapped) > 1:
                        self.screen.blit(self.normal_font.render(label + ":", True, self.WHITE), (x, y))
                        y += self.line_height
                        for wrapped_line in wrapped:
                            text = self.normal_font.render(wrapped_line, True, self.WHITE)
                            self.screen.blit(text, (x + 16, y))
                            y += self.line_height
                    else:
                        text = self.normal_font.render(line, True, self.WHITE)
                        self.screen.blit(text, (x, y))
                        y += self.line_height
                else:
                    text = self.normal_font.render(line, True, self.WHITE)
                    self.screen.blit(text, (x, y))
                    y += self.line_height

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
        category, obj, count = item
        # Show simple computed lines
        for label, val in (("Category", category),):
            text = self.normal_font.render(f"{label}: {val}", True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height

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
        if item_subtyp in ("Health", "Mana", "Elixir", "Stat") or getattr(obj, "name", "") == "Sanctuary Scroll":
            actions.append("Use")
        
        actions.extend(["Drop", "Cancel"])
        
        # Show action menu
        action_popup = SelectionPopup(
            self.presenter,
            self.parent_screen,
            title=f"Action: {getattr(obj, 'name', 'Item')}",
            header_message=f"What would you like to do with {getattr(obj, 'name', 'this item')}?",
            options=actions
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

            result = action_popup.show(player_char)
            action_popup.draw_background = original_draw_bg

            if not result or result[0] != "selection":
                break

            action = result[1]
            action_bg = self.screen.copy()

            if action == "Cancel":
                break
            if action == "Equip":
                self._equip_item(player_char, obj, category)
                break
            if action == "Use":
                self._use_item(player_char, obj, category, background_surface=action_bg)
            elif action == "Drop":
                self._drop_item(player_char, obj, category, background_surface=action_bg)

            remaining = [
                it for it in player_char.inventory.get(category, [])
                if getattr(it, "name", str(it)) == item_name
            ]
            if not remaining:
                break
            obj = remaining[0]
        
        # Return None to keep inventory open
        return None

    def handle_key_down(self, player_char, event) -> bool:
        if event.key in (pygame.K_s,):
            self._cycle_mode()
            self.build_items(player_char)
            if self.items and self.selected_index < 0:
                self.selected_index = 0
            self._ensure_visible()
            return True
        return False

    def help_footer(self) -> str:
        return "Arrows: Navigate  Enter: Select  S: Cycle Sort/Filter  Esc: Close  PgUp/PgDn: Scroll"
    
    def _equip_item(self, player_char, item, category):
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
            return

        # Enforce class equip restrictions
        if hasattr(player_char, "cls") and hasattr(player_char.cls, "equip_check"):
            if not player_char.cls.equip_check(item, slot):
                self.presenter.show_message(f"You cannot equip {getattr(item, 'name', 'that item')}.")
                return

        # Check if current item can be unequipped
        current = player_char.equipment.get(slot)
        if current and not getattr(current, "unequip", True):
            self.presenter.show_message(f"You cannot unequip {getattr(current, 'name', 'this item')}.")
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
                    result_popup.show(background_draw_func=lambda: self.screen.blit(result_bg, (0, 0)))
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
        popup = ConfirmationPopup(self.presenter, f"Drop {getattr(item, 'name', 'this item')}? This cannot be undone.")
        if not popup.show(background_draw_func=lambda: self.screen.blit(menu_bg, (0, 0))):
            return
        
        # Remove from inventory
        if category in player_char.inventory and item in player_char.inventory[category]:
            player_char.inventory[category].remove(item)
            if not player_char.inventory[category]:
                del player_char.inventory[category]
        
        # Rebuild items list
        self.build_items(player_char)


class EquipmentPopupMenu(BasePopupMenu):
    def __init__(self, presenter, parent_screen):
        super().__init__(presenter, parent_screen, title="Equipment")

    def build_items(self, player_char):
        eq = getattr(player_char, "equipment", {})
        items = []
        # items: (slot, obj)
        for slot in ("Weapon", "Armor", "OffHand", "Ring", "Pendant"):
            items.append((slot, eq.get(slot)))
        self.items = items
        self.selected_index = 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        slot, obj = item
        name = getattr(obj, "name")
        if not name:
            raise NotImplementedError("Equipment item missing name attribute")
        # Truncate long names to fit
        if len(name) > 20:
            name = name[:17] + "..."
        return f"{slot}: {name}"

    def draw_details(self, player_char):
        """Override to extract object from (slot, obj) tuple."""
        if not self.items:
            x = self.details_rect.left + 16
            y = self.details_rect.top + 12
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return
        
        slot, obj = self.items[self.selected_index]
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if obj is None:
            # Empty slot
            slot_text = self.large_font.render(f"{slot} Slot", True, self.WHITE)
            self.screen.blit(slot_text, (x, y))
            y += slot_text.get_height() + 8
            self.screen.blit(self.normal_font.render("Empty slot", True, self.GRAY), (x, y))
            return

        # Name
        name = getattr(obj, "name")
        if not name:
            raise NotImplementedError("Equipment item missing name attribute")
        name_text = self.large_font.render(name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        # Generic attributes if present
        attrs = []
        for key in ("description", "slot", "subtyp", "value", "weight"):
            if hasattr(obj, key):
                val = getattr(obj, key)
                attrs.append((key.capitalize(), val))

        for label, val in attrs:
            line = f"{label}: {val}"
            # Handle newlines in value
            if isinstance(val, str) and "\n" in val:
                self.screen.blit(self.normal_font.render(label + ":", True, self.WHITE), (x, y))
                y += self.line_height
                for desc_line in val.split("\n"):
                    # Wrap long description lines
                    wrapped = self._wrap_text(desc_line, self.details_rect.width - 32)
                    for wrapped_line in wrapped:
                        text = self.normal_font.render(wrapped_line, True, self.WHITE)
                        self.screen.blit(text, (x + 16, y))
                        y += self.line_height
            else:
                text = self.normal_font.render(line, True, self.WHITE)
                self.screen.blit(text, (x, y))
                y += self.line_height

        # Custom details hook
        self.draw_details_extra(player_char, (slot, obj), x, y)

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
        slot, obj = item
        text = self.normal_font.render(f"Slot: {slot}", True, self.WHITE)
        self.screen.blit(text, (x, y))
        y += self.line_height
        if obj is None:
            self.screen.blit(self.normal_font.render("Empty slot", True, self.GRAY), (x, y))

    def on_select(self, player_char, item):
        slot, obj = item
        
        # Get items from inventory that can be equipped in this slot
        equippable_items = self._get_equippable_items_for_slot(player_char, slot)
        
        # Build options list
        options = []
        
        # Add equippable items from inventory
        for inv_item in equippable_items:
            options.append(getattr(inv_item, "name", str(inv_item)))
        
        # Add unequip option if something is equipped (not a placeholder)
        is_placeholder = getattr(obj, "unequip", False) if obj else False
        if obj and not is_placeholder:
            options.append("Unequip")
        
        options.append("Cancel")
        
        # Show selection menu
        action_popup = EquipmentSelectionPopup(
            self.presenter,
            self.parent_screen,
            title=f"{slot} Slot",
            header_message=f"Select an item to equip in {slot} slot:",
            options=options,
            slot=slot,
            current_item=obj,
            player_char=player_char
        )
        
        # Capture current state for background
        self.parent_screen.draw_all(player_char, do_flip=False)
        self.draw_background(self.screen.copy())
        self.draw_popup(player_char)
        self.draw_list()
        self.draw_details(player_char)
        pygame.display.flip()
        action_bg = self.screen.copy()
        
        # Temporarily override draw_background for nested popup
        original_draw_bg = action_popup.draw_background
        action_popup.draw_background = lambda surf: self.screen.blit(action_bg, (0, 0))
        
        result = action_popup.show(player_char)
        action_popup.draw_background = original_draw_bg
        
        if result and result[0] == "selection":
            selected = result[1]
            
            # Check if unequip was selected
            if selected == "Unequip":
                self._unequip_item(player_char, slot, obj)
            # Check if it's cancel
            elif selected == "Cancel":
                pass  # Do nothing
            else:
                # Find the selected item in equippable_items
                for inv_item in equippable_items:
                    if getattr(inv_item, "name", str(inv_item)) == selected:
                        self._equip_from_inventory(player_char, slot, inv_item)
                        break
        
        return None
    
    def _get_equippable_items_for_slot(self, player_char, slot):
        """Get all items from inventory that can be equipped in the given slot."""
        equippable = []
        seen_item_names = set()
        
        # Map slot to item types
        slot_to_typ = {
            "Weapon": "Weapon",
            "Armor": "Armor",
            "OffHand": "OffHand",
            "Ring": "Ring",
            "Pendant": "Pendant",
        }
        
        target_typ = slot_to_typ.get(slot)
        if not target_typ:
            return equippable
        
        # Search through inventory
        for category, items_list in player_char.inventory.items():
            for inv_item in items_list:
                item_typ = getattr(inv_item, "typ", None)
                item_name = getattr(inv_item, "name", str(inv_item))

                if item_name in seen_item_names:
                    continue
                
                # Direct type match
                if item_typ == target_typ:
                    equippable.append(inv_item)
                    seen_item_names.add(item_name)
                # Handle accessories (Ring/Pendant)
                elif item_typ == "Accessory":
                    subtyp = getattr(inv_item, "subtyp", None)
                    if (subtyp == "Ring" and slot == "Ring") or (subtyp == "Pendant" and slot == "Pendant"):
                        equippable.append(inv_item)
                        seen_item_names.add(item_name)
        
        return equippable
    
    def _equip_from_inventory(self, player_char, slot, new_item):
        """Equip an item from inventory, unequipping current item if needed."""
        # Get current item
        current_item = player_char.equipment.get(slot)
        
        # If there's a current item that's not a placeholder, move it to inventory
        if current_item:
            is_placeholder = getattr(current_item, "unequip", False)
            if not is_placeholder:
                item_name = getattr(current_item, "name", "Unknown")
                if item_name not in player_char.inventory:
                    player_char.inventory[item_name] = []
                player_char.inventory[item_name].append(current_item)
        
        # Equip the new item
        player_char.equipment[slot] = new_item
        
        # Remove new item from inventory
        for category, items_list in player_char.inventory.items():
            if new_item in items_list:
                items_list.remove(new_item)
                if not items_list:
                    del player_char.inventory[category]
                break
        
        # Rebuild items list
        self.build_items(player_char)

    
    def _unequip_item(self, player_char, slot, item):
        """Unequip an item and move to inventory."""
        # Don't unequip placeholder items (NoRing, NoOffHand, etc.)
        if getattr(item, "unequip", False):
            return
        
        # Remove from equipment and replace with appropriate NoItem
        no_item_classes = {
            "Weapon": items.NoWeapon,
            "Armor": items.NoArmor,
            "OffHand": items.NoOffHand,
            "Ring": items.NoRing,
            "Pendant": items.NoPendant
        }
        
        if slot in no_item_classes:
            player_char.equipment[slot] = no_item_classes[slot]()
        else:
            player_char.equipment[slot] = None
        
        # Add to inventory using item name as key
        item_name = getattr(item, "name", "Unknown")
        if item_name not in player_char.inventory:
            player_char.inventory[item_name] = []
        player_char.inventory[item_name].append(item)
        
        # Rebuild items list
        self.build_items(player_char)


class QuestPopupMenu(BasePopupMenu):
    """Quest-specific popup that shows quest details."""
    def __init__(self, presenter, parent_screen):
        super().__init__(presenter, parent_screen, title="Quests")
        # Make quest popup larger for long descriptions
        self.popup_rect = pygame.Rect(int(self.width * 0.05), int(self.height * 0.08), int(self.width * 0.9), int(self.height * 0.82))
        self.list_rect = pygame.Rect(
            self.popup_rect.left + 24,
            self.popup_rect.top + 72,
            int(self.popup_rect.width * 0.33),
            self.popup_rect.height - 120,
        )
        self.details_rect = pygame.Rect(
            self.popup_rect.left + int(self.popup_rect.width * 0.35),
            self.popup_rect.top + 72,
            int(self.popup_rect.width * 0.6) - 32,
            self.popup_rect.height - 120,
        )

    def draw_popup(self, player_char):
        super().draw_popup(player_char)
        legend_text = "* = ready to turn in"
        text = self.small_font.render(legend_text, True, self.LIGHT_GRAY)
        self.screen.blit(text, (self.popup_rect.left + 16, self.popup_rect.bottom - text.get_height() - 36))
    
    def build_items(self, player_char):
        """Build list of quest objects from quest_dict."""
        self.items = []
        active_items = []
        completed_items = []
        quest_dict = getattr(player_char, "quest_dict", {})

        if not quest_dict:
            return
        
        # Store quest data as tuples: (display_name, quest_type, quest_name, quest_data)
        for quest_type, quests_by_type in quest_dict.items():
            if quest_type == "Bounty":
                # Bounty quests: {name: [bounty_data, count, completed]}
                for quest_name, quest_info in quests_by_type.items():
                    if isinstance(quest_info, list) and len(quest_info) >= 3:
                        bounty_data, count, completed = quest_info[0], quest_info[1], quest_info[2]
                        entry = (f"[{quest_type}] {quest_name}", quest_type, quest_name, {
                            'bounty_data': bounty_data,
                            'count': count,
                            'completed': completed
                        })
                        if completed:
                            completed_items.append(entry)
                        else:
                            active_items.append(entry)
            else:
                # Main/Side quests: check if it's nested by level or flat structure
                for key, value in quests_by_type.items():
                    if isinstance(value, dict):
                        # Check if this looks like quest data (has quest properties) or nested structure
                        if 'Type' in value or 'Who' in value or 'What' in value:
                            # This is quest data directly - flat structure
                            quest_name = key
                            quest_data = value
                            completed = quest_data.get('Completed', False)
                            turned_in = quest_data.get('Turned In', False)
                            display_name = f"[{quest_type}] {quest_name}"
                            if completed and not turned_in:
                                display_name = f"{display_name} *"
                            entry = (display_name, quest_type, quest_name, quest_data)
                            if turned_in:
                                completed_items.append(entry)
                            else:
                                active_items.append(entry)
                        else:
                            # This is a nested structure (level -> quests)
                            for quest_name, quest_data in value.items():
                                completed = quest_data.get('Completed', False)
                                turned_in = quest_data.get('Turned In', False)
                                display_name = f"[{quest_type}] {quest_name}"
                                if completed and not turned_in:
                                    display_name = f"{display_name} *"
                                entry = (display_name, quest_type, quest_name, quest_data)
                                if turned_in:
                                    completed_items.append(entry)
                                else:
                                    active_items.append(entry)
        
        self.items = active_items
        if completed_items:
            self.items.append({"is_header": True, "text": "Completed Quests"})
            self.items.extend(completed_items)

        if not self.items:
            self.items = [("No quests available", None, None, None)]
        
        self.selected_index = 0
        self.scroll_offset = 0
    
    def item_display_text(self, item):
        """Return display name from tuple."""
        if isinstance(item, dict) and item.get("is_header"):
            return item.get("text", "")
        if isinstance(item, tuple):
            return item[0]
        return str(item)
    
    def draw_details(self, player_char):
        """Override to show quest details instead of generic item attributes."""
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No quests", True, self.GRAY), (x, y))
            return
        
        if isinstance(item, dict) and item.get("is_header"):
            self.screen.blit(self.normal_font.render(item.get("text", ""), True, self.GRAY), (x, y))
            return

        if not isinstance(item, tuple) or item[1] is None:
            # No quest selected or no quests available
            self.screen.blit(self.normal_font.render(str(item[0]), True, self.GRAY), (x, y))
            return
        
        display_name, quest_type, quest_name, quest_data = item
        
        # Quest name as header
        name_text = self.large_font.render(quest_name, True, self.GOLD)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8
        
        if quest_type == "Bounty":
            self._draw_bounty_details(quest_data, x, y)
        else:
            self._draw_quest_details(player_char, quest_data, x, y)
    
    def _draw_bounty_details(self, quest_data, x, y):
        """Draw bounty quest details."""
        bounty_data = quest_data.get('bounty_data', {})
        count = quest_data.get('count', 0)
        completed = quest_data.get('completed', False)
        
        # Target - handle both enemy object and string
        if 'enemy' in bounty_data:
            enemy = bounty_data['enemy']
            if hasattr(enemy, 'name'):
                target = enemy.name
            else:
                target = str(enemy)
        else:
            target = "Unknown"
        
        lines = [
            f"Target: {target}",
            f"Required: {bounty_data.get('num', 1)}",
            f"Defeated: {count}",
            "",
            f"Status: {'Complete' if completed else 'In Progress'}",
            "",
            f"Reward: {bounty_data.get('gold', 0)} Gold",
            f"Experience: {bounty_data.get('exp', 0)}",
        ]
        
        if bounty_data.get('reward'):
            lines.append("+ Item Reward")
        
        for line in lines:
            text = self.normal_font.render(line, True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height
    
    def _draw_quest_details(self, player_char, quest_data, x, y):
        """Draw regular quest details."""
        if not isinstance(quest_data, dict):
            return
        
        # Quest type
        quest_type = quest_data.get('Type', 'Unknown')
        text = self.normal_font.render(f"Type: {quest_type}", True, self.WHITE)
        self.screen.blit(text, (x, y))
        y += self.line_height
        
        # Quest objective
        if quest_type == 'Defeat':
            what = quest_data.get('What', 'Unknown')
            total = quest_data.get('Total', 1)
            objective = f"Defeat: {what}" if total == 1 else f"Defeat: {what} ({total})"
            text = self.normal_font.render(objective, True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height
        elif quest_type == 'Collect':
            what = quest_data.get('What')

            # Resolve a readable target name and aliases for progress matching.
            item_name = None
            target_names = set()
            target_classes = set()

            if isinstance(what, str):
                if what == 'Relics':
                    item_name = 'Relics'
                    target_names.add('Relics')
                    target_classes.add('Relics')
                else:
                    target_names.add(what)
                    target_classes.add(what)
                    item_cls = getattr(items, what, None)
                    if item_cls and callable(item_cls):
                        try:
                            item_obj = item_cls()
                            item_name = getattr(item_obj, 'name', what)
                            target_names.add(item_name)
                            target_classes.add(item_cls.__name__)
                        except Exception:
                            item_name = what
                    else:
                        item_name = what
            elif callable(what):
                try:
                    item_obj = what()
                    item_name = getattr(item_obj, 'name', getattr(what, '__name__', str(what)))
                except Exception:
                    item_name = getattr(what, '__name__', str(what))
                target_names.add(item_name)
                target_classes.add(getattr(what, '__name__', item_name))
            elif hasattr(what, 'name'):
                item_name = what.name
                target_names.add(item_name)
                target_classes.add(what.__class__.__name__)
            else:
                item_name = str(what)
                target_names.add(item_name)
                target_classes.add(item_name)

            total = quest_data.get('Total', 1)
            text = self.normal_font.render(f"Collect: {item_name}", True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height

            # Progress (parity with bounty-style visibility).
            if isinstance(what, str) and what == 'Relics':
                relics = ["Triangulus", "Quadrata", "Hexagonum", "Luna", "Polaris", "Infinitas"]
                current = sum(1 for relic in relics if relic in player_char.special_inventory)
            else:
                current = 0
                for inventory_name in ('special_inventory', 'inventory'):
                    inventory = getattr(player_char, inventory_name, {})
                    for key, item_list in inventory.items():
                        if not item_list:
                            continue
                        sample = item_list[0]
                        sample_name = getattr(sample, 'name', key)
                        sample_class = sample.__class__.__name__
                        if key in target_names or sample_name in target_names or sample_class in target_classes:
                            current += len(item_list)

            text = self.normal_font.render(f"Collected: {current}/{total}", True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height
        elif quest_type == 'Locate':
            what = quest_data.get('What', 'Unknown')
            text = self.normal_font.render(f"Locate: {what}", True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height
        
        y += self.line_height // 2
        
        # Status
        completed = quest_data.get('Completed', False)
        turned_in = quest_data.get('Turned In', False)
        if turned_in:
            status = "Turned In"
        elif completed:
            status = "Complete - Ready to Turn In"
        else:
            status = "In Progress"
        text = self.normal_font.render(f"Status: {status}", True, self.GOLD if completed and not turned_in else self.WHITE)
        self.screen.blit(text, (x, y))
        y += self.line_height * 1.5
        
        # Rewards
        text = self.normal_font.render("Rewards:", True, self.GOLD)
        self.screen.blit(text, (x, y))
        y += self.line_height
        
        exp = quest_data.get('Experience', 0)
        if exp:
            text = self.normal_font.render(f"  {exp} Experience", True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += self.line_height
        
        reward = quest_data.get('Reward')
        reward_num = quest_data.get('Reward Number', 0)
        if reward:
            if isinstance(reward, list) and len(reward) > 0 and reward[0] == 'Gold':
                text = self.normal_font.render(f"  {reward_num} Gold", True, self.WHITE)
                self.screen.blit(text, (x, y))
                y += self.line_height
            elif isinstance(reward, list):
                for r in reward:
                    # Handle item classes/functions
                    name = None
                    
                    # Skip strings that are keywords like 'Gold'
                    if isinstance(r, str):
                        continue
                    
                    # Check if it's a class (type)
                    if isinstance(r, type):
                        # It's a class, use __name__
                        name = r.__name__
                    elif hasattr(r, 'name'):
                        # It's an instance with a name attribute
                        name = r.name
                    elif callable(r):
                        # It's callable but not a class, try to instantiate
                        try:
                            instance = r()
                            name = getattr(instance, 'name', r.__name__ if hasattr(r, '__name__') else None)
                        except Exception:
                            name = r.__name__ if hasattr(r, '__name__') else None

                    # Last resort
                    if name is None:
                        name = "Unknown Item"
                    
                    text = self.normal_font.render(f"  {name}", True, self.WHITE)
                    self.screen.blit(text, (x, y))
                    y += self.line_height
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width pixels."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.small_font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def on_select(self, player_char, item):
        """Quests are view-only for now."""
        return None  # Keep menu open


class SimpleListPopupMenu(BasePopupMenu):
    """Generic simple list popup for placeholders like Quests, Key Items, Specials, Class Menu."""
    def __init__(self, presenter, parent_screen, title, source_fn):
        super().__init__(presenter, parent_screen, title=title)
        self.source_fn = source_fn  # function(player_char) -> list[str]

    def build_items(self, player_char):
        raw = self.source_fn(player_char) or []
        # Handle case where raw is a callable (method) instead of a list
        if callable(raw):
            raw = raw()
        self.items = []
        for entry in (raw or []):
            if isinstance(entry, str) and entry.strip().startswith("---") and entry.strip().endswith("---"):
                # Treat as header row
                self.items.append({"is_header": True, "text": entry})
            elif isinstance(entry, dict) and "text" in entry:
                # Entry is already a properly formatted dict (e.g., from _get_key_items_list with quantities)
                self.items.append(entry)
            else:
                if isinstance(entry, object) and not isinstance(entry, str):
                    self.items.append({"is_header": False, "text": getattr(entry, 'name', str(entry)), "value": entry})
                else:
                    self.items.append({"is_header": False, "text": str(entry), "value": entry})
        self.selected_index = 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)

    def draw_details(self, player_char):
        """Override to handle abilities/skills specially - don't show description in attrs."""
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        # Extract header/value metadata when present
        is_header = isinstance(item, dict) and item.get("is_header")
        value = item.get("value") if isinstance(item, dict) else item
        text_label = item.get("text") if isinstance(item, dict) else None

        if is_header:
            header_text = self.large_font.render(text_label or "", True, self.GOLD)
            self.screen.blit(header_text, (x, y))
            return

        # Name
        name = getattr(value, "name", text_label if text_label else str(value))
        name_text = self.large_font.render(name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        # For abilities, skip showing description in attrs since we'll show it wrapped below
        # Custom details hook (will show description wrapped)
        self.draw_details_extra(player_char, value, x, y)

    def draw_details_extra(self, player_char, item, x, y):
        # Render description text for abilities if present; otherwise show a fallback
        desc = getattr(item, "description", None) or ""

        if desc:
            max_width = self.details_rect.width - 32
            words = str(desc).split()
            line = ""
            for w in words:
                test = f"{line} {w}".strip()
                if self.normal_font.size(test)[0] <= max_width:
                    line = test
                else:
                    text = self.normal_font.render(line, True, self.WHITE)
                    self.screen.blit(text, (x, y))
                    y += self.line_height
                    line = w
            if line:
                text = self.normal_font.render(line, True, self.WHITE)
                self.screen.blit(text, (x, y))
                y += self.line_height
        else:
            text = self.normal_font.render("No description available.", True, self.GRAY)
            self.screen.blit(text, (x, y))
            y += self.line_height

        # Add spacing
        y += 8

        # Show sub-type if available
        subtyp = getattr(item, "subtyp", None)
        if subtyp:
            subtyp_text = self.normal_font.render(f"Type: {subtyp}", True, self.LIGHT_GRAY)
            self.screen.blit(subtyp_text, (x, y))
            y += self.line_height

        # Show mana cost or "Passive" only for abilities (items with a 'cost' attribute)
        # This avoids showing mana cost for regular items like Key Items
        is_passive = getattr(item, "passive", False)
        has_cost_attr = hasattr(item, "cost")
        
        if is_passive or has_cost_attr:
            if is_passive:
                cost_text = self.normal_font.render("Passive", True, self.LIGHT_GRAY)
            else:
                cost = getattr(item, "cost", None)
                if cost is not None:
                    cost_text = self.normal_font.render(f"Mana Cost: {cost}", True, self.LIGHT_GRAY)
                else:
                    cost_text = self.normal_font.render("Mana Cost: —", True, self.LIGHT_GRAY)
            self.screen.blit(cost_text, (x, y))

    def on_select(self, player_char, item):
        value = item.get("value") if isinstance(item, dict) else item
        if getattr(value, "name", "") == "Chalice Map":
            try:
                map_tiles.reveal_chalice_map_on_inspect(player_char, value)
                progress = map_tiles.get_chalice_progress(player_char) or {}
                if progress.get("Revealed"):
                    self.presenter.show_message(
                        "Hidden ink blooms across the parchment, revealing the altar location on the sixth floor.",
                        title="Chalice Map",
                        image_path=map_tiles.CHALICE_ALTAR_IMAGE_PATH,
                        split_layout=True,
                    )
                elif progress.get("Adventurer"):
                    self.presenter.show_message(
                        "The map's markings are faint. Keep inspecting it to draw out the hidden ink.",
                        title="Chalice Map",
                        split_layout=True,
                    )
                else:
                    self.presenter.show_message(
                        "The map is too faded to read. You need another clue before its markings can be revealed.",
                        title="Chalice Map",
                        split_layout=True,
                    )
            except Exception:
                pass
            return None
        return ("list_item_selected", item)


class JumpModsPopupMenu(BasePopupMenu):
    """Popup menu for toggling Jump ability modifications."""

    MOD_DESCRIPTIONS = {
        "Crit": "Increases critical factor but reduces damage to 1.5x weapon damage.",
        "Thrust": "After landing, thrust for 3/4 weapon damage if the target survives.",
        "Defend": "Increased damage reduction while preparing to Jump.",
        "Rend": "Chance to apply Bleed, dealing damage over time.",
        "Quake": "Chance to stun the enemy upon landing.",
        "Acrobat": "Gain an evasion bonus while preparing to Jump.",
        "Dragon's Fury": "Deals additional random elemental damage.",
        "Soaring Strike": "Takes two turns to charge, but deals increased damage.",
        "Quick Dive": "Removes charge time but reduces damage to 0.75x.",
        "Retribution": "Taking damage while charging boosts the Jump damage.",
        "Unstoppable": "Jump cannot be interrupted once started.",
        "Recover": "Regain a small amount of health and mana upon landing.",
        "Skyfall": "Additional smaller hits fall on the target after landing.",
    }

    def __init__(self, presenter, parent_screen, title="Jump Modifications"):
        super().__init__(presenter, parent_screen, title=title)
        self.jump_skill = None

    def _get_jump_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Jump" in skills:
            return skills["Jump"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Jump":
                return skill
        return None

    def build_items(self, player_char):
        self.jump_skill = self._get_jump_skill(player_char)
        self.items = []

        if not self.jump_skill or not hasattr(self.jump_skill, "modifications"):
            self.items.append({"is_header": True, "text": "Jump not learned"})
            self.selected_index = 0
            self.scroll_offset = 0
            return

        # Show active/max count in header
        active_count = self.jump_skill.get_active_count() if hasattr(self.jump_skill, "get_active_count") else 0
        max_count = self.jump_skill.get_max_active_modifications(player_char) if hasattr(self.jump_skill, "get_max_active_modifications") else 99
        header_text = f"Toggle Modifications ({active_count}/{max_count} active)"
        self.items.append({"is_header": True, "text": header_text})
        
        # Only show unlocked modifications
        unlocked_mods = self.jump_skill.get_unlocked_modifications() if hasattr(self.jump_skill, "get_unlocked_modifications") else list(self.jump_skill.modifications.keys())
        
        for mod_name in unlocked_mods:
            active = self.jump_skill.modifications.get(mod_name, False)
            prefix = "[X]" if active else "[ ]"
            self.items.append({
                "is_header": False,
                "text": f"{prefix} {mod_name}",
                "value": mod_name,
            })

        self.selected_index = 1 if len(self.items) > 1 else 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)

    def draw_details(self, player_char):
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        is_header = isinstance(item, dict) and item.get("is_header")
        value = item.get("value") if isinstance(item, dict) else item
        text_label = item.get("text") if isinstance(item, dict) else None

        if is_header:
            header_text = self.large_font.render(text_label or "", True, self.GOLD)
            self.screen.blit(header_text, (x, y))
            return

        mod_name = str(value)
        active = False
        if self.jump_skill and hasattr(self.jump_skill, "modifications"):
            active = self.jump_skill.modifications.get(mod_name, False)

        name_text = self.large_font.render(mod_name, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        status_text = self.normal_font.render(
            f"Status: {'Active' if active else 'Inactive'}", True, self.LIGHT_GRAY
        )
        self.screen.blit(status_text, (x, y))
        y += self.line_height + 4

        # Show unlock requirement info
        if self.jump_skill and hasattr(self.jump_skill, "unlock_requirements"):
            req = self.jump_skill.unlock_requirements.get(mod_name, {})
            req_type = req.get("type", "")
            req_val = req.get("requirement")
            
            if req_type == "lancer_level":
                unlock_str = f"Unlocked: Lancer Level {req_val}"
            elif req_type == "dragoon_level":
                unlock_str = f"Unlocked: Dragoon Level {req_val}"
            elif req_type == "boss":
                unlock_str = f"Unlocked by defeating {req_val}"
            elif req_type == "item":
                unlock_str = f"Unlocked by finding {req_val}"
            else:
                unlock_str = "Initial modification"
            
            unlock_text = self.normal_font.render(unlock_str, True, self.GOLD)
            self.screen.blit(unlock_text, (x, y))
            y += self.line_height + 8

        desc = self.MOD_DESCRIPTIONS.get(mod_name, "")
        if desc:
            max_width = self.details_rect.width - 32
            words = desc.split()
            line = ""
            for w in words:
                test = f"{line} {w}".strip()
                if self.normal_font.size(test)[0] <= max_width:
                    line = test
                else:
                    self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))
                    y += self.line_height
                    line = w
            if line:
                self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))

    def on_select(self, player_char, item):
        if not self.jump_skill or not hasattr(self.jump_skill, "modifications"):
            return None
        if isinstance(item, dict) and item.get("is_header"):
            return None

        mod_name = item.get("value") if isinstance(item, dict) else str(item)
        current = self.jump_skill.modifications.get(mod_name, False)
        
        # Toggle the modification
        result = self.jump_skill.set_modification(mod_name, not current, player_char)
        
        # Handle the new tuple return format
        if isinstance(result, tuple):
            success, error_msg = result
            if not success and error_msg:
                # Could show error popup here if desired
                pass  # For now, just don't toggle if it failed
        
        self.build_items(player_char)
        return None


class TotemAspectsPopupMenu(BasePopupMenu):
    """Popup menu for selecting active Totem aspects."""

    def __init__(self, presenter, parent_screen, title="Totem Aspects"):
        super().__init__(presenter, parent_screen, title=title)
        self.totem_skill = None

    def _get_totem_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            return skills["Totem"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Totem":
                return skill
        return None

    def build_items(self, player_char):
        self.totem_skill = self._get_totem_skill(player_char)
        self.items = []

        if not self.totem_skill or not hasattr(self.totem_skill, "get_unlocked_aspects"):
            self.items.append({"is_header": True, "text": "Totem not learned"})
            self.selected_index = 0
            self.scroll_offset = 0
            return

        active = getattr(self.totem_skill, "active_aspect", "")
        header_text = f"Active Aspect: {active}" if active else "Active Aspect: None"
        self.items.append({"is_header": True, "text": header_text})

        unlocked = self.totem_skill.get_unlocked_aspects(player_char)
        for aspect in unlocked:
            prefix = "[X]" if aspect == active else "[ ]"
            self.items.append({
                "is_header": False,
                "text": f"{prefix} {aspect}",
                "value": aspect,
            })

        self.selected_index = 1 if len(self.items) > 1 else 0
        self.scroll_offset = 0

    def item_display_text(self, item):
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)

    def draw_details(self, player_char):
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        is_header = isinstance(item, dict) and item.get("is_header")
        value = item.get("value") if isinstance(item, dict) else item
        text_label = item.get("text") if isinstance(item, dict) else None

        if is_header:
            header_text = self.large_font.render(text_label or "", True, self.GOLD)
            self.screen.blit(header_text, (x, y))
            return

        aspect = str(value)
        name_text = self.large_font.render(aspect, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8

        if self.totem_skill and hasattr(self.totem_skill, "aspects"):
            aspect_data = self.totem_skill.aspects.get(aspect, {})
            cost = aspect_data.get("cost")
            if cost is not None:
                cost_text = self.normal_font.render(f"Mana Cost: {cost}", True, self.LIGHT_GRAY)
                self.screen.blit(cost_text, (x, y))
                y += self.line_height + 6

            desc = aspect_data.get("description", "")
            if desc:
                max_width = self.details_rect.width - 32
                words = desc.split()
                line = ""
                for w in words:
                    test = f"{line} {w}".strip()
                    if self.normal_font.size(test)[0] <= max_width:
                        line = test
                    else:
                        self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))
                        y += self.line_height
                        line = w
                if line:
                    self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))

    def on_select(self, player_char, item):
        if not self.totem_skill or not hasattr(self.totem_skill, "set_active_aspect"):
            return None
        if isinstance(item, dict) and item.get("is_header"):
            return None

        aspect = item.get("value") if isinstance(item, dict) else str(item)
        result = self.totem_skill.set_active_aspect(aspect)
        if isinstance(result, tuple):
            success, _ = result
            if not success:
                return None

        self.build_items(player_char)
        return None


class SelectionPopup(BasePopupMenu):
    """Generic selection popup: header + options, returns selected item."""
    def __init__(self, presenter, parent_screen, title="Select", header_message=None, options=None):
        super().__init__(presenter, parent_screen, title=title)
        self.header_message = header_message or ""
        self._options = options or []

    def build_items(self, player_char):
        self.items = list(self._options)

    def draw_details_extra(self, player_char, item, x, y):
        # Render header message
        if self.header_message:
            words = str(self.header_message).split()
            max_chars = max(20, (self.details_rect.width - 32) // 9)
            line = ""
            for w in words:
                nxt = f"{line} {w}".strip()
                if len(nxt) > max_chars:
                    self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))
                    y += self.line_height
                    line = w
                else:
                    line = nxt
            if line:
                self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))

    def on_select(self, player_char, item):
        return ("selection", item)


class EquipmentSelectionPopup(BasePopupMenu):
    """Equipment selection popup with stat diff display."""
    def __init__(self, presenter, parent_screen, title="Select", header_message=None, options=None, slot=None, current_item=None, player_char=None):
        super().__init__(presenter, parent_screen, title=title)
        self.header_message = header_message or ""
        self._options = options or []
        self.slot = slot
        self.current_item = current_item
        self.player_char_ref = player_char  # Store reference for equip_diff calls

    def build_items(self, player_char):
        self.items = list(self._options)

    def draw_details(self, player_char):
        """Override to show item details with equipment diffs."""
        item = self.items[self.selected_index] if self.items else None
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12

        if item is None:
            self.screen.blit(self.normal_font.render("No items", True, self.GRAY), (x, y))
            return

        # Extract the actual item from the option string
        item_str = str(item)
        
        # Display item name
        name_text = self.large_font.render(item_str, True, self.WHITE)
        self.screen.blit(name_text, (x, y))
        y += name_text.get_height() + 8
        
        # Handle different option types
        if item_str == "Cancel":
            return  # Don't show diff for cancel
        
        elif item_str == "Unequip":
            # Show diffs for unequipping (switching to placeholder)
            if self.slot and self.player_char_ref and self.current_item:
                no_item_classes = {
                    "Weapon": items.NoWeapon,
                    "Armor": items.NoArmor,
                    "OffHand": items.NoOffHand,
                    "Ring": items.NoRing,
                    "Pendant": items.NoPendant
                }
                
                if self.slot in no_item_classes:
                    placeholder = no_item_classes[self.slot]()
                    diff_str = self.player_char_ref.equip_diff(placeholder, self.slot)
                    if diff_str:
                        for line in diff_str.split("\n"):
                            text = self.normal_font.render(line, True, self.LIGHT_GRAY)
                            self.screen.blit(text, (x, y))
                            y += self.line_height
        
        else:
            # Search through inventory for matching item and show diff
            actual_item = None
            for category, items_list in player_char.inventory.items():
                for inv_item in items_list:
                    if getattr(inv_item, "name", str(inv_item)) == item_str:
                        actual_item = inv_item
                        break
                if actual_item:
                    break
            
            # If we found the item, show the diff
            if actual_item and self.slot and self.player_char_ref:
                try:
                    diff_str = self.player_char_ref.equip_diff(actual_item, self.slot)
                    if diff_str:
                        # Split diff into lines and display
                        for line in diff_str.split("\n"):
                            text = self.normal_font.render(line, True, self.LIGHT_GRAY)
                            self.screen.blit(text, (x, y))
                            y += self.line_height
                except Exception:
                    pass  # Silently fail if equip_diff fails

    def draw_details_extra(self, player_char, item, x, y):
        # Render header message
        if self.header_message:
            words = str(self.header_message).split()
            max_chars = max(20, (self.details_rect.width - 32) // 9)
            line = ""
            for w in words:
                nxt = f"{line} {w}".strip()
                if len(nxt) > max_chars:
                    self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))
                    y += self.line_height
                    line = w
                else:
                    line = nxt
            if line:
                self.screen.blit(self.normal_font.render(line, True, self.WHITE), (x, y))

    def on_select(self, player_char, item):
        return ("selection", item)
