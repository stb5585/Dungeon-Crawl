"""
Generic location menu screen for town locations (church, barracks, inn).
Provides a consistent menu interface with background support, using ShopScreen-style layout.
"""

import pygame

from .town_base import TownScreenBase


class LocationMenuScreen(TownScreenBase):
    """
    A generic menu screen for town locations.
    Uses a two-column layout similar to ShopScreen: options on left, content area on right.
    """
    
    def __init__(self, presenter, location_name):
        super().__init__(presenter)
        self.location_name = location_name
        
        # State
        self.current_option = 0
        self.scroll_offset = 0
        self.options_list = []
    
    def draw_all(self):
        """Draw the location menu interface."""
        self.draw_background()
        
        self.draw_top()
        self.draw_options()
        self.draw_content()
        pygame.display.flip()

    def draw_top(self):
        """Draw the top header with location name."""
        top_height = self.height // 12
        top_rect = pygame.Rect(0, 0, self.width, top_height)
        
        self.draw_semi_transparent_panel(top_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, top_rect, 2)
        
        # Center the location name
        text = self.large_font.render(self.location_name, True, self.colors.GOLD)
        text_rect = text.get_rect(center=(self.width // 2, top_rect.centery))
        self.screen.blit(text, text_rect)
    
    def draw_options(self):
        """Draw the menu options on the left side."""
        top_height = self.height // 12
        options_width = self.width // 3
        options_height = self.height // 4
        options_y = top_height
        options_rect = pygame.Rect(0, options_y, options_width, options_height)
        
        self.draw_semi_transparent_panel(options_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, options_rect, 2)
        
        # Calculate spacing for options
        num_options = len(self.options_list)
        option_height = options_rect.height // (num_options + 1)
        
        for idx, option in enumerate(self.options_list):
            # Highlight selected option
            color = self.colors.GOLD if idx == self.current_option else self.colors.WHITE
            
            # Draw option text centered
            text = self.normal_font.render(option, True, color)
            text_x = options_rect.centerx - text.get_width() // 2
            text_y = options_rect.top + (idx + 1) * option_height
            
            # Highlight background for selected
            if idx == self.current_option:
                highlight_pad_x = 12
                highlight_pad_y = 6
                highlight_rect = pygame.Rect(
                    options_rect.left + highlight_pad_x,
                    text_y - highlight_pad_y,
                    options_rect.width - (highlight_pad_x * 2),
                    text.get_height() + (highlight_pad_y * 2)
                )
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, highlight_rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, highlight_rect, 1)
            
            self.screen.blit(text, (text_x, text_y))
    
    def draw_content(self, content_text="", items_data=None):
        """Draw the content area on the right side with optional text or formatted items."""
        top_height = self.height // 12
        content_width = 2 * self.width // 3
        content_height = self.height - top_height
        content_x = self.width // 3
        content_y = top_height
        content_rect = pygame.Rect(content_x, content_y, content_width, content_height)
        
        self.draw_semi_transparent_panel(content_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, content_rect, 2)
        
        # Handle structured items data with proper alignment and scrolling
        if items_data:
            font = self.large_font
            line_height = 28
            
            # Calculate max visible items based on content height
            max_visible = (content_height - 80) // line_height  # Reserve space for top/bottom padding
            
            # Determine visible window of items
            visible_items = items_data[self.scroll_offset:self.scroll_offset + max_visible]
            
            text_y = content_rect.top + 40  # Start with some padding
            
            # Define column positions
            cursor_x = content_rect.left + 20
            item_x = cursor_x + 20
            quantity_x = content_rect.right - 80  # Right-aligned quantity column
            
            for idx, item_name, quantity, is_selected in visible_items:
                # Draw cursor for selected item
                if is_selected:
                    cursor = font.render(">", True, self.colors.GOLD)
                    self.screen.blit(cursor, (cursor_x, text_y))
                
                # Draw item name
                name_surface = font.render(item_name, True, self.colors.WHITE)
                self.screen.blit(name_surface, (item_x, text_y))
                
                # Draw quantity (right-aligned) if not zero
                if quantity > 0:
                    qty_text = f"x{quantity}"
                    qty_surface = font.render(qty_text, True, self.colors.WHITE)
                    qty_rect = qty_surface.get_rect(right=quantity_x, top=text_y)
                    self.screen.blit(qty_surface, qty_rect)
                
                text_y += line_height
            
            return
        
        # Draw content text if provided
        if content_text:
            text_x = content_rect.left + 20
            text_y = content_rect.top + 20
            
            # Check if this is an item list (contains cursor marker or item quantity pattern)
            import re
            is_item_list = '►' in content_text or bool(re.search(r'\bx\s*\d+\b', content_text))
            
            # Wrap text and render
            lines = content_text.split('\n')
            for line in lines:
                # For item lists, use monospace font and don't wrap
                if is_item_list:
                    # Use a smaller monospace-like font for item lists
                    font = self.large_font
                    text_surface = font.render(line, True, self.colors.WHITE)
                    self.screen.blit(text_surface, (text_x, text_y))
                    text_y += 28
                else:
                    # For regular text, wrap long lines
                    import textwrap
                    wrapped_lines = textwrap.wrap(line, width=50)
                    for wrapped_line in wrapped_lines:
                        text_surface = self.large_font.render(wrapped_line, True, self.colors.WHITE)
                        self.screen.blit(text_surface, (text_x, text_y))
                        text_y += 25
    
    def navigate(self, options, reset_cursor: bool = True):
        """
        Navigate the menu and return the selected option index.
        
        Args:
            options: List of menu options
            reset_cursor: When False, retain current selection index
        
        Returns:
            Index of selected option, or None if escaped
        """
        self.options_list = options
        if reset_cursor:
            self.current_option = 0
            self.scroll_offset = 0
        else:
            # Clamp to valid range in case options changed
            if self.options_list:
                self.current_option = max(0, min(self.current_option, len(self.options_list) - 1))
            else:
                self.current_option = 0
            self.scroll_offset = 0  # Reset scroll when options change
        
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
                        self.current_option = (self.current_option - 1) % len(self.options_list)
                    elif event.key == pygame.K_DOWN:
                        self.current_option = (self.current_option + 1) % len(self.options_list)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.current_option
            
            self.presenter.clock.tick(30)

    def display_items_list(self, items_data):
        """
        Display a list of items with quantities in the content area.
        items_data: list of tuples (item_name, quantity)
        """
        
        # Build items display text
        lines = []
        for item_name, quantity in items_data:
            lines.append(f"{item_name:30} x{quantity:3}")
        
        items_text = "\n".join(lines)
        
        # Continuously draw with items list displayed
        while True:
            self.draw_background()
            self.draw_top()
            self.draw_options()
            self.draw_content(items_text)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # Exit display on any key
                    return
            
            self.presenter.clock.tick(30)

    def draw_options_instructions(self):
        """Draw instructions only on the left side, without menu highlighting."""
        top_height = self.height // 12
        left_width = self.width // 3
        options_rect = pygame.Rect(0, top_height, left_width, self.height - top_height)
        
        self.draw_semi_transparent_panel(options_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, options_rect, 2)
        
        # Draw instructions text
        instr_font = self.normal_font
        instructions = [
            "[Use arrows to select]",
            "[Press ESC to go back]"
        ]
        
        y = options_rect.top + 20
        for instruction in instructions:
            text = instr_font.render(instruction, True, self.colors.GOLD)
            text_rect = text.get_rect(centerx=options_rect.centerx, top=y)
            self.screen.blit(text, text_rect)
            y += 40

    def navigate_with_content(self, items_data):
        """
        Navigate menu with items displayed in the right content area.
        items_data: list of tuples (item_name, quantity) to display and navigate on right
        """
        
        # Ensure indices are valid for the current items_data
        if items_data:
            self.current_option = min(self.current_option, max(0, len(items_data) - 1))
            self.scroll_offset = min(self.scroll_offset, max(0, len(items_data) - 1))
        else:
            self.current_option = 0
            self.scroll_offset = 0
        
        # Calculate max visible items
        top_height = self.height // 12
        content_height = self.height - top_height
        line_height = 28
        max_visible = (content_height - 80) // line_height  # Reserve space for top/bottom padding
        
        while True:
            self.draw_background()
            self.draw_top()
            self.draw_options_instructions()
            
            # Build structured items data with selection state
            formatted_items = []
            for idx, (item_name, quantity) in enumerate(items_data):
                is_selected = (idx == self.current_option)
                formatted_items.append((idx, item_name, quantity, is_selected))
            
            self.draw_content(items_data=formatted_items)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_UP:
                        self.current_option = (self.current_option - 1) % len(items_data)
                        # Adjust scroll offset
                        if self.current_option < self.scroll_offset:
                            self.scroll_offset = self.current_option
                        elif self.current_option == len(items_data) - 1:
                            # Wrapped to bottom
                            self.scroll_offset = max(0, len(items_data) - max_visible)
                    elif event.key == pygame.K_DOWN:
                        self.current_option = (self.current_option + 1) % len(items_data)
                        # Adjust scroll offset
                        if self.current_option >= self.scroll_offset + max_visible:
                            self.scroll_offset = self.current_option - max_visible + 1
                        elif self.current_option == 0:
                            # Wrapped to top
                            self.scroll_offset = 0
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.current_option
            
            self.presenter.clock.tick(30)
