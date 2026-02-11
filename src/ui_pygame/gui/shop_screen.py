"""
Shop screen that mimics the curses terminal shop layout for Pygame.
Layout structure:
- Top: Shop header message
- Below: Two boxes side-by-side (menu options left, item description right)
- Bottom: Large item list box (left), stat comparison box (right top), gold box (right bottom)
"""

from textwrap import wrap

import pygame

from .town_base import TownScreenBase


class ShopScreen(TownScreenBase):
    """
    Pygame shop interface that matches the curses terminal layout.
    """
    
    def __init__(self, presenter, player_char, shop_message):
        super().__init__(presenter)
        self.player_char = player_char
        self.shop_message = shop_message
        
        # State
        self.current_option = 0
        self.current_item = 0
        self.options_list = ["Buy", "Sell", "Quests", "Leave"]
        self.item_list = []  # List of tuples: (display_string, item_object, cost, owned_count)
        self.buy_or_sell = None
        self.scroll_offset = 0

        # Caching for equip_diff to prevent recalculation on every blit
        self.cached_item_index = -1
        self.cached_diff_str = ""
        
        # Calculate window positions (matching curses layout)
        self.calculate_window_rects()

    def set_options(self, options_list, reset_cursor=True):
        """Replace options and optionally reset the selection index."""
        self.options_list = options_list
        if reset_cursor:
            self.current_option = 0
    
    def calculate_window_rects(self):
        """Calculate the rectangles for each UI section matching curses layout."""
        # Top window: 1/12 of height
        top_height = self.height // 12
        self.top_rect = pygame.Rect(0, 0, self.width, top_height)
        
        # Options window: left 1/3, below top, height 1/4
        options_height = self.height // 4
        options_width = self.width // 3
        options_y = top_height
        self.options_rect = pygame.Rect(0, options_y, options_width, options_height)
        
        # Item description window: right 2/3, below top, height 1/4
        desc_width = 2 * self.width // 3
        self.desc_rect = pygame.Rect(options_width, options_y, desc_width, options_height)
        
        # Shop list window: left 2/3, below options, height 2/3
        list_y = options_y + options_height
        list_height = 2 * self.height // 3
        list_width = 2 * self.width // 3
        self.list_rect = pygame.Rect(0, list_y, list_width, list_height)
        
        # Mod window: right 1/3, below options, height 7/12
        mod_width = self.width // 3
        mod_height = 7 * self.height // 12
        self.mod_rect = pygame.Rect(list_width, list_y, mod_width, mod_height)
        
        # Gold window: right 1/3, at bottom, height 1/12
        gold_y = list_y + mod_height
        gold_height = self.height // 12
        self.gold_rect = pygame.Rect(list_width, gold_y, mod_width, gold_height)
    
    def draw_top(self):
        """Draw the top header with shop message."""
        self.draw_semi_transparent_panel(self.top_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.top_rect, 2)
        
        # Center the shop message
        text = self.large_font.render(self.shop_message, True, self.colors.GOLD)
        text_rect = text.get_rect(center=(self.width // 2, self.top_rect.centery))
        self.screen.blit(text, text_rect)
    
    def draw_options(self):
        """Draw the menu options (Buy, Sell, Quests, Leave)."""
        self.draw_semi_transparent_panel(self.options_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.options_rect, 2)
        
        # Calculate spacing for options
        num_options = len(self.options_list)
        option_height = self.options_rect.height // (num_options + 1)
        
        for idx, option in enumerate(self.options_list):
            # Highlight selected option
            color = self.colors.GOLD if idx == self.current_option else self.colors.WHITE
            
            # Draw option text centered
            text = self.normal_font.render(option, True, color)
            text_x = self.options_rect.centerx - text.get_width() // 2
            text_y = self.options_rect.top + (idx + 1) * option_height

            # Highlight background for selected
            if idx == self.current_option:
                highlight_rect = pygame.Rect(
                    self.options_rect.left + 10,
                    text_y - 5,
                    self.options_rect.width - 20,
                    text.get_height() + 10
                )
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, highlight_rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, highlight_rect, 2)
            
            self.screen.blit(text, (text_x, text_y))
    
    def draw_item_desc(self):
        """Draw the description of the currently highlighted item."""
        self.draw_semi_transparent_panel(self.desc_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.desc_rect, 2)
        
        if self.item_list and 0 <= self.current_item < len(self.item_list):
            display_str, item, _, _ = self.item_list[self.current_item]
            
            # Don't show description for "Go Back" or "Next Page"
            if display_str in ["Go Back", "Next Page"]:
                return
            
            if item and hasattr(item, 'description') and item.description:
                # Word wrap the description to fit
                lines = wrap(item.description, 60, break_on_hyphens=False)
                
                # Draw description lines centered vertically
                line_height = self.normal_font.get_height() + 2
                total_height = len(lines) * line_height
                start_y = self.desc_rect.centery - total_height // 2
                
                for i, line in enumerate(lines):
                    text = self.normal_font.render(line, True, self.colors.WHITE)
                    text_x = self.desc_rect.centerx - text.get_width() // 2
                    text_y = start_y + i * line_height
                    self.screen.blit(text, (text_x, text_y))
    
    def draw_shop_list(self):
        """Draw the list of items for sale or selling."""
        self.draw_semi_transparent_panel(self.list_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.list_rect, 2)
        
        if not self.item_list:
            # Display message when no items available
            no_items_text = self.normal_font.render("No items available", True, self.colors.GRAY)
            text_rect = no_items_text.get_rect(
                centerx=self.list_rect.centerx,
                centery=self.list_rect.centery
            )
            self.screen.blit(no_items_text, text_rect)
            return
        
        # Define fixed column positions (in pixels from left edge)
        base_x = self.list_rect.left + 10
        type_col_x = base_x
        item_col_x = base_x + 120  # After "Type" column
        cost_col_x = self.list_rect.right - 180  # Fixed position for Cost
        owned_col_x = self.list_rect.right - 60  # Fixed position for Owned
        
        # Draw header row at fixed positions
        header_y = self.list_rect.top + 10
        
        type_header = self.small_font.render("Type", True, self.colors.GOLD)
        self.screen.blit(type_header, (type_col_x, header_y))
        
        item_header = self.small_font.render("Item", True, self.colors.GOLD)
        self.screen.blit(item_header, (item_col_x, header_y))
        
        if self.buy_or_sell == "Buy":
            cost_header = self.small_font.render("Cost", True, self.colors.GOLD)
            self.screen.blit(cost_header, (cost_col_x, header_y))
        
        owned_header = self.small_font.render("Owned", True, self.colors.GOLD)
        self.screen.blit(owned_header, (owned_col_x, header_y))
        
        # Draw items (scrollable)
        max_visible = 19  # Show 19 items at a time (matching curses)
        line_height = (self.list_rect.height - 40) // max_visible
        
        visible_start = self.scroll_offset
        visible_end = min(self.scroll_offset + max_visible, len(self.item_list))
        
        for i in range(visible_start, visible_end):
            display_str, item, cost, owned = self.item_list[i]
            
            y = self.list_rect.top + 35 + (i - visible_start) * line_height
            
            # Highlight selected item
            if i == self.current_item:
                highlight_rect = pygame.Rect(
                    self.list_rect.left + 5,
                    y - 2,
                    self.list_rect.width - 10,
                    line_height - 2
                )
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, highlight_rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, highlight_rect, 1)
            
            # Draw each column at fixed positions
            color = self.colors.GOLD if i == self.current_item else self.colors.WHITE
            
            # Skip special items (like Next Page for pagination)
            if display_str in ["Next Page"]:
                text = self.small_font.render(display_str, True, color)
                self.screen.blit(text, (item_col_x, y))
                continue
            
            # Parse the item data
            if item:
                # Type column
                type_text = self.normal_font.render(item.typ, True, color)
                self.screen.blit(type_text, (type_col_x, y))
                
                # Item name column
                item_text = self.normal_font.render(item.name, True, color)
                self.screen.blit(item_text, (item_col_x, y))
                
                # Cost column (buy mode only)
                if self.buy_or_sell == "Buy":
                    cost_text = self.normal_font.render(str(cost), True, color)
                    self.screen.blit(cost_text, (cost_col_x, y))
                
                # Owned column
                owned_text = self.normal_font.render(f"x {owned}", True, color)
                self.screen.blit(owned_text, (owned_col_x, y))
    
    def draw_mod(self):
        """Draw equipment modification comparison."""
        self.draw_semi_transparent_panel(self.mod_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.mod_rect, 2)
        
        if not self.item_list or self.current_item >= len(self.item_list):
            return
        
        display_str, item, _, _ = self.item_list[self.current_item]
        
        # Skip for non-items
        if display_str in ["Go Back", "Next Page"] or not item:
            return
        
        # Only show for equipment that can be equipped
        if not hasattr(item, 'typ') or item.typ not in ["Weapon", "OffHand", "Armor", "Accessory"]:
            return
        
        # Draw title
        title = self.normal_font.render("Equipment Modifications", True, self.colors.GOLD)
        title_x = self.mod_rect.centerx - title.get_width() // 2
        self.screen.blit(title, (title_x, self.mod_rect.top + 10))
        
        # Get stat comparison (cached to prevent recalculation on every blit)
        try:
            equip_slot = item.typ
            if item.typ == "Accessory":
                equip_slot = item.subtyp

            # Show not equippable message
            if not self.player_char.cls.equip_check(item, equip_slot):
                cant_text = self.normal_font.render("Can't Equip", True, self.colors.RED)
                cant_rect = cant_text.get_rect(center=(self.mod_rect.centerx, self.mod_rect.centery))
                self.screen.blit(cant_text, cant_rect)
                return
            
            # Only recalculate if the item selection changed
            if self.current_item != self.cached_item_index:
                self.cached_diff_str = self.player_char.equip_diff(item, equip_slot, buy=True)
                self.cached_item_index = self.current_item

            stat_diff_str = self.cached_diff_str
            
            if stat_diff_str:
                lines = stat_diff_str.splitlines()
                line_height = self.normal_font.get_height() + 4
                
                y = self.mod_rect.top + 40
                for line in lines:
                    if line.strip():
                        # Parse stat name and value
                        parts = [x.strip() for x in line.split('  ') if x.strip()]
                        if len(parts) >= 2:
                            stat_name = parts[0]
                            stat_value = parts[1]
                            
                            # Color code based on positive/negative
                            if stat_value.startswith('+'):
                                value_color = self.colors.GREEN
                            elif stat_value.startswith('-'):
                                value_color = self.colors.RED
                            else:
                                value_color = self.colors.WHITE
                            
                            # Draw stat name (left aligned)
                            name_text = self.normal_font.render(stat_name, True, self.colors.WHITE)
                            self.screen.blit(name_text, (self.mod_rect.left + 10, y))
                            
                            # Draw stat value (right aligned)
                            value_text = self.normal_font.render(stat_value, True, value_color)
                            value_x = self.mod_rect.right - value_text.get_width() - 10
                            self.screen.blit(value_text, (value_x, y))
                            
                            y += line_height
        except (KeyError, AttributeError):
            pass
    
    def draw_gold(self):
        """Draw player's current gold."""
        self.draw_semi_transparent_panel(self.gold_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.gold_rect, 2)
        
        gold_str = f"{self.player_char.gold}G"
        text = self.normal_font.render(gold_str, True, self.colors.GOLD)
        text_x = self.gold_rect.right - text.get_width() - 10
        text_y = self.gold_rect.centery - text.get_height() // 2
        self.screen.blit(text, (text_x, text_y))
    
    def draw_all(self, do_flip=True):
        """Draw all shop UI elements. Set do_flip=False when drawing as a background for overlays."""
        self.draw_background()
        self.draw_top()
        self.draw_options()
        self.draw_item_desc()
        self.draw_shop_list()
        self.draw_mod()
        self.draw_gold()
        if do_flip:
            pygame.display.flip()
    
    def update_item_list(self, itemdict, buy_or_sell):
        """
        Update the list of items to display.
        itemdict: Dictionary of items from items_module.items_dict
        buy_or_sell: "Buy" or "Sell"
        """
        self.buy_or_sell = buy_or_sell
        self.item_list = []
        self.current_item = 0
        self.scroll_offset = 0
        
        if buy_or_sell == "Buy":
            self._build_buy_list(itemdict)
        else:
            self._build_sell_list(itemdict)
    
    def _build_buy_list(self, itemdict):
        """Build item list for buying."""
        for typ, item_classes in itemdict.items():
            for item_class in item_classes:
                item = item_class()
                
                # Check class restrictions
                if hasattr(item, 'restriction') and item.restriction:
                    if self.player_char.cls.name not in item.restriction:
                        continue
                
                # Check rarity for town shops
                if self.player_char.in_town():
                    min_rarity = max(0.4, (1.0 - (0.02 * self.player_char.player_level())))
                    if item.rarity < min_rarity:
                        continue
                
                # Calculate adjusted cost based on charisma
                from src.core.character import scaled_decay_function
                adj_scale = scaled_decay_function(self.player_char.stats.charisma // 2)
                adj_cost = max(1, int(item.value * adj_scale))
                
                # Count owned items
                owned = 0
                if item.name in self.player_char.inventory:
                    owned = len(self.player_char.inventory[item.name])
                
                # Store item data (no formatting needed - we render at fixed positions)
                self.item_list.append((item.name, item, adj_cost, owned))
        
        # Add navigation options
        if len(self.item_list) > 19:
            # TODO: Implement pagination
            pass
    
    def _build_sell_list(self, itemdict):
        """Build item list for selling."""
        for name, items_list in itemdict.items():
            if not items_list:
                continue
            
            item = items_list[0]
            typ = item.typ
            owned = len(items_list)
            
            # Calculate sell price (half value, adjusted by charisma)
            sell_price = int((item.value // 2) * (1 + 0.025 * self.player_char.stats.charisma))
            
            # Store item data (no formatting needed - we render at fixed positions)
            self.item_list.append((name, item, sell_price, owned))
    
    def navigate_options(self):
        """Navigate the main menu options (Buy, Sell, Quests, Leave)."""
        while True:
            self.draw_all()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "Leave"
                    elif event.key == pygame.K_UP:
                        self.current_option = (self.current_option - 1) % len(self.options_list)
                    elif event.key == pygame.K_DOWN:
                        self.current_option = (self.current_option + 1) % len(self.options_list)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.options_list[self.current_option]
            
            self.presenter.clock.tick(30)
    
    def navigate_items(self):
        """Navigate the item list and return selected item."""
        # Handle empty item list
        if not self.item_list:
            return None
            
        while True:
            self.draw_all()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_UP:
                        self.current_item = (self.current_item - 1) % len(self.item_list)
                        # Adjust scroll offset
                        if self.current_item < self.scroll_offset:
                            self.scroll_offset = self.current_item
                    elif event.key == pygame.K_DOWN:
                        self.current_item = (self.current_item + 1) % len(self.item_list)
                        # Adjust scroll offset
                        if self.current_item >= self.scroll_offset + 19:
                            self.scroll_offset = self.current_item - 18
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        display_str, item, cost, owned = self.item_list[self.current_item]
                        return (display_str, item, cost, owned)
            
            self.presenter.clock.tick(30)
