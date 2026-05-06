"""
Loot Popup Interface for Pygame.
Displays chest contents with visual flair.
"""
import pygame


class LootPopup:
    """Display loot from chests with an attractive popup."""
    
    def __init__(self, screen, presenter):
        self.screen = screen
        self.presenter = presenter
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.bg_overlay = (0, 0, 0, 180)  # Semi-transparent black
        self.panel_bg = (40, 30, 20)  # Dark wood color
        self.panel_border = (139, 90, 43)  # Light wood/bronze
        self.gold_color = (255, 215, 0)
        self.text_color = (220, 220, 220)
        self.rarity_colors = {
            'common': (200, 200, 200),
            'uncommon': (100, 255, 100),
            'rare': (100, 150, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 165, 0),
            'ultimate': (255, 50, 50)
        }
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.item_font = pygame.font.Font(None, 36)
        self.desc_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Animation
        self.animation_time = 0
        self.max_animation_time = 30  # frames
    
    def show_loot(
        self,
        items,
        chest_type="Chest",
        background_draw_func=None,
        flush_events: bool = False,
        require_key_release: bool = False,
    ):
        """
        Display loot popup and wait for player to acknowledge.
        
        Args:
            items: Single item or list of items found in chest
            chest_type: Type of chest (for display purposes)
            background_draw_func: Optional function to draw the background
        """
        # Normalize to list
        if not isinstance(items, list):
            items = [items] if items else []
        
        # Filter out None items
        items = [item for item in items if item is not None]
        
        if not items:
            return self._show_empty_chest(
                chest_type,
                background_draw_func,
                flush_events=flush_events,
                require_key_release=require_key_release,
            )

        if background_draw_func is None:
            background = self._get_background_surface()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))

        if flush_events:
            pygame.event.clear()
        input_armed = not require_key_release
        
        self.animation_time = 0
        waiting = True
        clock = pygame.time.Clock()
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type in (pygame.KEYUP, pygame.MOUSEBUTTONUP) and require_key_release:
                    input_armed = True
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if not input_armed:
                        continue
                    if self.animation_time >= self.max_animation_time:
                        waiting = False
            
            background_draw_func()
            self._render_loot_popup(items, chest_type)
            pygame.display.flip()
            
            if self.animation_time < self.max_animation_time:
                self.animation_time += 1
            
            clock.tick(60)
    
    def _show_empty_chest(
        self,
        chest_type,
        background_draw_func=None,
        flush_events: bool = False,
        require_key_release: bool = False,
    ):
        """Show empty chest message."""
        waiting = True

        if background_draw_func is None:
            background = self._get_background_surface()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))

        if flush_events:
            pygame.event.clear()
        input_armed = not require_key_release
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type in (pygame.KEYUP, pygame.MOUSEBUTTONUP) and require_key_release:
                    input_armed = True
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if not input_armed:
                        continue
                    waiting = False
            
            background_draw_func()
            self._render_empty_chest(chest_type)
            pygame.display.flip()
    
    def _render_loot_popup(self, items, chest_type):
        """Render the loot popup with items."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_overlay)
        self.screen.blit(overlay, (0, 0))
        
        # Calculate popup size based on number of items
        popup_width = 600
        popup_height = min(500, 200 + len(items) * 150)
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        
        # Animation: scale in
        if self.animation_time < self.max_animation_time:
            scale = self.animation_time / self.max_animation_time
            scale = self._ease_out_back(scale)  # Bouncy effect
            current_width = int(popup_width * scale)
            current_height = int(popup_height * scale)
            popup_x = (self.width - current_width) // 2
            popup_y = (self.height - current_height) // 2
        else:
            current_width = popup_width
            current_height = popup_height
        
        # Draw popup panel with border
        border_rect = pygame.Rect(popup_x - 5, popup_y - 5, current_width + 10, current_height + 10)
        pygame.draw.rect(self.screen, self.panel_border, border_rect, border_radius=10)
        panel_rect = pygame.Rect(popup_x, popup_y, current_width, current_height)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect, border_radius=8)
        
        if self.animation_time < self.max_animation_time:
            return  # Don't draw contents during animation
        
        # Title
        title_text = self.title_font.render(f"{chest_type} Opened!", True, self.gold_color)
        title_rect = title_text.get_rect(centerx=popup_x + current_width // 2, top=popup_y + 20)
        self.screen.blit(title_text, title_rect)
        
        # Draw items
        y = popup_y + 80
        for item in items:
            y = self._render_item(item, popup_x, y, current_width)
            y += 20  # Spacing between items
        
        # Footer instruction
        if self.animation_time >= self.max_animation_time:
            footer = self.small_font.render("Press any key to continue...", True, self.text_color)
            footer_rect = footer.get_rect(centerx=popup_x + current_width // 2, 
                                         bottom=popup_y + current_height - 15)
            self.screen.blit(footer, footer_rect)
    
    def _render_item(self, item, x, y, panel_width):
        """Render a single item in the loot display."""
        # Determine rarity color
        rarity_color = self.text_color
        if hasattr(item, 'rarity'):
            # Rarity is a float between 0-1, convert to category
            if item.rarity <= 0.1:
                rarity_color = self.rarity_colors['legendary']
            elif item.rarity <= 0.3:
                rarity_color = self.rarity_colors['epic']
            elif item.rarity <= 0.5:
                rarity_color = self.rarity_colors['rare']
            elif item.rarity <= 0.7:
                rarity_color = self.rarity_colors['uncommon']
            else:
                rarity_color = self.rarity_colors['common']
        
        # Item name
        name_text = self.item_font.render(item.name, True, rarity_color)
        name_rect = name_text.get_rect(centerx=x + panel_width // 2, top=y)
        self.screen.blit(name_text, name_rect)
        y += 40
        
        # Item description (wrapped)
        if hasattr(item, 'description') and item.description:
            desc_lines = item.description.split('\n')
            for line in desc_lines[:3]:  # Limit to 3 lines
                desc_text = self.desc_font.render(line.strip(), True, self.text_color)
                desc_rect = desc_text.get_rect(centerx=x + panel_width // 2, top=y)
                self.screen.blit(desc_text, desc_rect)
                y += 25
        
        # Item stats
        stats = []
        if hasattr(item, 'value') and item.value > 0:
            stats.append(f"Value: {item.value}g")
        
        if hasattr(item, 'damage'):
            stats.append(f"Damage: {item.damage}")
        if hasattr(item, 'armor'):
            stats.append(f"Armor: {item.armor}")
        if hasattr(item, 'subtyp'):
            stats.append(f"Type: {item.subtyp}")
        
        if stats:
            y += 5
            stats_text = " | ".join(stats)
            stats_render = self.small_font.render(stats_text, True, self.gold_color)
            stats_rect = stats_render.get_rect(centerx=x + panel_width // 2, top=y)
            self.screen.blit(stats_render, stats_rect)
            y += 25
        
        return y
    
    def _render_empty_chest(self, chest_type):
        """Render empty chest message."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_overlay)
        self.screen.blit(overlay, (0, 0))
        
        # Popup panel
        popup_width = 400
        popup_height = 200
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        
        border_rect = pygame.Rect(popup_x - 5, popup_y - 5, popup_width + 10, popup_height + 10)
        pygame.draw.rect(self.screen, self.panel_border, border_rect, border_radius=10)
        panel_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect, border_radius=8)
        
        # Title
        title_text = self.title_font.render("Empty Chest", True, (150, 150, 150))
        title_rect = title_text.get_rect(centerx=popup_x + popup_width // 2, top=popup_y + 40)
        self.screen.blit(title_text, title_rect)
        
        # Message
        msg_text = self.desc_font.render("The chest contains nothing of value.", True, self.text_color)
        msg_rect = msg_text.get_rect(centerx=popup_x + popup_width // 2, top=popup_y + 90)
        self.screen.blit(msg_text, msg_rect)
        
        # Footer
        footer = self.small_font.render("Press any key to continue...", True, self.text_color)
        footer_rect = footer.get_rect(centerx=popup_x + popup_width // 2, 
                                     bottom=popup_y + popup_height - 20)
        self.screen.blit(footer, footer_rect)
    
    def _ease_out_back(self, t):
        """Easing function for bouncy animation."""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    def show_unlock_prompt(
        self,
        locked_type="chest",
        background_draw_func=None,
        flush_events: bool = False,
        require_key_release: bool = False,
    ):
        """
        Show prompt asking if player wants to use a key.
        
        Args:
            locked_type: "chest" or "door"
        
        Returns:
            bool: True if player wants to use key, False otherwise
            background_draw_func: Optional function to draw the background
        """
        key_name = "Old Key" if locked_type == "door" else "Key"
        options = [f"Use {key_name}", "Cancel"]
        selected = 0
        waiting = True

        if background_draw_func is None:
            background = self._get_background_surface()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))

        if flush_events:
            pygame.event.clear()
        input_armed = not require_key_release
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type in (pygame.KEYUP, pygame.MOUSEBUTTONUP) and require_key_release:
                    input_armed = True
                elif event.type == pygame.KEYDOWN:
                    if not input_armed:
                        continue
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        return selected == 0
                    elif event.key == pygame.K_ESCAPE:
                        return False
            
            background_draw_func()
            self._render_unlock_prompt(locked_type, options, selected)
            pygame.display.flip()

    def _get_background_surface(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()
    
    def _render_unlock_prompt(self, locked_type, options, selected):
        """Render the unlock prompt."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_overlay)
        self.screen.blit(overlay, (0, 0))
        
        # Popup panel
        popup_width = 400
        popup_height = 250
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        
        border_rect = pygame.Rect(popup_x - 5, popup_y - 5, popup_width + 10, popup_height + 10)
        pygame.draw.rect(self.screen, self.panel_border, border_rect, border_radius=10)
        panel_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect, border_radius=8)
        
        # Title
        title_text = self.title_font.render("Locked!", True, (255, 100, 100))
        title_rect = title_text.get_rect(centerx=popup_x + popup_width // 2, top=popup_y + 20)
        self.screen.blit(title_text, title_rect)
        
        # Message
        msg = f"This {locked_type} is locked."
        msg_text = self.desc_font.render(msg, True, self.text_color)
        msg_rect = msg_text.get_rect(centerx=popup_x + popup_width // 2, top=popup_y + 70)
        self.screen.blit(msg_text, msg_rect)
        
        msg2_text = self.desc_font.render("Use a Key to unlock it?", True, self.text_color)
        msg2_rect = msg2_text.get_rect(centerx=popup_x + popup_width // 2, top=popup_y + 95)
        self.screen.blit(msg2_text, msg2_rect)
        
        # Options
        y = popup_y + 135
        for i, option in enumerate(options):
            if i == selected:
                # Highlight
                highlight_rect = pygame.Rect(popup_x + 50, y - 5, popup_width - 100, 35)
                pygame.draw.rect(self.screen, self.panel_border, highlight_rect)
                pygame.draw.rect(self.screen, self.gold_color, highlight_rect, 2)
            
            option_text = self.item_font.render(option, True, self.text_color)
            option_rect = option_text.get_rect(centerx=popup_x + popup_width // 2, top=y)
            self.screen.blit(option_text, option_rect)
            y += 45
        
        # Instructions
        footer = self.small_font.render("Arrow Keys: Navigate | Enter: Select | ESC: Cancel", 
                                       True, self.text_color)
        footer_rect = footer.get_rect(centerx=popup_x + popup_width // 2, 
                                     bottom=popup_y + popup_height - 10)
        self.screen.blit(footer, footer_rect)
